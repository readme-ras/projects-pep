# HF AI Agent — FastAPI + Weather Tool

An AI agent powered by **Hugging Face LLM** (Mistral-7B-Instruct) that uses
**function calling** to answer weather questions via a live Weather API.

## Architecture

```
User Request
    │
    ▼
FastAPI  (/chat)
    │
    ▼
Agent Loop
    ├── call_llm()  →  Hugging Face Inference API
    │                  (Mistral-7B-Instruct)
    │
    ├── parse_tool_call()  →  detects JSON tool_call block
    │
    └── execute_tool()  →  get_weather()
                               │
                               ▼
                        Open-Meteo API (free, no key)
                        Returns: temp, humidity, wind, description
```

## Project Structure

```
hf-agent/
├── agent/
│   ├── agent.py      # Agent loop (LLM ↔ tool orchestration)
│   └── llm.py        # HF Inference API client + prompt builder
├── tools/
│   ├── __init__.py   # Tool registry
│   └── weather.py    # Weather tool (Open-Meteo + geocoding)
├── api/
│   └── main.py       # FastAPI routes
├── requirements.txt
└── .env.example
```

## Setup & Run

```bash
pip install -r requirements.txt

cp .env.example .env
# Add your HF_API_TOKEN

uvicorn api.main:app --reload --port 8000
```

API docs → http://localhost:8000/docs

## Endpoints

### POST /chat
Send a natural language message. The agent decides whether to call the weather tool.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Whats the weather in Tokyo? Should I bring a jacket?"}'
```

Response:
```json
{
  "response": "It's currently 18°C and partly cloudy in Tokyo...",
  "tool_calls": [
    {
      "tool": "get_weather",
      "arguments": {"city": "Tokyo", "units": "celsius"},
      "result": {"temperature": 18.0, "description": "Partly cloudy", ...}
    }
  ],
  "steps": 2,
  "messages": [...]
}
```

### GET /weather/{city}
Call the weather tool directly (no LLM).
```bash
curl "http://localhost:8000/weather/London?units=celsius"
```

### GET /tools
List all available tool schemas.

### POST /chat/multi-turn
Multi-turn chat — pass the `messages` array from a previous response as `history`.

```bash
# Turn 1
curl -X POST http://localhost:8000/chat/multi-turn \
  -d '{"message": "Whats the weather in Paris?"}'

# Turn 2 — pass messages from Turn 1 response as history
curl -X POST http://localhost:8000/chat/multi-turn \
  -d '{"message": "What about London?", "history": [... messages from turn 1 ...]}'
```

## Adding More Tools

1. Create `tools/my_tool.py` with a function and a `TOOL_SCHEMA` dict
2. Register it in `tools/__init__.py`:
   ```python
   from tools.my_tool import my_fn, MY_SCHEMA
   TOOL_REGISTRY["my_tool"] = (my_fn, MY_SCHEMA)
   ```
That's it — the agent picks it up automatically.
