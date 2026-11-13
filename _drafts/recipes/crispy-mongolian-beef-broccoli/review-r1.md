# Review — Crispy Mongolian Beef with Broccoli and White Onion (round 1) · Verdict: CHANGES REQUESTED
| Critic | Score | Blockers | Major | Nit |
|---|---|---|---|---|
| Culinary & Safety | 5/5 | 0 | 0 | 1 |
| Editorial & Usability | 2/5 | 4 | 2 | 1 |
| Visual (rendered) | PENDING — run /browser | 0 | 0 | 1 |
| Structural audit (script) | PASS | — | — | — |

## Blockers
- [EDT-1] `instructions` (Steps 1, 3, 4, 5, 6) & narrative body (lines 350–375): Violates `<3 bolds per step` cap (Steps 1, 3, 4, 6 have 3 bolds; Step 5 has 4 bolds) and uses inline backtick chips and non-timer bolding inside the narrative essay — evidence: `_recipes/crispy-mongolian-beef-broccoli.md:170-176,350-375` → Fix | Waive (reason): ___
- [EDT-2] `engineer_grid_html` (Part 1, line 197): Uses a "reserve/stage" filler column (`Stage glaze bowl & slurry cup beside wok for Part 2`) with `action-cell--finish` on cold counter staging — evidence: `_recipes/crispy-mongolian-beef-broccoli.md:197` → Fix | Waive (reason): ___
- [EDT-3] `engineer_grid_html` (Part 2, lines 240–322): Dependency column ordering violation in Part 2 (`Stir-fry onion 60s in reserved 1 tbsp oil` sits in Action Column 2, one column to the left of `Shallow-fry in smoking oil... & leave 1 tbsp oil` in Action Column 3, and beef rows precede broccoli rows despite Step 3 cooking broccoli before Step 4 fries beef) — evidence: `_recipes/crispy-mongolian-beef-broccoli.md:240-322` → Fix | Waive (reason): ___
- [EDT-4] `instructions` (Steps 1, 2, 3): Tap water is chipped with backtick quantity tags (`1 tbsp` in Step 1, `1 tbsp` in Step 2, `2 tbsp` in Step 3) without a corresponding `water` entry in `ingredients` frontmatter — evidence: `_recipes/crispy-mongolian-beef-broccoli.md:170-172` → Fix | Waive (reason): ___
- [VIS-1] `_site/recipes/crispy-mongolian-beef-broccoli/index.html`: Live browser viewport screenshots (1280px, 390px, lightbox, print) pending Chrome remote debugging (static HTML/CSS structural & `@media print` checks passed 5/5) — evidence: `_site/recipes/crispy-mongolian-beef-broccoli/index.html` → Fix | Waive (reason): ___

## Major
- [EDT-5] `instructions` (Steps 1–5): Steps 1 (115w), 2 (78w), 3 (66w), 4 (98w), and 5 (95w) exceed the `<=60 words` and `<=1 primary action` limits, and Step 5 ends on a bare timer (`**30 seconds**`) without a sensory cue — evidence: `_recipes/crispy-mongolian-beef-broccoli.md:170-175` → Fix | Waive (reason): ___
- [EDT-6] `ingredients` vs. `instructions` vs. `engineer_grid_html` vs. narrative body: Ingredient names drift across surfaces (`chicken broth` vs `chicken bone broth`, `broccoli crown` vs `broccoli florets`) and narrative body (~650 words) repeats step mechanics — evidence: `_recipes/crispy-mongolian-beef-broccoli.md:42-375` → Fix | Waive (reason): ___

## Nits
- [CUL-1] `total_time_iso: "PT35M"`: Reflects active prep (`20m`) + cook (`15m`) time and excludes `50m` passive chilling (`20m` freezer + `30m` fridge) — evidence: `brief.md:7`, `research.md:6` → Waive (reason): Active time matches `brief.md` and `research.md`, and `excerpt` + Step 1 disclose chilling intervals upfront.
- [EDT-7] `instructions` (Step 6): Sensory cue (`rapid, bubbling simmer`) precedes the `**60 seconds**` timer instead of following it — evidence: `_recipes/crispy-mongolian-beef-broccoli.md:176` → Fix | Waive (reason): ___

## Approval: ☐ Approve (status → untested)  ☑ Request changes
