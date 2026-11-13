---
name: blog-research
description: Turns raw author brain dumps (_drafts/posts/<slug>/notes.md) and target Antigravity project repositories (c:\github\agy\<project>) into a verified, cited fact sheet (_drafts/posts/<slug>/facts.md) with zero invented numbers.
---

# Blog Research Skill (`blog-research`)

Use this skill before drafting any technical blog post to gather verified facts from the target repository (`c:\github\agy\<project>`) and pair them with the author's raw brain dump.

## Inputs & Outputs
- **Input 1 — Author Brain Dump:** `_drafts/posts/<slug>/notes.md` (created from the user's raw stream-of-consciousness prompt, quips, and angle).
- **Input 2 — Target Project Repo(s):** e.g., `c:\github\agy\blog`, `c:\github\agy\recipes`, or another sibling project repo under `c:\github\agy\`.
- **Output — Cited Fact Sheet:** `_drafts/posts/<slug>/facts.md`.

## Protocol

1. **Capture `notes.md` First:**
   - Write the user's raw brain dump, quips, and structural requests into `_drafts/posts/<slug>/notes.md` without sanitizing their tone.
2. **Inspect the Target Project Repository:**
   - Check `README.md`, `git log --oneline -n 30`, `docs/superpowers/specs/`, `docs/superpowers/plans/`, `.agents/skills/`, and test suites (`tests/`).
   - Record every concrete fact with a bracketed ID (`[f1]`, `[f2]`, ...):
     - Exact file paths, script names, and CLI flags
     - Real test counts, commit hashes, or round-over-round diff counts
     - Exact theme hex codes, model names, or protocol details
3. **Never Invent Numbers:**
   - If `notes.md` mentions a metric or event that cannot be verified from the repo or conversation logs, mark it in `facts.md` as `TODO-confirm: <question for author>` rather than guessing.
