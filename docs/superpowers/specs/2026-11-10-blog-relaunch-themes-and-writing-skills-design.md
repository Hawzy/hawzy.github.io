---
layout: single
title: "Blog Relaunch, 5-Theme Identity System & Agentic Writing Skills — Design Specification"
surface: blog
sitemap: false
search: false
comments: false
---

# Blog Relaunch, 5-Theme Identity System & Agentic Writing Skills — Design Specification

**Date:** 2026-11-10
**Repository:** `hawzy.github.io` (`c:\github\agy\recipes`, branch `feat/agentic-recipe-blog`)
**Scope:** Project-sized design covering:
1. **Sub-project A — Site Identity, Layout C Homepage & 5-Theme Palette Switcher**
2. **Sub-project B — 3-Skill Blog Writing Pipeline (`blog-voice`, `blog-research`, `blog-author`) + `audit_posts.py`**
3. **Sub-project C — Relaunch Post #1 Draft & 5-Post Backlog**

---

## 1. Intent & Why

The site began in 2022 as a `#100DaysOfCode` Jekyll blog and was recently expanded with a dual-surface (Human UI + Business-to-Agent JSON) recipe and weekly meal-planning system under the working title *"Hawzy's Kitchen & Code"*.

Before going live, the site needs to reflect what it actually is: **a builder's blog by `hawzy` about writing code and using AI agents (Google Antigravity) to automate real-life chores and hobbies**, where the agentic kitchen and weekly grocery planner is one flagship project alongside other home-automation and hobby tools added as they are published.

At the same time, publishing new posts should follow an agent-assisted workflow: the human author provides raw stream-of-consciousness notes and quips (`notes.md`), and the agent researches the target repository for verified facts (`facts.md`), drafts the post in the author's voice (`voice-profile.md`), prepares a companion X/Twitter hook and thread (`twitter-thread.md`), and validates the output with a deterministic Python stdlib auditor (`audit_posts.py`) plus a zero-context Editorial/Voice critic subagent.

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- **Quiet, high-craft identity:** Replace *"Hawzy's Kitchen & Code"* with a quiet `hawzy` wordmark whose header styling adapts to 5 distinct editor/terminal-inspired themes (`Gruvbox`, `Telemetry`, `Catppuccin`, `Kitchen`, `Paper`).
- **Blog-first homepage (Layout C):** Make `/` the blog and project hub (featured latest post card, project filter shelf, chronological post list, and the soft-archived 2022 `#100DaysOfCode` drawer), while moving the **Active Weekly Dinner Plan** + **Recipe Catalog** to `/recipes/` (`kitchen` in the top nav).
- **Palette button with live mini-previews:** Provide a top-bar palette button opening a 5-theme picker with CSS mini-thumbnails, persisted in `localStorage` (`hawzy-theme`) with zero flash of unstyled content (FOUC).
- **3-skill blog writing pipeline in `.agents/skills/`:** Build `blog-voice` (including a copy-paste Gemini Web Personal Intelligence `@Gmail`/`@Docs` voice-extraction prompt), `blog-research` (cross-repo fact extraction from `c:\github\agy\<project>`), and `blog-author` (post + Twitter thread drafting + `scripts/audit_posts.py` + zero-context Editorial/Voice critic).
- **Draft Relaunch Post #1:** Produce the first relaunch post (*Redesigning My Blog in Antigravity: Jekyll, Visual View Loops, and Spec-Driven Subagents*) and its companion Twitter thread using the new pipeline, keeping recipe-specific critic/script deep dives reserved for Post #2.

### Non-Goals
- **No external runtime dependencies:** No npm frontend frameworks, no third-party Python packages (stdlib only), and no custom Jekyll Ruby plugins unsupported by GitHub Pages.
- **No changes to B2A recipe/menu JSON contracts:** `/api/recipes.json`, `/api/weekly-menu.json`, `/llms.txt`, and the 7 modular `recipe-*` skills remain intact.
- **No resurrection of 2022 `#100DaysOfCode` posts:** The 17 archived 2022 posts stay soft-archived (`archived: true`, `noindex`, hidden from main feed/sitemap/search, accessible via the collapsible archive drawer).

