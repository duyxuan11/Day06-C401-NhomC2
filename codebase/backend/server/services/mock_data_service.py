import json
from pathlib import Path
from typing import Any, Dict, List, Optional


MOCK_DATA_DIR = Path(__file__).resolve().parents[3] / "mock-data"


def read_json_file(file_name: str, mock_data_dir: Path = MOCK_DATA_DIR) -> Any:
    file_path = mock_data_dir / file_name
    return json.loads(file_path.read_text(encoding="utf-8"))


def load_mock_data(mock_data_dir: Path = MOCK_DATA_DIR) -> Dict[str, Any]:
    return {
        "attractions": read_json_file("attractions.json", mock_data_dir),
        "stations": read_json_file("stations.json", mock_data_dir),
        "realtime_status": read_json_file("realtime_status.json", mock_data_dir),
        "weather": read_json_file("weather.json", mock_data_dir),
        "test_scenarios": read_json_file("test_scenarios.json", mock_data_dir),
    }


def get_station_by_id(stations: List[Dict[str, Any]], station_id: str) -> Optional[Dict[str, Any]]:
    return next((station for station in stations if station.get("station_id") == station_id), None)


def get_attraction_by_id(attractions: List[Dict[str, Any]], attraction_id: str) -> Optional[Dict[str, Any]]:
    return next((attraction for attraction in attractions if attraction.get("id") == attraction_id), None)


def get_realtime_status_by_id(
    realtime_status: Dict[str, Any],
    attraction_id: str,
) -> Optional[Dict[str, Any]]:
    return next(
        (
            item
            for item in realtime_status.get("attractions", [])
            if item.get("attraction_id") == attraction_id
        ),
        None,
    )

