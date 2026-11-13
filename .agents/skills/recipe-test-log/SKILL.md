---
name: recipe-test-log
description: Records real-world kitchen test notes in _drafts/recipes/<slug>/test-log.md, promotes recipe frontmatter to status: tested, and triggers scoped re-review if steps changed.
---

# Recipe Test Log Skill (`recipe-test-log`)

Implements **Gate 3 — Kitchen Test** after the user cooks an `untested` recipe in their kitchen and shares real-world feedback, adjustments, or photos.

---

## Workflow

1. **Prepend Entry to `_drafts/recipes/<slug>/test-log.md` (Newest First)**:
   ```markdown
   ## 2026-11-12 — Kitchen Cook #1 (Verdict: PASS with minor tweak)
   - **Cooked by:** Nick
   - **Scale / Equipment:** 1x batch in 14-inch carbon-steel wok
   - **Observations:** Cornstarch crust stayed crisp; sauce was slightly salty at 1/2 cup low-sodium soy.
   - **Recipe Adjustments Applied:** Reduced low-sodium soy sauce from `1/2 cup` to `6 tbsp` in `ingredients`, Step 2, and `engineer_grid_html`.
   ```

2. **Promote `_recipes/<slug>.md` Frontmatter**:
   - Set `status: "tested"`.
   - Set `tested_on: YYYY-MM-DD` (ISO date of the cook).
   - Set optional `test_notes: "<1–2 concise public lines>"` (rendered inside the `<details id="from-my-kitchen">` **"From my kitchen"** disclosure on the recipe page).
   - Update `stage: tested` in `_drafts/recipes/<slug>/brief.md`.

3. **Scoped Re-Review When Recipe Quantities or Steps Were Edited**:
   - If the kitchen test resulted in edits to `ingredients`, `instructions`, or `engineer_grid_html`:
     1. Run `python .agents/skills/recipe-review-panel/scripts/audit_recipes.py _recipes/<slug>.md` to verify chronological order, 3-tier grammar, and 2D rectangular matrix geometry.
     2. Run a **scoped** critic check on the modified steps/rows only to ensure no new `BLOCKER` was introduced.