### Anti-Goals (Failure Conditions Even If Technically Working)
- **Cringe or try-hard branding:** No slogans like *"Hawzy Labs"* or *"Hawzy on Automation"* in the masthead; no heavy `// TRANSMISSION_LOG :: OPERATOR_DOSSIER` roleplay chrome on the blog hub.
- **Invented technical claims or AI-slop prose:** Every command, file path, test count, or metric in a blog post must trace to `_drafts/posts/<slug>/facts.md` or `notes.md` (or be flagged `TODO-source`). Banned AI filler phrases (`delve`, `testament to`, `it's not just X—it's Y`, `tapestry`, `buckle up`, etc.) must fail `audit_posts.py`.
- **Fake Windows prompt paths in headers:** Powerline/pill headers use clean `hawzy` / `~/blog` / `main` segments rather than long `C:\github\...` paths.

---

## 3. Constraints

1. **Git Safety Invariant (`AGENTS.md` §3):** Autonomous agents must **NEVER** run `git push`. All commits stay strictly local on `feat/agentic-recipe-blog`.
2. **Python 3 Standard Library Only:** `.agents/skills/blog-author/scripts/audit_posts.py` and all unit/E2E tests under `tests/` must use Python 3 stdlib only.
3. **Jekyll & Existing Test Suite Compatibility:** `bundle exec jekyll build` and `python -m unittest discover -s tests -v` must pass with 0 failures and 0 skipped tests when the local server is running. Existing E2E tests in `tests/test_e2e_verification.py` that assert the pre-relaunch room layout (`test_10`, `test_11`) must be updated to verify the new Layout C homepage, `/recipes/` kitchen hub, and 5-theme system while preserving all recipe, B2A API, JSON-LD, and draft-isolation checks.

---

## 4. Approaches Considered

1. **Approach 1 — Single All-in-One Skill (`blog-writer`):**
   - One skill file that reads raw notes, scans the repo, writes `_posts/YYYY-MM-DD-<slug>.md`, and drafts a tweet thread in one pass.
   - *Tradeoff:* Fast to write, but mixes fact extraction and prose drafting in one context window and lacks a deterministic script check. Rejected.
2. **Approach 2 — 3-Skill Pipeline (`blog-voice`, `blog-research`, `blog-author`) + `audit_posts.py` (Selected):**
   - Separates voice profiling (`blog-voice`), verified cross-repo fact extraction (`blog-research`), and prose + social drafting + deterministic auditing (`blog-author` + `audit_posts.py` + 1 zero-context Editorial/Voice critic subagent).
   - *Why chosen:* Prevents hallucinated project details, enforces the author's voice without 7-skill ceremony, and gives Post #1 a clean blog-specific verification script to showcase.
3. **Approach 3 — Full 6-Skill Mirror of the Recipe Pipeline:**
   - Separate skills and multi-round `review-r1.md` diffing for every blog post.
   - *Tradeoff:* Too much ceremony for blog posts. Rejected.

---

## 5. Detailed Design

### 5.1 Sub-project A: Site Identity, Layout C & 5-Theme System

#### Configuration & Metadata (`_config.yml` & `_data/navigation.yml`)
- **Site Identity (`_config.yml`):**
  - `title: "hawzy"`
  - `masthead_title: "hawzy"`
  - `subtitle: ""` (empty—no slogan in the header)
  - `name: "Nick Hasenoehrl (hawzy)"`
  - `description: "Code, AI agents, and home automation projects by hawzy."`
  - `twitter.username: "hawzy"` (enables Twitter/X summary card meta tags via `_includes/seo.html`)
- **Top Navigation (`_data/navigation.yml`):**
  - `projects` → `/projects/`
  - `kitchen` → `/recipes/`
  - `about` → `/about/`
  - `@hawzy` → `https://x.com/hawzy`
  - Plus the **Palette Theme Button** and **Search Toggle** inside `_includes/masthead.html`.

