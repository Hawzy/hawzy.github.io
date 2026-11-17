---
title: "Rebuilding My Blog with Antigravity and Visual View Loops"
excerpt: "How I relaunched this static Jekyll blog after four years using Google Antigravity, a live browser view loop, five Oh My Posh themes, and a robot that reviews the other robot."
additive_asset: "Full 5-theme SCSS token table (#141617, #080C14, #1E1E2E, #FAF7F2, #FFFFFF), Oh My Posh prompt CSS mappings, and copy-paste audit_posts.py verification command"
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

The last time I published a post here was February 2022. My kids were three and eight months old, and I was attempting a New Year's resolution with a non-consecutive #100DaysOfCode run (seventeen short notes to my future self on PowerShell profile functions, running Jekyll in Docker Compose, installing Oh My Posh in Windows Terminal, and flashing QMK firmware onto a three-key Drop macropad). Then I got a new job, life got busy, and the blog sat untouched for four years.

I have even less free time now with three kids (ages 7, 5, and 4), but with AI agents the amount I can actually get done in an evening has jumped exponentially. As of this writing I'm on the Gemini AI Ultra $100 plan, which has been a pretty great value so far running Argon and Carbon inside **Google Antigravity**.

Lately I've been turning my attention to projects that make home life easier, like weekly recipe planning and grocery buying automations, and step one was a full site redesign to set all of that up. The whole thing ended up being one big plan followed by a lot of tiny revisions until I was happy with it. Here's how that went.

---

## Why I Stayed on Jekyll

