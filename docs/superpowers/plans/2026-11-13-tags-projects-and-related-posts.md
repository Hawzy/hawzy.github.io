---
layout: single
title: "Tags, Projects & Related Posts Implementation Plan"
surface: blog
sitemap: false
search: false
comments: false
---

# Tags, Projects & Related Posts Implementation Plan

**Goal:** Replace Minimal Mistakes' broken related-posts grid, 2022-leaking Previous/Next links, redundant `Categories: Blog` display, and 2022-cluttered `/tags/` index with a `_data/projects.yml` registry, build-time Liquid related-reading matching (`_includes/post-related.html`), and inline `?tag=<slug>` filtering on `/` and `/blog/`.

**Architecture:** `_data/projects.yml` serves as the single project registry consumed by `/projects/`, `_includes/blog-hub.html`, `_includes/post-related.html`, and `audit_posts.py`. Related posts are scored at build time (`+3` per shared project, `+1` per shared tag) with zero output when no active match exists, while `/` filters active posts in place by `?tag=<slug>` via vanilla JS.

**Spec:** `docs/superpowers/specs/2026-11-13-tags-projects-and-related-posts-design.md`

## Tasks

1. **Registry, Auditor, Skill & Post #1 Frontmatter:** Create `_data/projects.yml`, validate `project`/`projects` slugs against it in `.agents/skills/blog-author/scripts/audit_posts.py`, instruct tag reuse in `.agents/skills/blog-author/SKILL.md`, and add `projects: [blog-relaunch]` to `_posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md`.
2. **Templates & CSS:** Update `_pages/projects.md`, `_includes/blog-hub.html`, `_layouts/single.html`, `_includes/page__taxonomy.html`, `_includes/tag-list.html`, `_includes/post_pagination.html`, `_layouts/tags.html`, `_includes/posts-tag.html`, `_pages/{tag,category,year}-archive.md`, create `_includes/post-related.html`, and add `--hz-*` theme-aware styles in `assets/css/main.scss`.
3. **Tests & Verification:** Update `tests/test_e2e_verification.py` and `tests/test_blog_pipeline.py`, rebuild Jekyll, run `audit_posts.py`, commit locally on `main`, and pass the full `unittest` discovery suite.
