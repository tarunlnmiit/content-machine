#!/usr/bin/env python3
"""
Generate actionable worksheet outline from blog markdown using Claude.
Detects niche, extracts blog content, generates dynamic worksheet via Claude.

Usage:
  python3 scripts/generate_worksheet_outline.py --input content/blogs/[slug].md
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional
import argparse

from _console import console, spinner


def detect_niche(filename: str) -> str:
    """Extract niche from filename: 2026-05-12_[NICHE]_title.md"""
    match = re.search(r"_(\w+)_", filename)
    return match.group(1).lower() if match else "unknown"


def extract_sections(content: str) -> dict:
    """Extract H2 sections and their content."""
    sections = {}
    parts = re.split(r"^## ", content, flags=re.MULTILINE)[1:]

    for part in parts:
        lines = part.split("\n", 1)
        title = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ""
        sections[title] = body[:500]  # first 500 chars

    return sections


def run_claude(prompt: str, timeout: int = 300) -> str:
    """Execute Claude via subprocess and return output."""
    with spinner() as progress:
        task = progress.add_task("Generating worksheet...")
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        progress.update(task, description="[success]Worksheet generated[/success]")

    if result.returncode != 0:
        console.print(f"[error]claude error:[/error] {result.stderr.strip()}")
        sys.exit(1)
    if not result.stdout.strip():
        console.print("[error]claude returned empty output[/error]")
        sys.exit(1)
    return result.stdout.strip()


def generate_worksheet(blog_path: str) -> Optional[dict]:
    """Read blog → detect niche → generate worksheet via Claude."""
    blog_file = Path(blog_path)

    if not blog_file.exists():
        print(f"Error: {blog_path} not found")
        return None

    content = blog_file.read_text(encoding="utf-8")
    niche_raw = detect_niche(blog_file.name)

    # Poetry not suitable for worksheets
    if "poetry" in niche_raw:
        print(f"Info: Poetry niche not suitable for worksheet. Skipping.")
        return None

    sections = extract_sections(content)

    # Extract title (H1)
    title_match = re.search(r"^# (.+)$", content, flags=re.MULTILINE)
    blog_title = title_match.group(1) if title_match else "Untitled"

    # Build section context
    section_context = "\n".join(
        f"**{title}**\n{body}\n" for title, body in sections.items()
    )

    niche_label = {
        "data_science_tech": "Data Science/Tech",
        "life_self_dev": "Life & Self-Development",
    }.get(niche_raw, niche_raw)

    prompt = f"""You are a worksheet generator for Tarun Gupta's audience.
Given the blog content below, create an interactive, actionable worksheet.

Blog niche: {niche_label}
Blog title: {blog_title}

Key sections from the blog:
{section_context}

Generate a worksheet JSON with this exact structure (no other fields):
{{
  "type": "string (e.g., 'conversion_guide', 'design_template', 'framework')",
  "niche": "{niche_raw}",
  "title": "string — specific actionable takeaway derived from THIS blog",
  "sections": [
    {{
      "title": "string",
      "prompt": "string OR prompts list"
    }}
  ],
  "cta": "string — call-to-action specific to THIS blog's topic",
  "engage_potential": "high or very_high"
}}

Rules:
- Title must reflect THIS blog's core argument, not generic templates
- 4-5 sections derived from THIS blog's key insights
- Each prompt helps reader apply THIS blog's insight to their own situation
- CTA references the specific topic/lesson of THIS blog
- Output ONLY valid JSON, no preamble

Generate now:"""

    worksheet_json = run_claude(prompt, timeout=300)

    # Strip markdown fence if present
    if worksheet_json.startswith("```"):
        worksheet_json = re.sub(r"^```(?:json)?\n", "", worksheet_json)
        worksheet_json = re.sub(r"\n```$", "", worksheet_json)

    # Parse JSON
    try:
        worksheet = json.loads(worksheet_json)
    except json.JSONDecodeError as e:
        console.print(f"[error]Failed to parse Claude's JSON output: {e}[/error]")
        console.print(f"[error]Raw output:[/error]\n{worksheet_json}")
        return None

    # Validate required keys
    required_keys = {"type", "niche", "title", "sections", "cta"}
    if not required_keys.issubset(worksheet.keys()):
        missing = required_keys - set(worksheet.keys())
        console.print(f"[warn]Missing keys in worksheet: {missing}[/warn]")
        return None

    worksheet["blog_file"] = str(blog_file)
    worksheet["slug"] = blog_file.stem

    return worksheet


def save_worksheet(worksheet: dict, output_dir: str = "content/worksheets"):
    """Save worksheet JSON to output directory."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    slug = worksheet["slug"]
    output_path = Path(output_dir) / f"{slug}_worksheet.json"

    output_path.write_text(json.dumps(worksheet, indent=2), encoding="utf-8")
    print(f"✓ Saved: {output_path}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate worksheet outline from blog markdown"
    )
    parser.add_argument("--input", "-i", required=True, help="Path to blog markdown file")
    parser.add_argument("--output-dir", "-o", default="content/worksheets",
                        help="Output directory for worksheet JSON")

    args = parser.parse_args()

    worksheet = generate_worksheet(args.input)

    if worksheet:
        save_path = save_worksheet(worksheet, args.output_dir)
        print(json.dumps(worksheet, indent=2))
    else:
        print(f"No worksheet generated for {args.input}")
        sys.exit(1)


if __name__ == "__main__":
    main()
