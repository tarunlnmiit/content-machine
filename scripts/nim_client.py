#!/usr/bin/env python3
"""
NVIDIA NIM API client (OpenAI-compatible endpoint).
Primary AI backend for all non-Claude-Pro tasks.
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_MODEL_LARGE = "mistralai/mistral-large-3-675b-instruct-2512"
NIM_MODEL_SMALL = "meta/llama-3.1-8b-instruct"


def call_nim(
    prompt: str,
    model: str = NIM_MODEL_LARGE,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> tuple[str, dict]:
    """
    Call NVIDIA NIM API. Returns (text, usage_dict). Raises on error.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY not set in .env")

    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()

    req = urllib.request.Request(
        NIM_API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"NIM HTTP {e.code}: {e.read().decode()[:200]}")

    in_tok  = data.get("usage", {}).get("prompt_tokens", 0)
    out_tok = data.get("usage", {}).get("completion_tokens", 0)

    return data["choices"][0]["message"]["content"], {
        "input_tokens":  in_tok,
        "output_tokens": out_tok,
        "backend":       f"nim-{model}",
    }
