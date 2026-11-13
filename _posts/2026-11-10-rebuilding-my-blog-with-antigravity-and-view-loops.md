---
title: "Rebuilding My Blog with Antigravity and Visual View Loops"
excerpt: "How I relaunched this static Jekyll blog after four years using Google Antigravity skills, a live browser view loop, five Oh My Posh themes, and deterministic Python auditors."
date: 2026-11-10
categories:
  - Blog
projects:
  - blog-relaunch
tags:
  - antigravity
  - superpowers
  - jekyll
---

The last time I published a post here was February 2022. My kids were three and eight months old, and I was attempting a New Year's resolution with a non-consecutive `#100DaysOfCode` run (seventeen short notes to my future self on PowerShell profile functions, running Jekyll in Docker Compose, installing Oh My Posh in Windows Terminal, and flashing QMK firmware onto a three-key Drop macropad). Then I ended up getting a new job, life got busy, and the blog sat untouched for four years.

I have even less free time now with three kids (ages 7, 5, and 4), but with AI agents the amount I can actually get done in an evening has jumped exponentially. As of this writing I'm on the Gemini AI Ultra $100 plan, which has been a pretty great value so far running Argon and Carbon inside **Google Antigravity**.

Lately I've been turning my attention to projects that make home life easier, like weekly recipe planning and grocery buying automations, and my first task was a full site redesign to set all of that up. (During an early pass, the site header briefly turned into *"Hawzy's Kitchen & Code"* with a dinner schedule on the homepage, which lasted about forty-eight hours before I killed it off: #1 *"Hawzy's Kitchen & Code"* sounds like a daytime cable segment, and #2 dinner automation is only one of a half-dozen side projects I'm building.)

Since I had already manually configured Michael Rose's [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme back in 2022, I wanted to keep using GitHub Pages static hosting rather than starting over. So I tucked the seventeen 2022 `#100DaysOfCode` posts into a collapsible archive drawer at the bottom of [`/blog/`](/blog/) so none of the old URLs break, gave the active weekly dinner plan its own home at [`/recipes/`](/recipes/) (`kitchen` in the top nav), and rebuilt the rest of the site. This was my workflow.

---

## 1. Why Static Jekyll Still Wins for Agentic Workflows

When an AI agent is your primary pair programmer, a database-backed CMS is a liability. You don't want an agent clicking around an admin dashboard or mutating hidden state in SQLite just to add a project page or change a layout.

