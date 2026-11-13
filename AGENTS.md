# AGENTS.md - `blog` (`hawzy.github.io`) Repository Guide

Welcome to the **`hawzy.github.io` (`c:\github\agy\blog`)** site repository. This repository owns the **Jekyll layout, 5-theme palette system, blog posts (`_posts/`), published recipes (`_recipes/`), and B2A JSON/text endpoints**.

Private drafting, research dossiers, credentials, and growth campaigns live in adjacent sibling workspaces under `c:\github\agy\`:
- **`c:\github\agy\recipes`**: Recipe creation, multi-source culinary dossiers (`_drafts/recipes/<slug>/`), 3-critic panel reviews, Nano Banana image generation, kitchen test logs, and Kroger grocery cart consolidation.
- **`c:\github\agy\blog-ops`**: Raw blog post ideation (`dossiers/posts/<slug>/`) and Gemini Web Personal Intelligence (`@Gmail`/`@Docs`) voice extraction.
- **`c:\github\agy\x-growth`**: X (Twitter) hook drafts, UTM campaign dossiers (`campaigns/<slug>/x-promo.md`), GA4/Clarity runbooks, and 60-day X Premium experiment logs.

---

## 1. Dual-Surface Site Architecture

### Human Surface (Jekyll + Minimal Mistakes + 5-Theme System)
- **Layouts & Includes**: `_layouts/`, `_includes/` (including `_includes/seo.html` defaulting to `summary_large_image` with `/assets/images/og-default.png`, and `_includes/analytics-providers/custom.html` wiring GA4 `G-S4CZ8DD6EQ` + Clarity `a2fwrdncga` in production).
- **5-Theme Palette & Header Switcher** (`assets/css/main.scss`, `_sass/`): `gruvbox` (default), `telemetry`, `catppuccin`, `kitchen`, and `paper`, persisted in `localStorage["hawzy-theme"]` and reported to GA4 as `active_theme`.
- **Layout C Blog Hub (`/` and `/blog/`)**: Featured latest post card, project filter shelf (`/projects/`), chronological active post stream, and collapsible 2022 `#100DaysOfCode` archive drawer (`archived: true`).
- **Kitchen Hub (`/recipes/`)**: Active Weekly Dinner Plan (`_data/weekly_menu.yml`) alongside the Recipe Catalog (`_recipes/*.md`), trust badges (`untested` / `tested`), *Cooking for Engineers* block-grid tables, scaling controls, print stylesheet, and Schema.org `Recipe` JSON-LD.

### Agent Surface (B2A Endpoints)
- **`/llms.txt`**: Top-level manifest of site layout, active posts, published recipes (`[untested]` / `[tested]`, excluding `draft`), and machine endpoints.
- **`/api/recipes.json`**: Structured JSON index of published recipes, provenance, ingredients, UPCs, and instructions.
- **`/api/weekly-menu.json`**: Active weekly dinner rotation (`_data/weekly_menu.yml`) resolved against recipe ingredients and scale factors.

---

## 2. Core Workflows in `c:\github\agy\blog`

### A. Layout, Theme, & Site Development
```bash
# Local Jekyll preview
bundle exec jekyll serve --port 4000

# Run full repository verification suite (build hygiene, JSON-LD, blog & recipe audits)
python -m unittest discover -s tests -v
```

### B. 4-Skill Blog Writing & Promotion Pipeline (`blog-voice`, `blog-research`, `blog-author`, `blog-promote`)
- **`blog-voice`**: Captures post hook, technical meat, and takeaway into `notes.md` and maintains `.agents/skills/blog-voice/voice-profile.md` (`## Banned Phrases`).
- **`blog-research`**: Crawls adjacent `c:\github\agy\<project>` repositories to build a cited `facts.md` (`[fN]`) with zero invented numbers.
- **`blog-author`**: Drafts `_posts/YYYY-MM-DD-<slug>.md`, runs `python .agents/skills/blog-author/scripts/audit_posts.py`, and dispatches a zero-context Editorial/Voice critic.
- **`blog-promote`**: Generates X/Twitter campaign dossiers in `c:\github\agy\x-growth\campaigns\<slug>\x-promo.md` (`utm_source=twitter&utm_medium=social`).

### C. Publishing Approved Recipes from `c:\github\agy\recipes`
- Authoring, culinary research, 3-critic panel review, and kitchen testing happen inside **`c:\github\agy\recipes`**.
- Only Gate-2 approved `_recipes/<slug>.md` files (`status: untested` or `tested`), generated hero/grid images (`assets/images/recipes/`), and `_data/weekly_menu.yml` updates are published into this repo, verified by:
  ```bash
  python .agents/skills/recipe-review-panel/scripts/audit_recipes.py
  ```
- **Invariants for `_recipes/<slug>.md`**: Never write raw markdown ingredient lists in the body (the layout renders structured `ingredients` frontmatter + `engineer_grid_html`), and never invent numbers.

---

## 3. Safety Invariants

> [!CAUTION]
> **Git Safety Invariant**: Autonomous agents must **NEVER** push commits to a remote git repository (`git push`).
> All git actions (commits, branches, stashes) must remain strictly local. Only human users or authorized CI/CD deployment pipelines may push upstream.
