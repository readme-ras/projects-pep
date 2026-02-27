"""
Hugging Face Inference API client.
Model: mistralai/Mistral-7B-Instruct-v0.3  (instruction-tuned, good at tool use)
"""

import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN   = os.getenv("HF_API_TOKEN", "")
HF_MODEL   = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")
HF_MAX_TOK = int(os.getenv("HF_MAX_TOKENS", "1024"))
HF_TEMP    = float(os.getenv("HF_TEMPERATURE", "0.2"))
API_URL    = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def _build_prompt(messages: list[dict], tools: list[dict]) -> str:
    """
    Build a Mistral-style [INST] prompt that instructs the model to either
    respond directly or emit a JSON tool-call block.
    """
    tool_desc = json.dumps(tools, indent=2)

    system = f"""You are a helpful AI assistant with access to the following tools:

{tool_desc}

RULES:
- If you need to call a tool, respond ONLY with a JSON block like this (no extra text):
```tool_call
{{"tool": "<tool_name>", "arguments": {{...}}}}
```
- After receiving a tool result, answer the user naturally in plain text.
- Never make up weather data — always call get_weather when weather is asked.
"""

    parts = [f"<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n"]
    for i, msg in enumerate(messages):
        role    = msg["role"]
        content = msg["content"]
        if role == "user":
            if i == 0:
                parts.append(f"{content} [/INST]")
            else:
                parts.append(f"<s>[INST] {content} [/INST]")
        elif role == "assistant":
            parts.append(f" {content} </s>")
        elif role == "tool":
            parts.append(f"<s>[INST] Tool result: {content} [/INST]")

    return "".join(parts)


def call_llm(messages: list[dict], tools: list[dict]) -> str:
    """Send messages to HF and return the raw model response text."""
    if not HF_TOKEN:
        raise EnvironmentError("HF_API_TOKEN not set in .env")

    prompt = _build_prompt(messages, tools)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens":  HF_MAX_TOK,
            "temperature":     HF_TEMP,
            "return_full_text": False,
            "stop": ["</s>", "<s>"],
        },
    }
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    if isinstance(data, list):
        return data[0].get("generated_text", "").strip()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"HF API error: {data['error']}")
    return str(data).strip()


def parse_tool_call(text: str) -> dict | None:
    """Extract a tool_call JSON block from the model output, if present."""
    match = re.search(r"```tool_call\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Fallback: bare JSON object with "tool" key
    match = re.search(r'\{[^{}]*"tool"\s*:[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None
