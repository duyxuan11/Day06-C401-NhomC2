import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure the root of the project is in python path
sys.path.append(str(Path(__file__).resolve().parent))

from server.services.mock_data_service import load_mock_data
from server.services.context_builder import build_wonder_path_context
from server.ai.gemini_client import generate_itinerary_with_gemini

# Load environment variables
load_dotenv(Path(__file__).resolve().parent / ".env")

app = FastAPI(title="WonderPath AI Backend Server")

# Configure CORS to allow direct frontend connection from local files or live servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    current_station_id: str = "qr_station_01"
    current_time: Optional[str] = None
    user_profile: Optional[Dict[str, Any]] = None
    weather_condition: Optional[str] = "sunny"
    is_coaster_maintenance: Optional[bool] = False
    user_message: Optional[str] = None

@app.post("/api/recommend")
async def get_recommendation(request: RecommendRequest):
    try:
        # Load mock data
        mock_data = load_mock_data()
        
        # Weather Override Mapping
        weather_states = mock_data.get("weather", {}).get("states", {})
        weather_override = weather_states.get(request.weather_condition)
        
        # Roller Coaster Maintenance Override
        status_override = {}
        if request.is_coaster_maintenance:
            status_override["att_roller_coaster"] = {
                "status": "maintenance",
                "wait_time_mins": 0,
                "crowd_level": "low"
            }
        
        # Build context
        input_data = {
            "current_station_id": request.current_station_id,
            "current_time": request.current_time,
            "user_profile": request.user_profile,
            "weather_override": weather_override,
            "status_override": status_override
        }
        
        context = build_wonder_path_context(input_data, mock_data)
        
        # Inject user message if present
        if request.user_message:
            context["user_message"] = request.user_message
            
        # Call Gemini API
        result = generate_itinerary_with_gemini(context)
        return result
        
    except RuntimeError as re:
        # Handle configuration issues (e.g. missing API key)
        print(f"[Backend Error] Configuration error: {re}")
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        print(f"[Backend Error] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/api/health")
async def health_check():
    api_key_configured = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "ok",
        "gemini_api_key_set": api_key_configured
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
