---
name: recipe-visuals
description: Generates editorial hero photography and Cooking for Engineers infographic assets via Google Nano Banana API with image-to-recipe fidelity verification.
---

# Recipe Visuals Skill (`recipe-visuals`)

Generates optional editorial hero photography (`assets/images/recipes/<slug>-hero.jpg`) and architectural block-grid infographics (`assets/images/recipes/<slug>-grid.jpg`) for approved recipes via Google's **Nano Banana** API (`gemini-nano-banana-2.1` or `gemini-3-pro-image`).

Visuals are **optional for publishing** — if `GEMINI_API_KEY` is unset or `--dry-run` is passed, the script prints the exact prepared prompts and exits cleanly with code `0`.

---

## CLI Usage (`scripts/generate_recipe_visuals.py`)

```bash
# Generate or preview Nano Banana recipe visuals
python .agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py \
  --slug crispy-mongolian-beef-broccoli \
  --title "Crispy Weeknight Mongolian Beef & Broccoli" \
  --visual-cue "Glossy dark soy-ginger glazed flank steak strips with crispy edges, bright steamed broccoli florets, and bias-sliced scallions over jasmine rice" \
  --grid-summary "Steam broccoli 3m; whisk soy+water+brown sugar+ginger+garlic; dredge flank steak in cornstarch and sear 2m per side; simmer sauce+steak+broccoli+scallions 90s"
```

---

## Image-vs-Recipe Fidelity Check

Before wiring `image: /assets/images/recipes/<slug>-hero.jpg` into `_recipes/<slug>.md`:
1. Inspect the generated hero image (`read_file` on `assets/images/recipes/<slug>-hero.jpg`).
2. Confirm that:
   - The protein cut, sear/glaze color, and primary vegetable/starch match `_recipes/<slug>.md`.
   - Garnishes match the recipe's finishing ingredients (no hallucinated herbs, citrus wedges, or wrong noodles).
   - Serving vessel and table styling match the warm editorial kitchen aesthetic.
3. If the image passes, set `image: /assets/images/recipes/<slug>-hero.jpg` in `_recipes/<slug>.md`; otherwise regenerate with a refined `--visual-cue` or leave `image:` unset until a real kitchen photo is captured.
