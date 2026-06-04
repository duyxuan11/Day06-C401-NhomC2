# WonderPath AI — Codebase

Thu muc nay chua prototype WonderPath AI, gom giao dien frontend va phan Prompt/AI Logic bang Python.

## 1. Chay giao dien frontend

Frontend nam trong:

```text
codebase/frontend/index.html
```

Co 2 cach chay:

### Cach 1: Mo truc tiep file HTML

Mo file `codebase/frontend/index.html` bang Chrome, Edge hoac Firefox.

### Cach 2: Dung Live Server trong VS Code

Click chuot phai vao `codebase/frontend/index.html` va chon **Open with Live Server**.

Giao dien co bang gia lap ngu canh ben trai va mobile mockup ben phai. Co the test cac case:

- Happy Path: gia dinh co tre nho tai Cong Khu Co Tich.
- Low-confidence: user profile chua xac dinh.
- Failure Path: Tau Luon Sieu Toc bao tri.
- Emergency Path: thoi tiet dong bao canh bao do.

## 2. Chay Prompt & AI Logic

Phan nay dung de kiem thu prompt, response schema va Gemini API.

### Cai dat

```bash
cd codebase
python3 -m venv .venv
# Cai dat dependencies tu backend/requirements.txt
.venv/bin/python -m pip install -r backend/requirements.txt
# Copy file cau hinh .env vao backend/
cp backend/.env.example backend/.env
```

Sau do dien `GEMINI_API_KEY` that vao file `backend/.env`. Khong commit file `backend/.env`.

### Chay dry-run

Dry-run chi render prompt, khong goi Gemini:

```bash
.venv/bin/python run_eval.py --dry-run
```

### Chay eval goi Gemini that

```bash
.venv/bin/python run_eval.py --model gemini-3.1-flash-lite
```

Ket qua moi lan chay duoc luu vao:

```text
codebase/runs/eval_run_YYYYMMDDTHHMMSS.json
```

## 3. Cau truc phan AI Logic

```text
backend/server/
├── ai/
│   ├── prompt.py
│   ├── response_schema.py
│   ├── function_tools.py
│   └── gemini_client.py
├── services/
│   ├── context_builder.py
│   ├── mock_data_service.py
│   └── weather_service.py
└── utils/
    └── safety_rules.py
```

- `prompt.py`: tao system prompt cho WonderPath AI.
- `response_schema.py`: ep output Gemini ve JSON gom `message` va `ui_buttons`.
- `function_tools.py`: dinh nghia va thuc thi cac function tools cho parallel calling.
- `gemini_client.py`: goi Gemini API va dieu phoi parallel function calling.
- `context_builder.py`: ghep station, user profile, weather, realtime status va attractions thanh context.
- `mock_data_service.py`: doc du lieu trong `mock-data`.
- `weather_service.py`: lay thong tin thoi tiet tu Open-Meteo API.
- `safety_rules.py`: danh dau cac rui ro nhu tro bao tri, hang doi qua lau, weather red, khong phu hop tre nho/nguoi gia.

## 4. Luu y bao mat

- Khong commit `backend/.env`.
- Chi commit `backend/.env.example`.
- Thu muc `.venv/`, `venv/`, `__pycache__/` duoc ignore trong `.gitignore`.

