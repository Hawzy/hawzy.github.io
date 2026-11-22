---
title: "Building a No-Ad HELOC Calculator (and What the Rate Scenarios Actually Mean)"
excerpt: "I built a free, no-ad HELOC calculator for an upcoming renovation. Here is what payment shock, the 4 rate scenarios, and all 6 built-in presets actually mean."
additive_asset: "Plain-English guide to HELOC payment shock, all 4 Prime rate scenarios, all 6 built-in presets, and the 6 renovation planning drawers"
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

We have an upcoming home renovation on the calendar, and trying out online HELOC calculators annoyed me enough that I built my own. Most bank calculators online have two bad habits: they quote a low teaser draw payment while hiding the cliff when full amortization kicks in, and they load ad trackers onto a page where you are typing in your home value and mortgage balance.

So I had Google Antigravity turn a HELOC math engine I started into a free, zero-ad web app at [hawzy.github.io/heloc-calculator](https://hawzy.github.io/heloc-calculator/) (MIT source on [GitHub](https://github.com/Hawzy/heloc-calculator)). Everything executes locally in your browser with zero backend, zero cookies, and zero tracking scripts, so none of your numbers ever leave your machine.

Here is what payment shock and the built-in scenarios actually mean, plus a quick summary of what the AI built under the hood.

---

## What a HELOC Payment Cliff Actually Looks Like

Unlike a fixed home equity loan, a HELOC splits into two very different phases:

1. **Draw period:** You typically pay interest only (calculated via Regulation Z `12 CFR 1026.40` Daily Periodic Rates across a `365` or `360` day-count basis) while you are still able to pull funds up to your credit limit.
2. **Repayment period:** Revolving draws freeze and the remaining balance switches to fully amortizing principal-and-interest payments over the remaining months. Because variable Prime rate movements change the active APR each month, that required payment dynamically re-amortizes against the live balance instead of staying flat.

**Payment shock** is the dollar and percentage jump between your last draw-period required payment and your first repayment-period required payment. Every calculation also runs a twin `$0`-prepayment baseline in the background so you can see exactly how much interest and how many months extra monthly payments save you.

---

## What the 4 Prime Rate Scenarios Mean

Your variable HELOC rate equals `Prime + Margin`, capped at your rate ceiling (or your introductory teaser APR during the intro window). The four rate modes let you test how sensitive your monthly payment is if Prime moves while you carry a balance:

| Scenario | How Prime Moves Over Time | When to Use It |
| :--- | :--- | :--- |
| **`Flat`** | Holds your starting Prime rate steady for the whole loan. | Baseline sanity check assuming rates stay where they are today. |
| **`Rising`** | Steps up once per year (defaulting to `+0.50%/yr`). | Steady rate-hike drift across a multi-year renovation payoff. |
| **`Stress Test`** | Surges `+0.75%` every `6` months for 3 years, capping out at `+4.50%` above your starting Prime rate. | Worst-case affordability check to see if a sharp rate spike breaks your monthly budget. |
| **`Custom`** | Uses your own list of annual or monthly Prime rates, carrying the final rate forward across any remaining months. | Modeling a specific rate-cut or hike path you want to test manually. |

---

## What the 6 Built-In Presets Show

Six one-click presets at the top of the calculator show how those rate scenarios play out across very different borrowing and payoff plans:

| Built-In Preset | Setup | Initial Draw -> First Repay | Payment Shock | Total Interest | Payoff & Savings |
| :--- | :--- | :--- | :--- | ---: | :--- |
| **Blueprint Rising** *(default)* | `$50k` / `$100k` limit, `0.99%` 12-mo intro, `6%` Prime + `2%` (`+0.5%/yr`), `10yr` / `20yr`, `+$300/mo` prepay | `$41.25` -> `$164.02` | `+$15.06/mo` (`+10.1%`) | `$31,699.80` | `166` mos (`13.8` yrs), saving `$134,309.88` & `194` mos |
| **Flat Baseline** | `$50k` / `$100k` limit, no intro, flat `7%` Prime + `2%` (`9.0%` APR), `10yr` / `20yr`, `$0` prepay | `$375.00` -> `$449.86` | `+$74.86/mo` (`+19.96%`) | `$102,967.11` | `360` mos (`30.0` yrs), baseline (`$0` saved) |
| **Stress Test 15yr** | `$60k` / `$120k` limit, no intro, `6.5%` Prime + `2.5%` (`Stress Test`), `5yr` / `10yr`, `$0` prepay | `$450.00` -> `$913.65` | `+$238.65/mo` (`+35.4%`) | `$85,412.49` | `180` mos (`15.0` yrs) |
| **WA 25% Usury Cap** | `$20k` / `$50k` limit, `25%` Prime + `3%` (`30%` lifetime cap, clamped to `25.00%` WA Consumer Loan Act ceiling), `1yr` / `1yr` | `$416.67` -> `$1,900.89` | `+$1,484.22/mo` (`+356.2%`) | `$7,810.61` | `24` mos (`2.0` yrs) |
| **Early Draw Payoff** | `$10k` / `$50k` limit, `0.99%` 12-mo intro, flat `7%` Prime + `2%`, `+$2,000/mo` prepay | `$8.25` -> `$0.00` | `$0.00/mo` (`0.0%`) | `$24.75` | `5` mos (`0.4` yrs), saving `$19,767.67` & `355` mos |
| **Staged Reno + Bonus** | `$30k` / `$100k` limit, `6.5%` Prime + `2%` (`+0.5%/yr`), `5yr` / `10yr`, `+$200/mo`, `+$15k` Mo 14 draw, `-$8k` Mo 24 lump sum | `$212.50` -> `$344.38` | `+$123.88/mo` (`+56.18%`) | `$25,001.27` | `147` mos (`12.25` yrs, peak `$42,400`), saving `$29,143.01` & `33` mos |

A few takeaways from running those side by side:

- **Renovations rarely draw all the money on Day 1.** `Staged Reno + Bonus` starts at `$30,000`, adds a `+$15,000` Kitchen Reno draw at Month 14, knocks off an `-$8,000` Annual Bonus lump sum at Month 24, and still saves `33` months and `$29,143.01` in interest over the baseline.
- **Steady extra principal kills off the payment cliff.** On the default `Blueprint Rising` numbers, clicking `Zero Payment Shock` in the goal solver calculates `$416.67/mo` extra prepayment, retiring the whole line in `120` months (`10.0` yrs) for `$20,431.47` total interest and a `$0.00/mo` shock.
- **That WA 25% usury check was a fun detour.** I originally had the calculator enforce Washington's `WAC 208-620-235` `25.0%` Consumer Loan Act statutory ceiling alongside your contractual lifetime cap, only to learn afterward that statutory ceilings don't apply to BECU credit union loans, so I kind of built that cap check for nothing (oops!). I kept it around in case anyone borrows under a Consumer Loan Act lender.

---

## Six Collapsible Planning Drawers

To keep the main view clean, deeper planning controls sit inside `6` collapsed drawers:

1. **Home Equity & CLTV Estimator:** Enter your home value (`$600k`), first mortgage (`$350k`), and max CLTV (`85%`) to find your `$160,000` eligible credit line and click `Apply Eligible Limit to Credit Line`.
2. **Target Payoff Goal Solver:** Solves down to the cent for any target payoff horizon (years or months) or `Zero Payment Shock`, then applies that extra payment directly.
3. **Planned Draws & Lump Sums:** Schedules future renovation draws (`+$15k` Kitchen Reno at Month 14) and lump-sum paydowns (`-$5k` at Month 12) right onto the charts and milestone timeline.
4. **Draw Payment Rule & Fixed Loan Compare:** Tests interest-only draws against a `%` of balance or dollar floor minimum and compares your variable HELOC side by side with a fixed-rate Home Equity Loan (`7.5% / 15yr` at `$463.51/mo`).
5. **Start Date & Closing / Annual Fees:** Maps loan months onto real calendar dates and tracks upfront closing, annual, and early-closure fees separately from Regulation Z APR.
6. **Intro Teaser, Caps & Day-Count:** Holds the intro teaser toggle, lifetime cap, regulatory ceiling, balance calculation method (Average Daily Balance, Adjusted Balance, or Previous Balance), and `365`/`360` year basis.

Right above the charts, the toolbar also lets you save presets in your browser, compare two plans side by side, copy a shareable URL with your exact sliders filled in, export the schedule to CSV, switch between light and dark mode, or print a clean summary.

---

## What the AI Built Under the Hood

Full disclosure: I had basically zero involvement in writing the browser code. I gave Google Antigravity the HELOC formulas and asked for a free, zero-ad static site where nobody's financial inputs ever hit a server, and let it pick how to ship it.

Instead of trying to drag Python into the browser, it ported the core engine into plain zero-dependency JavaScript with inline SVG charts (`20` files total, `64.22 KiB` gzipped, zero external network requests), wrote its own rounding helper so JavaScript matches Python's banker's rounding down to `$0.0000`, and generated `85` automated tests (`66` Python and `19` JavaScript across `17` scenarios) that run in GitHub Actions before deploying to GitHub Pages alongside [/projects/](/projects/). What all `85` of those tests are checking, I definitely did not read line by line, though they all pass.

If you want to inspect the math or run the CLI yourself, the source lives on [GitHub](https://github.com/Hawzy/heloc-calculator). All things considered, having an ad-free calculator ready for our renovation is pretty nice (standard disclaimer: Regulation Z and Washington CLA modeling here is strictly an educational simulation, not financial or legal advice). If you spot a discrepancy in a scenario or something looks off, let me know.
