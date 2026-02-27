# Full-Stack: Hugging Face LLM + Google Sheets

A production-ready full-stack app with:
- **FastAPI** backend
- **Hugging Face Inference API** (or local models via `transformers`)
- **Google Sheets** as a persistent chat log / data store
- **Vanilla JS frontend** (dark terminal aesthetic, no build step needed)

---

## Project Structure

```
fullstack-hf-sheets/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app (serves frontend + API)
│   │   ├── routers/
│   │   │   ├── llm.py               # POST /api/llm/generate
│   │   │   ├── sheets.py            # Generic sheet CRUD
│   │   │   └── chat_log.py          # GET/POST /api/chat-log
│   │   └── services/
│   │       ├── hf_service.py        # Hugging Face inference
│   │       └── sheets_service.py    # Google Sheets client + logging
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html                   # Single-file UI (Chat + Sheets log viewer)
```

---

## Setup

### 1. Hugging Face

1. Sign up at [huggingface.co](https://huggingface.co) and go to **Settings → Access Tokens**
2. Create a token with **read** permissions
3. Choose your model — default is `mistralai/Mistral-7B-Instruct-v0.3`
   - Other great options: `HuggingFaceH4/zephyr-7b-beta`, `google/flan-t5-large` (smaller), `meta-llama/Llama-3-8B-Instruct` (requires approval)

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project → enable **Google Sheets API** + **Google Drive API**
3. **IAM & Admin → Service Accounts** → Create service account → Create JSON key → download as `credentials.json`
4. Share your Google Sheet with the service account email (Editor access)

### 3. Install & Configure

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in HF_API_TOKEN, GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID
```

### 4. Run

```bash
# From backend/
uvicorn app.main:app --reload
```

Open **http://localhost:8000** — the FastAPI server serves the frontend automatically.

Interactive API docs: **http://localhost:8000/docs**

---

## API Reference

### LLM

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/llm/generate` | Generate LLM response (optionally logs to Sheets) |
| GET  | `/api/llm/model-info` | Get current model config |

**Generate request body:**
```json
{
  "prompt": "Explain neural networks.",
  "system_prompt": "You are a helpful assistant.",
  "session_id": "optional-uuid",
  "log_to_sheets": true
}
```

### Chat Log (Google Sheets)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat-log/init` | Create ChatLog sheet with headers |
| GET  | `/api/chat-log/` | Get all log entries |
| GET  | `/api/chat-log/{session_id}` | Get logs for one session |

### Generic Sheets CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/sheets/list` | List all worksheets |
| GET    | `/api/sheets/{sheet_name}/rows` | Get all rows as dicts |
| POST   | `/api/sheets/rows` | Append a row |
| PUT    | `/api/sheets/rows/{row_index}` | Update a row |
| DELETE | `/api/sheets/{sheet_name}/rows/{row_index}` | Delete a row |

---

## Using Local Models

Uncomment in `requirements.txt`:
```
transformers>=4.40.0
torch>=2.2.0
accelerate>=0.29.0
```

Set in `.env`:
```
HF_USE_LOCAL=true
HF_MODEL_ID=microsoft/phi-2      # or any model that fits in your VRAM
```

The model is downloaded automatically on first request (~2-15 GB depending on model).

---

## Deployment Tips

- For cloud deployments, use `GOOGLE_CREDENTIALS_JSON` (inline JSON string) instead of a file path
- Add auth middleware (e.g. API key header) before exposing publicly
- Use `gunicorn -k uvicorn.workers.UvicornWorker app.main:app` for production
- The frontend can also be served from a CDN by pointing `const API = 'https://your-api.com'` in `index.html`
