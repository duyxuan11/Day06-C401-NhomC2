import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

# Coords of VinWonders Nam Hoi An
DEFAULT_LAT = 15.8239
DEFAULT_LON = 108.3846

def fetch_real_weather(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time weather using Open-Meteo API (free, no API key needed).
    Maps raw metrics to WonderPath weather structure.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,precipitation,weather_code,wind_speed_10m&"
        f"timezone=Asia/Ho_Chi_Minh"
    )

    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "WonderPath-Agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        current = data.get("current", {})
        temp = current.get("temperature_2m", 30.0)
        precip = current.get("precipitation", 0.0)
        code = current.get("weather_code", 0)
        wind = current.get("wind_speed_10m", 0.0)

        # Map WMO weather code and precipitation to condition & warning_level
        # WMO Codes: 95, 96, 99 = Thunderstorm; 65 = Heavy rain; 82 = Violent rain showers
        if code in {65, 82, 95, 96, 99} or precip > 5.0 or wind > 30.0:
            condition = "stormy"
            warning_level = "red"
        elif code in {51, 53, 55, 61, 63, 80, 81} or precip > 0.0:
            condition = "rainy"
            warning_level = "none"
        else:
            condition = "sunny"
            warning_level = "none"

        return {
            "condition": condition,
            "temperature_c": int(round(temp)),
            "warning_level": warning_level
        }
    except Exception as e:
        # Silently return None so the caller can fallback to mock weather
        return None
