---
name: blog-voice
description: Maintains Nick's (hawzy) writing voice profile (.agents/skills/blog-voice/voice-profile.md) and provides the Gemini Web Personal Intelligence (@Gmail/@Docs) handoff prompt for extracting real phrasing habits and banned AI clichés.
---

# Blog Voice Skill (`blog-voice`)

Use this skill when calibrating, updating, or auditing the authorial voice for `hawzy.github.io` blog posts and X/Twitter threads.

## Resources
- **Voice Profile:** `.agents/skills/blog-voice/voice-profile.md`
- **Gemini Web Personal Intelligence Handoff Prompt:** `.agents/skills/blog-voice/prompts/gemini-personal-intelligence-handoff.md`

## Workflows

### 1. Exporting the Gemini Web Personal Intelligence Prompt
When the user wants to enrich their voice profile from Gmail/Google Docs:
1. Point them to `.agents/skills/blog-voice/prompts/gemini-personal-intelligence-handoff.md` (or display the copy-paste block directly).
2. Once they paste back the Gemini Web response, merge the concrete sentence rhythm rules, signature transitions, and anti-voice phrases into `.agents/skills/blog-voice/voice-profile.md`.
3. Keep the `## Banned Phrases` section formatted as a simple markdown bullet list (`- <phrase>`) so `.agents/skills/blog-author/scripts/audit_posts.py` can parse and enforce it automatically.

### 2. Updating from Brain Dumps (`_drafts/posts/<slug>/notes.md`)
Whenever the user provides raw stream-of-consciousness notes or edits a draft:
- Note any recurring phrasing or corrections ("too cringe", "too formal", "drop the fake terminal roleplay") and codify them in `voice-profile.md`.