#### Five Themes & Header Wordmark Variants
The theme system is controlled by `document.documentElement.dataset.theme` (`"gruvbox" | "telemetry" | "catppuccin" | "kitchen" | "paper"`).
- **Default theme resolution (inline `<script>` in `_includes/head/custom.html` before paint):**
  1. Read `localStorage.getItem("hawzy-theme")`. If it is one of the 5 valid theme IDs, apply it.
  2. Otherwise, read `document.documentElement.dataset.defaultTheme` (set to `"kitchen"` on `/recipes/` and `layout: recipe` pages, and `"gruvbox"` on all other pages).
  3. Set `document.documentElement.dataset.theme` and update `<meta name="theme-color">`.

| Theme ID | Mode | Palette (`--hz-bg` / `--hz-surface` / `--hz-text` / `--hz-heading` / `--hz-accent` / `--hz-accent-2`) | Fonts (`--hz-head-font` / `--hz-body-font` / `--hz-mono`) | Header Wordmark Variant (`.hz-brand`) | Syntax Highlighting (`--syn-kw` / `--syn-fn` / `--syn-ty` / `--syn-st` / `--syn-cm`) |
|---|---|---|---|---|---|
| **`gruvbox`** *(default on blog/home)* | Warm Dark (Antigravity editor preset) | `#141617` / `#1D2021` / `#D4BE98` / `#DDC7A1` / `#E78A4E` / `#D8A657` | Inter/system sans / Inter/system sans / `JetBrains Mono` | **Rounded diamond pills:** `hawzy` (`#E78A4E`), `~/blog` (`#D8A657`), `main` (`#A9B665`) | `#EA6962` / `#A9B665` / `#D8A657` / `#A9B665` / `#7C6F64` |
| **`telemetry`** | Cool Dark | `#080C14` / `#0E1525` / `#CBD5E1` / `#F1F5F9` / `#38BDF8` / `#FBBF24` + subtle cyan radial glow | Inter/system sans / Inter/system sans / `JetBrains Mono` | **Plain monospace + blinking bar cursor (`\|`):** `hawzy` + `.hz-caret` (`2px` wide vertical bar, `1.06s` step blink) | `#F472B6` / `#38BDF8` / `#FBBF24` / `#34D399` / `#64748B` |
| **`catppuccin`** | Pastel Dark (Mocha) | `#1E1E2E` / `#181825` / `#BAC2DE` / `#CDD6F4` / `#CBA6F7` / `#A6E3A1` + pastel gradient top border on featured card | `JetBrains Mono` / Inter/system sans / `JetBrains Mono` | **Powerline triangular arrows:** `hawzy` (`#F5C2E7`) ▸ `~/blog` (`#CBA6F7`) ▸ `main ✓` (`#89B4FA`) | `#CBA6F7` / `#89B4FA` / `#F9E2AF` / `#A6E3A1` / `#6C7086` |
| **`kitchen`** *(default on `/recipes/`)* | Warm Light | `#FAF7F2` / `#FFFFFF` / `#44403C` / `#1C1917` / `#C84B31` / `#9A6B1F` | `Fraunces` serif / `Plus Jakarta Sans` / `JetBrains Mono` | **Serif wordmark + blinking bar cursor (`\|`):** `hawzy` in `Fraunces` + `.hz-caret` | `#C84B31` / `#3F6B4E` / `#9A6B1F` / `#5B7A2E` / `#A8A29E` |
| **`paper`** | Stark Light | `#FFFFFF` / `#FFFFFF` / `#24292F` / `#1F2328` / `#1A7F37` / `#0E7490` | `JetBrains Mono` / system sans / `JetBrains Mono` | **`robbyrussell` prompt:** `➜` (`#1A7F37`) `hawzy` (`#0E7490`) `git:(main)` (`#1D4ED8` / `#B91C1C`) | `#CF222E` / `#8250DF` / `#953800` / `#0A3069` / `#6E7781` |

