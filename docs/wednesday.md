# Wednesday — Poetry Blog + Repurpose All + Design (~40 min)

## Step 1 — Produce Poetry blog

Option A — topic only:
```bash
python3 scripts/produce_blog.py --topic 'YOUR POETRY TOPIC' --niche poetry --humanize
```

Option B — have poem file:
```bash
# Store poem in data/poems/[slug].txt
python3 scripts/ghostwrite.py --source data/poems/[slug].txt --niche poetry --format blog --poet "Poet Name"
# Omit --poet if poem is Tarun's own
```

Option C — have notes/draft:
```bash
python3 scripts/ghostwrite.py --source draft.txt --niche poetry --voice conversational
```

## Step 2 — Fill personal sections
```bash
grep -rn 'PERSONAL_INSERT' content/blogs/
```

## Step 3 — Add images to Poetry blog
```bash
python3 scripts/fetch_images.py --input content/blogs/[wednesday_poetry_blog].md --dry-run
python3 scripts/fetch_images.py --input content/blogs/[wednesday_poetry_blog].md
```

## Step 4 — Repurpose Life + Poetry blogs (with design prompts)
```bash
python3 scripts/repurpose_blog.py --input content/blogs/[tuesday_life_blog].md --design
python3 scripts/repurpose_blog.py --input content/blogs/[wednesday_poetry_blog].md --design
# → content/derivatives/{slug}/ (10 files each)
# → output/scheduled/claude_design_prompts_{slug}.md (4 sections each)
```

## Step 5 — Thumbnail briefs for Life + Poetry
```bash
python3 scripts/thumbnail_brief.py --input content/blogs/[tuesday_life_blog].md
python3 scripts/thumbnail_brief.py --input content/blogs/[wednesday_poetry_blog].md
# DS brief already done Tuesday
```

## Step 6 — Generate worksheet prompts (IG lead magnets, 5–10 min)

```bash
# Data Science
python3 scripts/generate_worksheet_outline.py -i content/blogs/[monday_ds_blog].md
python3 scripts/generate_canva_worksheet_prompt.py -i content/worksheets/[monday_ds_blog_slug]_worksheet.json

# Life & Self-Dev
python3 scripts/generate_worksheet_outline.py -i content/blogs/[tuesday_life_blog].md
python3 scripts/generate_canva_worksheet_prompt.py -i content/worksheets/[tuesday_life_blog_slug]_worksheet.json

# Poetry — auto-skipped (reflection format, no worksheet expected)
python3 scripts/generate_worksheet_outline.py -i content/blogs/[wednesday_poetry_blog].md
```

Prompts auto-save to `content/prompts/[slug]_worksheet_prompt.txt`

## Step 7 — Design worksheet + landing page in Claude Design (20 min)

**For DS Worksheet:**
1. Claude Design → Paste `content/prompts/[ds_slug]_worksheet_prompt.txt`
2. Generate worksheet design → Export PDF → `output/worksheets/[ds_slug]_worksheet.pdf`
3. Create new Claude Design → Design landing page layout
4. Embed ConvertKit form via HTML embed block
5. Export as shareable link → Save to `config/worksheet_config.json`

**For Life Worksheet:**
1. Claude Design → Paste `content/prompts/[life_slug]_worksheet_prompt.txt`
2. Generate worksheet design → Export PDF → `output/worksheets/[life_slug]_worksheet.pdf`
3. Create new Claude Design → Design landing page layout
4. Embed ConvertKit form via HTML embed block
5. Export as shareable link → Save to `config/worksheet_config.json`

## Step 8 — Use Claude Design prompts (15–20 min, 3 blogs)

```bash
mkdir -p assets/{slides,stories,social_posts,reels}
```

For each blog, open `output/scheduled/claude_design_prompts_{slug}.md` and paste each section into Claude Design:

| Section | Output | Save to |
|---------|--------|---------|
| 1. Slide deck | PDF | `assets/slides/{slug}_slides.pdf` |
| 2. Instagram Story sequence | PNG sequence | `assets/stories/{slug}_story_*.png` |
| 3. Reel cover | 9:16 PNG | `assets/reels/{slug}_cover.png` |
| 4. Social post set | 4 PNGs (IG · LinkedIn · Twitter · Threads) | `assets/social_posts/{slug}_*.png` |

Social post sizes:
- Instagram/Threads: 1080×1080
- LinkedIn: 1200×628
- Twitter/X: 1200×675
