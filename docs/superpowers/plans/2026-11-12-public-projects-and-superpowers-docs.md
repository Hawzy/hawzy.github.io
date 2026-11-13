---
layout: single
title: "Public Projects Scope & Rendered Superpowers Docs Implementation Plan"
surface: blog
sitemap: false
search: false
comments: false
---

# Public Projects Scope & Rendered Superpowers Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restrict public projects on `hawzy.github.io` (both rendered UI and git-tracked files) to published work plus a recipes teaser, move the multi-post backlog to `c:\github\agy\blog-ops`, and render scrubbed `docs/superpowers/` specs and plans as clickable Jekyll pages linked from Post #1.

**Architecture:** `_pages/projects.md` and `_includes/blog-hub.html` are trimmed to `#blog-relaunch` and `#dinner-planner`, while `_drafts/posts/BACKLOG.md` moves to `c:\github\agy\blog-ops\BACKLOG.md` and all unannounced project references are scrubbed from tracked files. Removing `docs/` from `_config.yml` `exclude` and adding frontmatter to `docs/superpowers/**/*.md` renders them at `/docs/superpowers/.../*.html` using `layout: single` (`sitemap: false`, `search: false`), verified by `audit_posts.py` and `tests/`.

**Tech Stack:** Jekyll 4 / Minimal Mistakes, Liquid, YAML frontmatter, Python 3.10+ Standard Library (`unittest`, `subprocess`, `pathlib`, `re`).

**Spec:** `docs/superpowers/specs/2026-11-12-public-projects-and-superpowers-docs-design.md`

## Global Constraints

- **Git Safety Invariant (`AGENTS.md` §3):** Never run `git push`.
- **Python 3 Standard Library Only:** All auditor and test updates use Python 3 stdlib only.
- **Anti-Goals:** Do not index `docs/superpowers/` pages in `/sitemap.xml` or Lunr search; do not leave unannounced hobby/side-project slugs or private identifiers in any git-tracked file outside the allowlisted test list itself.

## Review Focus

1. **Jekyll raw-copy trap for frontmatter-less `docs/*.md` files:** In Jekyll, a regular `.md` file outside a collection is copied verbatim as raw Markdown instead of compiled to HTML unless it begins with `---` YAML frontmatter. Every `.md` file under `docs/superpowers/` must start with `---` frontmatter so `/docs/superpowers/.../*.html` actually renders in `layout: single`.
2. **`test_01_build_hygiene` rejecting `_site/docs`:** `tests/test_e2e_verification.py` currently lists `"_site/docs"` as prohibited. Updating `test_01` must allow `_site/docs/superpowers/` HTML output while verifying no raw `.md` files or prohibited directories leak.
3. **`sitemap.xml` and Lunr search exclusion for `docs/superpowers/`:** Rendering `docs/superpowers/` pages must not pollute `_site/sitemap.xml` or `_site/assets/js/lunr/lunr-store.js`; tests must assert `sitemap: false` and `search: false` keep them out of both.
4. **`audit_posts.py` internal link check on `/docs/superpowers/.../*.html`:** Linking Post #1 to `/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html` would fail `audit_posts.py` (`candidate = repo_root / rel_target.lstrip("/")` looks for `.html` in source tree) unless `audit_posts.py` resolves `.html` → `.md` or recognizes `/docs/superpowers/` markdown sources.
5. **Self-referential test strings triggering the repo-wide spoiler scanner:** The test in `tests/test_blog_pipeline.py` that scans `git ls-files` for forbidden project slugs must exclude `tests/test_blog_pipeline.py` (and `docs/superpowers/{specs,plans}/2026-11-12-*` meta-descriptions, or avoid literal forbidden tokens in the 2026-11-12 docs) so the scanner checks real repo content cleanly.

---

### Task 1: Render `docs/superpowers/` in Jekyll & Support `.html` → `.md` Internal Links in `audit_posts.py`

**Files:**
- Modify: `_config.yml:139-154,253-284`
- Modify: `docs/superpowers/plans/2026-10-25-dual-surface-recipe-blog.md:1-5`
- Modify: `docs/superpowers/plans/2026-11-08-recipe-pipeline-and-go-live.md:1-5`
- Modify: `docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.md:1-5`
- Modify: `docs/superpowers/specs/2026-11-08-recipe-pipeline-and-go-live-design.md:1-5`
- Modify: `docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.md:1-5`
- Modify: `.agents/skills/blog-author/scripts/audit_posts.py:187-198`
- Modify: `tests/test_e2e_verification.py:50-72,379-425`
- Modify: `tests/test_blog_pipeline.py`

**Interfaces:**
- Consumes: `docs/superpowers/{specs,plans}/*.md`
- Produces:
  - Compiled HTML pages at `_site/docs/superpowers/{specs,plans}/<name>.html` (`surface-blog`, `noindex`/excluded from `sitemap.xml` and `lunr-store.js`)
  - Updated internal link check in `audit_posts.audit_post_file` accepting `/docs/.../<name>.html` when `docs/.../<name>.md` exists in `repo_root`

