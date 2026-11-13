---
name: recipe-review-panel
description: Runs the deterministic structural auditor and dispatches an independent 3-critic review panel (Culinary, Editorial, Visual) with no author context to produce _drafts/recipes/<slug>/review.md.
---

# Recipe Review Panel Skill (`recipe-review-panel`)

Executes the pre-publish quality gate on `_recipes/<slug>.md` by combining:
1. **Deterministic Structural & Matrix Audit** (`scripts/audit_recipes.py`)
2. **Three Independent Critic Subagents** (`Culinary & Safety`, `Editorial & Usability`, `Visual (rendered)`) dispatched in parallel with **no author context**
3. **Verdict & Round-Diff Engine** (`scripts/review_report.py`) producing `_drafts/recipes/<slug>/review.md` for Gate 2 sign-off.

---

## Critic Isolation Rule (No Author Context)

When invoking the 3 critic subagents via `invoke_subagent`:
- Pass **ONLY file paths**:
  - `_recipes/<slug>.md`
  - `_drafts/recipes/<slug>/brief.md`
  - `_drafts/recipes/<slug>/research.md` (when `origin: research`)
  - `_drafts/recipes/<slug>/sources.yml` (when `origin: research`)
- **Provide no author context**: Never include authoring conversation transcripts, excuses, or prior justifications in the critic prompts. Critics evaluate only what is written on disk.
- Severity levels:
  - `BLOCKER` — must be fixed or explicitly waived with a non-empty user reason before publish.
  - `MAJOR` — should be fixed; does not automatically block verdict once blockers are cleared.
  - `NIT` — optional polish.
- Each critic assigns a `1/5` to `5/5` score and stable finding IDs (`CUL-n`, `EDT-n`, `VIS-n`). On round `N > 1`, pass prior `_drafts/recipes/<slug>/review-r<N-1>.md` IDs so resolved/persisting findings keep the same ID numbers.

---

## Critic 1: Culinary & Safety Rubric (`CUL-n`)

| Check | Severity Rule |
|---|---|
| **Numbers ↔ dossier** | `BLOCKER` if any quantity, temperature, or duration in `_recipes/<slug>.md` is unsupported by, or contradicts, `research.md` / `brief.md`. |
| **Food safety** | `BLOCKER` if an internal temperature is below the USDA minimum without an explicit chef's-choice note in the step/notes (e.g., `125°F` medium-rare steak is permitted when noted). |
| **Ratio physics** | `BLOCKER` if physically implausible (reduction volume vs. time, starch:liquid thickening ratio, oil volume vs. pan surface). |
| **Timeline** | `BLOCKER` if sum of sequential step times vs. `total_time_iso` is off by `>30%`, or requires impossible parallelism for one home cook. |
| **Equipment / crowding** | `MAJOR` if pan size causes steaming instead of searing or overflow. |
| **Calories estimate** | `MAJOR` if `calories_per_serving` is off by `>25%` from an ingredient-based calculation. |

### Culinary Critic Subagent Prompt Template
```text
You are the independent Culinary & Food-Safety Critic (ID prefix: CUL-).
You have no author context. Read ONLY:
- _recipes/<slug>.md
- _drafts/recipes/<slug>/brief.md
- _drafts/recipes/<slug>/research.md (if present)
- _drafts/recipes/<slug>/sources.yml (if present)

Audit the recipe against the Culinary & Safety rubric:
1. Numbers <-> dossier traceability (BLOCKER on any unsupported/contradicting qty, temp, or time)
2. Food safety vs USDA baseline (BLOCKER if below USDA minimum without explicit chef's-choice note)
3. Ratio physics (BLOCKER if implausible reduction, starch:liquid, or fat ratio)
4. Timeline accuracy vs total_time_iso within 30% (BLOCKER)
5. Equipment & pan crowding (MAJOR)
6. Calories per serving within 25% of ingredient sum (MAJOR)

Return:
- Score: X/5
- Findings formatted as:
  - [CUL-1] <location>: <finding> — evidence: <dossier/recipe ref> → Fix | Waive (reason): ___
  grouped under BLOCKER, MAJOR, and NIT.
```

---

## Critic 2: Editorial & Usability Rubric (`EDT-n`)

| Check | Severity Rule |
|---|---|
| **3-tier grammar** | `BLOCKER` if any step has `>=3` bolded clauses, or puts a backtick chip on a timer, temperature, or slice/pan size. |
| **Grid logic** | `BLOCKER` if `engineer_grid_html` columns act as clock phases instead of combinatorial dependencies, an action merges rows it does not touch, filler `"reserve"` / `"stage"` cells appear, or thermal class (`--prep`, `--heat`, `--finish`) mismatches the step. |
| **Step readability** | `MAJOR` if a step packs `>1` primary action or `>60` words, or fails to place the sensory doneness cue right after the timer/temp. |
| **Narrative & naming** | `MAJOR` for throat-clearing filler prose or inconsistent ingredient naming across body narrative, `ingredients`, and `engineer_grid_html`. |
| **Ingredient accounting** | `BLOCKER` for any listed ingredient unused in `instructions` or `, divided` splits that do not sum to the total quantity. |

