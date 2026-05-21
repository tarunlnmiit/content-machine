# Weekly Production Steps — Thursday to Saturday

Generated: 2026-05-16 (use next week)

---

## THURSDAY — Video Production

**Step 1: Generate voiceover scripts** (~5 min each)

```bash
python3 scripts/ghostwrite.py --source content/blogs/YYYY-MM-DD_data_science_tech_*.md --niche ds --format yt
python3 scripts/ghostwrite.py --source content/blogs/YYYY-MM-DD_life_self_dev_*.md --niche life --format yt
python3 scripts/ghostwrite.py --source content/blogs/YYYY-MM-DD_poetry_quotes_*.md --niche poetry --format yt
```

Outputs: `content/scripts/YYYY-MM-DD-{slug}_yt.md` (3 files)

---

**Step 2: Fetch B-roll clips** (~10 min)

```bash
python3 scripts/fetch_videos.py --script content/scripts/YYYY-MM-DD-data-science-tech-*_yt.md --niche ds
python3 scripts/fetch_videos.py --script content/scripts/YYYY-MM-DD-life-self-dev-*_yt.md --niche life
python3 scripts/fetch_videos.py --script content/scripts/YYYY-MM-DD-poetry-quotes-*_yt.md --niche poetry
```

Outputs: `assets/videos/{slug}/` + `VIDEO_MAP.json`

---

**Step 3: Generate production guides** (~1 min each)

```bash
python3 scripts/generate_production_guide.py --script content/scripts/YYYY-MM-DD-life-self-dev-*_yt.md --niche life
python3 scripts/generate_production_guide.py --script content/scripts/YYYY-MM-DD-poetry-quotes-*_yt.md --niche poetry
```

Outputs: `content/scripts/{slug}_PRODUCTION_GUIDE.md` (section → clip mapping)

---

**Step 4: Record voiceovers** (~45 min total)

1. Open script: `content/scripts/YYYY-MM-DD-{slug}_yt.md`
2. Read aloud naturally (~130 wpm)
3. Mark [PAUSE] points by clapping (visible in waveform)
4. Record in one continuous take (edit pauses later)
5. Save: `assets/audio/{slug}_voiceover.wav`

Tools: Voice Memos, Audacity, or Adobe Audition

---

**Step 5: CapCut assembly** (~20-30 min per video)

Per video:
1. Open `content/scripts/{slug}_PRODUCTION_GUIDE.md` + `content/blogs/{slug}_CAPCUT_EDITING_GUIDE.md`
2. Import B-roll clips (Life/Poetry) or screen recording (DS) to video track
3. Drag voiceover audio to audio track
4. Sync clips to voiceover duration (trim as needed)
5. Add captions: Text → Auto Captions on voiceover
6. Add music (optional, 15-25 volume)
7. Add text overlays (section titles, key insights)
8. Check total runtime matches production guide
9. Export → `assets/video/edited/{slug}.mp4`

---

**Step 6: Generate worksheet outlines for email lead magnets** (~5 min)

```bash
python3 scripts/generate_worksheet_outline.py -i content/blogs/YYYY-MM-DD_data_science_tech_*.md
python3 scripts/generate_worksheet_outline.py -i content/blogs/YYYY-MM-DD_life_self_dev_*.md
python3 scripts/generate_worksheet_outline.py -i content/blogs/YYYY-MM-DD_poetry_quotes_*.md
```

Outputs: `content/worksheets/{slug}_worksheet.json` (auto-skips poetry — reflection format)

Generate Canva prompts:
```bash
python3 scripts/generate_canva_worksheet_prompt.py -i content/worksheets/YYYY-MM-DD_data_science_tech_*_worksheet.json
python3 scripts/generate_canva_worksheet_prompt.py -i content/worksheets/YYYY-MM-DD_life_self_dev_*_worksheet.json
```

Copy both prompts to clipboard (ready for Friday Canva design).

