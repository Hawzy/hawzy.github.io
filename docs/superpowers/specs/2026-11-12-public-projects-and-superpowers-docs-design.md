---
layout: single
title: "Public Projects Scope & Rendered Superpowers Docs — Short Design"
surface: blog
sitemap: false
search: false
comments: false
---

# Public Projects Scope & Rendered Superpowers Docs — Short Design

**Date:** 2026-11-12
**Repository:** `hawzy.github.io` (`c:\github\agy\blog`, branch `feat/agentic-recipe-blog`)
**Scope:** Small change

## 1. Intent & Why

Because `hawzy.github.io` is a public GitHub Pages repository, listing unpublished side projects on `/projects/`, the homepage shelf, or in tracked backlog/spec files spoils future posts before they are written. Only published projects and a light teaser for the upcoming Agentic Kitchen / recipes writeup should appear publicly, while the Superpowers design specs and implementation plans referenced in Post #1 should be scrubbed of spoilers and rendered as clickable pages right on the site.

## 2. Goals, Non-Goals & Anti-Goals

- **Goals:**
  - Show only `#blog-relaunch` (*This Site: 5-Theme Jekyll & Agentic Writing Pipeline*, linking to Post #1) and `#dinner-planner` (*Agentic Kitchen & Weekly Dinner Planner*, teasing the upcoming writeup and linking to `/recipes/`) on `/projects/` and `.hz-project-shelf`.
  - Move `_drafts/posts/BACKLOG.md` to private `c:\github\agy\blog-ops\BACKLOG.md`, remove it from git in `c:\github\agy\blog`, and scrub all unannounced project slugs/repos from Post #1, `_drafts/posts/rebuilding-my-blog-.../`, `.agents/skills/`, and `docs/superpowers/`.
  - Render `docs/superpowers/{specs,plans}/*.md` as clean `layout: single` (`surface: blog`, `sitemap: false`, `search: false`, `comments: false`) pages on `hawzy.github.io`, and link both **Superpowers** (`https://github.com/obra/superpowers`) and the rendered spec/plan URLs inside Post #1.
  - Enforce zero unannounced project leaks across all git-tracked files via automated tests.
- **Non-Goals:** Rewriting git commit history in this step; changing B2A JSON contracts (`/api/recipes.json`, `/api/weekly-menu.json`, `/llms.txt`).
- **Anti-Goals:** Running `git push`; indexing internal `docs/superpowers/` pages in `/sitemap.xml` or Lunr search (`assets/js/lunr/lunr-store.js`); leaking personal machine usernames, private emails, or unannounced project names in tracked files.

## 3. Constraints

- **Git Safety Invariant (`AGENTS.md` §3):** Never run `git push`.
- **Python 3 Standard Library Only:** All auditor and test updates use Python 3 stdlib only.
- **Full Suite Compatibility:** `bundle exec jekyll build` and `python -m unittest discover -s tests -v` pass with 0 failures and 0 skipped tests against the live local server.

## 4. Approaches Considered

1. **GitHub-only blob links + repo scrub:** Keep `docs/` excluded in `_config.yml` and link Post #1 to `https://github.com/hawzy/hawzy.github.io/blob/main/docs/superpowers/...`. Simple, but 404s until `feat/agentic-recipe-blog` is merged/pushed to `main` and leaves the 5-theme reader experience.
2. **Option 1 + Rendered Jekyll Pages (Selected):** Scrub `docs/superpowers/`, remove `docs/` from `_config.yml` `exclude`, add frontmatter + `_config.yml` defaults (`layout: single`, `surface: blog`, `sitemap: false`, `search: false`, `comments: false`), and link Post #1 to the rendered `/docs/superpowers/...` pages (plus `https://github.com/obra/superpowers` for Superpowers itself). Works immediately on `localhost:4000` and renders in the visitor's chosen theme.

## 5. Builder Calls

- Each Markdown file under `docs/superpowers/` gets explicit YAML frontmatter (`layout: single`, `title`, `surface: blog`, `sitemap: false`, `search: false`, `comments: false`) in addition to `_config.yml` path defaults (`path: "docs/superpowers"`), because Jekyll only processes non-collection `.md` files into HTML when they begin with `---` frontmatter.
- `.agents/skills/blog-author/scripts/audit_posts.py` adds `/docs/superpowers/` to `KNOWN_SITE_ROUTES` (or resolves `.html`/directory targets) so internal links to rendered Superpowers docs pass `audit_posts.py`.
