#!/usr/bin/env python3
"""
Read all derivative files from content/derivatives/*/
Insert scheduled posts into data/scheduling.db.
Generate output/scheduled/publer_import.csv for Instagram + Facebook + Threads (via Publer).

Schedule logic:
  LinkedIn posts   — Tuesday 8am IST, Thursday 12pm IST  (direct API via scheduler.py)
  Twitter threads  — manual for now (copy content/derivatives/{slug}/twitter_thread.txt)
  Instagram        — Wednesday 6pm IST, Friday 10am IST  (via Publer CSV)
  Facebook         — Wednesday 7pm IST, Friday 11am IST  (via Publer CSV)
  Threads          — Wednesday 8pm IST, Friday 12pm IST  (via Publer CSV)

Run after repurpose_blog.py has produced derivatives for the week.
Safe to re-run — skips slugs already in DB with status='pending' or 'posted'.
"""

import csv
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")

# IST = UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


def next_weekday(weekday: int, hour: int, minute: int = 0) -> datetime:
    """
    Return the next occurrence of weekday (0=Mon…6=Sun) at given hour:minute IST.
    If today is the target weekday and time hasn't passed, returns today.
    """
    now = datetime.now(IST)
    days_ahead = weekday - now.weekday()
    if days_ahead < 0:
        days_ahead += 7
    elif days_ahead == 0 and now.hour >= hour:
        days_ahead = 7
    target = now + timedelta(days=days_ahead)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


# Platform → list of (weekday, hour, minute) slots
SCHEDULE = {
    "linkedin":  [(1, 8, 0), (3, 12, 0)],    # Tue 8am, Thu 12pm  (direct API)
    "twitter":   [(0, 9, 0), (1, 19, 0)],    # Mon 9am, Tue 7pm   (Publer CSV)
    "instagram": [(2, 18, 0), (4, 10, 0)],   # Wed 6pm, Fri 10am  (Publer CSV)
    "facebook":  [(2, 19, 0), (4, 11, 0)],   # Wed 7pm, Fri 11am  (Publer CSV)
    "threads":   [(2, 20, 0), (4, 12, 0)],   # Wed 8pm, Fri 12pm  (Publer CSV)
}


def slug_already_loaded(conn: sqlite3.Connection, slug: str, platform: str) -> bool:
    row = conn.execute(
        "SELECT id FROM posts WHERE slug=? AND platform=? AND status IN ('pending','posted')",
        (slug, platform),
    ).fetchone()
    return row is not None


def parse_twitter_thread(txt_path: Path) -> list[str]:
    """Split on blank lines — each block = one tweet."""
    text = txt_path.read_text(encoding="utf-8").strip()
    return [b.strip() for b in text.split("\n\n") if b.strip()]


def insert_twitter(conn: sqlite3.Connection, slug: str, txt_path: Path, slot_index: int):
    if slug_already_loaded(conn, slug, "twitter"):
        print(f"  [skip] twitter/{slug} already in DB")
        return

    tweets = parse_twitter_thread(txt_path)
    if not tweets:
        print(f"  [skip] twitter/{slug} — empty thread file")
        return

    weekday, hour, minute = SCHEDULE["twitter"][slot_index % len(SCHEDULE["twitter"])]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()

    # Insert hook tweet as main row; rest as thread children
    parent_id = None
    for i, tweet in enumerate(tweets):
        row = conn.execute(
            """INSERT INTO posts (platform, content_text, scheduled_at, status, thread_parent_id,
               metadata_json, slug)
               VALUES (?,?,?,'pending',?,?,?)""",
            (
                "twitter",
                tweet,
                scheduled_at,
                parent_id,
                json.dumps({"tweet_index": i, "total_tweets": len(tweets)}),
                slug,
            ),
        )
        if i == 0:
            parent_id = row.lastrowid

    print(f"  [queued] twitter/{slug} — {len(tweets)} tweets at {scheduled_at}")


