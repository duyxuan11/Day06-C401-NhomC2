from typing import Any, Dict


ALLOWED_ACTIONS = {
    "navigate",
    "update_profile",
    "suggest_dining",
    "request_alternative",
}

GEMINI_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "description": "Lời chào và gợi ý lịch trình ngắn gọn bằng tiếng Việt.",
        },
        "ui_buttons": {
            "type": "array",
            "description": "Danh sách nút bấm phản hồi nhanh để hiển thị trên UI card.",
            "items": {
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "Nhãn hiển thị trên nút bấm.",
                    },
                    "action": {
                        "type": "string",
                        "description": "Loại hành động.",
                        "enum": [
                            "navigate",
                            "update_profile",
                            "suggest_dining",
                            "request_alternative",
                        ],
                    },
                    "target_id": {
                        "type": "string",
                        "nullable": True,
                        "description": "ID attraction nếu action là navigate, ngược lại là null.",
                    },
                    "data": {
                        "type": "object",
                        "nullable": True,
                        "description": "Dữ liệu kèm theo nếu cần update profile hoặc request alternative.",
                    },
                },
                "required": ["label", "action"],
            },
        },
    },
    "required": ["message", "ui_buttons"],
}


def normalize_ai_response(raw_response: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw_response, dict):
        raise ValueError("AI response must be a JSON object.")

    message = str(raw_response.get("message", "")).strip()
    if not message:
        raise ValueError("AI response is missing message.")

    raw_buttons = raw_response.get("ui_buttons", [])
    if not isinstance(raw_buttons, list):
        raw_buttons = []

    ui_buttons = []
    for button in raw_buttons:
        if not isinstance(button, dict):
            continue

        action = button.get("action")
        if action not in ALLOWED_ACTIONS:
            action = "request_alternative"

        ui_buttons.append(
            {
                "label": str(button.get("label") or "Đổi phương án khác").strip(),
                "action": action,
                "target_id": button.get("target_id"),
                "data": button.get("data"),
            }
        )

    return {
        "message": message,
        "ui_buttons": ui_buttons,
    }

