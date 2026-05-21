#!/usr/bin/env python3
"""
Consolidate ideas from all sources (Reddit, YouTube).
Deduplicate, apply novelty penalty vs archive, rank top 3 per niche.
Write data/ideas/weekly_ideas.md.
Use Ollama (gemma4:e2b) for classification.
"""

import json
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

import requests
from _console import console, progress_bar


def load_json_files(directory):
    all_ideas = []
    path = Path(directory)
    for json_file in path.glob("*.json"):
        try:
            data = json.loads(json_file.read_text())
            if isinstance(data, dict):
                for niche, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            item["source"] = json_file.stem
                            item["niche"] = niche
                            all_ideas.append(item)
            else:
                all_ideas.extend(data)
        except Exception as e:
            console.print(f"[warn]Error loading {json_file}: {e}[/warn]")
    return all_ideas


def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate(ideas, threshold=0.75):
    deduplicated, seen = [], []
    for idea in ideas:
        title = idea.get("title", "")
        if not any(string_similarity(title, s) >= threshold for s in seen):
            deduplicated.append(idea)
            seen.append(title)
    return deduplicated


def load_archive_titles(archive_dir="data/kb"):
    titles = []
    master = Path(archive_dir) / "master_brief.md"
    if master.exists():
        for line in master.read_text().splitlines():
            if line.startswith("## ") or line.startswith("### "):
                titles.append(line.strip("#").strip())
    return titles


def apply_novelty_penalty(ideas, archive_titles, penalty=0.5):
    for idea in ideas:
        title = idea.get("title", "")
        max_sim = max((string_similarity(title, a) for a in archive_titles), default=0)
        base = idea.get("score", 0) or idea.get("engagement_rate", 0) or 0.5
        idea["novelty_adjusted_score"] = base * penalty if max_sim > 0.6 else base
    return ideas


def classify_idea(title, niche):
    prompt = f"Classify this content idea into a brief category (1-3 words):\nNiche: {niche}\nIdea: {title}\nCategory:"

    # Backend 1: NVIDIA NIM
    try:
        from nim_client import call_nim, NIM_MODEL_SMALL
        text, _ = call_nim(prompt, model=NIM_MODEL_SMALL, max_tokens=20, temperature=0.3)
        return text.strip().split("\n")[0][:50]
    except Exception as e:
        console.print(f"[warn]NIM error: {e}[/warn]")

    # Backend 2: Ollama
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma4:e2b", "prompt": prompt, "stream": False},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip().split("\n")[0][:50]
    except Exception as e:
        console.print(f"[warn]Ollama error: {e}[/warn]")

    return "uncategorized"


def score_ideas(output_dir="data/ideas"):
    console.rule("[info]Idea Scorer[/info]")

    with progress_bar() as progress:
        load_task = progress.add_task("Loading ideas", total=None)
        ideas = load_json_files(output_dir)
        progress.update(load_task, description=f"Loaded {len(ideas)} ideas", completed=1, total=1)

        dedup_task = progress.add_task("Deduplicating", total=None)
        ideas = deduplicate(ideas)
        progress.update(dedup_task, description=f"After dedup: {len(ideas)} ideas", completed=1, total=1)

        archive_task = progress.add_task("Loading archive", total=None)
        archive_titles = load_archive_titles()
        progress.update(archive_task, description=f"Archive has {len(archive_titles)} titles", completed=1, total=1)

        novelty_task = progress.add_task("Applying novelty penalty", total=None)
        ideas = apply_novelty_penalty(ideas, archive_titles)
        progress.update(novelty_task, completed=1, total=1)

        # Group by niche
        by_niche = {}
        for idea in ideas:
            niche = idea.get("niche", "unknown")
            by_niche.setdefault(niche, []).append(idea)

        # Count top-3 classifications needed
        total_to_classify = sum(min(3, len(v)) for v in by_niche.values())
        classify_task = progress.add_task("Classifying ideas", total=total_to_classify)

        final_ideas = {}
        for niche, niche_ideas in by_niche.items():
            top_3 = sorted(niche_ideas, key=lambda x: x.get("novelty_adjusted_score", 0), reverse=True)[:3]
            for idea in top_3:
                progress.update(classify_task, description=f"Classifying: {idea['title'][:40]}")
                idea["category"] = classify_idea(idea["title"], niche)
                progress.advance(classify_task)
            final_ideas[niche] = top_3

    # Generate markdown report
    lines = ["# Weekly Ideas Report", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for niche, ideas_list in final_ideas.items():
        lines.append(f"## {niche.replace('_', ' ').title()}")
        lines.append("")
        for i, idea in enumerate(ideas_list, 1):
            lines += [
                f"### {i}. {idea.get('title', 'Untitled')}",
                f"- **Score:** {idea.get('novelty_adjusted_score', 0):.3f}",
                f"- **Category:** {idea.get('category', 'uncategorized')}",
                f"- **Source:** {idea.get('source', 'unknown')}",
            ]
            if "url" in idea:
                lines.append(f"- **URL:** {idea['url']}")
            lines.append("")

    out = Path("data/ideas") / "weekly_ideas.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    console.print(f"\n[success]✓ Saved to {out}[/success]")
    for niche, ideas_list in final_ideas.items():
        console.print(f"  [niche]{niche}[/niche]:")
        for i, idea in enumerate(ideas_list, 1):
            console.print(f"    {i}. [dim]{idea['title'][:65]}[/dim] ({idea.get('novelty_adjusted_score',0):.3f})")

    return final_ideas


if __name__ == "__main__":
    score_ideas()
