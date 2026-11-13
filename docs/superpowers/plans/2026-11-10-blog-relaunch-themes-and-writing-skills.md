---
layout: single
title: "Blog Relaunch, 5-Theme Identity & Agentic Writing Skills Implementation Plan"
surface: blog
sitemap: false
search: false
comments: false
---

# Blog Relaunch, 5-Theme Identity & Agentic Writing Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Relaunch `hawzy.github.io` with a Layout C blog-first homepage, a 5-theme palette switcher (`gruvbox`, `telemetry`, `catppuccin`, `kitchen`, `paper`) with Oh My Posh/editor header variants, a 3-skill blog writing pipeline (`blog-voice`, `blog-research`, `blog-author` + `audit_posts.py`), and Relaunch Post #1.

**Architecture:** Jekyll templates (`index.md`, `_pages/blog.md`, `recipes/index.md`, `_pages/projects.md`, `_includes/masthead.html`, `_includes/blog-hub.html`) and CSS custom properties on `html[data-theme="<id>"]` in `assets/css/main.scss` drive the 5-theme UI with an inline pre-paint script in `_includes/head/custom.html`. Three modular Antigravity skills under `.agents/skills/blog-{voice,research,author}/` plus a Python 3 stdlib auditor (`audit_posts.py`) govern post authoring and verify Relaunch Post #1.

**Tech Stack:** Jekyll 4 / Minimal Mistakes (`dirt` skin base), SCSS + CSS Custom Properties, Vanilla ES6 JS (`localStorage`), Python 3.10+ Standard Library (`unittest`, `re`, `pathlib`, `argparse`, `json`).

**Spec:** `docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.md`

## Global Constraints

- **Git Safety Invariant (`AGENTS.md` §3):** Autonomous agents must **NEVER** run `git push`. All commits stay strictly local on `feat/agentic-recipe-blog`.
- **Python 3 Standard Library Only:** `.agents/skills/blog-author/scripts/audit_posts.py` and all test files in `tests/` must use Python 3 stdlib only (no third-party pip packages).
- **Zero B2A / Recipe Regression:** `/api/recipes.json`, `/api/weekly-menu.json`, `/llms.txt`, and all 5 recipes in `_recipes/` (`audit_recipes.py`) must remain 100% intact and passing.
- **Anti-Cringe & Anti-Slop Rules:** Masthead title is lowercase `hawzy` with empty `subtitle: ""`; no `// TRANSMISSION_LOG` or `RETURN_TO_LOGS` roleplay text on active blog pages; no banned AI filler phrases (`delve`, `tapestry`, `testament to`, `buckle up`, `game-changer`, `it's not just`, `unleash`, `supercharge`, `symphony`, `realm of`) in published posts.

## Review Focus

