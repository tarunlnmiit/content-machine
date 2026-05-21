# Monday — DS Blog Production (~25 min)

## Step 1 — Pick topic (5 min)
```bash
cat data/ideas/weekly_ideas.md
# Read top 3 DS ideas. Pick one.
```

## Step 2 — Produce blog (~2 min running)

Option A — topic only:
```bash
python3 scripts/produce_blog.py --topic 'YOUR TOPIC' --niche ds
python3 scripts/produce_blog.py --topic 'YOUR TOPIC' --niche ds --humanize
```

Option B — have transcript/notes/draft:
```bash
python3 scripts/ghostwrite.py --source path/to/notes.txt --niche ds
python3 scripts/ghostwrite.py --source transcript.txt --niche ds --voice analytical --desire clarity
python3 scripts/ghostwrite.py --source notes.md --niche ds --topic 'YOUR TOPIC'
```

Saves to: `content/blogs/YYYY-MM-DD_data_science_tech_{slug}.md`

Voice options: `analytical` (default) · `conversational` · `deletion` · `decision`
Desire options: `success` · `clarity` · `status` · `tribe` · `fear` · `enjoyment`

## Step 3 — Fill personal sections (10 min)
```bash
grep -rn 'PERSONAL_INSERT' content/blogs/
# Open blog, replace every [PERSONAL_INSERT] with real memory/story
```

## Step 4 — Add images (5 min)
```bash
# Preview first
python3 scripts/fetch_images.py --input content/blogs/[monday_ds_blog].md --dry-run

# Auto-fetch from Pexels
python3 scripts/fetch_images.py --input content/blogs/[monday_ds_blog].md

# Manual swap (e.g. marker 1)
python3 scripts/fetch_images.py --input content/blogs/[monday_ds_blog].md --manual 1 --image ~/path/to/photo.jpg --alt "Caption"
```

Marker format:
```
[IMAGE_INSERT: laptop with python code]
[IMAGE_INSERT: laptop with python code | My workspace in 2023]
```

Images → `content/blogs/{stem}_images/` · Map → `content/blogs/{stem}_images/IMAGE_MAP.md`
