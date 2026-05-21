#!/usr/bin/env python3
"""
APScheduler daemon — polls scheduling.db every 60 seconds.
Fires pending posts when scheduled_at <= now.
Dispatches to post_twitter.py and post_linkedin.py.
Updates DB status to 'posted' or 'failed'.

Run as background daemon:
    nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &

Check it's running:
    ps aux | grep scheduler.py

Stop it:
    pkill -f scheduler.py
"""

import json
import logging
import signal
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")

IST = timezone(timedelta(hours=5, minutes=30))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("scheduler")


# ── Dispatch functions ────────────────────────────────────────────────────

def dispatch_twitter(post: dict):
    """Collect the full thread (parent + children) and post."""
    sys.path.insert(0, str(REPO / "scripts"))
    from post_twitter import post_thread, parse_thread_file

    post_id = post["id"]
    slug = post["slug"]
    content = post["content_text"]

    # Gather all tweets in thread order (parent first, then children by id)
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, content_text FROM posts WHERE (id=? OR thread_parent_id=?) AND platform='twitter' ORDER BY id ASC",
        (post_id, post_id),
    ).fetchall()
    conn.close()

    tweets = [r[1] for r in rows]
    db_ids = [r[0] for r in rows]

    log.info(f"Posting Twitter thread: slug={slug}, {len(tweets)} tweets")
    try:
        posted_ids = post_thread(tweets, db_post_id=post_id, slug=slug)
        # Mark all thread rows as posted
        conn = sqlite3.connect(DB_PATH)
        now = datetime.now(timezone.utc).isoformat()
        for db_id in db_ids:
            conn.execute(
                "UPDATE posts SET status='posted', posted_at=? WHERE id=?",
                (now, db_id),
            )
        conn.commit()
        conn.close()
        log.info(f"Twitter thread posted: {posted_ids[0] if posted_ids else 'unknown'}")
    except Exception as e:
        _mark_failed(post_id, str(e))
        log.error(f"Twitter post failed: {e}")


def dispatch_linkedin(post: dict):
    sys.path.insert(0, str(REPO / "scripts"))
    from post_linkedin import post_text, get_credentials

    post_id = post["id"]
    slug = post["slug"]
    text = post["content_text"]
    media_path = post["media_path"]

    image_path = (REPO / media_path) if media_path else None

    log.info(f"Posting LinkedIn: slug={slug}")
    try:
        token, urn = get_credentials()
        post_urn = post_text(token, urn, text, image_path)
        _mark_posted(post_id, {"post_urn": post_urn, "slug": slug})
        log.info(f"LinkedIn posted: {post_urn}")
    except Exception as e:
        _mark_failed(post_id, str(e))
        log.error(f"LinkedIn post failed: {e}")


DISPATCHERS = {
    "twitter": dispatch_twitter,
    "linkedin": dispatch_linkedin,
}


# ── DB helpers ────────────────────────────────────────────────────────────

def _mark_posted(post_id: int, meta: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE posts SET status='posted', posted_at=?, metadata_json=? WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), json.dumps(meta), post_id),
    )
    conn.commit()
    conn.close()


def _mark_failed(post_id: int, error: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE posts SET status='failed', posted_at=?, metadata_json=? WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), json.dumps({"error": error}), post_id),
    )
    conn.commit()
    conn.close()


# ── Poll function ─────────────────────────────────────────────────────────

def poll_and_fire():
    if not DB_PATH.exists():
        log.warning("scheduling.db not found — skipping poll")
        return

    now = datetime.now(IST).isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Only fire parent posts (thread_parent_id IS NULL) to avoid double-posting thread children
    due = conn.execute(
        """SELECT * FROM posts
           WHERE status='pending'
             AND scheduled_at <= ?
             AND (thread_parent_id IS NULL)
           ORDER BY scheduled_at ASC""",
        (now,),
    ).fetchall()
    conn.close()

    if not due:
        return

    log.info(f"Found {len(due)} due post(s)")

    for row in due:
        post = dict(row)
        platform = post["platform"]

        if platform not in DISPATCHERS:
            log.warning(f"No dispatcher for platform '{platform}' — marking cancelled")
            _mark_failed(post["id"], f"No dispatcher for platform: {platform}")
            continue

        try:
            DISPATCHERS[platform](post)
        except Exception as e:
            log.error(f"Dispatcher error for post {post['id']}: {e}")
            _mark_failed(post["id"], str(e))


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if not DB_PATH.exists():
        log.error(f"DB not found: {DB_PATH}")
        log.error("Run: python3 scripts/db_setup.py first")
        sys.exit(1)

    log.info("Starting APScheduler daemon (IST timezone)")
    log.info(f"DB: {DB_PATH}")
    log.info("Polling every 60 seconds. Stop with: pkill -f scheduler.py")

    scheduler = BackgroundScheduler(timezone=IST)
    scheduler.add_job(poll_and_fire, "interval", seconds=60, id="poll_and_fire")
    scheduler.start()

    # Run once immediately on startup
    poll_and_fire()

    def handle_shutdown(sig, frame):
        log.info("Shutting down scheduler ...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    while True:
        time.sleep(30)


if __name__ == "__main__":
    main()