---

## FRIDAY — Reels + YouTube Upload

**Step 1: Create vertical reels** (~20 min total)

```bash
python3 scripts/find_best_reel_moment.py --blog content/blogs/YYYY-MM-DD_data_science_tech_*.md --video assets/video/edited/YYYY-MM-DD_data_science_tech_*.mp4
# (returns top 3 timestamps + scores, pick #1)
python3 scripts/create_vertical_reels.py --slug YYYY-MM-DD_data_science_tech_* --start MM:SS --duration 60

python3 scripts/find_best_reel_moment.py --blog content/blogs/YYYY-MM-DD_life_self_dev_*.md --video assets/video/edited/YYYY-MM-DD_life_self_dev_*.mp4
python3 scripts/create_vertical_reels.py --slug YYYY-MM-DD_life_self_dev_* --start MM:SS --duration 60

python3 scripts/find_best_reel_moment.py --blog content/blogs/YYYY-MM-DD_poetry_quotes_*.md --video assets/video/edited/YYYY-MM-DD_poetry_quotes_*.mp4
python3 scripts/create_vertical_reels.py --slug YYYY-MM-DD_poetry_quotes_* --start MM:SS --duration 60
```

Outputs: `assets/video/edited/{slug}_reel.mp4` (3 files)

Verify: `ls -la assets/video/edited/ | grep reel`

---

**Step 2: Load all posts into schedule**

```bash
python3 scripts/load_posts.py
```

Inserts all derivative content into `data/scheduling.db`

---

**Step 3: Verify scheduler running**

```bash
ps aux | grep scheduler.py | grep -v grep
```

If not running:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

---

**Step 4: Check queue**

```bash
sqlite3 data/scheduling.db 'SELECT platform, scheduled_at, status, substr(content_text,1,60) FROM posts ORDER BY scheduled_at LIMIT 10'
```

---

**Step 5: Upload YouTube long-form videos** (~10 min each, 30 min total)

```bash
python3 scripts/upload_youtube.py --video assets/video/edited/YYYY-MM-DD_data_science_tech_*.mp4 --slug YYYY-MM-DD_data_science_tech_*

python3 scripts/upload_youtube.py --video assets/video/edited/YYYY-MM-DD_life_self_dev_*.mp4 --slug YYYY-MM-DD_life_self_dev_*

python3 scripts/upload_youtube.py --video assets/video/edited/YYYY-MM-DD_poetry_quotes_*.mp4 --slug YYYY-MM-DD_poetry_quotes_*
```

---

**Step 6: Upload YouTube Shorts** (~10 min total)

```bash
python3 scripts/upload_youtube.py --shorts --slug YYYY-MM-DD_data_science_tech_* --channel "Breath of Data Science" --video assets/video/edited/YYYY-MM-DD_data_science_tech_*_reel.mp4

python3 scripts/upload_youtube.py --shorts --slug YYYY-MM-DD_life_self_dev_* --channel "Breath of Life" --video assets/video/edited/YYYY-MM-DD_life_self_dev_*_reel.mp4

python3 scripts/upload_youtube.py --shorts --slug YYYY-MM-DD_poetry_quotes_* --channel "Breath of Poetry" --video assets/video/edited/YYYY-MM-DD_poetry_quotes_*_reel.mp4
```

---

**Step 7: Design worksheets in Canva** (~10 min per worksheet, 20 min total)

DS Worksheet:
1. Copy DS prompt from Thursday Step 6 output
2. Go to Canva.com → Create Design → Custom Size → A4 (210 x 297 mm)
3. Paste prompt into Canva AI Design (or design manually per structure)
4. Export as PDF → Save to `output/worksheets/YYYY-MM-DD_data_science_tech_*_worksheet.pdf`