With Jekyll on GitHub Pages (even after burying Minimal Mistakes' default skin under 2,900 lines of custom CSS), the entire site is plain text in git:

- Layouts and partials live in `_layouts/` and `_includes/`.
- Theme tokens live in `assets/css/main.scss`.
- Machine-readable endpoints for other agents ([`/llms.txt`](/llms.txt), [`/api/recipes.json`](/api/recipes.json), [`/api/weekly-menu.json`](/api/weekly-menu.json)) are generated in the same `bundle exec jekyll build` pass as the HTML pages.

If an agent makes a mess, `git diff` shows every line and `git checkout` undoes it in a millisecond.

---

## 2. Structuring the Work with Antigravity & Superpowers Skills

Left to its own devices on a prompt like *"redesign my blog,"* an LLM will immediately start spraying CSS across five files before you've even agreed on what goes on the homepage.

To keep that from happening, I run the **[Superpowers](https://github.com/obra/superpowers)** skill suite inside Antigravity. In Antigravity, a skill isn't an opaque plugin binary. Instead, it is a directory under `.agents/skills/` (or your user config) with a `SKILL.md` file and optional scripts that tell the agent *how* to execute a workflow phase:

1. **`brainstorming`**: Forces the agent to inspect the repo, ask one design question at a time, and get explicit sign-off on a written spec ([`2026-11-10-blog-relaunch-themes-and-writing-skills-design.md`](/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html)) before touching implementation code.
2. **`writing-plans`**: Breaks the approved spec into bite-sized TDD tasks ([`2026-11-10-blog-relaunch-themes-and-writing-skills.md`](/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html)), each with exact file paths, red/green test commands, and commit boundaries.
3. **`subagent-driven-development` / `executing-plans`**: Runs through the plan task by task, tracking commit ranges in a progress ledger and dispatching fresh-context review subagents at the end.

---

## 3. The Visual Companion View Loop (and Five Terminal Themes)

Agents are good at writing CSS and terrible at knowing whether the result actually looks good. Describing layouts in chat markdown is miserable when you're trying to judge typography, card density, or header chrome.

During the `brainstorming` phase, the agent spun up a local visual companion server that hot-reloaded interactive HTML mockups into my browser whenever it wrote a new `.html` file to `.superpowers/brainstorm/`.

We started by putting three blogs I actually enjoy reading side by side in the browser:

- **[Jesse Vincent (`blog.fsck.com`)](https://blog.fsck.com):** clean chronological stream and understated typography.
- **[Julia Evans (`jvns.ca`)](https://jvns.ca):** pragmatic grouping by topic so readers can find what they care about fast.
- **[Brian Krebs (`krebsonsecurity.com`)](https://krebsonsecurity.com):** high-signal featured lead story at the top.

Combining those gave us **Layout C** on [`/`](/) and [`/blog/`](/blog/): a featured latest-post card up top, a clickable project filter shelf ([`/projects/`](/projects/): `blog-relaunch`, `dinner-planner`), a clean chronological post list, and the collapsible 2022 archive drawer at the bottom.

### Iterating on the Header & Palette Switcher

While looking at header mockups in the browser, we ended up talking about terminal cursors. An early mockup used a blinking underscore (`_`) after the site title. Historically, hardware CRT terminals like the VT100 and IBM PC text-mode adapters used an underscore or block cursor because character-cell hardware addressed scanlines inside a fixed glyph box; modern GUI editors draw a 1 to 2px vertical bar (`|`) between character columns. Switching the prompt caret to a blinking `|` immediately made the header feel like a modern code editor instead of a 1983 green-screen.

From there I made a few style decisions, pulling in the color palette from my actual Antigravity editor (**Gruvbox Material**: `#141617` background, `#D4BE98` warm sandstone foreground, `#E78A4E` orange accent) and referencing the **Oh My Posh** prompt segments I set up back in my 2022 PowerShell posts, and picked five distinct themes for the **Palette** button in the top-right masthead (or `Ctrl+Shift+S` / `Cmd+Shift+S`):

| Theme ID | Palette Inspiration | Surface / Accent | Header Prompt Style |
| :--- | :--- | :--- | :--- |
| **`gruvbox`** *(default)* | Antigravity `Gruvbox Material` | `#141617` / `#E78A4E` | Oh My Posh Diamond pills (`◆ hawzy` `~/blog`) |
| **`telemetry`** | Dark ops telemetry | `#080C14` / `#38BDF8` | Minimal path + blinking bar cursor (`hawzy · ~/blog |`) |
| **`catppuccin`** | Catppuccin Mocha | `#1E1E2E` / `#CBA6F7` | Angled Powerline chevrons (`hawzy` ▸ `~/blog` ▸ `main`) |
| **`kitchen`** | Warm editorial light | `#FAF7F2` / `#C84B31` | Editorial italic serif (`hawzy · notes & recipes |`) |
| **`paper`** | Daylight newsprint | `#FFFFFF` / `#1A7F37` | Oh My Posh `robbyrussell` (`➜ hawzy git:(main)`) |

A tiny inline script in `_includes/head/custom.html` reads `localStorage["hawzy-theme"]` and sets `document.documentElement.dataset.theme` before first paint so the page never flashes the wrong background color on reload.

---

## 4. The Verification Loop: Tests, Scripts, and Subagents

Even with a solid plan, agents will still occasionally invent a number, forget a frontmatter tag, or slip generic AI throat-clearing into a paragraph. Rather than trusting the authoring agent to grade its own homework, the repo runs a quick verification loop before anything gets committed.

### Layer 1: Python Test & Audit Scripts

Antigravity and Gemini *love* making tests. We're up to 59 of them in this repo now (what is it testing, who knows!?). Between `tests/test_e2e_verification.py` and the new blog auditor `.agents/skills/blog-author/scripts/audit_posts.py`, the scripts check that:

- Every page and JSON endpoint ([`/`](/), [`/blog/`](/blog/), [`/recipes/`](/recipes/), [`/projects/`](/projects/), [`/about/`](/about/), [`/llms.txt`](/llms.txt), [`/api/recipes.json`](/api/recipes.json)) builds cleanly and returns `HTTP 200`.
- Blog posts have valid frontmatter, working `/...` internal links, no lingering `TODO-` placeholders, and companion X/Twitter threads (`twitter-thread.md`) under 280 characters.
- Prose is free of banned AI-slop words from `.agents/skills/blog-voice/voice-profile.md` (stripping code blocks first, then rejecting words like `delve`, `tapestry`, `buckle up`, or `game-changer` in paragraph text).

```powershell
python .agents/skills/blog-author/scripts/audit_posts.py `
  --post _posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md `
  --dossier _drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops
```

### Layer 2: Fresh-Context Reviewer Subagents

After the scripts pass, the orchestrator dispatches fresh subagents that never saw the drafting conversation:

- During **`blog-author`**, a zero-context Editorial & Voice critic reads only the draft post, `.agents/skills/blog-voice/voice-profile.md`, and the verified `_drafts/posts/<slug>/facts.md` sheet, flagging any unsupported number or off-voice phrasing in `_drafts/posts/<slug>/review.md`.
- At the end of an implementation plan, a whole-branch **`code-reviewer`** subagent inspects the full git diff against the design spec. In this run, it caught that I'd mentioned the `Ctrl+Shift+S` theme shortcut in this post before we'd actually wired up the `keydown` listener in `_includes/masthead.html`.

All things considered, rebuilding the whole site, theme switcher, and 3-skill writing pipeline (`blog-voice` → `blog-research` → `blog-author`) took one evening, which isn't bad. If you spot a discrepancy or something looks off, let me know.
