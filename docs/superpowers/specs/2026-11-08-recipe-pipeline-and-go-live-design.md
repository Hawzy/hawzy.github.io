---
layout: single
title: "Recipe Pipeline & Go-Live — Design Spec"
surface: blog
sitemap: false
search: false
comments: false
---

# Recipe Pipeline & Go-Live — Design Spec

- **Date:** 2026-11-08
- **Status:** Approved in brainstorming (sections 1–4); pending written-spec review
- **Branch:** `feat/agentic-recipe-blog` (local only — no `git push`, per `AGENTS.md`)

## 1. Goals & Non-Goals

### Goals
1. **Soft-archive** the 18 posts from 2022 (`#100DaysOfCode`) so they stay reachable at existing URLs but are hidden from the `/blog/` hub, search engines, sitemap, and on-site search.
2. Replace the single do-everything `recipe-reviewer` skill with a **stage-gated pipeline** of focused skills, a **per-recipe dossier** for provenance, an **independent 3-critic review panel**, and **three human gates**.
3. Surface recipe **trust signals** on the site: `Untested` / `Kitchen-tested` status, test notes, and sources.
4. Prove the pipeline end-to-end on one real recipe (Crispy Mongolian Beef) and keep the resulting `review.md` as a reference example.
5. Unblock Sub-project 3 (launch blog post), which will be written *using* this pipeline.

### Non-Goals
- Deploying / pushing to GitHub Pages (human-only).
- Writing the launch post (separate outline + approval after this lands).
- Nutrition-database integration (calories remain an estimate, sanity-checked by the culinary critic).
- Changing the weekly-menu / grocery consolidation math.

## 2. Recipe Origins

Two intake modes, both converging on the same dossier:

| Origin | Intake skill | Provenance requirement |
|---|---|---|
| `research` — synthesized by AI deep research | `recipe-research` | Every number traceable to a source id in `research.md`; ≥1 public source in frontmatter |
| `family` — recipes the user already cooks | `recipe-intake` | User's notes / interview in `brief.md`; no external sources required |

## 3. Data Model

### 3.1 Dossier: `_drafts/recipes/<slug>/`
Committed to git, never published. `_drafts/` is skipped by Jekyll by default; it is **also** added to `exclude:` in `_config.yml` so `--drafts` builds cannot leak it.

| File | Required for | Contents |
|---|---|---|
| `brief.md` | all | Goal, constraints, `origin`, current `stage` (`intake`, `research`, `gate-1`, `authoring`, `review`, `gate-2`, `published`, `tested`), and for `family`: interview/transcription notes. Unknowns marked `TODO-ask`. |
| `sources.yml` | `research` | List of `{id, title, url, author, accessed, used_for[]}` |
| `research.md` | `research` | Findings; every quantity/temp/time carries `[sN]` citations; a **Disagreements** section with resolution + rationale |
| `review.md` | all (after review) | Current panel report; prior rounds archived as `review-r<N>.md` |
| `test-log.md` | after first cook | Newest-first entries: date, changes made, verdict |

### 3.2 New `_recipes/<slug>.md` frontmatter
```yaml
origin: "research"            # research | family            (required)
status: "untested"            # draft | untested | tested    (required)
tested_on: 2026-11-12         # required iff status == tested
test_notes: "Cut soy to 3 tbsp; kids loved it."   # optional public 1–2 lines
sources:                      # required (>=1) iff origin == research
  - title: "Mongolian Beef"
    author: "RecipeTin Eats"
    url: "https://..."
review:                       # required unless status == draft
  round: 2
  verdict: "approved"         # approved | changes-requested
  approved_on: 2026-11-08
```

### 3.3 Draft semantics
`status: draft` recipes are still rendered by Jekyll (collection `output: true`) but:
- carry `<meta name="robots" content="noindex">` and are excluded from `sitemap.xml` (`sitemap: false` injected via the recipe layout check / jekyll-sitemap exclusion),
- are filtered out of `/`, `/recipes/`, the weekly-menu card render, lunr search index, `/api/recipes.json`, `/api/weekly-menu.json` meal expansion, and `/llms.txt`.

