1/ 17 posts sat untouched for 4 years while my site header turned into "Hawzy's Kitchen & Code."

So I paired with Google Antigravity agents and 55 Python stdlib tests to rebuild my blog in one evening.

Here are the 5 terminal themes and verification loops we shipped:

2/ Agents write CSS fast and have zero idea when a layout feels cramped or gimmicky until you look at it.

Using the Superpowers `brainstorming` visual companion server, we iterated on live HTML mockups in the browser before touching a single Jekyll template.

3/ Early header mockups used a 1980s CRT underscore cursor (`_`).

Swapping to a 2px vertical bar (`|`), pulling in my Antigravity Gruvbox Material palette (`#141617`), and adding Oh My Posh prompt styles gave us 5 live themes (`Ctrl+Shift+S`).

4/ The 5 themes in localStorage["hawzy-theme"]:
- gruvbox: Gruvbox Material + diamond pills
- telemetry: Dark ops #080C14 + blinking |
- catppuccin: Mocha #1E1E2E + Powerline chevrons
- kitchen: Warm light #FAF7F2 + serif
- paper: Daylight #FFFFFF + robbyrussell arrow

5/ Antigravity loves writing tests (55 in the repo now, what is it testing, who knows!?), so `audit_posts.py` + a zero-context critic subagent verify every claim against `facts.md` before commit:
https://hawzy.github.io/blog/2026/rebuilding-my-blog-with-antigravity-and-view-loops.html?utm_source=twitter&utm_medium=social&utm_campaign=rebuilding-my-blog-with-antigravity-and-view-loops&utm_content=reply-1
