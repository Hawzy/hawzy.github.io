---
name: recipe-author
description: Authors or updates _recipes/<slug>.md from a recipe dossier with status: draft, enforcing 3-tier typography grammar, Cooking for Engineers block-grid matrices, and zero invented numbers.
---

# Recipe Author Skill (`recipe-author`)

Transforms an approved Gate-1 dossier (`_drafts/recipes/<slug>/brief.md`, plus `research.md` and `sources.yml` when `origin: research`) into a structured recipe file at `_recipes/<slug>.md` with `status: draft`.

---

## Core Invariant: Never Invent Numbers (`TODO-source`)

- Every ingredient quantity, temperature, duration, and yield in `_recipes/<slug>.md` MUST trace directly to `_drafts/recipes/<slug>/research.md` (for `origin: research`) or `_drafts/recipes/<slug>/brief.md` (for `origin: family`).
- If a number is missing from the dossier, **never guess or hallucinate a number** — emit `TODO-source` (or preserve `TODO-ask`) and halt so the gap is resolved in the dossier first.
- New or re-authored drafts always start with `status: draft` (or `"draft"`), which isolates the recipe from `/`, `/recipes/`, search, sitemap, `/api/recipes.json`, `/api/weekly-menu.json`, and `/llms.txt` until Gate 2 review approval promotes it.

---

## Required Frontmatter Schema (`_recipes/<slug>.md`)

```yaml
---
title: "Recipe Title"
slug: "unique-recipe-slug"
excerpt: "Short descriptive summary."
date: 2026-11-08
origin: "research"            # "research" | "family"
status: "draft"               # "draft" | "untested" | "tested"
sources:                      # required (>=1) when origin == "research" (populated from sources.yml)
  - title: "Source Recipe Title"
    author: "Author / Publication"
    url: "https://..."
categories: ["Dinner", "Beef"]
tags: ["weeknight", "stir-fry"]
prep_time_iso: "PT15M"
cook_time_iso: "PT15M"
total_time_iso: "PT30M"
prep_minutes: 15
cook_minutes: 15
servings: 4
calories_per_serving: 520
cuisine: "Chinese-American"
engineer_grid_html: |
  <table class="engineer-grid-table">
    ...
  </table>
ingredients:
  - item: "flank steak"
    quantity: 1.5
    unit: "lb"
    display_text: "1 1/2 lbs flank steak, sliced 1/4-inch thick against the grain"
    category: "Meat & Seafood"
    pantry_staple: false
    retailer_query: "beef flank steak"
    preferred_upc: "0020146500000"
instructions:
  - "Step 1 prose with 3-tier grammar..."
---
```

---

## Mandatory 6-Point Usability & Block-Grid Checklist

### 1. Chronological Ingredient Order
- Order `ingredients` in the exact sequence each ingredient is first touched in `instructions`.
- Never group `ingredients` by supermarket aisle (retailer aisle lives on each item's `category:` field for B2A grocery consolidation).

### 2. Divided Ingredient Clarity
- Any ingredient used across two or more distinct steps MUST:
  1. Include `, divided` in `display_text`.
  2. State the exact sub-quantity inside each step where a portion is added.
  3. Appear as **separate rows** in `engineer_grid_html` summing to the total quantity so `rowspan` blocks never cross.

### 3. Cohesive 3-Tier Instruction Typography Grammar
Format `instructions` with a strict **3-tier** hierarchy:
1. **Monospace Chip (`` `qty unit` ``)** -> **ONLY exact ingredient measurements on first addition** (or each split of a `, divided` ingredient), placed immediately after the ingredient name (e.g., ``chicken bone broth `4 cups` ``, ``dark shoyu soy sauce `2 tbsp` ``). Never put backtick chips on timers, temperatures, slice thicknesses, or pan sizes.
2. **Short Bold (`**...**`)** -> **ONLY stove settings, timers, and target temperatures** (short 1–4 word anchors such as `**medium-high heat**`, `**6 minutes 30 seconds**`, `**125°F**`, at most 2 bolded clauses per step). Never bold full sentences or ingredient clauses.
3. **Plain Prose** -> Pure assembly/flipping steps with no new ingredient and no timer/heat control stay clean plain prose.

### 4. Sensory Cues + Natural Cookware
- Pair every heated or timed step with a **sensory doneness cue** immediately following the timer/temperature (visual, auditory, olfactory, tactile, or instant-read internal temperature).
- Name cookware naturally (`"a small bowl"`, `"a medium saucepan"`, `"a large heavy cast-iron skillet"`, `"a 14-inch flat-bottomed carbon-steel wok"`). Avoid robotic quart/pint/ounce vessel labels (`"1-pint bowl"`).

### 5. Cooking for Engineers Block Grid (`engineer_grid_html`)
- Define `engineer_grid_html: |` containing `<table class="engineer-grid-table">` (or modular `<div class="engineer-subgrid">` tables when a separate sauce/component merges downstream).
- **Topological Matrix Invariants**:
  1. **Header (`<thead>`)**: `<th scope="col">Qty</th>`, `<th scope="col">Unit</th>`, `<th scope="col">Ingredient</th>`, and `<th scope="col" colspan="N">Order of Operations (Read Left to Right)</th>`. Columns represent combinatorial dependency depth, never clock phases.
  2. **Left-hand Columns (`Cols 0–2`) & Downstream Stretching**: Every `<tr>` starts with `<td class="ing-qty" data-base-qty="...">`, `<td class="ing-unit">`, and `<td class="ing-name">` in chronological order. Stretch `<td class="ing-name" colspan="K">` right up to the column where a late-stage ingredient enters — never invent `"reserve"` or `"stage"` filler cells.
  3. **Progressive Merges (`td.action-cell`)**: Group sub-assemblies contiguously so adjacent `rowspan` cells merge without crossing unrelated rows.
  4. **Thermal/Phase Color Classes**:
     - `action-cell--prep`: Cold prep, dry-brining, whisking, tossing, chilling.
     - `action-cell--heat`: Boiling, simmering, searing, frying, reduction.
     - `action-cell--finish`: Final assembly/plating in the rightmost column spanning 100% of that table's `<tbody>` rows (`rowspan="<table_rows>"`).
  5. **Airtight Rectangular Geometry**: Every `(r, c)` coordinate in `0..R-1 × 0..C-1` is covered **exactly once**.

### 6. Schema.org Cleanliness
- Strip any `"Step 1:"`, `"1."`, or `"Directions:"` prefixes from `instructions`.

---

## Exit Verification

Always run the structural auditor before handing off to `recipe-review-panel`:

```bash
python .agents/skills/recipe-review-panel/scripts/audit_recipes.py _recipes/<slug>.md
```

Fix any reported chronology, 3-tier grammar, sensory cue, provenance, or 2D `rowspan`/`colspan` matrix errors before updating `stage: review` in `_drafts/recipes/<slug>/brief.md`.
