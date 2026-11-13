---
name: recipe-intake
description: Captures family and personal recipes via focused Q&A into a structured dossier brief (_drafts/recipes/<slug>/brief.md) without requiring external web sources.
---

# Family Recipe Intake Skill (`recipe-intake`)

Captures recipes the user already cooks (`origin: family`) from notes, photos, voice transcripts, or memory into `_drafts/recipes/<slug>/brief.md`.

Unlike `recipe-research`, family recipes do **not** require external web citations (`sources.yml` and `research.md` are omitted). Instead, `brief.md` serves as the authoritative provenance record.

---

## Workflow

1. **Seed `_drafts/recipes/<slug>/brief.md`**:
   - Set `origin: family` and `stage: intake`.
   - Record every ingredient, quantity, vessel, heat setting, timing, and family note exactly as shared by the user.
   - **Preserve family quirks**: Never silently "correct" or standardize a beloved family ratio or technique unless the user asks.

2. **Targeted Gap-Fill Interview (Ask Only What's Missing)**:
   - Inspect the draft notes for missing execution anchors:
     - Yield / servings count
     - Missing ingredient quantities or units
     - Pan size or material where crowding/evaporation matters
     - Stove / oven heat setting and timer ranges
     - Sensory doneness cues (color, texture, aroma, or internal temp)
   - Ask a **single concise batch of questions** covering only the missing items.
   - If the user doesn't know a specific measurement yet (e.g., "a splash of vinegar — I eyeball it until bright"), record their sensory description and tag the exact numeric slot as `TODO-ask` so `recipe-author` never invents a fake number.

3. **Dossier `brief.md` Template**:
   ```markdown
   # Brief — <Recipe Title>

   - **Slug:** `<slug>`
   - **Origin:** `family`
   - **Stage:** `gate-1`
   - **Servings:** <N>
   - **Target Time:** <prep + cook>

   ## Family Provenance & Notes
   - <Who/where this recipe comes from, what makes it special, what must not change>

   ## Ingredients (Chronological)
   - <item>: <qty unit> (<notes or TODO-ask>)

   ## Method & Sensory Cues
   1. <Step + heat + timer + sensory doneness cue or TODO-ask>
   ```

---

## Exit Criteria & Gate 1 Output

1. Every ingredient in `brief.md` has an explicit quantity/unit or `TODO-ask`.
2. Every heated or timed step has a sensory doneness cue or `TODO-ask`.
3. Update `stage: gate-1` in `_drafts/recipes/<slug>/brief.md`.
4. Present a **<=15-line Gate-1 summary** (yield, ingredient highlights, method flow, any remaining `TODO-ask` items) and wait for the user to reply `"go"` before invoking `recipe-author`.
