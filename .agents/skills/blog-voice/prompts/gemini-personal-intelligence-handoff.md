# Gemini Web Personal Intelligence — Voice Extraction Handoff Prompt

Use this prompt in **Gemini Web** (with `@Gmail`, `@Google Docs`, or `@Google Drive` extensions enabled) whenever you want to sharpen or refresh `.agents/skills/blog-voice/voice-profile.md` using your real sent emails, docs, and notes.

---

## Copy-Paste Prompt for Gemini Web

```text
@Gmail @Google Docs Analyze my sent emails and personal documents from the last 12–24 months where I am explaining a technical project, troubleshooting an issue, or writing casually to friends/colleagues (ignore short 1-line replies, calendar invites, and automated forwards).

Build a structured "Voice & Style Profile" I can drop into my blog-writing AI agent's `voice-profile.md` file. Do NOT quote private personal data or email addresses; only extract linguistic patterns and anonymized phrasing habits. Cover:

1. Sentence & Paragraph Rhythm:
   - Typical sentence length range, how I open emails/notes, and how I transition between ideas.
2. Humor, Quips & Parentheticals:
   - How I express dry humor, skepticism, annoyance, or enthusiasm (e.g., parentheticals, understatement, specific idioms).
3. Signature Words & Phrasing:
   - 10–15 transitional phrases, verbs, or qualifiers I naturally reach for.
4. Technical Explanation Style:
   - How I frame a problem, introduce a script/tool, and admit what went wrong.
5. Anti-Voice (What I Never Sound Like):
   - 10–15 clichés, corporate buzzwords, or AI-style openings that would immediately sound fake coming from me.

Format the output as clean Markdown sections matching `.agents/skills/blog-voice/voice-profile.md`.
```

---

## How to Import the Result

1. Paste Gemini Web's output into chat or save it to `_drafts/voice-raw.md`.
2. Invoke `blog-voice` and ask the agent to merge the new patterns and anti-voice terms into `.agents/skills/blog-voice/voice-profile.md` (preserving the `## Banned Phrases` heading so `audit_posts.py` picks up any newly banned phrases automatically).
