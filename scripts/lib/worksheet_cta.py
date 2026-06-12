"""Worksheet CTA helpers.

Shared by produce_blog.py (Phase 3: auto-insert into new blog markdown) and
worksheet_links.py (Phase 1/2: emit copy-paste links for blogs already on
Medium). The public URL shape is the single source of truth here.
"""

from __future__ import annotations

import os

DEFAULT_BASE_URL = "https://worksheets-mistakenlyhuman.vercel.app"

# Marker so auto-insertion is idempotent (guard against double-insert).
CTA_MARKER = "<!-- worksheet-cta -->"


def base_url() -> str:
    """Base URL for the worksheet delivery app (no trailing slash)."""
    return os.environ.get("WORKSHEET_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def worksheet_url(slug: str) -> str:
    """Public, gated download URL for a worksheet slug."""
    return f"{base_url()}/get-worksheet?slug={slug}"


def worksheet_cta_markdown(slug: str, title: str | None = None) -> str:
    """Markdown CTA block to append to a blog body.

    Wrapped in CTA_MARKER so it can be detected and not duplicated.
    """
    link_text = "Download the companion worksheet →"
    body = (
        f"{CTA_MARKER}\n\n"
        "---\n\n"
        "### Want to put this into practice?\n\n"
        f"[{link_text}]({worksheet_url(slug)})\n\n"
        "_Free PDF. Enter your email and it opens right away._\n"
    )
    return body


def has_cta(markdown: str) -> bool:
    """True if a worksheet CTA is already present."""
    return CTA_MARKER in markdown