#### Palette Popover Component (`_includes/masthead.html` + `assets/css/main.scss`)
- A compact `<button class="hz-theme-btn" aria-label="Change color theme" aria-expanded="false">` in the masthead showing a line-art palette SVG icon and a `9px` dot in `var(--hz-accent)`.
- Clicking toggles `<div class="hz-theme-menu" role="menu">` containing the 5 options (`gruvbox`, `telemetry`, `catppuccin`, `kitchen`, `paper`), each with a `50x30px` CSS `.hz-theme-mini` preview swatch, theme title, and 2–3 word subtitle (`warm dark · rounded pills`, `cool navy · blinking cursor`, `pastel dark · powerline`, `warm light · serif`, `stark light · robbyrussell ➜`).
- Clicking an option or pressing `Escape` / clicking outside closes the popover.

#### Page Routes & Layouts
1. **Homepage (`/`, `index.md`) — Layout C:**
   - Uses a shared `_includes/blog-hub.html` partial so `/` and `/blog/` stay synchronized.
   - **Featured Latest Post Card (`.hz-feature-card`):** Displays the newest non-archived post (`where_exp: "item", "item.archived != true"`), with eyebrow tags (`Latest · #tag1 · #tag2`), linked title, and excerpt. (If zero non-archived posts exist, shows a fallback card).
   - **Project Chips Shelf (`.hz-project-shelf`):** Clickable pills linking to `/projects/#<slug>` or tag filters: `blog-relaunch`, `dinner-planner` (additional projects added as posts are published).
   - **Chronological Post List (`.hz-post-list`):** Clean `YYYY-MM-DD` tabular date + linked post title for all remaining non-archived posts.
   - **Collapsible 2022 Archive Drawer (`.scifi-archive-drawer` / `.hz-archive-drawer`):** Retains `<details class="scifi-archive-drawer">` at the bottom with `// 2022 ARCHIVE — 17 logs (#100DaysOfCode)` so existing archive links and E2E archive checks continue working.
2. **Kitchen Hub (`/recipes/`, `recipes/index.md`):**
   - Houses the **Active Weekly Dinner Plan** (`weekly-menu-container` moved from `index.md`) at the top, followed by the **From the Recipe Box** catalog grid (`{% include recipe-catalog-grid.html %}`).
   - Sets `surface: kitchen` (`data-default-theme="kitchen"`), while respecting `localStorage.getItem("hawzy-theme")` when the user switches themes.
3. **Projects Page (`/projects/`, `_pages/projects.md`):**
   - Structured project index with anchor cards (`#blog-relaunch`, `#dinner-planner`) summarizing each published `c:\github\agy` project, its stack, and links to related posts.
4. **Post Page (`_layouts/single.html` for posts):**
   - Replaces heavy `RETURN_TO_LOGS` / `// TRANSMISSION_LOG` text with clean Layout C post header: post title, `YYYY-MM-DD · N min read · #tag1 #tag2` metadata line, and body prose styled by the active theme's CSS custom properties (`--hz-*` and `--syn-*`).

---

### 5.2 Sub-project B: 3-Skill Blog Writing Pipeline (`.agents/skills/`)

All three skills live in `c:\github\agy\recipes\.agents\skills\` and store per-post working artifacts in `_drafts/posts/<slug>/` (which is already excluded from Jekyll publishing).

```
.agents/skills/
  blog-voice/
    SKILL.md
    voice-profile.md
    prompts/
      gemini-personal-intelligence-handoff.md
  blog-research/
    SKILL.md
  blog-author/
    SKILL.md
    scripts/
      audit_posts.py
_drafts/posts/<slug>/
  notes.md            # Human author's raw brain dump / quips / stream-of-consciousness
  facts.md            # Verified repo facts, commit hashes, metrics, file paths, commands
  twitter-thread.md   # Companion X/Twitter hook tweet + 3-6 tweet thread
  review.md           # Zero-context Editorial/Voice critic report + audit_posts.py status
