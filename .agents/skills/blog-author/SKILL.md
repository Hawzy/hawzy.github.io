---
name: blog-author
description: Drafts canonical hawzy.github.io Jekyll blog posts (_posts/YYYY-MM-DD-<slug>.md) with a declared Additive Asset from a post dossier (notes.md + facts.md + voice-profile.md), runs scripts/audit_posts.py, and dispatches a zero-context Editorial/Voice critic.
---

# Blog Author Skill (`blog-author`)

Use this skill to author or revise a canonical blog post in `c:\github\agy\blog\_posts\YYYY-MM-DD-<slug>.md` from a research dossier (`notes.md` + `facts.md`) using `.agents/skills/blog-voice/voice-profile.md`.

All X (Twitter) promotion copy (`~60%` native rewrite, Curiosity Reply, UTM links, and launch checklists) lives separately in `c:\github\agy\x-growth` via the global `blog-promote` skill so duplicate X drafts never live inside the public blog repository.

## Required Dossier & Output Files
- `notes.md` — Author's raw brain dump and angle (`blog-ops/dossiers/<slug>/notes.md` or `_drafts/posts/<slug>/notes.md`)
- `facts.md` — Verified `[fN]` repository facts from `blog-research`
- `review.md` — Output of `audit_posts.py` + zero-context Editorial/Voice critic review
- `_posts/YYYY-MM-DD-<slug>.md` — Canonical Jekyll post in `c:\github\agy\blog`

## Required Post Frontmatter Schema
```yaml
---
title: "Post Title"
excerpt: "1-2 sentence summary (20-220 chars) used on Layout C featured cards and Twitter/X summary cards."
additive_asset: "Specific blog-exclusive table, copy-paste script/config, checklist, or diagram pitched from X Reply #1 (min 15 chars)."
# Optional once published on X: activates the theme-synced lazy-loaded X discussion footer
# x_post_url: "https://x.com/hawzzy/status/1856789012345678901"
categories:
  - Blog
projects:
  - blog-relaunch
tags:
  - antigravity
  - jekyll
---
```

## Authoring & Verification Workflow

1. **Read Three Inputs Only:**
   - Read `notes.md`, `facts.md`, and `voice-profile.md`.
   - Every technical number, command, filename, or bug story must trace to `facts.md` or `notes.md`. Never invent metrics.
2. **Draft the Canonical Post with an Additive Asset:**
   - Write `_posts/YYYY-MM-DD-<slug>.md` following `voice-profile.md` (first-person builder voice, dry parenthetical quips, concise purposeful code blocks, zero banned AI-slop phrases).
   - Ensure the post contains the concrete **Additive Asset** named in `additive_asset:` (benchmark tables, copy-paste scripts/configs, checklists, or architecture diagrams) so readers from X have a clear, non-redundant reason to visit the blog.
3. **Run the Deterministic Auditor (`scripts/audit_posts.py`):**
   ```bash
   python .agents/skills/blog-author/scripts/audit_posts.py \
     --post _posts/YYYY-MM-DD-<slug>.md \
     --dossier _drafts/posts/<slug>
   ```
4. **Zero-Context Editorial/Voice Critic Pass:**
   - Dispatch a fresh `research` subagent with **only** `_posts/YYYY-MM-DD-<slug>.md`, `facts.md`, and `voice-profile.md` (no author conversation history) to check for:
     - Unsourced claims not in `facts.md`
     - Sections that drift into generic AI tutorial tone
     - Weak opener or sluggish pacing
   - Record findings in `review.md` and resolve any blockers before presenting the draft to the user.
5. **Hand Off to `blog-promote` (and Backfill `x_post_url` After Launch):**
   - Once the blog post is published and indexed in Google Search Console, run `blog-promote` in `c:\github\agy\x-growth` to draft `campaigns/<slug>/x-promo.md`.
   - After posting manually on X, add `x_post_url: "https://x.com/<handle>/status/<id>"` to the post frontmatter to enable the lazy-loaded X discussion embed footer.
