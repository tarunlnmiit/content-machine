#!/usr/bin/env python3
"""Test LLM-based trend classification with mock data."""

import json
from datetime import datetime
from pathlib import Path
import os

from openrouter_client import call_openrouter

# Mock trend data
MOCK_TRENDS = [
    {"keyword": "Python 3.13 new features", "score": 95},
    {"keyword": "Machine learning model compression", "score": 88},
    {"keyword": "Building daily habits for productivity", "score": 82},
    {"keyword": "Meditation techniques for anxiety", "score": 78},
    {"keyword": "Shakespeare sonnets explained", "score": 65},
    {"keyword": "Modern poetry trends", "score": 72},
    {"keyword": "Neural network architectures", "score": 90},
    {"keyword": "Self-improvement through journaling", "score": 75},
]

NICHE_KEYWORDS = {
    "data_science_tech": ["data science", "machine learning", "python", "ai", "algorithm", "neural network", "deep learning"],
    "life_self_dev": ["productivity", "habit building", "motivation", "self improvement", "wellness", "meditation"],
    "poetry_quotes": ["poetry", "poem", "creative writing", "literature", "sonnet"],
}


def classify_trend_keyword_match(keyword):
    """Fallback: classify using keyword matching."""
    keyword_lower = keyword.lower()
    for niche, keywords in NICHE_KEYWORDS.items():
        for kw in keywords:
            if kw in keyword_lower:
                return niche
    return None


def classify_trend_llm(keyword):
    """Classify using LLM. Returns (classification, raw_response)."""
    prompt = f"""Classify this trending topic into ONE category only:
- data_science_tech
- life_self_dev
- poetry_quotes

Trend: {keyword}

Respond with ONLY the category name (exactly as shown above) or "unclassified"."""

    response, ok = call_openrouter(prompt, max_tokens=15)
    if not ok or not response:
        return classify_trend_keyword_match(keyword), f"[Error/Fallback: {response[:30]}]"

    raw = response.lower().strip()

    # Try exact match first
    for niche in NICHE_KEYWORDS:
        if niche in raw:
            return niche, raw

    if "unclassified" in raw:
        return None, raw

    # Fallback if LLM gave weird response
    return classify_trend_keyword_match(keyword), f"[Fallback from: {raw[:30]}]"


if __name__ == "__main__":
    print("Testing LLM vs Keyword Match Classification\n")
    print(f"{'Trend':<50} {'Keyword':<20} {'LLM':<20}")
    print("-" * 90)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set")
        exit(1)

    results = {"data_science_tech": 0, "life_self_dev": 0, "poetry_quotes": 0, "unclassified": 0}

    for trend in MOCK_TRENDS:
        keyword = trend["keyword"]
        kw_class = classify_trend_keyword_match(keyword)
        llm_class, raw_response = classify_trend_llm(keyword)

        results[llm_class or "unclassified"] += 1

        llm_display = llm_class or "unclassified"
        print(f"{keyword:<50} {kw_class or 'none':<20} {llm_display:<20}")
        print(f"  LLM raw: {raw_response}")

    print("\nResults Summary:")
    for niche, count in results.items():
        print(f"  {niche}: {count}")
