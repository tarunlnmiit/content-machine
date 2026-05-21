#!/usr/bin/env python3
"""Test OpenRouter API connectivity with provided config."""

import json
import urllib.request
import urllib.error
import sys

import os

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
PRIMARY_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
FALLBACK_MODELS = [
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free"
]

def test_model(model: str) -> bool:
    """Test single model, return True if successful."""
    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'OK'"}],
        "max_tokens": 10,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://content-machine.local",
        "X-Title": "Content Machine Trend Classifier"
    }

    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"✓ {model}: {result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()}")
            return True

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"✗ {model}: HTTP {e.code}")
        try:
            error_json = json.loads(error_body)
            print(f"  Error: {error_json.get('error', {}).get('message', error_body[:100])}")
        except:
            print(f"  Body: {error_body[:200]}")
        return False

    except Exception as e:
        print(f"✗ {model}: {type(e).__name__}: {str(e)[:100]}")
        return False

if __name__ == "__main__":
    print("Testing OpenRouter API with provided credentials...\n")

    results = {"primary": False, "fallbacks": []}

    print(f"Primary: {PRIMARY_MODEL}")
    results["primary"] = test_model(PRIMARY_MODEL)

    print(f"\nFallbacks:")
    for model in FALLBACK_MODELS:
        ok = test_model(model)
        results["fallbacks"].append((model, ok))

    passed = sum([results["primary"]] + [ok for _, ok in results["fallbacks"]])
    total = 1 + len(FALLBACK_MODELS)

    print(f"\n{passed}/{total} models working")
    sys.exit(0 if results["primary"] else 1)
