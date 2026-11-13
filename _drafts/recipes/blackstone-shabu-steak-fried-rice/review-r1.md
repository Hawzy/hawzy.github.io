# Review — Blackstone Shabu Steak and Egg Fried Rice (round 1) · Verdict: CHANGES REQUESTED
| Critic | Score | Blockers | Major | Nit |
|---|---|---|---|---|
| Culinary & Safety | 5/5 | 0 | 0 | 1 |
| Editorial & Usability | 2/5 | 3 | 2 | 1 |
| Visual (rendered) | PENDING — run /browser | 0 | 0 | 1 |
| Structural audit (script) | PASS | — | — | — |

## Blockers
- [EDT-1] `instructions` (Steps 3, 4, 5): Violates `<3 bolds per step` cap (Step 3 has 7 bold spans, Step 4 has 4 bold spans, Step 5 has 3 bold spans) — evidence: `_recipes/blackstone-shabu-steak-fried-rice.md:208-210` → Fix | Waive (reason): ___
- [EDT-2] `instructions` (Steps 1, 2, 3, 5, 6, 8): Double-chips compound `garlic butter` in Steps 3/5/6 after already chipping its components (`4 tbsp` butter, `4 cloves` garlic, `1 tsp` lemon juice) in Step 1, and chips `scallions` once as a total (`6 stalks`) in Step 2 instead of chipping the divided additions (`6 whites` in Step 3, `6 greens` in Step 8) — evidence: `_recipes/blackstone-shabu-steak-fried-rice.md:206-213` → Fix | Waive (reason): ___
- [EDT-3] `engineer_grid_html` (Part 1, line 232): Uses a "reserve/stage" filler column (`Stage by griddle for Part 2...`) with `action-cell--finish` on cold counter staging — evidence: `_recipes/blackstone-shabu-steak-fried-rice.md:232` → Fix | Waive (reason): ___
- [VIS-1] `_site/recipes/blackstone-shabu-steak-fried-rice/index.html`: Live browser viewport screenshots (1280px, 390px, lightbox, print) pending Chrome remote debugging (static HTML/CSS structural & `@media print` checks passed 5/5) — evidence: `_site/recipes/blackstone-shabu-steak-fried-rice/index.html` → Fix | Waive (reason): ___

## Major
- [EDT-4] `instructions` (Steps 2, 3, 4, 5, 6): Steps 2 (77w), 3 (105w), 4 (102w), and 5 (69w) exceed `<=60 words` and `<=1 primary action`, and Step 6 lacks a sensory cue immediately after `**20 to 30 seconds**` — evidence: `_recipes/blackstone-shabu-steak-fried-rice.md:207-211` → Fix | Waive (reason): ___
- [EDT-5] `ingredients` vs. `instructions` vs. `engineer_grid_html`: Inconsistent naming/units for `lemon` (`0.5 lemon` vs `1 tsp` + `2 tsp` lemon juice), `japanese barbecue sauce` (`Bachan's Japanese barbecue sauce` vs `Bachan's sauce`), and `kewpie mayonnaise` (`Kewpie mayo`) — evidence: `_recipes/blackstone-shabu-steak-fried-rice.md:39-172,206-394` → Fix | Waive (reason): ___

## Nits
- [CUL-1] `calories_per_serving: 760`: Tracks the base formulation without the optional `1 1/2 tbsp` Kewpie mayonnaise (~794 kcal base vs ~831 kcal with Kewpie, both well within the 25% threshold) — evidence: `_recipes/blackstone-shabu-steak-fried-rice.md:14,168` → Waive (reason): Within 4.3% (base) and 8.5% (with optional Kewpie) of calculated sum.
- [EDT-6] `engineer_grid_html` (Part 2, Col 1): Rows 1–3 start directly with `--heat` while Rows 6–9, 13, and 17 start with `--prep` in Column 1 — evidence: `_recipes/blackstone-shabu-steak-fried-rice.md:259-354` → Fix | Waive (reason): ___

## Approval: ☐ Approve (status → untested)  ☑ Request changes