Life Worksheet:
1. Copy Life prompt from Thursday Step 6 output
2. Canva.com → Create Design → Custom Size → A4 Portrait
3. Paste prompt → AI Design → Export PDF
4. Save to `output/worksheets/YYYY-MM-DD_life_self_dev_*_worksheet.pdf`

Verify: `ls output/worksheets/ | grep worksheet.pdf`

---

## SATURDAY — Publishing

**Step 1: Publish to Medium** (~15 min total)

```bash
python3 scripts/publish_medium.py --input content/blogs/YYYY-MM-DD_data_science_tech_*.md --canonical-url https://breathofdatascience.substack.com/

python3 scripts/publish_medium.py --input content/blogs/YYYY-MM-DD_life_self_dev_*.md --canonical-url https://thisisbreathoflife.substack.com/

python3 scripts/publish_medium.py --input content/blogs/YYYY-MM-DD_poetry_quotes_*.md --canonical-url https://breathofpoetry.substack.com/
```

---

**Step 2: Instagram + Facebook + Threads via Publer** (~10 min)

1. Open Publer dashboard
2. Import `output/scheduled/publer_ig_fb.csv` → select Instagram + Facebook → schedule
3. Import `output/scheduled/publer_threads.csv` → select Threads → schedule

---

**Step 3: Twitter** (~10 min)

Auto (fires if load_posts.py ran):
```bash
sqlite3 data/scheduling.db "SELECT * FROM posts WHERE platform='twitter' ORDER BY scheduled_at"
```

Manual fallback:
```bash
cat content/derivatives/YYYY-MM-DD_data_science_tech_*/twitter_thread.txt
cat content/derivatives/YYYY-MM-DD_life_self_dev_*/twitter_thread.txt
cat content/derivatives/YYYY-MM-DD_poetry_quotes_*/twitter_thread.txt
# (paste each into Twitter scheduler)
```

---

**Step 4: Newsletter (optional)** (~5 min)

```bash
cat content/derivatives/YYYY-MM-DD_data_science_tech_*/newsletter.txt
cat content/derivatives/YYYY-MM-DD_life_self_dev_*/newsletter.txt
cat content/derivatives/YYYY-MM-DD_poetry_quotes_*/newsletter.txt
# (paste each to Beehiiv → schedule)
```

---

**Step 5: Upload worksheets to ConvertKit + share on Instagram** (~10 min)

DS Worksheet:
1. ConvertKit → Forms → Create new → Landing Page
2. Title: "Your Model → SQL Translation Checklist"
3. Description: "Free worksheet: translate your ML model to warehouse SQL. No API server required."
4. Upload PDF: `output/worksheets/YYYY-MM-DD_data_science_tech_*_worksheet.pdf`
5. Save → copy landing page URL
6. Edit `config/worksheet_config.json` → paste URL in `worksheets[slug].convertkit.landing_page_url`
7. Add tags: data-science, ml-production, sql

Life Worksheet:
1. ConvertKit → Create new landing page
2. Title: "Design Your Check-in for Your Worst Day"
3. Description: "Free worksheet: redesign your daily habit for the version of you who's tired, busy, and low-energy."
4. Upload PDF: `output/worksheets/YYYY-MM-DD_life_self_dev_*_worksheet.pdf`
5. Save → copy URL → update config with URL
6. Add tags: habits, self-development, design

Share on Instagram:
1. Pull caption hooks from `config/worksheet_config.json` (`ig_caption_hook` + `ig_cta`)
2. IG Stories: add link sticker → landing page URL
3. Grid post: worksheet preview image + caption structure: [hook] + 📋 Free worksheet in link + [key insight] + [CTA] + #hashtags
4. Pin story for 24h

---

## Notes

- Replace `YYYY-MM-DD` with actual dates from your blog filenames
- Replace `*` with actual slugs if scripts don't support wildcards
- Cronjobs auto-run Sunday 8pm (analytics) + 10pm (knowledge base rebuild)
- Check `data/analytics/weekly_insights.md` on Sunday for recap
