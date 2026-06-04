# Codebase

Thu muc nay chua mock data, eval script va cac helper Python cho prototype WonderPath AI.

## Cai dat

```bash
cd codebase
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Sau do dien `GEMINI_API_KEY` that vao file `.env`. Khong commit file `.env`.

## Chay kiem thu Prompt & AI Logic

Kiem tra render prompt, khong goi Gemini:

```bash
.venv/bin/python run_eval.py --dry-run
```

Chay eval co goi Gemini:

```bash
.venv/bin/python run_eval.py --model gemini-1.5-flash
```

Ket qua moi lan chay duoc luu vao `runs/eval_run_YYYYMMDDTHHMMSS.json`.

## Cau truc lien quan den phan AI Logic

```text
server/
├── ai/
│   ├── prompt.py
│   ├── response_schema.py
│   └── gemini_client.py
├── services/
│   ├── context_builder.py
│   └── mock_data_service.py
└── utils/
    └── safety_rules.py
```

- `prompt.py`: tao system prompt cho WonderPath AI.
- `response_schema.py`: ep output Gemini ve JSON gom `message` va `ui_buttons`.
- `gemini_client.py`: goi Gemini API.
- `context_builder.py`: ghep station, user profile, weather, realtime status va attractions thanh context.
- `mock_data_service.py`: doc du lieu trong `mock-data`.
- `safety_rules.py`: danh dau cac rui ro nhu tro bao tri, hang doi qua lau, weather red, khong phu hop tre nho/nguoi gia.
