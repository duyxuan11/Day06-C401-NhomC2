import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import google.generativeai as genai
from dotenv import load_dotenv

from server.ai.prompt import build_wonder_path_prompt
from server.ai.response_schema import GEMINI_RESPONSE_SCHEMA, normalize_ai_response


CODEBASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(CODEBASE_DIR / ".env")


def parse_json_response(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Gemini returned an empty response.")

    return json.loads(str(text).strip())


def generate_itinerary_with_gemini(
    context: Dict[str, Any],
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout_seconds: int = 20,
) -> Dict[str, Any]:
    key = api_key or os.getenv("GEMINI_API_KEY")
    model = model_name or os.getenv("GEMINI_MODEL") or "gemini-1.5-flash"

    if not key:
        raise RuntimeError("Missing GEMINI_API_KEY. Create codebase/.env from codebase/.env.example.")

    genai.configure(api_key=key)
    prompt = build_wonder_path_prompt(context)
    gemini_model = genai.GenerativeModel(model)

    response = gemini_model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=GEMINI_RESPONSE_SCHEMA,
            temperature=0.0,
        ),
        request_options={"timeout": timeout_seconds},
    )

    return normalize_ai_response(parse_json_response(response.text))