def insert_linkedin(conn: sqlite3.Connection, slug: str, txt_path: Path, slot_index: int):
    if slug_already_loaded(conn, slug, "linkedin"):
        print(f"  [skip] linkedin/{slug} already in DB")
        return

    text = txt_path.read_text(encoding="utf-8").strip()
    if not text:
        return

    # Check for matching thumbnail
    thumb = REPO / "assets" / "thumbnails" / f"{slug}_thumb.png"
    media_path = str(thumb.relative_to(REPO)) if thumb.exists() else None

    weekday, hour, minute = SCHEDULE["linkedin"][slot_index % len(SCHEDULE["linkedin"])]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()

    conn.execute(
        """INSERT INTO posts (platform, content_text, media_path, scheduled_at, status,
           metadata_json, slug)
           VALUES (?,?,?,?,?,?,?)""",
        ("linkedin", text, media_path, scheduled_at, "pending", json.dumps({}), slug),
    )
    print(f"  [queued] linkedin/{slug} — at {scheduled_at}" + (f" + image" if media_path else ""))


PUBLER_FIELDS = [
    "Date",
    "Text",
    "Link(s)",
    "Media URL(s)",
    "Title",
    "Label(s)",
    "Alt text(s)",
    "Comment(s)",
    "Pin board, FB album, or Google category",
    "Post subtype",
    "CTA",
    "Reminder",
]


def _publer_row(scheduled_dt: datetime, text: str, image: str = "",
                subtype: str = "", label: str = "") -> dict:
    return {
        "Date": scheduled_dt.strftime("%m/%d/%Y %H:%M"),
        "Text": text,
        "Link(s)": "",
        "Media URL(s)": image,
        "Title": "",
        "Label(s)": label,
        "Alt text(s)": "",
        "Comment(s)": "",
        "Pin board, FB album, or Google category": "",
        "Post subtype": subtype,
        "CTA": "",
        "Reminder": "",
    }


def _parse_ig_subtype(caption_text: str) -> str:
    """Extract format (carousel/reel/story) from instagram_caption.txt first line."""
    first = caption_text.splitlines()[0].lower() if caption_text else ""
    if "reel" in first:
        return "reel"
    if "carousel" in first:
        return ""  # Publer default for carousel is blank subtype
    if "story" in first:
        return "story"
    return ""


