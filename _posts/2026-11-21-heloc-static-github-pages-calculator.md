---
title: "Building a No-Ad HELOC Calculator (and What the Rate Scenarios Actually Mean)"
excerpt: "I built a free, browser-only HELOC calculator for an upcoming renovation. Here is what payment shock and each built-in rate scenario mean, plus how it matches Python to $0.0000."
additive_asset: "Plain-English guide to all 4 Prime rate scenarios and 6 built-in presets, plus the 20-file bundle table (64.22 KiB gzipped), copy-paste IEEE-754 BigInt pyRound() function, and CI parity YAML"
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

We have an upcoming home renovation on the calendar, and trying out online HELOC calculators annoyed me enough that I built my own. Most bank calculators online have two bad habits: they quote a low teaser draw payment while hiding the cliff when full amortization kicks in, and they fire half a dozen ad trackers onto a page where you are typing in your home value and mortgage balance. Almost none of them check statutory ceilings like Washington's `WAC 208-620-235` 25.0% usury cap alongside contractual lifetime caps either.

So I turned my Python HELOC engine (`heloc-calculator`) into a free, zero-ad web app at [hawzy.github.io/heloc-calculator](https://hawzy.github.io/heloc-calculator/) (MIT source on [GitHub](https://github.com/Hawzy/heloc-calculator)). Everything executes locally in your browser with zero backend, zero cookies, zero external font or CDN requests, and `<meta name="referrer" content="no-referrer">` so shareable parameter URLs do not leak out in HTTP headers.

If you just want to run numbers for a project, here is what the payment cliff and the built-in scenarios actually mean, followed by how the math stays identical to Python down to `$0.0000`.

---

## What a HELOC Payment Cliff Actually Looks Like

Unlike a fixed home equity loan, a HELOC splits into two very different phases:

1. **Draw period:** You typically pay interest only (calculated via Regulation Z `12 CFR 1026.40` Daily Periodic Rates across your `365` or `360` year basis) while you are still able to pull funds up to your credit limit.
2. **Repayment period:** Revolving draws freeze and the remaining balance `P` switches to fully amortizing payments over the remaining months `n = M_total - m + 1`. Because variable Prime movements change the effective APR each month, the payment dynamically re-amortizes against the live balance rather than staying frozen.

**Payment shock** is the dollar and percentage jump between your last draw-period required payment and your first repayment-period required payment. Every run also simulates a twin `$0`-prepayment baseline in the background so you can see exactly how much interest and how many months extra monthly payments save you.

---

## What the 4 Prime Rate Scenarios Mean

A HELOC rate equals `Prime + Margin`, clamped between `0%` and `min(lifetime_cap, regulatory_ceiling)` (or your introductory teaser APR during the intro window). The four rate modes let you test how sensitive your payment is to Prime moving while you carry a balance:

| Scenario | How Prime Moves Each Month | When to Use It |
| :--- | :--- | :--- |
| **`Flat`** | Holds `base_prime` constant for every month (`[base_prime] * total_months`). | Baseline sanity check assuming rates stay where they are today. |
| **`Rising`** | Steps up once per year (`base_prime + ((m // 12) * annual_step)`, defaulting to `+0.50%/yr`). | Steady rate-hike drift across a multi-year renovation payoff. |
| **`Stress Test`** | Surges `+0.75%` every `6` months (`semester_idx = min(m // 6, 6)`), topping out at `+4.50%` over 3 years. | Worst-case affordability test to see if a sharp rate spike breaks your monthly budget. |
| **`Custom`** | Reads your own annual (expanded `12x`) or monthly Prime rate list, padding with the final value if shorter than the loan. | Modeling a specific rate cut/hike path you want to test manually. |

---

## What the 6 Built-In Presets Show

If you open the calculator for the first time, six one-click presets at the top show very different ways a HELOC behaves under those scenarios:

| Built-In Preset | Setup | Initial Draw -> First Repay | Payment Shock | Total Interest | Payoff & Savings |
| :--- | :--- | :--- | :--- | ---: | :--- |
| **Blueprint Rising** *(default)* | `$50k` / `$100k` limit, `0.99%` 12-mo intro, `6%` Prime + `2%` (`+0.5%/yr`), `10yr` / `20yr`, `+$300/mo` prepay | `$41.25` -> `$164.02` | `+$15.06/mo` (`+10.1%`) | `$31,699.80` | `166` mos (`13.8` yrs), saving `$134,309.88` & `194` mos |
| **Flat Baseline** | `$50k` / `$100k` limit, no intro, flat `7%` Prime + `2%` (`9.0%` APR), `10yr` / `20yr`, `$0` prepay | `$375.00` -> `$449.86` | `+$74.86/mo` (`+19.96%`) | `$102,967.11` | `360` mos (`30.0` yrs), baseline (`$0` saved) |
| **Stress Test 15yr** | `$60k` / `$120k` limit, no intro, `6.5%` Prime + `2.5%` (`stress_test`), `5yr` / `10yr`, `$0` prepay | `$450.00` -> `$913.65` | `+$238.65/mo` (`+35.4%`) | `$85,412.49` | `180` mos (`15.0` yrs) |
| **WA 25% Usury Cap** | `$20k` / `$50k` limit, `25%` Prime + `3%` (`30%` lifetime cap, clamped to `25.00%` WA CLA), `1yr` / `1yr` | `$416.67` -> `$1,900.89` | `+$1,484.22/mo` (`+356.2%`) | `$7,810.61` | `24` mos (`2.0` yrs) |
| **Early Draw Payoff** | `$10k` / `$50k` limit, `0.99%` 12-mo intro, flat `7%` Prime + `2%`, `+$2,000/mo` prepay | `$8.25` -> `$0.00` | `$0.00/mo` (`0.0%`) | `$24.75` | `5` mos (`0.4` yrs), saving `$19,767.67` & `355` mos |
| **Staged Reno + Bonus** | `$30k` / `$100k` limit, `6.5%` Prime + `2%` (`+0.5%/yr`), `5yr` / `10yr`, `+$200/mo`, `+$15k` Mo 14 draw, `-$8k` Mo 24 lump sum | `$212.50` -> `$344.38` | `+$123.88/mo` (`+56.18%`) | `$25,001.27` | `147` mos (`12.25` yrs, peak `$42,400`), saving `$29,143.01` & `33` mos |

Two patterns jump out from those presets right away:

- **Renovations rarely draw all the money on Day 1.** `Staged Reno + Bonus` starts with `$30,000`, adds a `+$15,000` Kitchen Reno draw at Month 14, applies an `-$8,000` Annual Bonus lump sum at Month 24, and still knocks `33` months and `$29,143.01` of interest off the baseline.
- **Steady extra principal crushes the payment cliff.** On the default `Blueprint Rising` numbers, clicking `Zero Payment Shock` in the goal solver finds `$416.67/mo` extra prepayment via binary search, paying the entire line off in `120` months (`10.0` yrs) for `$20,431.47` total interest and a `$0.00/mo` shock.

---

## Six Collapsible Planning Drawers (Plus Offline Tools)

To keep the initial view clean, deeper planning controls live inside `6` collapsed `<details>` drawers:

1. **CLTV Borrowing Power Estimator (`#drawer-cltv`):** Enter home value (`$600k`), first mortgage (`$350k`), and max CLTV (`85%`) to calculate your `$160,000` eligible credit line, then click `Apply Eligible Limit to Credit Line`.
2. **Binary-Search Goal Solver (`#drawer-solver`):** Solves down to the cent for any target payoff horizon (years or months) or `Zero Payment Shock`, then applies that extra payment directly.
3. **Staged Draws & Lump Sums (`#drawer-events`):** Plots mid-loan draws (`+$15k` Kitchen Reno at Month 14) and bonus paydowns (`-$5k` at Month 12) onto the chart markers and milestone timeline.
4. **Draw Minimum Rules & Fixed HELoan Comparison (`#drawer-draw-heloan`):** Tests interest-only draws against `%` of balance / dollar floors and compares the variable line against a fixed-rate Home Equity Loan (`7.5% / 15yr` at `$463.51/mo`).
5. **Calendar Dates & Non-APR Fee Ledger (`#drawer-dates-fees`):** Maps months onto location-agnostic calendar dates (`calendar_month` appends to the 12-column CSV export) and tracks closing, annual, and early-closure fees separately from Reg Z APR.
6. **Intro Teaser, Caps & Day-Count (`#drawer-advanced`):** Keeps the `intro_apr` toggle, lifetime cap, WA regulatory ceiling, balance method (`average_daily_balance`, `adjusted_balance`, `previous_balance`), and `365`/`360` year basis out of the way until you tweak them.

Outside those drawers, the toolbar handles `localStorage` saved presets, a side-by-side `Compare vs.` delta strip, shareable URL query strings, light/dark switching, 1-click CSV export, synchronized pointer/keyboard (`Home` / `ArrowRight`) chart crosshairs, and `@media print` formatting.

---

## Under the Hood (For the Nerds)

### 1. Why I Skipped Pyodide, Bundlers, and Chart Libraries
The original v1 core Python engine (`heloc/core/{formulas.py,models.py,rates.py,simulator.py}`) totaled `17,891` bytes (~18 KB, growing to `33,949` bytes across five core modules in v2 once `analytics.py` landed). Shipping Pyodide/WASM plus `pydantic` and `pandas` into a visitor's tab for a 360-month loop would have forced tens of megabytes of cold boot.

I got a reminder of why browser finance tools shouldn't haul C-extension stacks around on `2026-11-20` when running `pytest` in my global Python `3.12` environment:

```text
ValueError: numpy.dtype size changed, may indicate binary incompatibility.
Expected 96 from C header, got 88 from PyObject
```

Four test files crashed at collection time on `import pandas` inside `heloc/core/simulator.py`. Using an isolated `.venv` (Python `3.12.7`) fixed local tests immediately, and cemented keeping the Python package, `heloc` CLI, and `calculate_heloc_trajectory` tool intact while porting the core math to plain ES modules under `web/js/engine/`. I also skipped Vite/TypeScript (`node_modules` overhead) and `Chart.js`/`uPlot` (`50-200 KB` + canvas theming glue) in favor of `20` static files using `@supports (color: light-dark(white, black))` CSS tokens, native Popover API toggletips, and custom inline SVG charts.

### 2. IEEE-754 Banker's Rounding + CI Golden Fixtures (`$0.0000` Delta)
JavaScript's `Math.round()` rounds `.5` ties toward positive infinity, whereas Python's `round(x, ndigits)` implements IEEE-754 binary64 round-half-to-even (banker's rounding). Left alone, halfway ties drift by a penny across long schedules. Instead, `web/js/engine/rounding.js` (`1,858` bytes, `761` bytes gzipped) reads the raw 64-bit IEEE-754 layout with `DataView.getBigUint64(0, false)` and computes exact `BigInt` remainder tie-breaks:

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

To keep Python and JavaScript synced permanently, `scripts/generate_golden_fixtures.py` exports `tests/fixtures/golden_parity_vectors.json` (`1,096,619` bytes) covering `17` scenarios, `4` formula groups, and `3` v2 analytics groups (`cltv`, `goal_solver`, `heloan`), with `.github/workflows/ci.yml` enforcing parity on Python `3.12` + Node `24`:

```yaml
- name: Run Python test suites
  run: pytest -v
- name: Check Python-to-JS golden parity fixtures for drift
  run: python scripts/generate_golden_fixtures.py --check
- name: Run JS parity and UI utility tests
  run: node --test web/tests/*.test.mjs
```

That runs `66` Python tests across `9` modules plus `19` Node tests (`7` parity + `12` UI/regression checks in `125.5ms`). CI fails above `$0.01` currency or `0.0001%` rate drift, and the observed max delta across all `17` scenarios and every monthly row is **`$0.0000` currency and `0.000000%` APR**.

### 3. Deployed 20-File Bundle Breakdown (`64.22 KiB` Gzipped)
Measured across `web/` (excluding `web/tests/`) with Python `pathlib` and `gzip.compress(..., compresslevel=9)`, cold-loading in `19` same-origin `HTTP 200` requests:

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

*(Engine breakdown: `simulator.js` `11,911` B, `models.js` `10,099` B, `analytics.js` `9,192` B, `trajectory.js` `8,310` B, `rates.js` `2,481` B, `formulas.js` `1,923` B, `rounding.js` `1,858` B, `index.js` `677` B. Other UI: `state.js` `16,777` B, `a11y.js` `10,398` B, `table.js` `7,893` B, `dates.js` `3,905` B, `presets.js` `3,576` B, `theme.js` `2,768` B, `csv.js` `2,439` B.)*

### 4. The `stepMismatch` Freeze (and Two CSS Traps)
My favorite QA bug catch came from plain HTML5 Constraint Validation (`commit 49cb1fa`). In v1 `web/index.html`, `#lifetime-cap` (default `18.0`) and `#usury-cap` (default `25.0`) had `min="0.01" max="100" step="0.25"`. HTML5 anchors valid `step` increments to `min`, not `0`, meaning the browser considered `0.01, 0.26, ..., 18.01, 25.01` valid and flagged `18.0` and `25.0` as `stepMismatch` invalid on page load. Because `app.js` checked `ctrl.validity.valid` across all enabled inputs on every edit, changing *any* field froze the calculator on the default scenario (oops!).

Switching decimal inputs to `step="any"` (`16` named fields enforced by `web/tests/ui-utils.test.mjs`) and naming the offending field in `#validation-banner` (`Fix "Lifetime Cap (%)" to update results; displaying last valid trajectory.`) fixed it cleanly. In the same headless Chromium checks across `1440×900`, `768×1024`, `390×844`, and `320×568` (`0` console errors, `0` horizontal overflow), `@layer utilities` added `[hidden]:not([hidden="until-found"]) { display: none !important; }` so `display: flex`/`grid` rules couldn't override `[hidden]`, and `figure { margin: 0; }` widened the inline SVG charts on `320×568` phones from `159px` to `258.54px` (`328.54px` on `390×844`), paired with `@container (width < 780px)` stacked schedule cards.

---

## Hosting It Separately on GitHub Pages

Keeping `Hawzy/heloc-calculator` in its own repo lets `.github/workflows/deploy-pages.yml` (`configure-pages@v5`, `upload-pages-artifact@v3` on `path: web`, `deploy-pages@v4`) publish straight to GitHub Pages without touching Jekyll (well under Pages' `1 GB` site cap, `100 GB/month` bandwidth, `10-minute` timeout, and bypassing Jekyll's 10 builds/hour soft cap), while `_data/projects.yml` links it from [/projects/](/projects/).

All things considered, building a `64.22 KiB` browser-only HELOC calculator that matches Python to the cent without any ad trackers feels pretty good (obligatory fine print: Regulation Z and Washington CLA modeling here is strictly for educational simulation, not financial or legal advice). If you spot a discrepancy in a scenario or something looks off on your phone screen, let me know.
