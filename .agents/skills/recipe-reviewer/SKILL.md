---
name: recipe-reviewer
description: Deprecated pointer to the modular 7-skill stage-gated recipe pipeline (recipe-pipeline, recipe-research, recipe-intake, recipe-author, recipe-review-panel, recipe-visuals, recipe-test-log).
---

# `recipe-reviewer` (Deprecated — Split into Modular Pipeline Skills)

> **Deprecation Notice:** The monolithic `recipe-reviewer` skill has been replaced by the 7-skill stage-gated recipe pipeline. Please activate the specific skill below for your task:

| Task | Replacement Skill |
|---|---|
| End-to-end orchestration & human gates (`Gate 1..3`) | `.agents/skills/recipe-pipeline/SKILL.md` |
| Web research (`>=3` sources, USDA/FDA safety) or `research-raw.*` import | `.agents/skills/recipe-research/SKILL.md` |
| Family recipe Q&A intake (`origin: family`) | `.agents/skills/recipe-intake/SKILL.md` |
| Authoring `_recipes/<slug>.md` (3-tier grammar, *Cooking for Engineers* grid) | `.agents/skills/recipe-author/SKILL.md` |
| Structural auditor (`audit_recipes.py`) + 3-critic panel (`review_report.py`) | `.agents/skills/recipe-review-panel/SKILL.md` |
| Nano Banana hero & block-grid image generation (`generate_recipe_visuals.py`) | `.agents/skills/recipe-visuals/SKILL.md` |
| Logging real-world kitchen cook notes (`status: tested`) | `.agents/skills/recipe-test-log/SKILL.md` |

## Backward-Compatible Script Shims

For compatibility with existing scripts and tests, both legacy script entrypoints remain functional as `importlib.util` forwarding shims:
- `.agents/skills/recipe-reviewer/scripts/audit_recipes.py` -> forwards to `.agents/skills/recipe-review-panel/scripts/audit_recipes.py`
- `.agents/skills/recipe-reviewer/scripts/generate_recipe_visuals.py` -> forwards to `.agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py`