### 3.4 Backfill of existing 5 recipes
The user hands off the **original deep-research document for each existing recipe** into its dossier as `_drafts/recipes/<slug>/research-raw.<md|pdf|docx|txt>`.
- **Interim (until a recipe's raw doc is processed):** `origin: research`, `status: untested`, `review: {round: 0, verdict: approved, approved_on: 2026-11-08}`. The validator permits empty `sources` **only** when `review.round == 0` (grandfathered).
- **Re-run (per recipe, once `research-raw.*` lands):** `recipe-research` in **import mode** normalizes the raw doc into `sources.yml` + cited `research.md` (no new web research unless a number is uncited), then the full review panel runs against the live recipe. Gate 2 approval sets `review.round >= 1` and public `sources:`, ending the grandfather exemption.
- The user may mark any already-cooked recipe as `tested` at any time.

## 4. Skills

All under `.agents/skills/<name>/` with `SKILL.md`; scripts are Python 3 stdlib only.

| Skill | Input → Output | Responsibilities | Exit criteria |
|---|---|---|---|
| `recipe-research` (new) | `brief.md` → `sources.yml`, `research.md` | **Research mode:** web research; **≥3 independent sources** for core ratios/temps/times; **food-safety temps from USDA/FDA only**; log disagreements and pick with rationale. **Import mode:** if `research-raw.*` exists, normalize it into `sources.yml` + cited `research.md`, web-searching only to fill uncited numbers | Every number cited; disagreements resolved or flagged; ≤15-line Gate-1 summary emitted |
| `recipe-intake` (new) | user notes / photo / Q&A → `brief.md` | Ask only for missing info (yield, pan, heat, doneness cues); preserve family quirks | Every ingredient has qty; every step has a doneness cue or `TODO-ask` |
| `recipe-author` (new; absorbs formatting rules from `recipe-reviewer`) | dossier → `_recipes/<slug>.md` with `status: draft` | Chronological ingredients, 3-tier Chip/Bold/Plain grammar, sensory cues, natural cookware, *Cooking for Engineers* grid rules, narrative. **Never invents numbers**: anything absent from dossier is emitted as a `TODO-source` flag | `audit_recipes.py` passes |
| `recipe-review-panel` (new; absorbs audit) | draft + dossier → `review.md` | Run structural audit; dispatch 3 critic subagents in parallel (no author context); merge into scored report; diff vs prior round | Report written; verdict computed per §5.4 |
| `recipe-visuals` (split from `recipe-reviewer`) | approved recipe → `assets/images/recipes/<slug>-hero.jpg` (+ optional grid) | Existing Nano Banana script + image-vs-recipe fidelity check | Image wired or explicitly skipped (optional for publish) |
| `recipe-test-log` (new, small) | user cook notes → `test-log.md` + frontmatter | Log entry; offer to apply recipe edits; edited steps trigger a **scoped** re-review (changed steps only) | `status: tested`, `tested_on` set |
| `recipe-pipeline` (new, orchestrator) | "new recipe: X" | Route to intake/research → author → panel → visuals; track `stage` in `brief.md`; **halt at each gate** | — |

### 4.1 Retirement of `recipe-reviewer`
- `SKILL.md` becomes a short deprecation pointer to the new skills for one release, then is deleted.
- `audit_recipes.py` moves to `.agents/skills/recipe-review-panel/scripts/audit_recipes.py`. The old path keeps a **thin shim module** that re-exports from the new location (no symlink — Windows symlinks require elevated privileges), so existing tests/docs keep working.
- `generate_recipe_visuals.py` moves to `recipe-visuals/scripts/` with the same shim approach.
- `AGENTS.md` §2.D is updated to describe the pipeline.

## 5. Review Panel

Critics receive: the draft recipe file + `brief.md` + `research.md` + `sources.yml`. They do **not** receive authoring transcripts or rationale. Severity: `BLOCKER` (must fix or waive) · `MAJOR` (should fix) · `NIT` (optional). Each critic returns a 1–5 score.

### 5.1 Culinary & Food-Safety Critic
| Check | BLOCKER when |
|---|---|
| Numbers ↔ dossier | Any qty/temp/time unsupported by, or contradicting, `research.md`/`brief.md` |
| Food safety | Internal temp below USDA minimum without an explicit chef's-choice note (e.g., 125°F medium-rare steak permitted with note) |
| Ratio physics | Physically implausible (reduction volume vs. time, starch:liquid, oil vs. pan) |
| Timeline | Sum of step times vs. `total_time_iso` off by >30%, or impossible parallelism |
| Equipment / crowding | MAJOR only |
| Calories estimate | MAJOR if off by >25% from ingredient-based estimate |

### 5.2 Editorial & Usability Critic
| Check | BLOCKER when |
|---|---|
| 3-tier grammar | Any step has ≥3 bolded clauses, or a chip on a timer/temp/size |
| Grid logic | Columns used as clock phases, an action merges rows it doesn't touch, filler "reserve/stage" cells, or thermal color mismatch |
| Step readability | MAJOR if a step has >1 primary action or >60 words; doneness cue must follow timer |
| Narrative | MAJOR for filler; ingredient naming must match across narrative/list/grid |
| Ingredient accounting | Unused listed ingredient, or divided splits not summing |

### 5.3 Visual / Rendered-Page Critic
Builds the site and uses the **chrome-devtools** MCP to capture `/recipes/<slug>/` at 1280px, 390px, grid lightbox open, and print emulation.
- Grid readable without horizontal scroll at 1280px; lightbox opens; no 390px overflow
- Chips wrap cleanly; no clipping; status badge + sources render
- Print ≈1–2 pages with interactive controls hidden
- Hero (if present) depicts the dish faithfully

**Fallback:** if Chrome remote debugging (port 9222) is unavailable, the critic performs HTML/CSS structural checks only and sets its row to **`PENDING — run /browser`**. A PENDING visual row is a BLOCKER until the user confirms visually or waives it.

### 5.4 `review.md` format & verdict rules
```markdown
# Review — <Title> (round N) · Verdict: APPROVED | CHANGES REQUESTED
| Critic | Score | Blockers | Major | Nit |
|---|---|---|---|---|
| Culinary & Safety | 4/5 | 1 | 1 | 2 |
| Editorial & Usability | 5/5 | 0 | 0 | 3 |
| Visual (rendered) | 4/5 | 0 | 1 | 0 |
| Structural audit (script) | PASS | — | — | — |

## Blockers
- [CUL-1] <location>: <finding> — evidence: <dossier ref>  → Fix | Waive (reason): ___
## Major
## Nits
## Changes since round N-1
## Approval: ☐ Approve (status → untested)  ☐ Request changes
```
- Verdict = **APPROVED iff zero open BLOCKERs and structural audit PASS**.
- A waiver requires a non-empty user reason, persisted inline.
- Finding ids are stable across rounds (`CUL-n`, `EDT-n`, `VIS-n`) so diffs are readable.
- A parser (`recipe-review-panel/scripts/review_report.py`) computes the verdict and is what Gate 2 uses to set frontmatter.

## 6. Human Gates

1. **Gate 1 — Direction:** after research/intake. User reviews ≤15-line summary (method, key numbers, open disagreements, source list). Reply "go" or redirect.
2. **Gate 2 — Review:** user reads `review.md`; resolves/waives BLOCKERs; approval sets `status: untested` and `review.*`, making the recipe live.
3. **Gate 3 — Kitchen test:** user notes → `recipe-test-log` → `status: tested`.

## 7. Site Changes

### 7.1 Recipe surface
- **Status badge** in recipe-card header + top quick pills: `● Untested draft` (amber outline) / `✓ Kitchen-tested · <date>` (sage fill). Text + icon, never color alone. Tested badge anchors to a `<details>` **"From my kitchen"** block rendering `test_notes`.
- **Sources & inspiration** block under the block grid from `sources:`; research → "Researched across N sources"; family → "Family recipe". Print shows a one-line credit only.
- Status dot on catalog cards and weekly-menu meal cards.
- JSON-LD: add `isBasedOn` (array of source URLs) for research recipes; all existing fields unchanged.

### 7.2 Agent surface (B2A)
- `/api/recipes.json`: add `status`, `origin`, `tested_on`, `sources[]`; exclude drafts.
- `/api/weekly-menu.json`: add per-meal `status`.
- `consolidate_menu.py`: emit a non-blocking warning line for untested recipes in the active menu.
- `/llms.txt`: exclude drafts; mention status field.

### 7.3 Blog soft archive (Sub-project 1)
- `_config.yml` default scoped to `_posts/2022-*`: `archived: true`, `sitemap: false`, `search: false`, `related: false`, `comments: false`.
  - **Risk:** posts live in per-date subfolders (`_posts/2022-01-01/…`). Verify glob scoping matches; fallback is per-file frontmatter added by script.
- `_includes/head/custom.html`: `noindex` when `page.archived`.
- `/blog/` hub: main list filters `archived != true`; bottom `<details>` "// 2022 ARCHIVE — N logs (#100DaysOfCode)".
- Archived post banner (amber): "Archived 2022 log — kept for reference."
- `/blog/` empty state ("First transmission incoming") until the launch post exists.

## 8. Testing

- **`tests/test_recipe_pipeline.py`** (new):
  - validator rejects `origin: research` without sources; `status: tested` without `tested_on`; non-draft without `review`
  - `review_report.py`: open BLOCKER ⇒ not approved; waiver without reason ⇒ invalid; PENDING visual ⇒ not approved
  - shims: old `audit_recipes` / `generate_recipe_visuals` import paths still resolve
- **E2E (`tests/test_e2e_verification.py`)**:
  - a fixture draft recipe is absent from `/`, `/recipes/`, search index, sitemap, `/api/recipes.json`, `/llms.txt`, and has `noindex`
  - status badge renders for untested/tested; `isBasedOn` present in JSON-LD for research recipes
  - archived posts: `noindex`, absent from sitemap and `/blog/` main list, present inside the archive `<details>`
- **Dogfood:** once the user's `research-raw.*` docs land, run import → review panel → Gate 2 on **all 5 existing recipes**, starting with `crispy-mongolian-beef-broccoli`; commit each dossier and `review.md`.
- All pre-existing tests (25+) pass; `bundle exec jekyll build` exit 0; local commits only.

## 9. Implementation Order (for the plan)
1. Blog soft archive (independent, quick win)
2. Frontmatter schema + validator + backfill of 5 recipes
3. Site rendering: badges, sources, draft filtering, API/llms changes
4. Skill split + shims + `AGENTS.md` update
5. `review_report.py` + `recipe-review-panel` critic prompts/rubrics
6. `recipe-research`, `recipe-intake`, `recipe-test-log`, `recipe-pipeline`
7. Dogfood on Mongolian Beef; capture `review.md`
8. Full verification

## 10. Open Risks
- **Visual critic tooling** depends on Chrome remote debugging; mitigated by explicit PENDING fallback.
- **Critic independence** relies on subagent prompts excluding author context; enforced by passing only file paths, never conversation history.
- **Archive glob scoping** on nested post folders (see §7.3).
- **Backfill timing** depends on the user's `research-raw.*` handoff; until processed, recipes stay `review.round: 0` (grandfathered, sources may be empty).
