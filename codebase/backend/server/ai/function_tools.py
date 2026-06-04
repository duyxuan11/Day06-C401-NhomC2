"""
Gemini Function Calling tools for WonderPath AI chatbot.

Defines tool declarations and execution logic so the AI can dynamically
fetch park data (attractions, weather, time) during a conversation.
"""

import json
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
from server.utils.safety_rules import get_safety_flags


# ---------------------------------------------------------------------------
# Tool declarations (Gemini function_declarations format)
# ---------------------------------------------------------------------------

TOOL_DECLARATIONS = [
    {
        "name": "get_nearby_attractions",
        "description": (
            "Lấy danh sách các điểm vui chơi, nhà hàng, khu nghỉ gần một trạm QR cụ thể. "
            "Kết quả bao gồm tên, khoảng cách, thời gian chờ, trạng thái hoạt động, "
            "mức độ cảm giác mạnh, giới hạn chiều cao/tuổi."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "station_id": {
                    "type": "string",
                    "description": "Mã trạm QR (ví dụ: qr_station_01, qr_station_02, ...)",
                }
            },
            "required": ["station_id"],
        },
    },
    {
        "name": "get_weather",
        "description": (
            "Lấy thông tin thời tiết hiện tại tại công viên. "
            "Trả về điều kiện (sunny/rainy/stormy), nhiệt độ, mức cảnh báo."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_current_time",
        "description": (
            "Lấy thời gian hiện tại tại công viên (múi giờ Asia/Ho_Chi_Minh). "
            "Trả về giờ:phút và trạng thái mở/đóng cửa công viên (09:00-21:00)."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_attraction_detail",
        "description": (
            "Lấy thông tin chi tiết về một điểm vui chơi/nhà hàng cụ thể: "
            "mô tả, khu vực, loại hình, mức cảm giác mạnh, giới hạn chiều cao/tuổi, "
            "thời gian chơi, trạng thái hoạt động hiện tại."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "attraction_id": {
                    "type": "string",
                    "description": "Mã ID điểm vui chơi (ví dụ: att_magic_castle, att_roller_coaster, ...)",
                }
            },
            "required": ["attraction_id"],
        },
    },
]


# ---------------------------------------------------------------------------
# Helper: parse time
# ---------------------------------------------------------------------------

def _parse_time_to_minutes(time_str: str) -> int:
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError, AttributeError):
        return -1


