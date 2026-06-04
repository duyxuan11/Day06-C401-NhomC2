import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure the root of the project is in python path
sys.path.append(str(Path(__file__).resolve().parent))

from server.services.mock_data_service import load_mock_data
from server.services.context_builder import build_wonder_path_context
from server.ai.gemini_client import generate_itinerary_with_gemini, chat_with_function_calling

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

# ---------------------------------------------------------------------------
# In-memory session store for chat history
# ---------------------------------------------------------------------------
session_store: Dict[str, List[Dict[str, Any]]] = {}


# ---------------------------------------------------------------------------
# Legacy: /api/recommend (backward compatible for eval)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# New: /api/chat (multi-turn with function calling)
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    user_message: str
    station_id: Optional[str] = None
    chat_history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    ui_buttons: List[Dict[str, Any]]
    chat_history: List[Dict[str, Any]]

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Resolve session
        session_id = request.session_id or str(uuid.uuid4())

        # Use client-provided history, or fallback to server session store
        if request.chat_history is not None:
            chat_history = request.chat_history
        else:
            chat_history = session_store.get(session_id, [])

        print(f"[Chat] session={session_id[:8]}... history_len={len(chat_history)} msg=\"{request.user_message[:50]}\"")

        # Call Gemini with function calling
        result = chat_with_function_calling(
            chat_history=chat_history,
            user_message=request.user_message,
            station_id=request.station_id,
        )

        # Update server-side session store
        updated_history = result.get("chat_history", chat_history)
        session_store[session_id] = updated_history

        return {
            "session_id": session_id,
            "message": result["message"],
            "ui_buttons": result.get("ui_buttons", []),
            "chat_history": updated_history,
        }

    except RuntimeError as re:
        print(f"[Chat Error] Configuration error: {re}")
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        print(f"[Chat Error] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    api_key_configured = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "ok",
        "gemini_api_key_set": api_key_configured,
        "active_sessions": len(session_store),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