I'd already set up Michael Rose's [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme on GitHub Pages back in 2022, so starting over wasn't very appealing. It also turns out a static site is about the best thing you can hand an agent: every layout, theme token, and page lives in git as plain text, so if it makes a mess, `git diff` shows every line and `git checkout` undoes it.

So I tucked the seventeen 2022 posts into a collapsible archive drawer at the bottom of [/blog/](/blog/) (none of the old URLs break), gave the weekly dinner plan its own home at [/recipes/](/recipes/), and rebuilt everything else. The machine-readable endpoints for other agents ([/llms.txt](/llms.txt), [/api/recipes.json](/api/recipes.json), [/api/weekly-menu.json](/api/weekly-menu.json)) come out of the same `bundle exec jekyll build` as the HTML, which is nice.

---

## Be Opinionated (and Type a Lot)

The biggest thing I've learned working this way is that the agent will happily make a decision for you if you don't. Sometimes it guesses well. Sometimes I look at what it picked and immediately don't like it. Sometimes I have a better alternative ready, and sometimes I don't, but saying "no, not that" is still the important part.

The best example from this project: during an early pass, the agent turned the site header into *"Hawzy's Kitchen & Code"* and put the dinner schedule on the homepage. That lasted about forty-eight hours before I killed it off, because #1 it sounds like a daytime cable segment, and #2 dinner automation is only one of a half-dozen side projects I'm building. Nothing about that was "wrong" from the agent's point of view. It just wasn't what I wanted.

It also helps that I type a lot. My prompts in Antigravity are pretty verbose, which comes from always being a quick typist (I worked as a classroom transcriptionist in college and could get up to 150 wpm with their software). More context up front means fewer bad guesses later.

I also run the **[Superpowers](https://github.com/obra/superpowers)** skill pack in Antigravity. It wasn't doing a ton of heavy lifting on this particular project, but it does help with consistency: the agent asks design questions one at a time, writes a short [spec](/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html) and [plan](/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html) before touching code, and generally ends up closer to the destination I described instead of wandering off.

---

## Looking at It Instead of Describing It

Agents are good at writing CSS and terrible at knowing whether the result actually looks good. Describing layouts in chat is miserable when you're trying to judge typography or card density, so instead the agent ran a local preview server that pushed HTML mockups into a browser tab while we talked.

We started by putting three blogs I actually enjoy reading side by side:

- **[Jesse Vincent (blog.fsck.com)](https://blog.fsck.com):** clean chronological stream and understated typography.
- **[Julia Evans (jvns.ca)](https://jvns.ca):** pragmatic grouping by topic so readers can find what they care about fast.
- **[Brian Krebs (krebsonsecurity.com)](https://krebsonsecurity.com):** high-signal featured lead story at the top.

Mashing those together gave me what's on [/](/) and [/blog/](/blog/) now: a featured latest-post card, #tag filter chips, a plain chronological list, and the 2022 archive drawer at the bottom, with projects getting their own page at [/projects/](/projects/).

Most of the session was conversational pivots rather than big rewrites. At one point we got sidetracked on terminal cursors: an early header mockup had a blinking underscore after the site title, which turns out to be a CRT-era thing (old terminals drew the cursor inside a fixed character box). Switching to a thin `|` bar made the header feel like a modern editor instead of a 1983 green-screen.

### Five Themes

From there I pulled the color palette from my actual Antigravity editor (**Gruvbox Material**: `#141617` background, `#D4BE98` foreground, `#E78A4E` orange accent), borrowed the **Oh My Posh** prompt segments from my 2022 PowerShell posts, and ended up with five themes behind the palette button in the top-right corner (or `Ctrl+Shift+S` / `Cmd+Shift+S` from anywhere on the page):

| Theme ID | Palette Inspiration | Surface / Accent | Header Prompt Style |
| :--- | :--- | :--- | :--- |
| **`gruvbox`** *(default)* | Antigravity `Gruvbox Material` | `#141617` / `#E78A4E` | Oh My Posh Diamond pills (`◆ hawzy` `~/blog`) |
| **`telemetry`** | Dark ops telemetry | `#080C14` / `#38BDF8` | Minimal path + blinking bar cursor (`hawzy · ~/blog |`) |
| **`catppuccin`** | Catppuccin Mocha | `#1E1E2E` / `#CBA6F7` | Angled Powerline chevrons (`hawzy` ▸ `~/blog` ▸ `main`) |
| **`kitchen`** | Warm editorial light | `#FAF7F2` / `#C84B31` | Editorial italic serif (`hawzy · notes & recipes |`) |
| **`paper`** | Daylight newsprint | `#FFFFFF` / `#1A7F37` | Oh My Posh `robbyrussell` (`➜ hawzy git:(main)`) |

Gruvbox is the default because it's what I stare at all day in Antigravity, but I keep catching myself switching the site to Catppuccin (even though pink is usually not my color). A tiny inline script in `_includes/head/custom.html` reads `localStorage["hawzy-theme"]` and sets the theme before first paint, so the page never flashes the wrong background on reload.

---

## Letting the Robots Check the Robot

The most useful bug report I got on this project came from a robot. I'd written in this post that you could press `Ctrl+Shift+S` to switch themes, and a fresh-context code-reviewer subagent pointed out that nobody had actually wired that up yet (oops!). That's the whole argument for not letting the agent that wrote something grade its own homework.

So nothing gets committed without two layers of checks.

**Layer 1: Python tests and an audit script.** Antigravity and Gemini *love* making tests. We're up to 63 of them in this repo now (what is it testing, who knows!? I am definitely not reading all that). Between `tests/test_e2e_verification.py` and the blog auditor, the scripts check that:

- Every page and JSON endpoint builds cleanly and returns `HTTP 200`.
- Blog posts have valid frontmatter, working internal links, and no leftover `TODO-` placeholders.
- Prose and formatting get a lint pass before anything ships.

```powershell
python .agents/skills/blog-author/scripts/audit_posts.py `
  --post _posts/2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md `
  --dossier _drafts/posts/rebuilding-my-blog-with-antigravity-and-view-loops
```

**Layer 2: a code reviewer that never saw the conversation.** A fresh subagent reads the full diff against the design spec, which is how the shortcut thing got caught.

All things considered, rebuilding the whole site, the theme switcher, and the writing pipeline took a couple evenings, which isn't bad. Next up is the dinner planner: the recipe pipeline, *Cooking for Engineers* block grids, and getting the weekly grocery order mostly on autopilot. If you spot a discrepancy or something looks off in the meantime, let me know.
