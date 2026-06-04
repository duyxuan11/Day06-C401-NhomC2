from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from server.services.mock_data_service import (
    get_attraction_by_id,
    get_realtime_status_by_id,
    get_station_by_id,
    load_mock_data,
)
from server.services.weather_service import fetch_real_weather
from server.utils.safety_rules import build_safety_summary, get_safety_flags


def get_current_time() -> str:
    return datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")


def parse_time_to_minutes(time_str: str) -> int:
    """Parses 'HH:MM' string to minutes since start of day."""
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError, AttributeError):
        return -1


def apply_status_override(
    realtime_status: Dict[str, Any],
    status_override: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    next_status = deepcopy(realtime_status)
    if not status_override:
        return next_status

    status_map = {
        item.get("attraction_id"): item
        for item in next_status.get("attractions", [])
    }

    for attraction_id, override in status_override.items():
        current = status_map.get(attraction_id)
        if current is not None:
            current.update(override)
        else:
            next_status.setdefault("attractions", []).append(
                {"attraction_id": attraction_id, **override}
            )

    return next_status


def build_nearby_attractions(
    station: Dict[str, Any],
    attractions: List[Dict[str, Any]],
    realtime_status: Dict[str, Any],
    user_profile: Optional[Dict[str, Any]],
    weather: Dict[str, Any],
    current_time: str,
) -> List[Dict[str, Any]]:
    nearby_attractions = []

    for nearby in station.get("nearby_attractions", []):
        attraction = get_attraction_by_id(attractions, nearby.get("attraction_id"))
        if not attraction:
            continue

        realtime = get_realtime_status_by_id(realtime_status, nearby.get("attraction_id"))
        realtime_copy = deepcopy(realtime) if realtime else {}

        # Time-aware Show Scheduler Logic
        starts_in_mins = None
        is_upcoming_soon = False
        showtimes = realtime_copy.get("upcoming_showtimes") or []
        curr_mins = parse_time_to_minutes(current_time)

        # Check if park is open (09:00 - 21:00). If closed, force attraction status to closed.
        if curr_mins >= 0 and not (9 * 60 <= curr_mins <= 21 * 60):
            realtime_copy["status"] = "closed"

        if showtimes and curr_mins >= 0:
            valid_diffs = []
            for showtime in showtimes:
                show_mins = parse_time_to_minutes(showtime)
                if show_mins >= 0:
                    diff = show_mins - curr_mins
                    if diff >= 0:  # Show is in the future or starting now
                        valid_diffs.append((diff, showtime))
            
            if valid_diffs:
                valid_diffs.sort()
                starts_in_mins = valid_diffs[0][0]
                is_upcoming_soon = starts_in_mins <= 30

        realtime_copy["starts_in_mins"] = starts_in_mins
        realtime_copy["is_upcoming_soon"] = is_upcoming_soon

        nearby_attractions.append(
            {
                "attraction": attraction,
                "distance_meters": nearby.get("distance_meters"),
                "walking_time_mins": nearby.get("walking_time_mins"),
                "realtime_status": realtime_copy,
                "safety_flags": get_safety_flags(attraction, realtime_copy, user_profile, weather),
            }
        )

    return sorted(
        nearby_attractions,
        key=lambda item: item.get("distance_meters") or 0,
    )


def build_wonder_path_context(
    input_data: Optional[Dict[str, Any]] = None,
    mock_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    input_data = input_data or {}
    mock_data = mock_data or load_mock_data()

    current_station_id = (
        input_data.get("current_station_id")
        or input_data.get("qr_station_id")
        or "qr_station_01"
    )
    current_time = (
        input_data.get("current_time")
        or input_data.get("scan_time")
        or get_current_time()
    )
    user_profile = input_data.get("user_profile")
    
    # Try fetching real weather, fallback to mock if override is absent
    weather = input_data.get("weather_override")
    if not weather:
        real_weather = fetch_real_weather()
        weather = real_weather or mock_data["weather"]["current"]

    realtime_status = apply_status_override(
        mock_data["realtime_status"],
        input_data.get("status_override"),
    )

    station = get_station_by_id(mock_data["stations"], current_station_id)
    if not station:
        raise ValueError(f"Unknown station id: {current_station_id}")

    nearby_attractions = build_nearby_attractions(
        station,
        mock_data["attractions"],
        realtime_status,
        user_profile,
        weather,
        current_time,
    )

    return {
        "current_station_id": current_station_id,
        "current_time": current_time,
        "user_profile": user_profile,
        "station": station,
        "weather": weather,
        "realtime_status": realtime_status,
        "nearby_attractions": nearby_attractions,
        "safety_summary": build_safety_summary(nearby_attractions, user_profile, weather),
    }


