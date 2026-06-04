from typing import Any, Dict, List, Optional


MAX_WAIT_TIME_MINS = 45


def is_bad_weather(weather: Optional[Dict[str, Any]]) -> bool:
    return bool(weather and weather.get("warning_level") == "red")


def is_outdoor(attraction: Optional[Dict[str, Any]]) -> bool:
    return bool(attraction and attraction.get("indoor_outdoor") == "outdoor")


def get_wait_time(realtime_status: Optional[Dict[str, Any]]) -> int:
    if not realtime_status:
        return 0
    return int(realtime_status.get("wait_time_mins") or 0)


def is_unavailable(realtime_status: Optional[Dict[str, Any]]) -> bool:
    if not realtime_status:
        return False
    return realtime_status.get("status") in {"maintenance", "closed"}


def has_too_long_wait(realtime_status: Optional[Dict[str, Any]]) -> bool:
    return get_wait_time(realtime_status) > MAX_WAIT_TIME_MINS


def violates_height_limit(
    attraction: Dict[str, Any],
    user_profile: Optional[Dict[str, Any]],
) -> bool:
    if not user_profile or not user_profile.get("min_height_cm"):
        return False

    constraints = attraction.get("constraints") or {}
    min_height = constraints.get("min_height_cm")
    return bool(min_height and user_profile["min_height_cm"] < min_height)


def is_too_thrilling(
    attraction: Dict[str, Any],
    user_profile: Optional[Dict[str, Any]],
) -> bool:
    if not user_profile:
        return False

    thrill_level = attraction.get("thrill_level")
    if user_profile.get("has_elderly") and thrill_level != "low":
        return True

    return (
        user_profile.get("group_type") == "family_with_kids"
        and thrill_level == "high"
    )


def get_safety_flags(
    attraction: Dict[str, Any],
    realtime_status: Optional[Dict[str, Any]],
    user_profile: Optional[Dict[str, Any]],
    weather: Dict[str, Any],
) -> List[str]:
    flags = []

    if is_bad_weather(weather) and is_outdoor(attraction) and attraction.get("category") != "rest_area":
        flags.append("blocked_by_red_weather")

    if is_unavailable(realtime_status):
        flags.append("blocked_by_maintenance")

    if has_too_long_wait(realtime_status):
        flags.append("blocked_by_long_wait")

    if violates_height_limit(attraction, user_profile):
        flags.append("blocked_by_height_limit")

    if is_too_thrilling(attraction, user_profile):
        flags.append("blocked_by_profile_risk")

    return flags


def build_safety_summary(
    nearby_attractions: List[Dict[str, Any]],
    user_profile: Optional[Dict[str, Any]],
    weather: Dict[str, Any],
) -> Dict[str, Any]:
    blocked = [
        {
            "id": item["attraction"].get("id"),
            "name": item["attraction"].get("name"),
            "flags": item.get("safety_flags", []),
        }
        for item in nearby_attractions
        if item.get("safety_flags")
    ]

    return {
        "mode": "emergency_weather" if is_bad_weather(weather) else "normal",
        "user_profile_missing": not bool(user_profile),
        "max_wait_time_mins": MAX_WAIT_TIME_MINS,
        "blocked": blocked,
    }

