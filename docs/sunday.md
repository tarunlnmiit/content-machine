# Sunday — Publishing + Review (~20 min)

---

## Step 1 — Instagram + Facebook + Threads via Publer (10 min)

Open Publer dashboard:
- Import `output/scheduled/publer_ig_fb.csv` → select Instagram + Facebook → schedule
- Import `output/scheduled/publer_threads.csv` → select Threads → schedule

---

## Step 2 — Twitter/X (manual or auto)

Auto (APScheduler fires once `load_posts.py` ran Saturday):
```bash
sqlite3 data/scheduling.db \
  "SELECT * FROM posts WHERE platform='twitter' ORDER BY scheduled_at"
```

Manual:
```bash
cat content/derivatives/[ds_slug]/twitter_thread.txt
cat content/derivatives/[life_slug]/twitter_thread.txt
cat content/derivatives/[poetry_slug]/twitter_thread.txt
# Paste into Twitter/X scheduler
```

---

## Step 3 — Newsletter (optional, 5 min)

```bash
cat content/derivatives/[ds_slug]/newsletter.txt
cat content/derivatives/[life_slug]/newsletter.txt
cat content/derivatives/[poetry_slug]/newsletter.txt
# Copy each to Beehiiv → schedule
```

---

## Step 4 — Analytics review (5 min)

Cron auto-runs at 8pm:
```bash
cat data/analytics/weekly_insights.md     # auto-generated 8pm
cat data/analytics/research_log.txt | tail -20   # cron health
```

---

## Step 5 — Read KB for next week (5 min)

Cron auto-rebuilds at 10pm:
```bash
cat data/kb/master_brief.md
# Read before picking Monday's DS topic
```

> Twitter + LinkedIn fire automatically via APScheduler once `load_posts.py` runs Saturday.
> Verify rows exist with correct `scheduled_at` times before closing.
