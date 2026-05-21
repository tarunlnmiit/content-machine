#!/usr/bin/env python3
"""
Groq API client with key rotation based on daily token usage.
Usage tracked in data/groq_usage.json, reset daily at UTC midnight.
Keys picked by lowest used_tokens among non-exhausted keys.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

USAGE_FILE = REPO / "data" / "groq_usage.json"
DAILY_TOKEN_LIMIT = 500_000  # Groq free tier per key per day
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

_KEY_NAMES = ["GROQ_API_KEY_1", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_usage() -> dict:
    today = _today_utc()
    if USAGE_FILE.exists():
        data = json.loads(USAGE_FILE.read_text())
        if data.get("date") == today:
            return data
    # New day or missing file — reset
    return {"date": today, "keys": {k: {"tokens": 0, "requests": 0} for k in _KEY_NAMES}}


def _save_usage(usage: dict) -> None:
    USAGE_FILE.write_text(json.dumps(usage, indent=2))


def _pick_key(usage: dict) -> tuple[str, str]:
    """Return (key_name, api_key) with lowest usage that is under limit."""
    keys_data = usage["keys"]
    available = [
        (name, keys_data[name]["tokens"])
        for name in _KEY_NAMES
        if keys_data.get(name, {}).get("tokens", 0) < DAILY_TOKEN_LIMIT
        and os.getenv(name)
    ]
    if not available:
        raise RuntimeError("All Groq API keys exhausted for today. Resets at UTC midnight.")
    name = min(available, key=lambda x: x[1])[0]
    return name, os.getenv(name)


def call_groq(prompt: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 4096) -> tuple[str, dict]:
    """
    Call Groq API using key with lowest daily usage.
    Returns (text, usage_dict). Raises on error or all keys exhausted.
    """
    usage = _load_usage()
    key_name, api_key = _pick_key(usage)

    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()

    req = urllib.request.Request(
        GROQ_API_URL,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Groq HTTP {e.code} ({key_name}): {e.read().decode()[:200]}")

    in_tok  = data.get("usage", {}).get("prompt_tokens", 0)
    out_tok = data.get("usage", {}).get("completion_tokens", 0)
    total   = in_tok + out_tok

    # Update usage
    key_stats = usage["keys"].setdefault(key_name, {"tokens": 0, "requests": 0})
    key_stats["tokens"]   += total
    key_stats["requests"] += 1
    _save_usage(usage)

    return data["choices"][0]["message"]["content"], {
        "input_tokens":  in_tok,
        "output_tokens": out_tok,
        "backend":       f"groq-{model}",
        "groq_key":      key_name,
        "key_day_tokens": key_stats["tokens"],
    }


def usage_report() -> str:
    """Human-readable daily usage summary for all keys."""
    usage = _load_usage()
    lines = [f"Groq usage — {usage['date']} (UTC)"]
    for name in _KEY_NAMES:
        stats = usage["keys"].get(name, {"tokens": 0, "requests": 0})
        pct   = stats["tokens"] / DAILY_TOKEN_LIMIT * 100
        lines.append(
            f"  {name}: {stats['tokens']:,} / {DAILY_TOKEN_LIMIT:,} tokens "
            f"({pct:.1f}%)  |  {stats['requests']} reqs"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(usage_report())
