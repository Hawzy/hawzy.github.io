---
name: recipe-research
description: Synthesizes multi-source culinary research or normalizes raw deep-research handoffs into a cited recipe dossier (sources.yml and research.md) with a Gate-1 summary.
---

# Recipe Research Skill (`recipe-research`)

Produces traceable culinary provenance in `_drafts/recipes/<slug>/` (`sources.yml` + `research.md`) before a single line of `_recipes/<slug>.md` is authored.

Supports two execution modes that converge on the exact same dossier files:
1. **Research mode** — fresh multi-source web synthesis from `_drafts/recipes/<slug>/brief.md`.
2. **Import mode** — normalizes a user-supplied `_drafts/recipes/<slug>/research-raw.<md|pdf|docx|txt>` document into `sources.yml` and `[sN]`-cited `research.md`.

---

## Dossier Contract (`_drafts/recipes/<slug>/`)

| File | Purpose |
|---|---|
| `brief.md` | Goal, target yield, equipment constraints, `origin: research`, and current `stage` (`research` or `research-import` → `gate-1`). |
| `sources.yml` | Structured YAML list of `{id, title, url, author, accessed, used_for[]}`. Every `id` (`s1`, `s2`, ...) matches inline `[sN]` citations in `research.md`. |
| `research.md` | Every quantity, ratio, temperature, and duration carries an inline `[sN]` citation. Includes a mandatory **Disagreements** table with chosen resolution + culinary rationale. |

### `sources.yml` Schema
```yaml
- id: "s1"
  title: "Mongolian Beef"
  author: "Nagi Maehashi (RecipeTin Eats)"
  url: "https://www.recipetineats.com/mongolian-beef/"
  accessed: "2026-11-08"
  used_for: ["flank steak slice thickness", "cornstarch velvetting ratio", "soy-brown-sugar glaze ratio"]
- id: "s2"
  title: "Safe Minimum Internal Temperature Chart"
  author: "USDA FSIS"
  url: "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-minimum-internal-temperature-chart"
  accessed: "2026-11-08"
  used_for: ["beef safe internal temperature baseline"]
```

---

## Mode 1: Research mode (New Dish from `brief.md`)

Use **Research mode** when `_drafts/recipes/<slug>/research-raw.*` does not exist.

1. **Minimum Source Diversity (`>=3` Independent Sources)**:
   - Consult **at least 3 independent culinary sources** (`s1`, `s2`, `s3`, ...) for core ratios, cooking temperatures, and timings.
   - Prefer tested culinary references (Serious Eats, RecipeTin Eats, Woks of Life, Just One Cookbook, America's Test Kitchen, King Arthur Baking, primary cookbooks).
2. **Food-Safety Authority Rule (`USDA` / `FDA` Only)**:
   - All food-safety minimum internal temperatures, cooling windows, and curing/acidification thresholds MUST be cited from **USDA** (`fsis.usda.gov`) or **FDA** (`fda.gov`) guidance only.
   - If the recipe targets a culinary doneness below the USDA minimum (e.g., `125°F` medium-rare ribeye or `6 minutes 30 seconds` jammy egg yolk), record both the USDA baseline `[sN]` and the explicit chef's-choice note in `research.md`.
3. **Disagreements Log**:
   - Whenever sources disagree on a key ratio, temperature, technique, or timing, log a row in `## Disagreements` inside `research.md`:
     ```markdown
     | Topic | Source A | Source B | Chosen Resolution & Rationale |
     |---|---|---|---|
     | Soy : brown sugar ratio | 1:1 by volume `[s1]` | 1:0.75 with hoisin `[s3]` | **1:0.75 + 2 tbsp hoisin `[s3]`** — prevents cloying sweetness on weeknight stovetop reduction |
     ```
4. **Zero Uncited Numbers**:
   - Every ingredient quantity, ratio, pan temperature, internal temperature, and step timer in `research.md` must carry `[s1]`, `[s2]`, etc.

---

## Mode 2: Import mode (`research-raw.*` Handoff)

Use **Import mode** when `_drafts/recipes/<slug>/research-raw.<md|pdf|docx|txt>` is present (including backfilling existing recipes).

1. Read `research-raw.*` (and `_recipes/<slug>.md` if backfilling an already-published recipe).
2. Extract all referenced URLs, authors, and publications into `_drafts/recipes/<slug>/sources.yml` with sequential IDs (`s1`, `s2`, ...).
3. Normalize the findings into `_drafts/recipes/<slug>/research.md`, attaching `[sN]` citations to every quantity, ratio, temperature, and time, plus a `## Disagreements` table.
4. **Targeted Gap-Fill Only**: Do **not** run broad new web research if `research-raw.*` already cites the numbers. Search the web **only** when a specific quantity, temperature, or USDA/FDA safety baseline is uncited in `research-raw.*`, or mark it for review at Gate 1.

---

## Exit Criteria & Gate 1 Output

Before finishing:
1. Verify `_drafts/recipes/<slug>/sources.yml` has valid `http(s)://` URLs and every `[sN]` in `research.md` resolves to an entry in `sources.yml`.
2. Update `stage: gate-1` in `_drafts/recipes/<slug>/brief.md`.
3. Emit a **<=15-line Gate-1 summary** to the user covering:
   - Core method & target yield
   - Key ratios, temperatures, and timings with `[sN]` citations
   - Any open disagreements or resolution choices
   - Numbered source list (`s1..sN`)
   - Prompt: *"Reply `go` to proceed to `recipe-author`, or tell me what to adjust."*
