# Saturday — Edit Life + Poetry + Reels + Upload + Publish (~2 hrs)

---

## Step 1 — Edit Life in DaVinci Resolve (20–30 min)

Reference files:
- Production guide: `content/scripts/[life_slug]_PRODUCTION_GUIDE.md`
- Captions: `content/scripts/[life_slug]_captions.srt`
- Clips: `assets/videos/[life_slug]/`

Steps:
1. Media Pool → Import all clips from `assets/videos/[life_slug]/`
2. Drag clips to timeline in section order (_clip_00, _clip_01, ...)
3. Import voiceover → `assets/audio/[life_slug]_voiceover.wav`
4. Import captions → `content/scripts/[life_slug]_captions.srt`
5. Sync clips to voiceover duration, trim as needed
6. Review captions → Fusion → Caption Editor (adjust timestamps if needed)
7. Add music (optional, -15 to -25 dB)
8. Add text overlays for key insights
9. Export → `assets/video/edited/[life_slug].mp4` (H.264, YouTube preset, 1080p)

---

## Step 2 — Edit Poetry in DaVinci Resolve (20–30 min)

Reference files:
- Production guide: `content/scripts/[poetry_slug]_PRODUCTION_GUIDE.md`
- Captions: `content/scripts/[poetry_slug]_captions.srt`
- Poem overlay (if generated): `content/scripts/[poetry_slug]_poetry_overlay.srt`
- Clips: `assets/videos/[poetry_slug]/`

Steps:
1. Media Pool → Import all clips from `assets/videos/[poetry_slug]/`
2. Arrange in section order per production guide
3. Import voiceover → `assets/audio/[poetry_slug]_voiceover.wav`
4. Import captions → `content/scripts/[poetry_slug]_captions.srt`
5. Poetry overlay: Import `[poetry_slug]_poetry_overlay.srt` as separate caption track — white text, sans serif, center, fade in/out over visual gaps
6. Sync, trim, review
7. Add ambient music (-20 to -25 dB — quieter than Life, more atmospheric)
8. Export → `assets/video/edited/[poetry_slug].mp4` (H.264, YouTube preset, 1080p)

---

## Step 3 — Generate Life reel (~5 min)

```bash
python3 scripts/find_best_reel_moment.py \
  --blog content/blogs/[tuesday_life_blog].md \
  --video assets/video/edited/[life_slug].mp4
# Pick top timestamp

python3 scripts/create_vertical_reels.py \
  --slug [life_slug] \
  --start MM:SS \
  --duration 60
# → assets/video/edited/[life_slug]_reel.mp4
```

---

## Step 4 — Generate Poetry reel (~5 min)

```bash
python3 scripts/find_best_reel_moment.py \
  --blog content/blogs/[wednesday_poetry_blog].md \
  --video assets/video/edited/[poetry_slug].mp4

python3 scripts/create_vertical_reels.py \
  --slug [poetry_slug] \
  --start MM:SS \
  --duration 60
# → assets/video/edited/[poetry_slug]_reel.mp4
```

Verify all 6 video files exist:
```bash
ls -la assets/video/edited/
# 3 × .mp4 (long-form) + 3 × _reel.mp4 = 6 files total
```

---

## Step 5 — Upload Life + Poetry to YouTube (~15 min)

Long-form:
```bash
python3 scripts/upload_youtube.py \
  --video assets/video/edited/[life_slug].mp4 \
  --slug [life_slug]

python3 scripts/upload_youtube.py \
  --video assets/video/edited/[poetry_slug].mp4 \
  --slug [poetry_slug]
```

Shorts:
```bash
python3 scripts/upload_youtube.py \
  --shorts \
  --slug [life_slug] \
  --channel "Breath of Life" \
  --video assets/video/edited/[life_slug]_reel.mp4

python3 scripts/upload_youtube.py \
  --shorts \
  --slug [poetry_slug] \
  --channel "Breath of Poetry" \
  --video assets/video/edited/[poetry_slug]_reel.mp4
```

Or use the pre-built script for all shorts at once:
```bash
bash output/scheduled/upload_shorts.sh
```

---

## Step 6 — Publish to Medium (~15 min)

```bash
python3 scripts/publish_medium.py \
  --input content/blogs/[monday_ds_blog].md \
  --canonical-url https://breathofdatascience.substack.com/

python3 scripts/publish_medium.py \
  --input content/blogs/[tuesday_life_blog].md \
  --canonical-url https://thisisbreathoflife.substack.com/

python3 scripts/publish_medium.py \
  --input content/blogs/[wednesday_poetry_blog].md \
  --canonical-url https://breathofpoetry.substack.com/
```

---

## Step 7 — Load posts into scheduler

```bash
python3 scripts/load_posts.py
# Inserts all derivative content into data/scheduling.db
```

Verify scheduler running:
```bash
ps aux | grep scheduler.py | grep -v grep
# If not running:
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

Check queue:
```bash
sqlite3 data/scheduling.db \
  'SELECT platform, scheduled_at, status, substr(content_text,1,60) FROM posts ORDER BY scheduled_at LIMIT 15'
```
