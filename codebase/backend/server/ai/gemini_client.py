import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv

from server.ai.prompt import build_wonder_path_prompt, CHAT_SYSTEM_PROMPT
from server.ai.response_schema import GEMINI_RESPONSE_SCHEMA, normalize_ai_response
from server.ai.function_tools import TOOL_DECLARATIONS, execute_function_call
from server.services.mock_data_service import load_mock_data


CODEBASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(CODEBASE_DIR / ".env")

MAX_FUNCTION_CALL_ROUNDS = 5


def parse_json_response(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Gemini returned an empty response.")

    return json.loads(str(text).strip())


# ---------------------------------------------------------------------------
# Legacy: single-shot generate (used by /api/recommend and run_eval.py)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# New: multi-turn chat with function calling (used by /api/chat)
# ---------------------------------------------------------------------------

def chat_with_function_calling(
    chat_history: List[Dict[str, Any]],
    user_message: str,
    station_id: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """
    Multi-turn chat with Gemini using function calling.

    Args:
        chat_history: List of {"role": "user"|"model", "parts": [str]} dicts
        user_message: The latest user message
        station_id: Optional current QR station ID for context
        model_name: Gemini model name override
        api_key: API key override

    Returns:
        {"message": str, "ui_buttons": [...], "chat_history": [...]}
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    model = model_name or os.getenv("GEMINI_MODEL") or "gemini-2.0-flash"

    if not key:
        raise RuntimeError("Missing GEMINI_API_KEY.")

    genai.configure(api_key=key)

    # Load mock data for pre-fetching and execution
    mock_data = load_mock_data()

    # Pre-fetch weather and time to enrich context and avoid extra tool calls
    weather_json = execute_function_call("get_weather", {}, mock_data)
    time_json = execute_function_call("get_current_time", {}, mock_data)
    
    try:
        w_data = json.loads(weather_json)
        t_data = json.loads(time_json)
        context_prefix = (
            f"[Thời tiết: {w_data.get('condition', 'sunny')}, {w_data.get('temperature_c', 30)}°C, cảnh báo: {w_data.get('warning_level', 'none')}] "
            f"[Thời gian: {t_data.get('current_time', '09:00')} ({t_data.get('day_of_week', 'Monday')})]"
        )
    except Exception:
        context_prefix = ""

    # Enrich user message with station context and pre-fetched weather/time
    enriched_parts = []
    if context_prefix:
        enriched_parts.append(context_prefix)
    if station_id:
        enriched_parts.append(f"[Trạm hiện tại: {station_id}]")
    enriched_parts.append(user_message)
    enriched_message = " ".join(enriched_parts)

    # Build tool config
    tools = genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name=td["name"],
                description=td["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description=v.get("description", ""),
                        )
                        for k, v in td["parameters"].get("properties", {}).items()
                    },
                    required=td["parameters"].get("required", []),
                ),
            )
            for td in TOOL_DECLARATIONS
        ]
    )

    # Create model with system instruction and tools
    gemini_model = genai.GenerativeModel(
        model,
        system_instruction=CHAT_SYSTEM_PROMPT,
        tools=[tools],
        generation_config=genai.GenerationConfig(
            temperature=0.3,
        ),
    )

    # Build conversation history for Gemini
    history_for_gemini = []
    for msg in chat_history:
        role = msg.get("role", "user")
        parts = msg.get("parts", [])
        if isinstance(parts, str):
            parts = [parts]
        history_for_gemini.append(
            genai.protos.Content(
                role=role,
                parts=[genai.protos.Part(text=p) for p in parts],
            )
        )

    # Start chat session
    chat = gemini_model.start_chat(history=history_for_gemini)

    # Send enriched user message
    response = chat.send_message(
        enriched_message,
        request_options={"timeout": timeout_seconds},
    )

    # Function calling loop supporting parallel calls and higher limit
    max_rounds = 10
    for round_idx in range(max_rounds):
        # Extract all function calls from the current response candidates
        function_calls = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call and part.function_call.name:
                    function_calls.append(part.function_call)

        if not function_calls:
            break  # No more function calls, we have the final response

        print(f"  [Round {round_idx + 1}] Found {len(function_calls)} function call(s)")

        # Execute all function calls to build the response parts list
        function_responses = []
        for fc in function_calls:
            func_name = fc.name
            func_args = dict(fc.args) if fc.args else {}
            print(f"    [Function Call] {func_name}({json.dumps(func_args, ensure_ascii=False)})")
            
            result_json = execute_function_call(func_name, func_args, mock_data)
            print(f"    [Function Result] {result_json[:200]}...")
            
            function_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=func_name,
                        response=json.loads(result_json),
                    )
                )
            )

        # For rounds > 1, the model response came from generate_content and is NOT in chat.history yet.
        # For round 1, it came from send_message and is already in chat.history.
        if round_idx > 0:
            chat.history.append(response.candidates[0].content)

        # Append function responses content to chat history
        chat.history.append(
            genai.protos.Content(
                role="function",
                parts=function_responses
            )
        )

        print(f"  [Chat History State] Round {round_idx + 1}:")
        for i, c in enumerate(chat.history):
            print(f"    Msg {i}: role={c.role}")
            for j, p in enumerate(c.parts):
                if p.text:
                    print(f"      Part {j} (text): {repr(p.text[:100])}")
                elif p.function_call:
                    print(f"      Part {j} (call): {p.function_call.name}")
                elif p.function_response:
                    print(f"      Part {j} (response): {p.function_response.name}")

        # Generate content based on updated history
        response = gemini_model.generate_content(
            chat.history,
            tools=[tools],
            generation_config=genai.GenerationConfig(
                temperature=0.3,
            ),
            request_options={"timeout": timeout_seconds},
        )

    # Append the final model response to chat history
    if response.candidates and response.candidates[0].content:
        chat.history.append(response.candidates[0].content)

    # Extract final text response
    final_text = ""
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.text:
                final_text += part.text

    # Parse and normalize the response
    try:
        print(f"  [Gemini Raw Response] {final_text}")
        parsed = parse_json_response(final_text)
        result = normalize_ai_response(parsed)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"  [Parsing Error] Failed to parse JSON: {e}. Raw text: {repr(final_text)}")
        result = {
            "message": final_text.strip() if final_text.strip() else "Xin lỗi, tôi gặp lỗi xử lý. Bạn thử lại nhé!",
            "ui_buttons": [],
        }

    # Build updated chat history
    updated_history = chat_history.copy()
    updated_history.append({"role": "user", "parts": [enriched_message]})
    updated_history.append({"role": "model", "parts": [json.dumps(result, ensure_ascii=False)]})

    result["chat_history"] = updated_history
    return result
