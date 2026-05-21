# Thursday — DS Video: Script + Record + Edit + Reel + Upload (~2 hrs)

DS is self-contained today. Life + Poetry video production moves to Friday.

---

## Step 1 — Generate DS YouTube script (~5 min)

Screen recording script with [SCREEN:] cues:
```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[monday_ds_blog].md \
  --niche ds --format yt
# --video-style screen is default for DS
```

Output: `content/scripts/YYYY-MM-DD-data-science-tech-{slug}_yt.md`
- [SCREEN: show X] cues for screen transitions
- [CODE_INSERT: filename/function] for code blocks
- [PAUSE] markers for breath points

Optional — conceptual DS (no screen recording):
```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[monday_ds_blog].md \
  --niche ds --format yt --video-style stock
# Then follow Life/Poetry B-roll workflow (Friday)
```

---

## Step 2 — Screen record DS code walkthrough (30–45 min)

1. Open screen recorder (ScreenFlow · OBS · built-in Mac)
2. Open IDE showing blog code at 200% zoom for visibility
3. Follow script — show code, run demos, narrate [SCREEN:] cues
4. Save: `assets/video/raw/{slug}_screen.mp4`

---

## Step 3 — Record DS voiceover (15–20 min)

1. Read script aloud naturally at ~130 wpm
2. Clap at [PAUSE] points (visible in waveform for easy trim)
3. Save: `assets/audio/{slug}_voiceover.wav`

Tools: Voice Memos (quick) · Audacity (control) · Adobe Audition (pro)

---

## Step 4 — Generate captions with Whisper (~2 min)

```bash
python3 scripts/generate_captions.py \
  --audio assets/audio/{slug}_voiceover.wav \
  --format srt \
  --output content/scripts/{slug}_captions.srt
```

---

## Step 5 — Edit DS in DaVinci Resolve (20–30 min)

Reference files:
- Script: `content/scripts/YYYY-MM-DD-data-science-tech-{slug}_yt.md`
- Captions: `content/scripts/{slug}_captions.srt`

Steps:
1. Import screen recording to video track
2. Import voiceover to audio track
3. Optionally add B-roll intro/outro clips (`assets/videos/{slug}/`)
4. Import captions → Fusion → Caption Editor
5. Trim dead space, sync audio/video
6. Add text overlays for section titles
7. Add music (optional, -15 to -25 dB)
8. Export → `assets/video/edited/{slug}.mp4` (H.264, YouTube preset, 1080p)

Optional B-roll fetch before editing:
```bash
python3 scripts/fetch_videos.py \
  --input content/blogs/[monday_ds_blog].md \
  --niche ds
# → assets/videos/{slug}/ (6–10 clips for intro/outro)
```

---

## Step 6 — Generate DS reel (~5 min)

Find best 60-second moment:
```bash
python3 scripts/find_best_reel_moment.py \
  --blog content/blogs/[monday_ds_blog].md \
  --video assets/video/edited/[monday_ds_blog].mp4
# Returns top 3 timestamps + relevance scores
```

Create vertical reel (use top timestamp):
```bash
python3 scripts/create_vertical_reels.py \
  --slug [monday_ds_blog_slug] \
  --start MM:SS \
  --duration 60
# → assets/video/edited/{slug}_reel.mp4 (9:16 vertical)
```

---

## Step 7 — Upload DS to YouTube (~10 min)

Long-form:
```bash
python3 scripts/upload_youtube.py \
  --video assets/video/edited/[monday_ds_blog].mp4 \
  --slug [monday_ds_blog_slug]
```

Short (reel):
```bash
python3 scripts/upload_youtube.py \
  --shorts \
  --slug [monday_ds_blog_slug] \
  --channel "Breath of Data Science" \
  --video assets/video/edited/[monday_ds_blog_slug]_reel.mp4
```

Verify export:
```bash
ls -la assets/video/edited/
# Should show {slug}.mp4 + {slug}_reel.mp4
```
