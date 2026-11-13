---
name: blog-author
description: Drafts Jekyll blog posts (_posts/YYYY-MM-DD-<slug>.md) and companion X/Twitter threads (_drafts/posts/<slug>/twitter-thread.md) from a post dossier (notes.md + facts.md + voice-profile.md), runs scripts/audit_posts.py, and dispatches a zero-context Editorial/Voice critic.
---

# Blog Author Skill (`blog-author`)

Use this skill to author or revise a blog post and its companion X/Twitter thread from `_drafts/posts/<slug>/{notes.md,facts.md}` using `.agents/skills/blog-voice/voice-profile.md`.

## Required Dossier & Output Files
- `_drafts/posts/<slug>/notes.md` — Author's raw brain dump and angle
- `_drafts/posts/<slug>/facts.md` — Verified `[fN]` repository facts from `blog-research`
- `_drafts/posts/<slug>/twitter-thread.md` — 3–6 numbered tweets (`1/`, `2/`, ...), each `<= 280` characters (URLs count as 23 chars)
- `_drafts/posts/<slug>/review.md` — Output of `audit_posts.py` + zero-context Editorial/Voice critic review
- `_posts/YYYY-MM-DD-<slug>.md` — Published Jekyll post

## Required Post Frontmatter Schema
```yaml
---
title: "Post Title"
excerpt: "1-2 sentence summary (20-220 chars) used on Layout C featured cards and Twitter/X summary cards."
categories:
  - Blog
tags:
  - antigravity
  - jekyll
---
```

## Authoring & Verification Workflow

1. **Read Three Inputs Only:**
   - Read `_drafts/posts/<slug>/notes.md`, `_drafts/posts/<slug>/facts.md`, and `.agents/skills/blog-voice/voice-profile.md`.
   - Every technical number, command, filename, or bug story must trace to `facts.md` or `notes.md`. Never invent metrics.
2. **Draft the Post & Companion X/Twitter Thread:**
   - Write `_posts/YYYY-MM-DD-<slug>.md` following `voice-profile.md` (first-person builder voice, dry parenthetical quips, concise purposeful code blocks, zero banned AI-slop phrases).
   - Write `_drafts/posts/<slug>/twitter-thread.md` with numbered tweets (`1/`, `2/`, ...) that hook readers with the real problem/visual and link to the post.
3. **Run the Deterministic Auditor (`scripts/audit_posts.py`):**
   ```bash
   python .agents/skills/blog-author/scripts/audit_posts.py \
     --post _posts/YYYY-MM-DD-<slug>.md \
     --dossier _drafts/posts/<slug>
   ```
4. **Zero-Context Editorial/Voice Critic Pass:**
   - Dispatch a fresh `research` subagent with **only** `_posts/YYYY-MM-DD-<slug>.md`, `_drafts/posts/<slug>/facts.md`, `_drafts/posts/<slug>/twitter-thread.md`, and `.agents/skills/blog-voice/voice-profile.md` (no author conversation history) to check for:
     - Unsourced claims not in `facts.md`
     - Sections that drift into generic AI tutorial tone
     - Weak opener or sluggish pacing
   - Record findings in `_drafts/posts/<slug>/review.md` and resolve any blockers before presenting the draft to the user.