def _write_publer_csv(path: Path, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PUBLER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_publer_csvs(slugs_data: list[str]) -> tuple[Path, Path]:
    """
    Generate two Publer bulk import CSVs.

    publer_ig_fb.csv  — 1 row per blog, import with Instagram + Facebook selected
    publer_threads.csv — 1 row per blog, import with Threads selected

    Each row = one post sent to ALL accounts selected at import time.
    Publer does not support per-row account targeting in bulk import.
    """
    out_dir = REPO / "output" / "scheduled"
    out_dir.mkdir(parents=True, exist_ok=True)

    ig_fb_rows = []
    threads_rows = []

    for i, slug in enumerate(slugs_data):
        slug_dir = REPO / "content" / "derivatives" / slug
        thumb = REPO / "assets" / "thumbnails" / f"{slug}_thumb.png"
        image = str(thumb) if thumb.exists() else ""

        # Instagram + Facebook — one row, same slot, same caption
        ig_caption_path = slug_dir / "instagram_caption.txt"
        if ig_caption_path.exists():
            ig_caption = ig_caption_path.read_text(encoding="utf-8").strip()
            subtype = _parse_ig_subtype(ig_caption)
            clean_caption = "\n".join(
                l for l in ig_caption.splitlines()
                if not l.startswith("Format:") and not l.startswith("Why:")
            ).strip()
            slots = SCHEDULE["instagram"]
            weekday, hour, minute = slots[i % len(slots)]
            scheduled_dt = next_weekday(weekday, hour, minute)
            ig_fb_rows.append(_publer_row(scheduled_dt, clean_caption, image, subtype, label=slug))

        # Threads — separate CSV, no image, no subtype
        threads_path = slug_dir / "threads_post.txt"
        if threads_path.exists():
            threads_text = threads_path.read_text(encoding="utf-8").strip()
            slots = SCHEDULE["threads"]
            weekday, hour, minute = slots[i % len(slots)]
            scheduled_dt = next_weekday(weekday, hour, minute)
            threads_rows.append(_publer_row(scheduled_dt, threads_text, label=slug))

    ig_fb_path = out_dir / "publer_ig_fb.csv"
    threads_path = out_dir / "publer_threads.csv"
    _write_publer_csv(ig_fb_path, ig_fb_rows)
    _write_publer_csv(threads_path, threads_rows)

    return ig_fb_path, threads_path


def build_shorts_upload_script(slugs: list[str]) -> Path | None:
    """
    Generate output/scheduled/upload_shorts.sh with pre-filled upload_youtube.py --shorts
    commands for each slug that has youtube_shorts_metadata.json.

    Niche is inferred from slug prefix (ds|life|poetry) → channel name.
    """
    NICHE_TO_CHANNEL = {
        "ds":     "Breath of Data Science",
        "life":   "Breath of Life",
        "poetry": "Breath of Poetry",
    }
    DEFAULT_CHANNEL = "Breath of Data Science"

    lines = ["#!/bin/bash", "# YouTube Shorts upload commands — generated by load_posts.py", "# Run on Friday after recording.", ""]

    found = []
    for slug in slugs:
        meta_path = REPO / "content" / "derivatives" / slug / "youtube_shorts_metadata.json"
        if not meta_path.exists():
            continue

        # Infer channel from slug
        channel = DEFAULT_CHANNEL
        for prefix, ch in NICHE_TO_CHANNEL.items():
            if f"-{prefix}-" in slug or slug.startswith(f"{prefix}-"):
                channel = ch
                break

        # Infer reel video path — same file used for IG reel
        reel_path = f"assets/video/edited/{slug}_reel.mp4"

        lines.append(f"# {slug}")
        lines.append(
            f'python3 scripts/upload_youtube.py --shorts --slug "{slug}" '
            f'--channel "{channel}" '
            f'--video "{reel_path}" '
            f'--category 22'
        )
        lines.append("")
        found.append(slug)

    if not found:
        return None

    out_path = REPO / "output" / "scheduled" / "upload_shorts.sh"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    out_path.chmod(0o755)
    return out_path


def main():
    if not DB_PATH.exists():
        sys.exit(f"DB not found: {DB_PATH}\nRun: python3 scripts/db_setup.py first")

    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        sys.exit("content/derivatives/ not found — run repurpose_blog.py first")

    slugs = sorted([d.name for d in deriv_dir.iterdir() if d.is_dir()])
    if not slugs:
        sys.exit("No derivative folders found.")

    print(f"Loading {len(slugs)} slug(s) into scheduling.db ...\n")

    conn = sqlite3.connect(DB_PATH)

    for i, slug in enumerate(slugs):
        slug_dir = deriv_dir / slug
        print(f"[{i+1}/{len(slugs)}] {slug}")

        linkedin_file = slug_dir / "linkedin_post.txt"
        if linkedin_file.exists():
            insert_linkedin(conn, slug, linkedin_file, i)

    conn.commit()

    # Summary
    total = conn.execute("SELECT COUNT(*) FROM posts WHERE status='pending'").fetchone()[0]
    conn.close()

    print(f"\nDB: {total} pending LinkedIn post(s) in scheduling.db")

    # Publer CSVs — two separate imports
    ig_fb_path, thr_path = build_publer_csvs(slugs)
    print(f"Publer IG+FB CSV  : {ig_fb_path.relative_to(REPO)}")
    print("  → Import with Instagram + Facebook accounts selected")
    print(f"Publer Threads CSV: {thr_path.relative_to(REPO)}")
    print("  → Import with Threads account selected")

    # YouTube Shorts upload script
    shorts_script = build_shorts_upload_script(slugs)
    if shorts_script:
        print(f"YT Shorts script  : {shorts_script.relative_to(REPO)}")
        print("  → Run on Friday after recording: bash output/scheduled/upload_shorts.sh")
        print("  → Ensure reel video files exist at assets/video/edited/{slug}_reel.mp4")
    else:
        print("YT Shorts script  : skipped (no youtube_shorts_metadata.json found)")

    print("\nNext: start APScheduler daemon (LinkedIn only):")
    print("  nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &")


if __name__ == "__main__":
    main()
