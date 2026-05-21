# Weekly Operating Guide

Last updated: 2026-05-20

## Week at a Glance

| Day | Focus | Time |
|-----|-------|------|
| [Monday](monday.md) | DS Blog — produce, fill, images | ~25 min |
| [Tuesday](tuesday.md) | Life Blog + Repurpose DS (with design prompts) | ~35 min |
| [Wednesday](wednesday.md) | Poetry Blog + Repurpose all + Claude Design + Worksheets | ~40 min + 15–20 min Claude Design |
| [Thursday](thursday.md) | DS video: script → record → edit → reel → upload | ~2 hrs |
| [Friday](friday.md) | Life + Poetry: scripts → B-roll → voiceover recording | ~1.5 hrs |
| [Saturday](saturday.md) | Edit Life + Poetry → reels → upload → publish Medium → load scheduler | ~2 hrs |
| [Sunday](sunday.md) | Social scheduling (Publer + Twitter) + review | ~20 min |

---

## Setup (one-time)

Install dependencies:
```bash
pip install openai-whisper nltk anthropic python-dotenv
```

Install DaVinci Resolve (editing):
- Download: https://www.blackmagicdesign.com/products/davinciresolve
- Free version sufficient

Start scheduler daemon:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

**Claude Design (primary visual tool)**
Access: claude.ai → Design tab
Used Wednesday for: slide decks · Instagram story sequences · reel covers · social post sets (IG · LinkedIn · Twitter/X · Threads)

---

## Build Status

| Day | Focus | Status |
|-----|-------|--------|
| Day 1 | Foundation — folder, CLAUDE.md, MCPs | ✅ Done |
| Day 2 | Research + KB pipeline | ✅ Done |
| Day 3 | Writing + Repurposing agents | ✅ Done |
| Day 3b | Ghostwriter agent | ✅ Done (`ghostwrite.py` + `ghostwriter_agent.md`) |
| Day 4 | Claude Design pipeline | ✅ Done — `generate_design_prompts.py` + `claude_design_agent.md` |
| Day 5 | Distribution automation | ⚠️ Scripts done — scheduler not running, DB empty |
| Day 6 | First full production run | ⚠️ Blogs + derivatives exist, no posts loaded, no videos |
| Day 7 | SOP + analytics | ⚠️ `collect_analytics.py` done — Streamlit dashboard not built |

**Remaining before fully automated:**
- Load current blogs: `python3 scripts/load_posts.py`
- Start APScheduler: `nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &`
- Build Streamlit dashboard: `dashboard/app.py` (not yet created)
- Get Twitter archive → build `data/kb/twitter_hook_patterns.json`

---

## What runs automatically

| Time | What |
|------|------|
| Every day 6am | `rss_scraper.py` + `youtube_scraper.py` + `idea_scorer.py` → `data/ideas/weekly_ideas.md` |
| Sunday 8pm | `collect_analytics.py` → `data/analytics/weekly_insights.md` |
| Sunday 10pm | `build_knowledge_base.py` → `data/kb/master_brief.md` |
| Continuous | `scheduler.py` → fires pending posts from `data/scheduling.db` every 60s |

> Check scheduler: `ps aux | grep scheduler.py | grep -v grep`

---

## Key Files

```
data/ideas/weekly_ideas.md                       ← Monday topic picking
data/kb/master_brief.md                          ← read before every writing session
data/poems/                                      ← POETRY: one poem per file ({slug}.txt)

content/blogs/                                   ← finished blogs (check [PERSONAL_INSERT] resolved)
content/blogs/{stem}_images/                     ← downloaded images + IMAGE_MAP.md
content/scripts/
  ├── YYYY-MM-DD-{niche}-{slug}_yt.md            ← YouTube voiceover script
  ├── {slug}_PRODUCTION_GUIDE.md                 ← section → clip mapping + timing
  ├── {slug}_captions.srt                        ← Whisper captions for DaVinci
  └── {slug}_poetry_overlay.srt                  ← POETRY ONLY: full poem SRT overlay

content/derivatives/{slug}/                      ← 10 files per blog
  ├── twitter_thread.txt
  ├── linkedin_post.txt
  ├── instagram_caption.txt
  ├── threads_post.txt
  ├── newsletter.txt
  ├── slide_outline.json
  ├── youtube_metadata.json
  ├── youtube_shorts_metadata.json
  ├── polls.json
  ├── thumbnail_brief.json
  └── claude_design_brief.json                   ← emotional core, key quotes, story frames

prompts/claude_design_agent.md                   ← Claude Design art direction system
output/scheduled/claude_design_prompts_{slug}.md ← 4 design prompts per blog (paste into Claude Design)
output/scheduled/validated_code_{slug}.json      ← DS tutorial: tested code blocks

assets/
  ├── slides/{slug}_slides.pdf                   ← from Claude Design
  ├── stories/{slug}_story_*.png                 ← from Claude Design
  ├── social_posts/{slug}_instagram.png          ← 1080×1080
  ├── social_posts/{slug}_linkedin.png           ← 1200×628
  ├── social_posts/{slug}_twitter.png            ← 1200×675
  ├── social_posts/{slug}_threads.png            ← 1080×1080
  ├── reels/{slug}_cover.png                     ← 9:16 from Claude Design
  ├── audio/{slug}_voiceover.wav                 ← recorded voiceover
  ├── videos/{slug}/                             ← B-roll clips + VIDEO_MAP.json
  ├── video/edited/{slug}.mp4                    ← long-form YouTube (FINAL)
  └── video/edited/{slug}_reel.mp4              ← YouTube Short / reel (FINAL, 9:16)

output/scheduled/publer_ig_fb.csv               ← import with Instagram + Facebook selected
output/scheduled/publer_threads.csv             ← import with Threads selected
output/scheduled/upload_shorts.sh               ← pre-filled YouTube Shorts upload commands
data/scheduling.db                              ← post queue
data/analytics/scheduler.log                   ← APScheduler activity
```

---

## Fallback Canva path (if Claude Design unavailable)

```bash
python3 scripts/generate_canva_prompts_legacy.py   # Canva AI 2.0 prompts
python3 scripts/generate_slides.py                  # → output/scheduled/{slug}_slides.csv
python3 scripts/generate_quote_cards.py             # → output/scheduled/quote_cards.csv
python3 scripts/generate_canva_prompts.py           # → output/scheduled/canva_prompts.md (thumbnails)
```

---

## Still to build

| Item | What's needed |
|------|--------------|
| Streamlit dashboard | `dashboard/app.py` — not yet created |
| Twitter hook patterns | Request Twitter archive → extract → `data/kb/twitter_hook_patterns.json` |
| LinkedIn OAuth refresh | Tokens expire 60 days — rerun `scripts/linkedin_auth.py` when needed |
| Worksheet automation | `scripts/auto_worksheet_workflow.py` — worksheet gen + Claude Design prompt in one call |