### Editorial Critic Subagent Prompt Template
```text
You are the independent Editorial & Usability Critic (ID prefix: EDT-).
You have no author context. Read ONLY:
- _recipes/<slug>.md
- _drafts/recipes/<slug>/brief.md

Audit the recipe against the Editorial & Usability rubric:
1. 3-tier grammar: chips (`qty unit`) ONLY on first ingredient additions; short bold (**...**) ONLY on heat/timers/temps (<3 bolds per step); plain prose elsewhere (BLOCKER)
2. Cooking for Engineers grid logic: dependency columns, zero "reserve/stage" filler cells, honest thermal classes (--prep/--heat/--finish), contiguous merges (BLOCKER)
3. Step readability: <=1 primary action, <=60 words, sensory doneness cue after timer (MAJOR)
4. Narrative tightness & consistent ingredient naming across narrative/list/grid (MAJOR)
5. Ingredient accounting: every ingredient used, divided splits sum to total (BLOCKER)

Return:
- Score: X/5
- Findings formatted as:
  - [EDT-1] <location>: <finding> — evidence: <step/grid ref> → Fix | Waive (reason): ___
  grouped under BLOCKER, MAJOR, and NIT.
```

---

## Critic 3: Visual / Rendered-Page Rubric (`VIS-n`)

Builds the site (`bundle exec jekyll build`) and inspects `/recipes/<slug>/` via the **`chrome-devtools`** MCP at:
- `1280px` desktop viewport (block grid readable without horizontal scroll; status badge + sources block visible)
- `390px` mobile viewport (chips wrap cleanly, zero horizontal overflow or clipping)
- Grid lightbox open state (`[data-grid-zoom-open]`)
- Print media emulation (`@media print` fits ~1–2 pages with interactive controls hidden and 1-line source credit visible)
- Hero image fidelity check (if `image:` is set, depicts the actual protein, cut, sauce, and garnish of the recipe)

**Fallback when Chrome remote debugging is unavailable**:
- If Chrome remote debugging (port 9222) is offline, perform compiled HTML/CSS structural checks on `_site/recipes/<slug>/index.html` and set the critic table row score to **`PENDING — run /browser`**.
- `review_report.py` treats `PENDING — run /browser` as a blocking condition (`CHANGES REQUESTED`) until the user runs `/browser` to confirm visually or waives it with a non-empty reason.

---

## Panel Workflow & CLI Tooling

1. **Archive prior round (if re-running)**:
   - If `_drafts/recipes/<slug>/review.md` already exists from round `N-1`, copy it to `_drafts/recipes/<slug>/review-r<N-1>.md`.
2. **Run Structural & Matrix Auditor**:
   ```bash
   python .agents/skills/recipe-review-panel/scripts/audit_recipes.py _recipes/<slug>.md
   ```
3. **Dispatch the 3 Critics in Parallel** (`Culinary`, `Editorial`, `Visual`) with no author context and merge their findings into `_drafts/recipes/<slug>/review.md`:
   ```markdown
   # Review — <Title> (round N) · Verdict: APPROVED | CHANGES REQUESTED
   | Critic | Score | Blockers | Major | Nit |
   |---|---|---|---|---|
   | Culinary & Safety | 5/5 | 0 | 1 | 0 |
   | Editorial & Usability | 5/5 | 0 | 0 | 1 |
   | Visual (rendered) | 5/5 | 0 | 0 | 0 |
   | Structural audit (script) | PASS | — | — | — |

   ## Blockers
   ## Major
   ## Nits
   ## Changes since round N-1
   ## Approval: ☐ Approve (status → untested)  ☐ Request changes
   ```
4. **Compute Diff & Verdict via `scripts/review_report.py`**:
   ```bash
   # Compare against prior round and append markdown diff
   python .agents/skills/recipe-review-panel/scripts/review_report.py --diff _drafts/recipes/<slug>/review-r1.md _drafts/recipes/<slug>/review.md

   # Validate zero open blockers, non-empty waiver reasons, non-PENDING visual row, and Structural audit PASS
   python .agents/skills/recipe-review-panel/scripts/review_report.py --check _drafts/recipes/<slug>/review.md

   # At Gate 2 after user approval: promote _recipes/<slug>.md frontmatter (status: untested, review.*)
   python .agents/skills/recipe-review-panel/scripts/review_report.py --approve _drafts/recipes/<slug>/review.md --recipe _recipes/<slug>.md
   ```
