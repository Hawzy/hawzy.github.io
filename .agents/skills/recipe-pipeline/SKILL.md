---
name: recipe-pipeline
description: Stage-gated orchestrator for creating, backfilling, reviewing, publishing, and kitchen-testing recipes across the 7 modular recipe skills and 3 human gates.
---

# Recipe Pipeline Orchestrator Skill (`recipe-pipeline`)

Coordinates the end-to-end lifecycle of every recipe in `_recipes/<slug>.md` and its provenance dossier in `_drafts/recipes/<slug>/`, tracking progress via `stage:` in `_drafts/recipes/<slug>/brief.md` and halting at three mandatory human gates.

---

## Stage Transitions in `brief.md`

```text
intake -> research | research-import -> gate-1 -> authoring -> review -> gate-2 -> published -> tested
```

| Stage in `brief.md` | Active Skill | Output Artifacts |
|---|---|---|
| `intake` | `recipe-intake` (for `origin: family`) or seed `brief.md` (for `origin: research`) | `_drafts/recipes/<slug>/brief.md` |
| `research` / `research-import` | `recipe-research` | `_drafts/recipes/<slug>/sources.yml`, `_drafts/recipes/<slug>/research.md` |
| `gate-1` | **Human Gate 1** | User reviews `<=15`-line summary and replies `"go"` or redirects |
| `authoring` | `recipe-author` | `_recipes/<slug>.md` (`status: draft`) passing `audit_recipes.py` |
| `review` | `recipe-review-panel` | `_drafts/recipes/<slug>/review.md` (`review_report.py --check`) |
| `gate-2` | **Human Gate 2** | User resolves/waives blockers; `review_report.py --approve` sets `status: untested` |
| `published` | `recipe-visuals` (optional) | `assets/images/recipes/<slug>-hero.jpg` + `bundle exec jekyll build` |
| `tested` | **Human Gate 3** + `recipe-test-log` | `_drafts/recipes/<slug>/test-log.md` + `status: tested` + `tested_on` |

---

## The Three Mandatory Human Gates (Always Halt)

### Gate 1 — Direction (After `recipe-research` or `recipe-intake`)
- **Action**: Present the `<=15`-line summary (method, key numbers with `[sN]` citations, open disagreements + chosen resolution, numbered source list).
- **Halt Rule**: **STOP** and wait for the user to reply `"go"` (or give adjustments) before invoking `recipe-author`.

### Gate 2 — Review Panel Sign-Off (After `recipe-review-panel`)
- **Action**: Present `_drafts/recipes/<slug>/review.md` scorecard and any `BLOCKER` / `MAJOR` findings.
- **Halt Rule**: **STOP** and wait for the user to either:
  1. Request fixes (loop back to `recipe-author` -> re-run `recipe-review-panel` as `round N+1`, archiving `review-r<N>.md`),
  2. Supply a non-empty waiver reason inline (`Waive (reason): <reason>`), or
  3. Approve publication once `review_report.py --check` exits `0` (`APPROVED`), then run:
     ```bash
     python .agents/skills/recipe-review-panel/scripts/review_report.py --approve _drafts/recipes/<slug>/review.md --recipe _recipes/<slug>.md
     ```

### Gate 3 — Kitchen Test (After Real-World Cooking)
- **Action**: Triggered only when the user reports real-world cook notes. Never mark a recipe `status: tested` without user cook notes.
- Run `recipe-test-log` to log notes in `_drafts/recipes/<slug>/test-log.md` and promote `status: "tested"` + `tested_on`.
