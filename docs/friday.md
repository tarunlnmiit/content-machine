# Friday — Life + Poetry Video: Scripts + B-roll + Recording (~1.5 hrs)

Record both Life and Poetry today. Edit moves to Saturday.

---

## Step 1 — Generate Life YT script (~5 min)

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[tuesday_life_blog].md \
  --niche life --format yt --video-style stock
```

Output: `content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md`
- [BROLL: description] cues for stock footage placement
- [PAUSE] markers for breath points
- Suitable for both YouTube + Spotify podcast

---

## Step 2 — Generate Poetry YT script (~5 min)

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[wednesday_poetry_blog].md \
  --niche poetry --format yt --video-style stock
```

Output: `content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md`
- Poem read twice: opening (uncontextualized) + mid-script (with pauses)
- Includes poet attribution if third-party poem
- [BROLL:] cues for visual sections

---

## Step 3 — Fetch B-roll clips for Life + Poetry (5–10 min)

```bash
python3 scripts/fetch_videos.py \
  --script content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --niche life

python3 scripts/fetch_videos.py \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md \
  --niche poetry
```

Output: `assets/videos/{slug}/`
- `{slug}_clip_00.mp4`, `{slug}_clip_01.mp4`, ... (2 clips per [BROLL:] cue)
- `VIDEO_MAP.json` (clip → section_cue mapping)

---

## Step 4 — Generate production guides (1–2 min each)

```bash
python3 scripts/generate_production_guide.py \
  --script content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --niche life

python3 scripts/generate_production_guide.py \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md \
  --niche poetry \
  --poem data/poems/[slug].txt \
  --full-poem
```

Output: `content/scripts/{slug}_PRODUCTION_GUIDE.md`
- Section → clip mapping table
- Estimated runtime (~7–9 min)
- DaVinci Resolve assembly steps

Poetry only: `--full-poem` also generates `content/scripts/{slug}_poetry_overlay.srt` (full poem text distributed across voiceover duration for overlay captions)

---

## Step 5 — Record Life voiceover (20–30 min)

1. Open `content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md`
2. Read aloud at ~130 wpm, clap at [PAUSE] points
3. Save: `assets/audio/[life_slug]_voiceover.wav`

---

## Step 6 — Record Poetry voiceover (20–30 min)

1. Open `content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md`
2. Read poem twice as scripted — first read slow and uncontextualized, second with pauses marked
3. Save: `assets/audio/[poetry_slug]_voiceover.wav`

---

## Step 7 — Generate captions for Life + Poetry (~2 min each)

```bash
python3 scripts/generate_captions.py \
  --audio assets/audio/[life_slug]_voiceover.wav \
  --format srt \
  --output content/scripts/[life_slug]_captions.srt

python3 scripts/generate_captions.py \
  --audio assets/audio/[poetry_slug]_voiceover.wav \
  --format srt \
  --output content/scripts/[poetry_slug]_captions.srt
```