```

#### Skill 1: `blog-voice` (`.agents/skills/blog-voice/`)
- **Purpose:** Maintains `.agents/skills/blog-voice/voice-profile.md`—the authoritative style guide for Nick (`hawzy`)'s writing voice—and provides `.agents/skills/blog-voice/prompts/gemini-personal-intelligence-handoff.md`.
- **Gemini Web Personal Intelligence Handoff Prompt (`prompts/gemini-personal-intelligence-handoff.md`):**
  - Ready-to-paste prompt for Gemini Web (`@Gmail`, `@Google Docs`, `@Google Drive`) that instructs Gemini to sample Nick's sent casual/technical emails and notes and extract:
    1. Sentence length distribution and paragraph pacing
    2. Humor style, self-deprecating asides, and parenthetical quips
    3. How technical problems and frustrations are introduced
    4. Transition phrases and sign-offs actually used
    5. "Anti-voice" patterns (words/openers Nick never uses)
    formatted as a drop-in YAML/Markdown update to `voice-profile.md`.
- **Initial Baseline `voice-profile.md`:**
  - Seeded immediately from Nick's existing writing and conversation style:
    - Pragmatic, first-person builder voice ("I wanted X because Y was annoying me").
    - Short punchy sentences mixed with concrete technical specifics; parenthetical dry asides.
    - Never salesy, never breathless, never roleplaying a sci-fi operator.
    - **Banned AI-slop list (enforced by `audit_posts.py`):** `delve`, `delving`, `tapestry`, `testament to`, `buckle up`, `game-changer`, `game changer`, `in today's fast-paced`, `let's dive in`, `without further ado`, `it's not just`, `unleash`, `supercharge`, `symphony`, `realm of`.

