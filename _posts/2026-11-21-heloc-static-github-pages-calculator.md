---
title: "Shipping a Zero-Backend HELOC Calculator on GitHub Pages (with $0.0000 Python-to-JS Parity)"
excerpt: "How I turned a deterministic Python HELOC engine into a 64.2 KiB zero-dependency GitHub Pages web app with BigInt banker's rounding, CI parity fixtures, and zero telemetry."
additive_asset: "Full 20-file bundle size breakdown (64.22 KiB gzipped), copy-paste IEEE-754 BigInt pyRound() function, CI parity workflow YAML, and 4-scenario benchmark comparison table"
date: 2026-11-21
categories:
  - Blog
projects:
  - heloc-calculator
tags:
  - antigravity
  - finance
  - github-pages
  - python
  - javascript
---

Most bank HELOC calculators online have two annoying habits. First, they happily quote your teaser draw-period payment while hiding the cliff when the draw period ends and the principal starts amortizing. Second, they load half a dozen ad trackers onto a page where you are typing in your home value, mortgage balance, and credit margin. Plus almost none of them model statutory rate ceilings like Washington's `WAC 208-620-235` 25.0% usury cap alongside contractual lifetime caps.

I already had a clean Python HELOC simulation engine sitting on disk (`heloc-calculator`), so I used Google Antigravity to port it into a 100% client-side static web app hosted separately on GitHub Pages at [hawzy.github.io/heloc-calculator](https://hawzy.github.io/heloc-calculator/) (source on [GitHub](https://github.com/Hawzy/heloc-calculator), MIT licensed). Zero backend, zero cookies, zero external CDN or font requests, and `<meta name="referrer" content="no-referrer">` so shareable query-string scenarios never leak out in HTTP headers.

Getting a browser calculator to stay light while matching Python down to the last cent took a few deliberate constraints. Here is how that shook out.

---

## Why I Skipped Pyodide, Bundlers, and Chart Libraries

The original v1 core Python engine (`heloc/core/{formulas.py,models.py,rates.py,simulator.py}`) was only `17,891` bytes across four files (~18 KB, growing to `33,949` bytes across five core modules in v2 once `analytics.py` landed). Shipping Python in the browser via Pyodide/WASM plus `pydantic` and `pandas` would have hauled tens of megabytes into a visitor's tab just to run a 360-month loop.

I got a timely reminder of why browser finance tools shouldn't drag heavy C-extension stacks around on `2026-11-20` when running `pytest` in my global Python `3.12` environment:

```text
ValueError: numpy.dtype size changed, may indicate binary incompatibility.
Expected 96 from C header, got 88 from PyObject
```

Four test files crashed at collection time on `import pandas` inside `heloc/core/simulator.py`. An isolated `.venv` (Python `3.12.7`) fixed local tests immediately, and it cemented the static web choice: keep the Python package, CLI (`heloc`), and `calculate_heloc_trajectory` agent tool intact, and port the core math to plain ES modules under `web/js/engine/`.

I also skipped Vite/TypeScript (`node_modules` overhead for a handful of modules) and external chart libraries like `Chart.js` or `uPlot` (`50-200 KB` of code plus canvas theming and accessibility glue). Everything in `web/` ships straight to GitHub Pages with no build step: plain CSS using `light-dark()` tokens, native Popover API toggletips, and three inline SVG charts with pointer and keyboard (`Home` / `ArrowRight`) crosshairs.

---

## The `$0.0000` Parity Trick (Banker's Rounding + Golden Fixtures)

Porting financial math from Python to JavaScript looks straightforward until a halfway tie diverges by a penny. JavaScript's `Math.round()` rounds `.5` ties toward positive infinity, whereas Python's built-in `round(x, ndigits)` implements IEEE-754 binary64 round-half-to-even (banker's rounding) on the exact underlying float representation.

Rather than fudging rounding tolerances, `web/js/engine/rounding.js` (`1,858` bytes, `761` bytes gzipped) reads the exact 64-bit IEEE-754 mantissa and exponent via `DataView.getBigUint64(0, false)` and resolves halfway ties with `BigInt` arithmetic:

```js
const _view = new DataView(new ArrayBuffer(8));
export function pyRound(value, ndigits = 2) {
  if (!Number.isFinite(value)) return value;
  if (value === 0) return 0;
  _view.setFloat64(0, value, false);
  const bits = _view.getBigUint64(0, false);
  const expBits = Number((bits >> 52n) & 0x7ffn), fracBits = bits & 0xfffffffffffffn;
  const mantissa = expBits === 0 ? fracBits : (1n << 52n) | fracBits;
  const exp = expBits === 0 ? -1074 : expBits - 1075;
  if (exp >= 0) return value;
  const num = mantissa * (10n ** BigInt(ndigits)), den = 1n << BigInt(-exp);
  let q = num / den, r = num % den, half = den >> 1n;
  if (r > half || (r === half && (q & 1n) === 1n)) q += 1n;
  if (q === 0n) return 0;
  const sign = (bits >> 63n) === 1n ? "-" : "";
  return ndigits === 0 ? Number(`${sign}${q}`) : Number(`${sign}${q}e-${ndigits}`);
}
```

*(Works copy-pasted as-is for any `ndigits >= 0`; `web/js/engine/rounding.js` also handles negative `ndigits`.)*

To keep Python and JavaScript locked together permanently, `scripts/generate_golden_fixtures.py` exports `tests/fixtures/golden_parity_vectors.json` (`1,096,619` bytes) straight from the Python engine across `17` benchmark and edge-case scenarios, `4` formula vector groups, and `3` v2 analytics groups (`cltv`, `goal_solver`, `heloan`). Passing `--check` fails CI if anyone updates Python without regenerating fixtures:

```yaml
- name: Run Python test suites
  run: pytest -v
- name: Check Python-to-JS golden parity fixtures for drift
  run: python scripts/generate_golden_fixtures.py --check
- name: Run JS parity and UI utility tests
  run: node --test web/tests/*.test.mjs
```

Running both suites locally and in `.github/workflows/ci.yml` (Python `3.12` + Node `24`) passes `66` Python tests across `9` test modules and `19` Node tests (`7` parity + `12` UI/regression checks in `125.5ms`). CI enforces a `<= $0.01` currency and `<= 0.0001%` APR gate, and the actual measured max delta across all `17` scenarios and every monthly row is **`$0.0000` currency and `0.000000%` APR**.

---

## Deployed Bundle Size Breakdown (20 Files, 64.22 KiB Gzipped)

Every file shipped inside `web/` (excluding `web/tests/`) was measured with Python `pathlib` and `gzip.compress(..., compresslevel=9)`. Because there are zero third-party bundles or font downloads, the entire app cold-loads in `19` same-origin `HTTP 200` requests:

| Component (`web/`) | Uncompressed | Gzipped | Included Files |
| :--- | ---: | ---: | :--- |
| **`web/js/app.js`** | `59,220` B | `13,677` B | Main UI controller & state wiring |
| **`web/index.html`** | `48,807` B | `9,541` B | Semantic form, KPI cards, 6 collapsed drawers |
| **`web/styles.css`** | `44,096` B | `7,746` B | Layered CSS, `light-dark()`, `@container`, `@media print` |
| **Core JS Engine (`8` files)** | `46,451` B (`45.36 KiB`) | `13,377` B (`13.06 KiB`) | `simulator.js`, `models.js`, `analytics.js`, `trajectory.js`, `rates.js`, `formulas.js`, `rounding.js`, `index.js` |
| **`web/js/ui/charts.js`** | `27,492` B | `7,343` B | 3 synchronized inline SVG charts + crosshairs |
| **Other UI Modules (`7` files)** | `47,756` B (`46.64 KiB`) | `14,059` B (`13.73 KiB`) | `state.js`, `a11y.js`, `table.js`, `dates.js`, `presets.js`, `theme.js`, `csv.js` |
| **`web/.nojekyll`** | `0` B | `20` B | Disables Jekyll processing on Pages artifact |
| **Total Deployed Site (`20` files)** | **`273,822` B (`267.40 KiB`)** | **`65,763` B (`64.22 KiB`)** | **Zero external requests, zero `node_modules`** |

*(Individual engine sizes: `simulator.js` `11,911` B, `models.js` `10,099` B, `analytics.js` `9,192` B, `trajectory.js` `8,310` B, `rates.js` `2,481` B, `formulas.js` `1,923` B, `rounding.js` `1,858` B, `index.js` `677` B. Other UI sizes: `state.js` `16,777` B, `a11y.js` `10,398` B, `table.js` `7,893` B, `dates.js` `3,905` B, `presets.js` `3,576` B, `theme.js` `2,768` B, `csv.js` `2,439` B.)*

---

## Four Benchmark Scenarios and What v2 Added

The engine models Regulation Z (`12 CFR 1026.40`) Daily Periodic Rates (`DPR = APR / (100 * B)` across `365`/`360` year bases and `average_daily_balance` / `adjusted_balance` / `previous_balance`), monthly dynamic re-amortization over `n = M_total - m + 1`, and contractual lifetime caps (`18.0%` default) intersected with Washington's `WAC 208-620-235` `25.0%` usury limit. Every run automatically simulates a twin `$0`-prepayment baseline so you can see real interest and months saved:

| Scenario | Key Inputs | Initial Draw -> First Repay | Payment Shock | Total Interest | Payoff |
| :--- | :--- | :--- | :--- | ---: | :--- |
| **Blueprint Rising + `$300/mo` Prepay** | `$50k` / `$100k` limit, `0.99%` 12-mo intro, `6%` Prime + `2%` (`+0.5%/yr`), `10yr` draw / `20yr` repay | `$41.25` -> `$164.02` | `+$15.06/mo` (`+10.1%`) | `$31,699.80` | `166` mos (`13.8` yrs), saving `$134,309.88` & `194` mos |
| **Zero Shock Goal Solver (v2)** | Blueprint defaults solved by binary search (`$416.67/mo` extra prepay) | Solved `$0.00` cliff | `$0.00/mo` (`0.0%`) | `$20,431.47` | `120` mos (`10.0` yrs) |
| **Stress Test 15yr** | `$60k` / `$120k` limit, `6.5%` Prime + `2.5%` (`stress_test`), `5yr` draw / `10yr` repay, `$0` prepay | `$450.00` -> `$913.65` | `+$238.65/mo` (`+35.4%`) | `$85,412.49` | `180` mos (`15.0` yrs) |
| **WA 25% Usury Cap** | `$20k` / `$50k` limit, `25%` Prime + `3%` margin clamped to `25.00%` Month 1, `1yr` / `1yr` | `$416.67` -> `$1,900.89` | `+$1,484.22/mo` (`+356.2%`) | `$7,810.61` | `24` mos (`2.0` yrs) |

In v2 (`commit 85fc95b`), I pushed the deeper levers into `6` collapsed `<details>` Quick-View drawers so the landing view stays fast to scan without stripping away real planning tools:

1. **CLTV Borrowing Power Estimator (`#drawer-cltv`):** Plug in `$600k` home value, `$350k` first mortgage, and `85%` max CLTV to get a `$160,000` eligible line, then click `Apply Eligible Limit to Credit Line`.
2. **Binary-Search Goal Solver (`#drawer-solver`):** Solves down to the cent for any target payoff horizon (years or months) or `Zero Payment Shock`, then applies that extra monthly payment straight to the simulation.
3. **Staged Draws & Lump Sums (`#drawer-events`):** Drops planned draws (`+$15k` Kitchen Reno at Month 14) and bonus paydowns (`-$5k` at Month 12) directly onto the chart markers and milestone timeline.
4. **Draw Minimum Rules & Fixed HELoan Comparison (`#drawer-draw-heloan`):** Tests interest-only draws against `%` of balance / dollar floors and compares the variable line side by side with a fixed-rate Home Equity Loan (`7.5% / 15yr` at `$463.51/mo`).
5. **Calendar Dates & Non-APR Fee Ledger (`#drawer-dates-fees`):** Maps months onto location-agnostic calendar dates (`calendar_month` appends to the 12-column CSV export) and tracks upfront/annual/early-closure fees separately from Reg Z APR.
6. **Intro Teaser, Caps & Day-Count (`#drawer-advanced`):** Keeps the `intro_apr` toggle, lifetime cap, WA regulatory ceiling, balance method, and `365`/`360` year basis tucked out of the way until you need them.

Outside those drawers, the toolbar handles `localStorage` saved presets, a side-by-side Compare vs. delta strip, shareable URL query strings, light/dark switching, and `@media print` styling.

---

## The Dumbest Bug Caught in QA (and Two CSS Traps)

My favorite bug catch from this build was pure HTML5 Constraint Validation trivia (`commit 49cb1fa`). In v1 `web/index.html`, `#lifetime-cap` (default `18.0`) and `#usury-cap` (default `25.0`) both had `min="0.01" max="100" step="0.25"`.

I forgot that HTML5 calculates valid `step` increments starting from `min`, not `0`. With `min="0.01"`, the browser considered `0.01, 0.26, 0.51, ..., 18.01, 25.01` valid and flagged `18.0` and `25.0` as `stepMismatch` invalid the instant the page loaded. Because `app.js` checked `ctrl.validity.valid` across every enabled form control on each edit, touching *any* input froze the whole calculator on the default scenario with a generic validation banner (oops!). Fixing it took three small moves:

- Set `step="any"` on the decimal inputs (`16` named fields locked down by a Node regression test in `web/tests/ui-utils.test.mjs`).
- Updated `#validation-banner` to print the exact offending field label (`Fix "Lifetime Cap (%)" to update results; displaying last valid trajectory.`).
- Ran real headless browser checks across four viewports (`1440×900`, `768×1024`, `390×844`, `320×568`) with `0` console errors and `0` horizontal overflow.

Two CSS traps showed up in the same browser pass (`commits e9b5370` & `49cb1fa`): component `display: flex` / `grid` rules overrode the browser's user-agent `[hidden] { display: none; }` until `@layer utilities` added `[hidden]:not([hidden="until-found"]) { display: none !important; }`, and default `<figure>` margins squeezed the inline SVG charts down to `159px` wide on a `320×568` screen until `figure { margin: 0; }` opened them back up to `258.54px` (`328.54px` on `390×844`), paired with `@container (width < 780px)` stacked table cards.

---

## Hosting It Separately on GitHub Pages

Keeping `Hawzy/heloc-calculator` in its own repo instead of stuffing it inside this Jekyll repository keeps builds completely decoupled, while still staying miles below GitHub Pages limits (`1 GB` site cap, `100 GB/month` bandwidth, `10-minute` deploy timeout). Using `.github/workflows/deploy-pages.yml` (`configure-pages@v5`, `upload-pages-artifact@v3` on `path: web`, `deploy-pages@v4`) with `web/.nojekyll` also skips default Jekyll builds (and its 10 builds/hour soft limit) altogether.

Meanwhile, adding a card to `_data/projects.yml` links [hawzy.github.io/heloc-calculator](https://hawzy.github.io/heloc-calculator/) straight from [/projects/](/projects/) right alongside the main blog. All things considered, shipping a `64.22 KiB` gzipped calculator with exact Python parity and zero telemetry feels pretty good (just remember the statutory fine print: Regulation Z and Washington CLA modeling here is strictly an educational simulation, not financial or legal advice).

If you spot a discrepancy in the math or an edge case on your phone screen, let me know.
