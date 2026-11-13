---
layout: single
title: "Tags, Projects & Related Posts — Design Spec"
surface: blog
sitemap: false
search: false
comments: false
---

# Tags, Projects & Related Posts — Short Design

**Date:** 2026-11-13
**Repository:** `hawzy.github.io` (`c:\github\agy\blog`, branch `main`)
**Scope:** Small change

## 1. Intent & Why

Minimal Mistakes' stock `site.related_posts` footer recommends Post #1 to itself using an old 2022 stock image (`teaser.jpg`), `post_pagination.html` links Previous into soft-archived 2022 `#100DaysOfCode` logs, `page__taxonomy.html` outputs a redundant `Categories: Blog` pill, and `/tags/` mixes active 2026+ posts with 17 archived 2022 logs. Meanwhile, upcoming builds naturally group along two dimensions: concrete **projects** (`projects:`) and free-form cross-cutting **`#tags`**.

## 2. Goals, Non-Goals & Anti-Goals

- **Goals:**
  - Single project registry in `_data/projects.yml` driving `/projects/`, the homepage project shelf, project validation in `audit_posts.py`, and optional live-surface callouts (e.g., `dinner-planner` → `/recipes/`).
  - Free-form `tags:` and multi-project `projects:` frontmatter, with `blog-author/SKILL.md` instructing agents to scan existing active post tags and `_data/projects.yml` first and reuse overlapping slugs before creating new ones.
  - Build-time "Related Reading" (`_includes/post-related.html`) scoring other active posts (`+3` per shared project, `+1` per shared tag) and rendering up to 3 compact one-line rows (`YYYY-MM-DD · Title · matching #tags`), outputting nothing when no other active post or live surface matches.
  - Inline `?tag=<slug>` filtering on `/` and `/blog/` via lightweight vanilla JS with a clearable filter pill, plus clean `#tag` links across posts and hub cards.
  - Active-only Previous/Next pagination, removal of `Categories: Blog`, and active-only `/tags/` archive filtering.
- **Non-Goals:** No custom Ruby plugins; no strict tag allowlist blocking new tags.
- **Anti-Goals:** Running `git push`; self-referential related posts, stock `teaser.jpg` thumbnails, or `// TRANSMISSION` roleplay titles; introducing unannounced project spoilers into tracked files.

## 3. Constraints

- **Git Safety Invariant (`AGENTS.md` §3):** Never run `git push`.
- **Python 3 Standard Library Only:** `audit_posts.py` and `tests/*.py` use stdlib only.
- **5-Theme Compatibility:** All CSS rules in `assets/css/main.scss` use `var(--hz-*)` custom properties.

## 4. Approaches Considered

1. **Build-Time Liquid Matching + Inline `?tag=` Filter on `/` (Selected):** Scores related posts in static HTML via Liquid at build time and adds minimal vanilla JS on `/` for `?tag=` filtering. Zero network fetches, works without JS for related links, and keeps static SEO clean.
2. **Client-Side `/api/posts.json` Engine:** Emits a posts JSON feed and runs both related-post matching and filtering in client JS. Rejected because related links wouldn't appear in static HTML without JS.

## 5. Builder Calls

- Support both `projects: [slug1, slug2]` and `project: slug1` in Liquid templates and `audit_posts.py`, validating against `_data/projects.yml`.
- Add `projects: [blog-relaunch]` to Post #1 frontmatter so `/projects/#blog-relaunch` automatically lists Post #1.
- Update `test_07_git_safety_check` in `tests/test_e2e_verification.py` to accept `main` as well as `feat/agentic-recipe-blog` so the full suite passes cleanly on `main`.
