# Interview Notes — Rebuilding My Blog with Antigravity and Visual View Loops

- **Slug:** `rebuilding-my-blog-with-antigravity-and-view-loops`
- **Target Date:** `2026-11-10`
- **Project Tags:** `antigravity`, `superpowers`, `jekyll`

## 1. The Hook (Why Relaunch?)
- Last posted in February 2022 during a `#100DaysOfCode` New Year's resolution run when my kids were 3 and 8 months old (PowerShell profile functions, Docker Compose for Jekyll, Oh My Posh setup, flashing QMK firmware on a 3-key macropad). Ended up getting a new job and life got busy.
- Now I have even less free time—my kids are 7, 5, and 4—but with AI agents the amount I can accomplish has exponentially increased. Currently on the Gemini AI Ultra $100 plan, which has been a pretty great value so far with Argon and Carbon.
- Turning my attention to home-life automations like weekly recipe planning and grocery buying, and my first step was a full site redesign to set that up (after a brief detour where the header turned into `"Hawzy's Kitchen & Code"` and put the dinner schedule on `/`, which felt too narrow since dinner automation is just one of half a dozen side projects).
- Since I had already manually configured Minimal Mistakes back in 2022, I wanted to stick with GitHub Pages static hosting, tuck the 17 `#100DaysOfCode` posts into a collapsible archive drawer on `/blog/` (`archived: true`) so no old URLs break, move the Active Weekly Dinner Plan to `/recipes/` (`kitchen` in the nav), and walk through my workflow.

## 2. The Technical Meat
- **Google Antigravity + Superpowers Skills:**
  - How skills work in Antigravity: markdown instruction packages (`SKILL.md` + deterministic helper scripts) that structure how the agent approaches work instead of winging a giant prompt.
  - Used `brainstorming` (interactive design interview + visual companion), `writing-plans` (bite-sized TDD task breakdown), and `subagent-driven-development` / `executing-plans` to design and ship the relaunch.
- **Static Hosting (Jekyll + GitHub Pages):**
  - Why static files win for agentic workflows: every page, layout, CSS variable, and JSON endpoint (`/llms.txt`, `/api/recipes.json`) lives in git as plain text. No database migrations, no CMS state to corrupt.
- **The Visual Companion View Loop:**
  - Agents are great at writing CSS and terrible at knowing whether a layout feels cramped or gimmicky until you look at it.
  - Using the `brainstorming` skill's local visual companion server (`start-server.sh`), the agent pushed interactive HTML mockups to a live browser tab while we talked.
  - We compared Jesse Vincent's `blog.fsck.com`, Julia Evans's `jvns.ca`, and Brian Krebs's security blog, settled on **Layout C** (featured latest post card + project filter shelf + chronological stream), and iterated on the header.
  - Killed the fake Windows path gimmick (`C:\github\...`) immediately—it didn't do anything for me—and instead wired up **5 distinct themes** that change both the site color palette and the header prompt style:
    1. `gruvbox` (default): My actual Antigravity IDE dark preset (`Gruvbox Material`: `#141617` background, `#D4BE98` foreground, `#E78A4E` orange accent) paired with an Oh My Posh diamond pill header (`◆ hawzy` + `~/blog`).
    2. `telemetry`: High-contrast dark ops palette (`#0D1117` / `#38BDF8`) with a clean `hawzy · ~/blog` prompt and a blinking vertical bar cursor (`|`) instead of a retro 1980s CRT underscore (`_`).
    3. `catppuccin`: Catppuccin Mocha lavender/mauve (`#1E1E2E` / `#CBA6F7`) with angled Powerline chevrons (`hawzy` -> `~/blog` -> `main`).
    4. `kitchen`: Warm cast-iron and butcher-block dark (`#1C1613` / `#E07A5F`) with an editorial italic serif header (`hawzy — notes & recipes |`).
    5. `paper`: Warm solarized/newsprint light mode (`#FAF7F2` / `#B45309`) with an Oh My Posh `robbyrussell` arrow prompt (`➜ hawzy git:(main)`).
- **The Review & Verification Loop (Code & Blog):**
  - Separating the blog/code review cycle from the recipe review panel (the 3-critic culinary/editorial/visual recipe panel gets its own deep dive in Post #2).
  - For code and blog changes, verification happens in two layers:
    1. **Subagent Review Loop:** Fresh-context reviewer subagents (`spec-reviewer` checking implementation against the design spec, `code-reviewer` checking implementation quality, plus a zero-context Editorial/Voice critic for blog posts) that never saw the authoring conversation.
    2. **Deterministic Python Stdlib Scripts:**
       - `tests/test_e2e_verification.py`: Boots against the built `_site/` and live local Jekyll server (`http://127.0.0.1:4000`) to assert layout structure, theme switcher attributes, JSON/LLM endpoints, and HTTP 200 status codes.
       - `.agents/skills/blog-author/scripts/audit_posts.py`: Audits `_posts/*.md` and `_drafts/posts/<slug>/` for required frontmatter, broken internal links, lingering `TODO-` markers, 23-character `t.co`-adjusted X/Twitter thread limits (`<= 280` chars), and strips fenced/inline code blocks before scanning prose against the banned AI-slop phrase list in `.agents/skills/blog-voice/voice-profile.md`.

## 3. Takeaway & What's Next
- Treating the blog itself like software—with voice profiles, provenance dossiers (`notes.md`, `facts.md`, `twitter-thread.md`, `review.md`), and deterministic auditors—makes writing a lot less tedious.
- Next up: **Post #2** on the Agentic Kitchen (recipe pipeline, *Cooking for Engineers* block grids, and weekly dinner/grocery automation), with other side-project writeups kept private in `blog-ops/BACKLOG.md` until published.