- [ ] **Step 1: Write failing tests in `tests/test_blog_pipeline.py` and `tests/test_e2e_verification.py`**

In `tests/test_blog_pipeline.py`, add `test_audit_accepts_rendered_docs_html_links_when_md_exists`:
```python
    def test_audit_accepts_rendered_docs_html_links_when_md_exists(self):
        audit_posts = load_audit_posts()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            post = tmp_path / "2026-11-12-doc-link.md"
            post.write_text(
                "---\n"
                'title: "Doc Link Test"\n'
                'excerpt: "Verifies rendered docs/superpowers HTML links resolve against .md sources."\n'
                "categories:\n  - Blog\n"
                "tags:\n  - antigravity\n"
                "---\n\n"
                "See [the spec](/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html) "
                "and [missing](/docs/superpowers/specs/does-not-exist.html).\n",
                encoding="utf-8",
            )
            errors = audit_posts.audit_post_file(post, REPO_ROOT)
            self.assertEqual(len(errors), 1, f"Expected only missing doc to fail, got {errors}")
            self.assertIn("does-not-exist.html", errors[0])
```

In `tests/test_e2e_verification.py`:
- Remove `"_site/docs"` from `prohibited` in `test_01_build_hygiene`.
- In `test_10_dual_surface_room_separation_and_themes`, assert:
  - `(REPO_ROOT / "_site" / "docs" / "superpowers" / "specs" / "2026-11-10-blog-relaunch-themes-and-writing-skills-design.html").exists()`
  - `(REPO_ROOT / "_site" / "docs" / "superpowers" / "plans" / "2026-11-10-blog-relaunch-themes-and-writing-skills.html").exists()`
  - Both rendered HTML files contain `"surface-blog"` and `'data-default-theme="gruvbox"'`.
  - `_site/sitemap.xml` does NOT contain `/docs/superpowers/`.

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python -m unittest tests.test_blog_pipeline.TestBlogPipeline.test_audit_accepts_rendered_docs_html_links_when_md_exists tests.test_e2e_verification.TestEndToEndVerification.test_10_dual_surface_room_separation_and_themes -v`
Expected: FAIL (`2026-11-10-blog-relaunch-themes-and-writing-skills-design.html` rejected by `audit_posts.py` and missing from `_site/docs/superpowers/`).

- [ ] **Step 3: Enable rendered `docs/superpowers/` pages and update `audit_posts.py`**

- In `.agents/skills/blog-author/scripts/audit_posts.py` (`audit_post_file` link check): if `not candidate.exists()` and `candidate.suffix == ".html"`, also check `candidate.with_suffix(".md")`.
- In `_config.yml`:
  - Remove `- docs/` from `exclude:`.
  - Add a `defaults:` entry for `path: "docs/superpowers"` (`layout: single`, `author_profile: false`, `read_time: true`, `comments: false`, `share: false`, `related: false`, `surface: blog`, `sitemap: false`, `search: false`).
- Prepend YAML frontmatter (`---`, `title: "<H1 title>"`, `---`) to the 5 existing `.md` files in `docs/superpowers/{specs,plans}/` (and remove duplicate `# H1` line if Minimal Mistakes `layout: single` already renders `page.title` as `<h1>`).

- [ ] **Step 4: Rebuild Jekyll and verify Task 1 tests pass**

Run: `bundle exec jekyll build; python -m unittest tests.test_blog_pipeline.TestBlogPipeline.test_audit_accepts_rendered_docs_html_links_when_md_exists -v`
Expected: `OK` (and `_site/docs/superpowers/.../*.html` generated cleanly).

---

### Task 2: Scope Public Projects, Move `BACKLOG.md` to `blog-ops`, Scrub Unannounced Spoilers & Link Docs in Post #1

