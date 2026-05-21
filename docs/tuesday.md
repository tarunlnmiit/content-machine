# Tuesday — Life Blog + Repurpose DS (~35 min)

## Step 1 — Produce Life blog

Option A — topic only:
```bash
python3 scripts/produce_blog.py --topic 'YOUR LIFE TOPIC' --niche life --humanize
```

Option B — have notes/transcript:
```bash
python3 scripts/ghostwrite.py --source notes.txt --niche life --voice conversational
```

## Step 2 — Fill personal sections
```bash
grep -rn 'PERSONAL_INSERT' content/blogs/
```

## Step 3 — Add images to Life blog
```bash
python3 scripts/fetch_images.py --input content/blogs/[tuesday_life_blog].md --dry-run
python3 scripts/fetch_images.py --input content/blogs/[tuesday_life_blog].md
```

## Step 4 — Repurpose Monday's DS blog (with design prompts)
```bash
python3 scripts/repurpose_blog.py --input content/blogs/[monday_ds_blog].md --design
# Saves 10 files to content/derivatives/{slug}/
# Includes claude_design_brief.json
# Calls generate_design_prompts.py automatically
# → output/scheduled/claude_design_prompts_{slug}.md (4 sections)
# For DS tutorial blogs: extracts + validates code blocks before generating slide deck prompt
```

## Step 5 — DS thumbnail brief
```bash
python3 scripts/thumbnail_brief.py --input content/blogs/[monday_ds_blog].md
# → content/derivatives/{slug}/thumbnail_brief.json
```
