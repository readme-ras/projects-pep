"""
Hugging Face Inference API service.

Supports two modes:
  1. HF Inference API (cloud) — just set HF_API_TOKEN + HF_MODEL_ID
  2. Local pipeline        — set HF_USE_LOCAL=true (downloads model on first run)
"""

import os
from typing import Generator

import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN  = os.getenv("HF_API_TOKEN", "")
HF_MODEL_ID   = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")
HF_USE_LOCAL  = os.getenv("HF_USE_LOCAL", "false").lower() == "true"
HF_MAX_TOKENS = int(os.getenv("HF_MAX_TOKENS", "512"))
HF_TEMPERATURE = float(os.getenv("HF_TEMPERATURE", "0.7"))

# ── Cloud inference (default) ─────────────────────────────────────────────────

def _cloud_generate(prompt: str, system_prompt: str | None = None) -> str:
    """Call the HF Inference API."""
    if not HF_API_TOKEN:
        raise EnvironmentError("Set HF_API_TOKEN in your .env")

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    # Build messages for instruction-tuned models
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "inputs": _format_messages(messages),
        "parameters": {
            "max_new_tokens": HF_MAX_TOKENS,
            "temperature": HF_TEMPERATURE,
            "return_full_text": False,
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, list) and data:
        return data[0].get("generated_text", "").strip()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"HF API error: {data['error']}")
    return str(data)


def _format_messages(messages: list[dict]) -> str:
    """Format messages into a simple prompt string for text-generation models."""
    parts = []
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "system":
            parts.append(f"<s>[INST] <<SYS>>\n{content}\n<</SYS>>\n\n")
        elif role == "user":
            parts.append(f"{content} [/INST]")
        else:
            parts.append(f" {content} </s><s>[INST] ")
    return "".join(parts)


# ── Local pipeline ─────────────────────────────────────────────────────────────

_local_pipeline = None

def _get_local_pipeline():
    global _local_pipeline
    if _local_pipeline is None:
        from transformers import pipeline
        _local_pipeline = pipeline(
            "text-generation",
            model=HF_MODEL_ID,
            max_new_tokens=HF_MAX_TOKENS,
            temperature=HF_TEMPERATURE,
            do_sample=True,
        )
    return _local_pipeline


def _local_generate(prompt: str, system_prompt: str | None = None) -> str:
    pipe = _get_local_pipeline()
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    result = pipe(full_prompt)
    return result[0]["generated_text"][len(full_prompt):].strip()


# ── Public API ─────────────────────────────────────────────────────────────────

def generate(
    prompt: str,
    system_prompt: str | None = None,
) -> str:
    """Generate a response from the configured HF model."""
    if HF_USE_LOCAL:
        return _local_generate(prompt, system_prompt)
    return _cloud_generate(prompt, system_prompt)


def get_model_info() -> dict:
    return {
        "model_id": HF_MODEL_ID,
        "mode": "local" if HF_USE_LOCAL else "cloud",
        "max_tokens": HF_MAX_TOKENS,
        "temperature": HF_TEMPERATURE,
    }
