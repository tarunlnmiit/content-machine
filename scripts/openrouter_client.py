#!/usr/bin/env python3
"""OpenRouter API client with fallback to free/open models."""

import json
import os
import urllib.request
import urllib.error
from typing import Tuple

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(prompt: str, model: str = None, max_tokens: int = 1024) -> Tuple[str, bool]:
    """Call OpenRouter API. Return (response_text, success)."""
    if not OPENROUTER_API_KEY:
        return "", False

    model = model or OPENROUTER_MODEL

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://content-machine.local",
        "X-OpenRouter-Title": "Content Machine",
    }

    try:
        req = urllib.request.Request(
            OPENROUTER_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return text, True

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get("error", {}).get("message", str(e))
        except:
            error_msg = f"HTTP {e.code}: {error_body[:100]}"
        return f"Error: {error_msg}", False

    except Exception as e:
        return f"Error: {str(e)[:200]}", False


if __name__ == "__main__":
    test_prompt = "Classify this trend into one of: data_science_tech, life_self_dev, poetry_quotes. Trend: 'Python 3.13 new features'"
    result, ok = call_openrouter(test_prompt, max_tokens=50)
    print(f"Success: {ok}")
    print(f"Response: {result}")
