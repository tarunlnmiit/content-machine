# Worksheet Workflow — IG Lead Magnet + Email Collection

Generate actionable PDF worksheets from blogs. Convert blog readers into email subscribers via ConvertKit landing pages.

## Quick Start (Existing Blogs)

### For This Week's 3 Blogs

**Data Science (ML-to-SQL):**
```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/2026-05-12_data_science_tech_ml-model-sql-translation.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/2026-05-12_data_science_tech_ml-model-sql-translation_worksheet.json
```

**Life & Self-Dev (Check-in Design):**
```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/2026-05-13_life_self_dev_why-do-most-daily-check-in-habits-fall-apart-after-a-few-day.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/2026-05-13_life_self_dev_why-do-most-daily-check-in-habits-fall-apart-after-a-few-day_worksheet.json
```

**Poetry (Ada Limón):**
— Skips automatically (reflection format, no worksheet)

---

## Full Workflow (Per Blog)

### Step 1: Generate Worksheet Outline
```bash
python3 scripts/generate_worksheet_outline.py -i content/blogs/[BLOG_SLUG].md
```

Outputs:
- `content/worksheets/[BLOG_SLUG]_worksheet.json` — worksheet structure
- Console: JSON preview

**What it checks:**
- Niche detection (data_science, life_self_dev, poetry_quotes)
- Engagement potential (high = suitable for worksheet)
- Auto-skips low-engagement blogs (e.g., poetry commentary)

---

### Step 2: Generate Canva Prompt
```bash
python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/[BLOG_SLUG]_worksheet.json
```

Outputs:
- Console: Canva design prompt (ready to copy-paste)

**How to use:**
1. Copy entire prompt
2. Go to [Canva.com](https://www.canva.com)
3. New Design → Custom Size → A4 (or custom)
4. Paste prompt into **Canva AI Design** (or manually design following the structure)
5. Export as **PDF**
6. Save to `output/worksheets/[BLOG_SLUG]_worksheet.pdf`

---

### Step 3: Set Up ConvertKit Landing Page
1. Log in to ConvertKit
2. Create Form → Landing Page
3. Add PDF as free download (upload worksheet PDF from Step 2)
4. Copy landing page URL
5. Note the landing page ID (if available)

---

### Step 4: Update Config
Edit `config/worksheet_config.json`:

```json
"[BLOG_SLUG]": {
  "convertkit": {
    "landing_page_id": "12345",
    "landing_page_url": "https://tarun.ck.page/[slug]",
    ...
  }
}
```

---

### Step 5: Share on IG
Use manual posting (via IG app or Publer):

**Caption structure:**
```
[Hook from config → ig_caption_hook]

📋 Free worksheet in link (stories/bio)

[Blog excerpt or key insight]

[CTA from config → ig_cta]

#[niche-hashtags]
```

**Link placement:**
- Stories: Add link sticker → worksheet landing page URL
- Bio: Add worksheet landing page URL (rotate or pin story)
- Comments: Reply with landing page link if engagement

---

## Integration with Blog Creation Workflow

When writing new blogs, **immediately** decide: worksheet or not?

**Decision tree:**

```
Is this blog actionable? (How-to, personal practice, framework)
  ├─ YES: Data Science/Tech
  │   └─ → Generate DS worksheet (SQL, code, technical checklist)
  ├─ YES: Life & Self-Dev
  │   └─ → Generate Life worksheet (design template, reflection prompts)
  ├─ NO: Poetry/Commentary/Reflection
  │   └─ → Skip worksheet
  └─ MAYBE: Ambiguous
      └─ → Run script, it auto-detects and skips if unsuitable
```

---

## Adding Worksheet Decision to Production Script

When you enhance `scripts/produce_blog.py` or similar, add:

```python
# After blog is written, before derivative generation:
from pathlib import Path
import subprocess

blog_file = Path(f"content/blogs/{slug}.md")

# Check worksheet eligibility
result = subprocess.run([
    "python3", "scripts/generate_worksheet_outline.py",
    "-i", str(blog_file)
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"✓ Worksheet eligible: {slug}")
    print(f"  → Next: run generate_canva_worksheet_prompt.py")
    print(f"  → Then: design in Canva + upload to ConvertKit")
else:
    print(f"⊘ Worksheet not suitable for this blog")
```

---

## Email Collection Flow

1. **Reader sees IG post** → clicks link → ConvertKit landing page
2. **Lands on page** → sees worksheet description + form
3. **Enters email** → ConvertKit captures (added to your list)
4. **Gets PDF** → automatic delivery via email
5. **Receives welcome email** → link back to blog + CTA

---

## Measurement

Track in ConvertKit:
- **Form views** (click-through from IG)
- **Form conversions** (emails collected)
- **Download rate** (PDF opened)
- **Reply rate** (email responses)

Update `data/analytics/worksheet_performance.csv` weekly:
```
date,blog_slug,worksheet_type,form_views,conversions,conversion_rate,pdf_downloads
2026-05-17,2026-05-12_ml_sql,conversion_guide,143,28,19.6%,26
2026-05-17,2026-05-13_checkin,design_template,267,54,20.2%,52
```

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/generate_worksheet_outline.py` | Blog → worksheet JSON |
| `scripts/generate_canva_worksheet_prompt.py` | Worksheet JSON → Canva prompt |
| `prompts/worksheet_canva_prompts.md` | Design templates per niche |
| `config/worksheet_config.json` | ConvertKit mappings + IG CTAs |
| `content/worksheets/` | Generated worksheet JSONs |
| `output/worksheets/` | Final PDFs (store before uploading to ConvertKit) |

---

## Tips

- **Worksheet-first mindset:** When writing, ask: "Will readers want to *do* something with this?" If yes → worksheet-eligible.
- **Time investment:** Prompt generation (free), Canva design (15-20 min), ConvertKit setup (5 min).
- **Reusable designs:** Once you design a DS worksheet template in Canva, duplicate it for future DS blogs (just swap sections).
- **Poetry workaround:** If you want worksheets for reflection, manually create them outside this script (it auto-skips poetry).