def _enrich_realtime(realtime: Dict[str, Any], current_time: str) -> Dict[str, Any]:
    """Add starts_in_mins and is_upcoming_soon to a realtime status entry."""
    rt = deepcopy(realtime) if realtime else {}
    curr_mins = _parse_time_to_minutes(current_time)

    starts_in_mins = None
    is_upcoming_soon = False
    showtimes = rt.get("upcoming_showtimes") or []

    if showtimes and curr_mins >= 0:
        valid_diffs = []
        for showtime in showtimes:
            show_mins = _parse_time_to_minutes(showtime)
            if show_mins >= 0:
                diff = show_mins - curr_mins
                if diff >= 0:
                    valid_diffs.append((diff, showtime))
        if valid_diffs:
            valid_diffs.sort()
            starts_in_mins = valid_diffs[0][0]
            is_upcoming_soon = starts_in_mins <= 30

    rt["starts_in_mins"] = starts_in_mins
    rt["is_upcoming_soon"] = is_upcoming_soon
    return rt


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def execute_function_call(
    name: str,
    args: Dict[str, Any],
    mock_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Execute a function call and return JSON string result."""
    mock_data = mock_data or load_mock_data()

    if name == "get_nearby_attractions":
        return _exec_get_nearby_attractions(args, mock_data)
    elif name == "get_weather":
        return _exec_get_weather(mock_data)
    elif name == "get_current_time":
        return _exec_get_current_time()
    elif name == "get_attraction_detail":
        return _exec_get_attraction_detail(args, mock_data)
    else:
        return json.dumps({"error": f"Unknown function: {name}"}, ensure_ascii=False)


def _exec_get_nearby_attractions(args: Dict[str, Any], mock_data: Dict[str, Any]) -> str:
    station_id = args.get("station_id", "qr_station_01")
    station = get_station_by_id(mock_data["stations"], station_id)

    if not station:
        return json.dumps(
            {"error": f"Không tìm thấy trạm '{station_id}'. Các trạm có sẵn: qr_station_01..04"},
            ensure_ascii=False,
        )

    current_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")
    results = []

    for nearby in station.get("nearby_attractions", []):
        att_id = nearby.get("attraction_id")
        attraction = get_attraction_by_id(mock_data["attractions"], att_id)
        if not attraction:
            continue

        realtime = get_realtime_status_by_id(mock_data["realtime_status"], att_id)
        realtime_enriched = _enrich_realtime(realtime, current_time)

        results.append({
            "id": attraction["id"],
            "name": attraction["name"],
            "zone": attraction.get("zone"),
            "category": attraction.get("category"),
            "indoor_outdoor": attraction.get("indoor_outdoor"),
            "thrill_level": attraction.get("thrill_level"),
            "constraints": attraction.get("constraints"),
            "description": attraction.get("description"),
            "duration_mins": attraction.get("duration_mins"),
            "distance_meters": nearby.get("distance_meters"),
            "walking_time_mins": nearby.get("walking_time_mins"),
            "status": realtime_enriched.get("status", "unknown"),
            "wait_time_mins": realtime_enriched.get("wait_time_mins", 0),
            "crowd_level": realtime_enriched.get("crowd_level", "unknown"),
            "upcoming_showtimes": realtime_enriched.get("upcoming_showtimes", []),
            "is_upcoming_soon": realtime_enriched.get("is_upcoming_soon", False),
        })

    return json.dumps(
        {
            "station": {"id": station["station_id"], "name": station["name"], "zone": station.get("zone")},
            "current_time": current_time,
            "nearby_attractions": results,
        },
        ensure_ascii=False,
    )


def _exec_get_weather(mock_data: Dict[str, Any]) -> str:
    real_weather = fetch_real_weather()
    if real_weather:
        weather = real_weather
    else:
        weather = mock_data.get("weather", {}).get("current", {})

    return json.dumps(
        {
            "condition": weather.get("condition", "sunny"),
            "temperature_c": weather.get("temperature_c", 30),
            "warning_level": weather.get("warning_level", "none"),
        },
        ensure_ascii=False,
    )


def _exec_get_current_time() -> str:
    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    current_time = now.strftime("%H:%M")
    curr_mins = now.hour * 60 + now.minute
    is_park_open = 9 * 60 <= curr_mins <= 21 * 60

    return json.dumps(
        {
            "current_time": current_time,
            "date": now.strftime("%Y-%m-%d"),
            "day_of_week": now.strftime("%A"),
            "is_park_open": is_park_open,
            "park_hours": "09:00 - 21:00",
        },
        ensure_ascii=False,
    )


def _exec_get_attraction_detail(args: Dict[str, Any], mock_data: Dict[str, Any]) -> str:
    att_id = args.get("attraction_id", "")
    attraction = get_attraction_by_id(mock_data["attractions"], att_id)

    if not attraction:
        all_ids = [a["id"] for a in mock_data["attractions"]]
        return json.dumps(
            {"error": f"Không tìm thấy '{att_id}'. Các ID có sẵn: {', '.join(all_ids)}"},
            ensure_ascii=False,
        )

    realtime = get_realtime_status_by_id(mock_data["realtime_status"], att_id)
    current_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")
    realtime_enriched = _enrich_realtime(realtime, current_time)

    return json.dumps(
        {
            **attraction,
            "realtime_status": {
                "status": realtime_enriched.get("status", "unknown"),
                "wait_time_mins": realtime_enriched.get("wait_time_mins", 0),
                "crowd_level": realtime_enriched.get("crowd_level", "unknown"),
                "upcoming_showtimes": realtime_enriched.get("upcoming_showtimes", []),
                "is_upcoming_soon": realtime_enriched.get("is_upcoming_soon", False),
            },
        },
        ensure_ascii=False,
    )