1. **Banned phrase inside fenced code block vs. prose (`audit_posts.py`):** A post quoting banned AI phrases inside a ```markdown or ```python code block (or inline backticks documenting the rule) must NOT fail the banned-phrase check, whereas the same phrase in normal paragraph prose MUST fail.
2. **X/Twitter `t.co` URL length accounting (`audit_posts.py`):** A tweet containing a long `https://hawzy.github.io/blog/rebuilding-my-blog-with-antigravity-and-view-loops/` URL (81 chars raw, 23 chars via `t.co`) must have its URL counted as 23 characters so valid tweets aren't falsely rejected, while a tweet exceeding 280 adjusted chars must fail.
3. **Archived 2022 posts exemption (`audit_posts.py`):** The 17 soft-archived 2022 `#100DaysOfCode` posts (`archived: true`) lack `excerpt` frontmatter and must be skipped by `audit_posts.py` when scanning `_posts/`, while any non-archived post missing `excerpt` or `tags` must fail.
4. **Invalid or tampered `localStorage["hawzy-theme"]` value (`_includes/head/custom.html`):** If `localStorage.getItem("hawzy-theme")` is `null` or an unknown string (`"invalid-theme"`), the pre-paint script must fall back cleanly to `document.documentElement.dataset.defaultTheme` (`"gruvbox"` or `"kitchen"`).
5. **Homepage and `/blog/` with 0 vs. `>=1` non-archived posts (`_includes/blog-hub.html`):** When `active_posts` has `>=1` post (after Post #1 is added), `.hz-feature-card` renders the newest post and `.hz-post-list` renders remaining posts without duplicating the featured post; `.scifi-archive-drawer` still renders the 17 archived 2022 logs.

---

### Task 1: Site Identity, Navigation, Kitchen Hub Relocation & Layout C Templates

**Files:**
- Modify: `_config.yml:19-25,100-120`
- Modify: `_data/navigation.yml`
- Modify: `_layouts/default.html`
- Modify: `_layouts/single.html:28-44`
- Create: `_includes/blog-hub.html`
- Modify: `index.md`
- Modify: `_pages/blog.md`
- Modify: `recipes/index.md`
- Create: `_pages/projects.md`
- Modify: `_pages/about.md`
- Test: `tests/test_e2e_verification.py`

**Interfaces:**
- Consumes: `site.data.weekly_menu`, `site.recipes`, `site.posts`
- Produces:
  - `<html data-default-theme="kitchen|gruvbox">` in `_layouts/default.html`
  - `_includes/blog-hub.html` rendering `.hz-hub`, `.hz-feature-card`, `.hz-project-shelf`, `.hz-post-list`, and `<details class="scifi-archive-drawer">`
  - `/recipes/` containing both `.weekly-menu-container` and `.recipes-catalog-container`
  - `/projects/` containing `#blog-relaunch` and `#dinner-planner`

- [ ] **Step 1: Update `test_10` in `tests/test_e2e_verification.py` to assert the new identity, routes, and Kitchen relocation**

Update `TestEndToEndVerification.test_10_dual_surface_room_separation_and_themes` in `tests/test_e2e_verification.py` to assert:
```python
        home_html = (REPO_ROOT / "_site" / "index.html").read_text(encoding="utf-8")
        self.assertIn("surface-blog", home_html)
        self.assertIn('data-default-theme="gruvbox"', home_html)
        self.assertIn("hz-hub", home_html)
        self.assertIn("hz-project-shelf", home_html)
        self.assertIn("scifi-archive-drawer", home_html)

        recipes_html = (REPO_ROOT / "_site" / "recipes" / "index.html").read_text(encoding="utf-8")
        self.assertIn("surface-kitchen", recipes_html)
        self.assertIn('data-default-theme="kitchen"', recipes_html)
        self.assertIn("Active Weekly Dinner Plan", recipes_html)
        self.assertIn("recipe-catalog-card", recipes_html)
        for slug in self.expected_catalog_slugs:
            self.assertIn(f"/recipes/{slug}/", recipes_html)

        projects_html = (REPO_ROOT / "_site" / "projects" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="blog-relaunch"', projects_html)
        self.assertIn('id="dinner-planner"', projects_html)
```

- [ ] **Step 2: Run `test_10` to verify it fails before implementation**

Run: `python -m unittest tests.test_e2e_verification.TestEndToEndVerification.test_10_dual_surface_room_separation_and_themes -v`
Expected: FAIL (`surface-blog` not in `_site/index.html`)

- [ ] **Step 3: Update `_config.yml`, `_data/navigation.yml`, `_layouts/default.html`, `_layouts/single.html`, `_includes/blog-hub.html`, `index.md`, `_pages/blog.md`, `recipes/index.md`, `_pages/projects.md`, and `_pages/about.md`**

- In `_config.yml`:
  - `title: "hawzy"`, `masthead_title: "hawzy"`, `subtitle: ""`, `name: "Nick Hasenoehrl (hawzy)"`, `description: "Code, AI agents, and home automation projects by hawzy."`, `twitter:\n  username: "hawzy"`.
- In `_data/navigation.yml`:
  ```yaml
  main:
    - title: "projects"
      url: /projects/
    - title: "kitchen"
      url: /recipes/
    - title: "about"
      url: /about/
    - title: "@hawzy"
      url: https://x.com/hawzy
  ```
- In `_layouts/default.html`:
  - Set `is_kitchen_surface = true` when `page.collection == 'recipes' or page.surface == 'kitchen'`, and `is_blog_surface = true` otherwise.
  - Add `data-default-theme="{% if is_kitchen_surface %}kitchen{% else %}gruvbox{% endif %}"` on `<html>`.
  - Keep `surface-blog` vs `surface-kitchen` class on `<body>`.
- In `_layouts/single.html`:
  - Change `<a href="{{ '/blog/' | relative_url }}" class="scifi-back-link">&larr; // RETURN_TO_LOGS</a>` to `<a href="{{ '/' | relative_url }}" class="scifi-back-link">&larr; all posts</a>` and format post date as `{{ page.date | date: "%Y-%m-%d" }}`.
- Create `_includes/blog-hub.html`:
  - Partition `visible_posts` (`hidden != true`) into `active_posts` (`archived != true`) and `archived_posts` (`archived == true`).
  - If `active_posts.size > 0`: render `first_post = active_posts.first` inside `<article class="hz-feature-card">` with `.hz-eyebrow` (`Latest{% for tag in first_post.tags limit:3 %} · #{{ tag }}{% endfor %}`), `<h2 class="hz-feature-card__title"><a href="{{ first_post.url | relative_url }}">{{ first_post.title }}</a></h2>`, and `<p class="hz-feature-card__excerpt">{{ first_post.excerpt | strip_html | strip_newlines }}</p>`.
  - If `active_posts.size == 0`: render `<section class="scifi-empty-state"><p class="scifi-empty-state__title">First transmission incoming</p></section>`.
  - Render `<nav class="hz-project-shelf" aria-label="Projects">` with links to `/projects/#blog-relaunch` and `/projects/#dinner-planner`.
  - Render `<ul class="hz-post-list">` for `active_posts` (`offset: 1` when `active_posts.size > 1`, plus also include `first_post` in `.hz-post-list` or list all `active_posts` chronologically with `<span class="hz-post-list__date">{{ post.date | date: "%Y-%m-%d" }}</span>` and `<a href="{{ post.url | relative_url }}">{{ post.title }}</a>`).
  - Preserve `<details class="scifi-archive-drawer">` at the bottom with `<summary class="scifi-archive-drawer__summary">// 2022 ARCHIVE &mdash; {{ archived_posts.size }} logs (#100DaysOfCode)</summary>`.
- Update `index.md` (`surface: blog`, `classes: [wide, surface-blog]`, `{% include blog-hub.html %}`) and `_pages/blog.md` (`{% include blog-hub.html %}`).
- Update `recipes/index.md` (`surface: kitchen`, `classes: [wide, kitchen-home, kitchen-recipes]`) to include the `<section class="weekly-menu-container" ...>` block above `<section class="recipes-catalog-container" ...>{% include recipe-catalog-grid.html %}</section>`.
- Create `_pages/projects.md` (`permalink: /projects/`, `title: "Projects"`, `surface: blog`) with project cards for `#blog-relaunch` and `#dinner-planner`.
- Update `_pages/about.md` (`title: "About"`) to reflect the new `/` (blog & projects) and `/recipes/` (kitchen & weekly menu) routes.

- [ ] **Step 4: Build Jekyll and verify `test_01` through `test_09` and `test_12` still pass**

Run: `$env:PATH = "C:\Ruby33-x64\bin;" + $env:PATH; bundle exec jekyll build`
Expected: `done in ... seconds` with exit code 0.

---

### Task 2: 5-Theme CSS System, Header Wordmark Variants & Palette Switcher Popover

**Files:**
- Modify: `_includes/head/custom.html`
- Modify: `_includes/masthead.html`
- Modify: `assets/css/main.scss`
- Modify: `tests/test_e2e_verification.py`

**Interfaces:**
- Consumes: `html[data-default-theme]` from `_layouts/default.html`
- Produces:
  - `html[data-theme="gruvbox|telemetry|catppuccin|kitchen|paper"]` set pre-paint in `_includes/head/custom.html`
  - `.hz-brand` with 5 header variants (`.hv-diamond`, `.hv-plain`, `.hv-powerline`, `.hv-serif`, `.hv-robby`) and `.hz-theme-picker` / `.hz-theme-btn` / `.hz-theme-menu` in `_includes/masthead.html`
  - 5 theme CSS blocks and `.hz-hub` / `.hz-feature-card` / `.hz-project-shelf` / `.hz-post-list` / `.hz-project-grid` styles in `assets/css/main.scss`

- [ ] **Step 1: Add 5-theme, header-variant, and FOUC-fallback assertions to `test_10` and `test_11` in `tests/test_e2e_verification.py`**

In `tests/test_e2e_verification.py`:
- In `test_10_dual_surface_room_separation_and_themes`:
  - Assert `home_html` contains `hz-theme-btn`, `hz-theme-menu`, `data-theme-opt="gruvbox"`, `data-theme-opt="telemetry"`, `data-theme-opt="catppuccin"`, `data-theme-opt="kitchen"`, `data-theme-opt="paper"`, `hv-diamond`, `hv-plain`, `hv-powerline`, `hv-serif`, `hv-robby`, and `localStorage.getItem("hawzy-theme")`.
  - Assert `css_lower` (`_site/assets/css/main.css`) contains `[data-theme="gruvbox"]` (or `[data-theme=gruvbox]`), `#141617`, `#080c14`, `#1e1e2e`, `#faf7f2`, `#ffffff`, `.hz-feature-card`, and `.hz-theme-menu`.
  - Assert `/projects/` is included in the live-server HTTP 200 route loop (`["/recipes/", "/blog/", "/projects/", "/about/"]`).
- In `test_11_blog_soft_archive`:
  - Update the post header check on `sample_post` (`_site/blog/2022/hello-world.html`) to assert `all posts` instead of `RETURN_TO_LOGS`, and allow `.hz-feature-card` when active posts exist.

- [ ] **Step 2: Run `test_10` and `test_11` to verify they fail before CSS/masthead implementation**

Run: `python -m unittest tests.test_e2e_verification.TestEndToEndVerification.test_10_dual_surface_room_separation_and_themes tests.test_e2e_verification.TestEndToEndVerification.test_11_blog_soft_archive -v`
Expected: FAIL (`hz-theme-btn` not found in `home_html`)

- [ ] **Step 3: Implement pre-paint theme script in `_includes/head/custom.html`, brand variants + palette popover in `_includes/masthead.html`, and 5-theme CSS in `assets/css/main.scss`**

- In `_includes/head/custom.html`:
  ```html
  <script>
    (function () {
      var valid = { gruvbox: "#141617", telemetry: "#080C14", catppuccin: "#1E1E2E", kitchen: "#FAF7F2", paper: "#FFFFFF" };
      var root = document.documentElement;
      var saved = null;
      try { saved = localStorage.getItem("hawzy-theme"); } catch (e) {}
      var def = root.getAttribute("data-default-theme") || "gruvbox";
      var chosen = (saved && valid[saved]) ? saved : (valid[def] ? def : "gruvbox");
      root.setAttribute("data-theme", chosen);
    })();
  </script>
  ```
- In `_includes/masthead.html`:
  - Inside `<a class="site-title hz-brand" href="{{ '/' | relative_url }}" aria-label="hawzy home">`, output the 5 `.hv` spans:
    - `<span class="hv hv-diamond"><span class="hv-seg hv-seg--1">hawzy</span><span class="hv-seg hv-seg--2">~/blog</span><span class="hv-seg hv-seg--3">main</span></span>`
    - `<span class="hv hv-plain">hawzy<i class="hz-caret" aria-hidden="true"></i></span>`
    - `<span class="hv hv-powerline"><span class="hv-seg hv-seg--1">hawzy</span><span class="hv-seg hv-seg--2">~/blog</span><span class="hv-seg hv-seg--3">main &#10003;</span></span>`
    - `<span class="hv hv-serif">hawzy<i class="hz-caret" aria-hidden="true"></i></span>`
    - `<span class="hv hv-robby"><span class="hv-arrow">&rarr;</span><span class="hv-dir">hawzy</span><span class="hv-git">git:(<span class="hv-br">main</span>)</span></span>`
  - Before the search toggle button, render `<div class="hz-theme-picker">` with `<button class="hz-theme-btn" type="button" aria-label="Select color theme" aria-expanded="false">` (palette SVG + `<span class="hz-theme-dot"></span>`) and `<div class="hz-theme-menu" role="menu">` with the 5 `.hz-theme-opt` buttons (`data-theme-opt="gruvbox|telemetry|catppuccin|kitchen|paper"`), plus a compact inline script that binds click/Escape/outside-click, updates `document.documentElement.setAttribute("data-theme", t)`, writes `localStorage.setItem("hawzy-theme", t)`, and updates `.is-active` on `.hz-theme-opt`.
- In `assets/css/main.scss`:
  - Map `html[data-theme="gruvbox"]`, `html[data-theme="telemetry"]`, `html[data-theme="catppuccin"]`, `html[data-theme="kitchen"]`, and `html[data-theme="paper"]` to both `--hz-*` and `--scifi-*` custom properties (plus `--syn-kw`, `--syn-fn`, `--syn-ty`, `--syn-st`, `--syn-cm`) and apply them to `body` (so switching themes works on both `surface-blog` and `surface-kitchen` pages).
  - Style `.hz-brand`, `.hv-diamond`, `.hv-plain`, `.hv-powerline`, `.hv-serif`, `.hv-robby`, `.hz-caret`, `.hz-theme-picker`, `.hz-theme-btn`, `.hz-theme-menu`, `.hz-hub`, `.hz-feature-card`, `.hz-project-shelf`, `.hz-post-list`, and `.hz-project-grid`.

- [ ] **Step 4: Rebuild Jekyll and run `test_e2e_verification.py`**

Run: `$env:PATH = "C:\Ruby33-x64\bin;" + $env:PATH; bundle exec jekyll build; python -m unittest tests/test_e2e_verification.py -v`
Expected: All tests in `test_e2e_verification.py` pass (except `test_07_git_safety_check` until committed).

- [ ] **Step 5: Commit Tasks 1 & 2 locally**

```powershell
git add _config.yml _data/navigation.yml _layouts/default.html _layouts/single.html _includes/head/custom.html _includes/masthead.html _includes/blog-hub.html index.md _pages/blog.md _pages/projects.md _pages/about.md recipes/index.md assets/css/main.scss tests/test_e2e_verification.py
git commit -m "feat(ui): launch Layout C homepage, /projects/ hub, and 5-theme palette switcher"
```

---

### Task 3: 3-Skill Blog Writing Pipeline (`blog-voice`, `blog-research`, `blog-author`) & `audit_posts.py`

**Files:**
- Create: `.agents/skills/blog-voice/SKILL.md`
- Create: `.agents/skills/blog-voice/voice-profile.md`
- Create: `.agents/skills/blog-voice/prompts/gemini-personal-intelligence-handoff.md`
- Create: `.agents/skills/blog-research/SKILL.md`
- Create: `.agents/skills/blog-author/SKILL.md`
- Create: `.agents/skills/blog-author/scripts/audit_posts.py`
- Modify: `AGENTS.md`
- Create: `tests/test_blog_pipeline.py`

**Interfaces:**
- Consumes: `_posts/*.md`, `_drafts/posts/<slug>/{notes.md,facts.md,twitter-thread.md,review.md}`, `.agents/skills/blog-voice/voice-profile.md`
- Produces:
  - `audit_posts.audit_post_file(post_path: Path, repo_root: Path, banned_phrases: list[str] | None = None) -> list[str]`
  - `audit_posts.audit_twitter_thread(thread_path: Path) -> list[str]`
  - `audit_posts.compute_tweet_length(text: str) -> int` (replaces `https?://\S+` with 23 chars per X `t.co` specification)
  - CLI: `python .agents/skills/blog-author/scripts/audit_posts.py [--post <path>] [--dossier <path>]` (exits 0 on pass, 1 on any error)

- [ ] **Step 1: Write the failing unit tests in `tests/test_blog_pipeline.py`**

Create `tests/test_blog_pipeline.py` covering:
- `test_blog_skills_frontmatter_and_voice_handoff_exist`: verifies `SKILL.md` frontmatter (`name`, `description`) for `blog-voice`, `blog-research`, `blog-author`, plus `.agents/skills/blog-voice/voice-profile.md` and `.agents/skills/blog-voice/prompts/gemini-personal-intelligence-handoff.md`.
- `test_audit_skips_archived_2022_posts`: verifies `audit_post_file` returns `[]` on `_posts/2022-01-01/2022-01-01-hello-world.md` (`archived: true`).
- `test_audit_flags_banned_slop_in_prose_but_allows_inside_code_blocks`: verifies a post containing `"Let's delve into this tapestry"` in paragraph text fails, whereas the same words inside a fenced ```block or inline `` `delve` `` code span pass.
- `test_audit_flags_missing_frontmatter_todo_markers_and_broken_links`: verifies missing `excerpt`/`tags`, lingering `TODO-source`, or broken `/assets/missing.png` link are reported.
- `test_twitter_thread_validator_uses_23_char_tco_url_accounting`: verifies a 265-char tweet containing an 85-char `https://hawzy.github.io/...` URL passes (`compute_tweet_length <= 280`), while a 295-char plain-text tweet fails.

- [ ] **Step 2: Run `tests/test_blog_pipeline.py` to verify it fails**

Run: `python -m unittest tests/test_blog_pipeline.py -v`
Expected: FAIL (missing `.agents/skills/blog-author/scripts/audit_posts.py`)

- [ ] **Step 3: Implement `blog-voice`, `blog-research`, `blog-author`, `audit_posts.py`, and update `AGENTS.md`**

- Create `.agents/skills/blog-voice/voice-profile.md` defining:
  - Core persona & tone (first-person pragmatic engineer, dry parenthetical humor, leads with the problem/annoyance and concrete outcomes).
  - Structural habits (short paragraphs, real terminal commands and file paths, honest about what broke in round 1).
  - Machine-readable `## Banned Phrases` bullet list (`- delve`, `- delving`, `- tapestry`, `- testament to`, `- buckle up`, `- game-changer`, `- game changer`, `- in today's fast-paced`, `- let's dive in`, `- without further ado`, `- it's not just`, `- unleash`, `- supercharge`, `- symphony`, `- realm of`).
- Create `.agents/skills/blog-voice/prompts/gemini-personal-intelligence-handoff.md` with the copy-paste `@Gmail` / `@Google Docs` / `@Google Drive` voice-extraction prompt and instructions for merging the output into `voice-profile.md`.
- Create `.agents/skills/blog-voice/SKILL.md`, `.agents/skills/blog-research/SKILL.md`, and `.agents/skills/blog-author/SKILL.md`.
- Implement `.agents/skills/blog-author/scripts/audit_posts.py` using Python 3 stdlib only (`re`, `sys`, `argparse`, `pathlib`). Strip fenced code blocks (` ```...``` `) and inline code (` `...` `) before running case-insensitive word-boundary checks for banned phrases.
- Document the 3-skill blog pipeline (`blog-voice`, `blog-research`, `blog-author` + `audit_posts.py`) in `AGENTS.md`.

- [ ] **Step 4: Run `tests/test_blog_pipeline.py` and verify all tests pass**

Run: `python -m unittest tests/test_blog_pipeline.py -v`
Expected: PASS (5/5 tests)

- [ ] **Step 5: Commit Task 3 locally**

```powershell
git add .agents/skills/blog-voice/ .agents/skills/blog-research/ .agents/skills/blog-author/ AGENTS.md tests/test_blog_pipeline.py
git commit -m "feat(skills): add blog-voice, blog-research, blog-author skills and audit_posts.py"
```

---

### Task 4: Relaunch Post #1 Dossier, Published Post, Twitter Thread & 5-Post Backlog

**Files:**
- Create: `_drafts/posts/BACKLOG.md`
- Create: `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/notes.md`
- Create: `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/facts.md`
- Create: `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/twitter-thread.md`
- Create: `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/review.md`
- Create: `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md`
- Modify: `tests/test_blog_pipeline.py`

**Interfaces:**
- Consumes: `audit_posts.py` from Task 3, Layout C & 5-theme system from Tasks 1–2
- Produces:
  - Published post `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md` rendered on `/` (in `.hz-feature-card`), `/blog/`, and `/blog/rebuilding-my-blog-with-antigravity-and-view-loops/`
  - Validated dossier `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/` and `_drafts/posts/BACKLOG.md`

- [ ] **Step 1: Add an E2E test in `tests/test_blog_pipeline.py` asserting Post #1 and its dossier pass `audit_posts.py`**

Add `test_relaunch_post_1_and_dossier_pass_audit` in `tests/test_blog_pipeline.py` asserting:
- `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md` exists and returns `[]` from `audit_post_file`.
- `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/twitter-thread.md` exists and returns `[]` from `audit_twitter_thread`.
- `_drafts/posts/BACKLOG.md` exists and lists Posts #1–#5.

- [ ] **Step 2: Run `test_relaunch_post_1_and_dossier_pass_audit` to verify it fails**

Run: `python -m unittest tests.test_blog_pipeline.TestBlogPipeline.test_relaunch_post_1_and_dossier_pass_audit -v`
Expected: FAIL (Post #1 not yet created)

- [ ] **Step 3: Create `_drafts/posts/BACKLOG.md`, the Post #1 dossier (`notes.md`, `facts.md`, `twitter-thread.md`, `review.md`), and `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md`**

- Create `_drafts/posts/BACKLOG.md` with the 5 planned posts and their target `c:\github\agy` repos.
- Create `notes.md` (capturing the user's raw intent and quips from this session) and `facts.md` (verified repo facts `[f1..f12]`: Jekyll 4 static build, `superpowers` skills `brainstorming` + `writing-plans` + `subagent-driven-development`, visual companion server loop, 5 themes `gruvbox`/`telemetry`/`catppuccin`/`kitchen`/`paper`, `audit_posts.py`, `test_e2e_verification.py`).
- Author `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md` in Nick's voice (`voice-profile.md`), covering:
  1. Why relaunch the blog around coding projects that automate real-life chores (and why "Hawzy's Kitchen & Code" got axed).
  2. Working inside Google Antigravity with composable skills (`brainstorming`, `writing-plans`, `subagent-driven-development`) on top of static Jekyll + GitHub Pages.
  3. The Visual Companion View Loop: iterating live in a browser tab from Krebs / `jvns.ca` / `blog.fsck.com` inspirations to Layout C and a 5-theme palette switcher pulling from Antigravity's `Gruvbox Material` preset and Oh My Posh prompt styles (`diamond`, `powerline`, `robbyrussell`).
  4. The Verification & Subagent Review Loop: how `spec-reviewer` and `code-reviewer` subagents plus deterministic Python stdlib scripts (`test_e2e_verification.py` and `audit_posts.py`) catch bugs before commit.
  5. What's next on the blog (teasing Post #2 on the 7-skill Agentic Kitchen & 3-critic recipe panel).
- Draft `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/twitter-thread.md` (5-tweet thread, each `<= 280` chars) and `review.md`.

- [ ] **Step 4: Run `audit_posts.py`, rebuild Jekyll, and run the entire test suite**

Run:
```powershell
$env:PATH = "C:\Ruby33-x64\bin;" + $env:PATH
python .agents/skills/blog-author/scripts/audit_posts.py --post _posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md --dossier _drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops
bundle exec jekyll build
```
Expected: `[PASS]` from `audit_posts.py` and clean Jekyll build.

- [ ] **Step 5: Commit Task 4 locally and run full `unittest` discovery**

```powershell
git add _drafts/posts/ _posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md tests/test_blog_pipeline.py
git commit -m "feat(blog): publish relaunch post #1, dossier, and 5-post backlog"
python -m unittest discover -s tests -v
```
Expected: All unit and E2E tests pass (`OK`, 0 failures, 0 skipped with local Jekyll server running).