#### Skill 2: `blog-research` (`.agents/skills/blog-research/`)
- **Purpose:** Turns `_drafts/posts/<slug>/notes.md` (the human brain dump) + one or more project paths (`c:\github\agy\<project>`) into `_drafts/posts/<slug>/facts.md`.
- **Workflow:**
  1. Reads `_drafts/posts/<slug>/notes.md` (or creates it from the user's inline prompt if they pasted their brain dump directly in chat).
  2. Inspects the target project directory (`git log`, `README.md`, `docs/superpowers/specs/`, `docs/superpowers/plans/`, test files, scripts) and extracts verified facts with `[f1]`, `[f2]` citations (exact filenames, line counts, test counts, CLI flags, commit messages, error cases).
  3. Flags any claim from `notes.md` that cannot be verified in the repo as `TODO-confirm-with-author` so the author can clarify before or during review.

#### Skill 3: `blog-author` + `scripts/audit_posts.py` (`.agents/skills/blog-author/`)
- **Purpose:** Drafts `_posts/YYYY-MM-DD-<slug>.md` and `_drafts/posts/<slug>/twitter-thread.md` from `notes.md` + `facts.md` + `voice-profile.md`, runs `scripts/audit_posts.py`, and dispatches 1 zero-context Editorial/Voice critic subagent.
- **Deterministic Post Auditor (`.agents/skills/blog-author/scripts/audit_posts.py`):**
  - Uses Python 3 stdlib only.
  - Skips archived 2022 posts (`archived: true`).
  - Validates every non-archived post in `_posts/` (or a specific post passed via `--post <path>`):
    1. **Frontmatter schema:** Requires `title`, `date` (or `YYYY-MM-DD-` filename prefix), `categories`, `tags` (`>=1` tag from the canonical tag taxonomy or lowercase slug format `^[a-z0-9-]+$`), `excerpt` (`20..220` chars for Twitter/X card descriptions).
    2. **Zero banned AI-slop phrases:** Scans prose outside fenced code blocks against the banned phrase list in `voice-profile.md`.
    3. **Zero unresolved `TODO-source` / `TODO-confirm` markers:** Fails if any `TODO-` marker remains in a published post.
    4. **Internal link & asset integrity:** Verifies relative internal links (`/recipes/...`, `/projects/...`, `/assets/...`) resolve in the repo.
    5. **Companion Twitter thread check (when `--dossier _drafts/posts/<slug>` is provided):** Verifies `twitter-thread.md` exists and every numbered tweet (`1/`, `2/`, ...) is `<= 280` characters (counting URLs as 23 chars per X's `t.co` wrapper rule).

---

### 5.3 Sub-project C: Relaunch Post #1 & 5-Post Backlog

#### Relaunch Post #1 (To Be Drafted & Published in This Build)
- **File:** `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md`
- **Dossier:** `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/{notes.md,facts.md,twitter-thread.md,review.md}`
- **Tags:** `["antigravity", "jekyll", "superpowers", "view-loops", "themes"]`
- **Scope & Structure:**
  1. **Why relaunch now:** Moving from a single-purpose recipe/2022 log site to a general home-automation & coding blog (`hawzy`), and why static Jekyll on GitHub Pages is still ideal when agents write and maintain the templates.
  2. **How Antigravity + Superpowers skills work together:** Using `brainstorming`, `writing-plans`, and `subagent-driven-development` instead of one-shot prompting.
  3. **The Visual Companion View Loop:** How the `brainstorming` visual server let us iterate live in a browser tab from initial homepage wireframes (Krebs vs. `jvns.ca` vs. `blog.fsck.com` vs. Hybrid C) to a palette switcher with 5 distinct editor and Oh My Posh themes (`Gruvbox` from Antigravity settings, `Telemetry`, `Catppuccin`, `Kitchen`, `Paper`).
  4. **The Verification & Code Review Loop:** How `spec-reviewer` and `code-reviewer` subagents plus deterministic Python stdlib scripts (`test_e2e_verification.py` against `bundle exec jekyll serve` and `audit_posts.py`) keep the site honest.
  5. **What's next:** Teaser for Post #2 (the 7-skill Agentic Kitchen & 3-critic recipe pipeline); additional project posts tracked in private `blog-ops/BACKLOG.md` until published.

#### Backlog Stubs Recorded in Private `c:\github\agy\blog-ops\BACKLOG.md`
1. **Post #2:** *The Agentic Kitchen: Deep-Research PDFs, a 3-Critic Panel & Automated Grocery Carts* (`recipes` repo: `audit_recipes.py`, `review_report.py`, `consolidate_menu.py`, `generate_recipe_visuals.py`, `/api/*.json`, `/llms.txt`)
2. Future hobby & home-automation posts are kept in private `blog-ops` until published.

---

## 6. Builder Decisions & Defaults (Explicitly Marked)

The following defaults were chosen by the agent during design and can be overridden by the human author at any time:
- **Default Theme Per Surface:** `gruvbox` is the default theme on `/`, `/blog/`, `/projects/`, `/about/`, and post pages; `kitchen` is the default theme on `/recipes/` and individual recipe pages, unless the visitor has explicitly selected a theme in the palette menu (`localStorage["hawzy-theme"]`).
- **Kitchen Hub Location:** Moving the homepage to Layout C moves the **Active Weekly Dinner Plan** section from `/` to the top of `/recipes/` (`recipes/index.md`) so the `kitchen` nav link gives the complete kitchen experience on one page.
- **Canonical Post URL Pattern:** New 2026+ posts live in `_posts/YYYY-MM-DD-<slug>.md` with `categories: [Blog]` (rendering at `/blog/<slug>/` per `_config.yml`'s `permalink: /:categories/:title/`), while soft-archived 2022 posts retain their explicit frontmatter permalinks (`/blog/2022/...`) so zero legacy URLs break.
- **Post #1 Author Brain Dump:** The initial `notes.md` for Post #1 will be seeded from the user's statements in this conversation, and the user can add or tweak any quips when reviewing the Post #1 draft.
