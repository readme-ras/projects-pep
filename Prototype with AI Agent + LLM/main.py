"""
FastAPI app — AI Agent with Weather tool.

Endpoints:
  POST /chat               — Single-turn agent call
  POST /chat/stream        — Same but response includes step trace
  GET  /weather/{city}     — Call weather tool directly
  GET  /tools              — List available tools
  GET  /health             — Health check
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any

from agent.agent import Agent
from tools import ALL_SCHEMAS
from tools.weather import get_weather

app = FastAPI(
    title="HF AI Agent — Weather",
    description="An AI agent powered by Hugging Face LLM with a Weather tool.",
    version="1.0.0",
)

# One agent instance (stateless — history passed in per request)
_agent = Agent()


# ── Schemas ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., example="What's the weather like in Tokyo right now?")
    history: list[dict] | None = Field(
        default=None,
        description="Previous messages for multi-turn context",
        example=None,
    )

    model_config = {"json_schema_extra": {"example": {
        "message": "What's the weather in Paris? Should I bring an umbrella?",
    }}}


class ToolCallInfo(BaseModel):
    tool:      str
    arguments: dict
    result:    Any


class ChatResponse(BaseModel):
    response:   str
    tool_calls: list[ToolCallInfo]
    steps:      int
    messages:   list[dict]


class WeatherResponse(BaseModel):
    city:        str
    temperature: float
    feels_like:  float
    humidity:    int
    wind_speed:  float
    description: str
    temp_unit:   str
    wind_unit:   str
    source:      str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "tools": [s["name"] for s in ALL_SCHEMAS]}


@app.get("/tools")
def list_tools():
    """Return all tool schemas the agent can use."""
    return {"tools": ALL_SCHEMAS}


@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    """
    Send a message to the AI agent.
    The agent will call tools as needed and return a final response.
    """
    try:
        result = _agent.run(body.message, history=body.history)
        return ChatResponse(
            response=result["response"],
            tool_calls=[ToolCallInfo(**tc) for tc in result["tool_calls"]],
            steps=result["steps"],
            messages=result["messages"],
        )
    except EnvironmentError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather/{city}", response_model=WeatherResponse)
def weather_direct(city: str, units: str = "celsius"):
    """
    Call the weather tool directly without going through the LLM.
    Useful for testing or direct integrations.
    """
    try:
        data = get_weather(city, units)
        return WeatherResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/multi-turn", response_model=ChatResponse)
def chat_multi_turn(body: ChatRequest):
    """
    Multi-turn chat. Pass the `messages` array from the previous response
    as `history` to continue the conversation.
    """
    return chat(body)