**Files:**
- Move/Delete: `_drafts/posts/BACKLOG.md` → `c:\github\agy\blog-ops\BACKLOG.md` (`git rm _drafts/posts/BACKLOG.md`)
- Modify: `_pages/projects.md`
- Modify: `_includes/blog-hub.html:27-34`
- Modify: `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md`
- Modify: `_drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops/{notes.md,facts.md,review.md}` (and sync `c:\github\agy\blog-ops\dossiers\rebuilding-my-blog-with-antigravity-and-view-loops\`)
- Modify: `.agents/skills/blog-research/SKILL.md:12`
- Modify: `.agents/skills/blog-voice/voice-profile.md:8`
- Modify: `docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.md`
- Modify: `docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.md`
- Modify: `docs/superpowers/specs/2026-11-12-public-projects-and-superpowers-docs-design.md`
- Modify: `docs/superpowers/plans/2026-11-12-public-projects-and-superpowers-docs.md`
- Modify: `tests/test_e2e_verification.py:396-401,459`
- Modify: `tests/test_blog_pipeline.py:138-179`

**Interfaces:**
- Consumes: Rendered `/docs/superpowers/...` routes from Task 1
- Produces:
  - `/projects/` with `#blog-relaunch` and `#dinner-planner` only
  - `.hz-project-shelf` with `blog-relaunch` and `dinner-planner` chips only
  - Post #1 linking `[Superpowers](https://github.com/obra/superpowers)`, `[design spec](/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html)`, and `[implementation plan](/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html)`
  - Zero occurrences of unannounced project tokens across `git ls-files`

- [ ] **Step 1: Add the repo-wide public-hygiene & project-scope assertions in `tests/test_blog_pipeline.py` and `tests/test_e2e_verification.py`**

In `tests/test_blog_pipeline.py`:
- Update `test_relaunch_post_1_and_dossier_pass_audit` to assert `not (REPO_ROOT / "_drafts" / "posts" / "BACKLOG.md").exists()` and verify Post #1 links to `https://github.com/obra/superpowers`, `/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html`, and `/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html`.
- Add `test_no_unannounced_projects_or_private_info_in_tracked_files` scanning every text file returned by `git ls-files` (excluding `tests/test_blog_pipeline.py` and archived 2022 logs) case-insensitively for unannounced project tokens and private identifiers.

In `tests/test_e2e_verification.py` (`test_10_dual_surface_room_separation_and_themes`):
- Assert `self.assertIn('id="blog-relaunch"', projects_html)` and `self.assertIn('id="dinner-planner"', projects_html)`, plus verify unannounced project slugs do not appear in `projects_html` or `home_html`.
- Add `"/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html"` and `"/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html"` to the live server HTTP 200 route loop.

- [ ] **Step 2: Run the updated tests to verify they fail**

Run: `python -m unittest tests/test_blog_pipeline.py -v`
Expected: FAIL (`BACKLOG.md` still exists and unannounced project tokens appear across tracked files).

- [ ] **Step 3: Move `BACKLOG.md` to `blog-ops`, update `/projects/`, `blog-hub.html`, and Post #1, and scrub tracked files**

- Copy `_drafts/posts/BACKLOG.md` to `c:\github\agy\blog-ops\BACKLOG.md` and run `git rm _drafts/posts/BACKLOG.md`.
- Update `_pages/projects.md` to render two cards:
  1. `#blog-relaunch`: **This Site (`hawzy.github.io`)** (`Jekyll · 5 Themes · Antigravity Skills`) — *"Static GitHub Pages blog rebuilt with a live browser view loop, five Oh My Posh / editor palettes, and a deterministic Python post auditor."* linking to `/blog/2026/rebuilding-my-blog-with-antigravity-and-view-loops.html`.
  2. `#dinner-planner`: **Agentic Kitchen & Weekly Dinner Planner** (`Jekyll · Python · B2A JSON`) — *"Dual-surface family recipe catalog and weekly meal rotation pairing Cooking for Engineers dependency grids with machine-readable `/api/recipes.json` and `/api/weekly-menu.json` endpoints (full pipeline writeup coming soon)."* linking to `/recipes/`.
- Update `_includes/blog-hub.html` `.hz-project-shelf` to show only `blog-relaunch` (`/projects/#blog-relaunch`) and `dinner-planner` (`/projects/#dinner-planner`).
- Update `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md`:
  - Link `[Superpowers](https://github.com/obra/superpowers)` in Section 2.
  - Turn the `brainstorming` spec reference into `[2026-11-10-blog-relaunch-themes-and-writing-skills-design.md](/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html)` and the `writing-plans` plan reference into `[2026-11-10-blog-relaunch-themes-and-writing-skills.md](/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html)`.
  - Update line 61 project shelf list to `([/projects/](/projects/): blog-relaunch, dinner-planner)` and bump `55` → `58` (matching actual test count) in Section 4 (`facts.md` + `twitter-thread.md` synced).
- Scrub unannounced project slugs/repo names from `_drafts/posts/rebuilding-my-blog-.../{notes.md,facts.md,review.md}`, `.agents/skills/blog-research/SKILL.md`, `.agents/skills/blog-voice/voice-profile.md`, and `docs/superpowers/{specs,plans}/*.md` (including wording in `2026-11-12-*` docs so no forbidden token appears literally).

- [ ] **Step 4: Restart local Jekyll server (since `_config.yml` changed), run `audit_posts.py`, and run full test discovery**

Run:
```powershell
bundle exec jekyll build
python .agents/skills/blog-author/scripts/audit_posts.py --post _posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md --dossier _drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops
```
Restart the background `jekyll serve --port 4000` task, commit locally on `feat/agentic-recipe-blog` (never `git push`), and run `python -m unittest discover -s tests -v`.
Expected: `OK` across all tests (including `test_07_git_safety_check`), 0 failures, 0 skipped.
