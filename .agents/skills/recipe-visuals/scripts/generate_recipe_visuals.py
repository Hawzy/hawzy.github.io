#!/usr/bin/env python3
"""
Generates a Hero Dish Photo and a Cooking for Engineers Block-Grid Infographic
via Google's Nano Banana API (gemini-nano-banana-2.1 or gemini-3-pro-image).

Uses Python 3 standard library only. Exits gracefully with code 0 and prints
the exact prepared prompts when GEMINI_API_KEY is not set locally.
"""

import argparse
import base64
import json
import os
from pathlib import Path
import sys
from typing import Dict, Tuple
import urllib.error
import urllib.request

SUPPORTED_MODELS = (
    "gemini-nano-banana-2.1",
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-lite-image",
    "gemini-3-pro-image",
)


def build_prompts(title: str, visual_cue: str, grid_summary: str) -> Tuple[str, str]:
    """Constructs the editorial hero photo prompt and block-grid infographic prompt."""
    hero_prompt = (
        f"Editorial food photography of {title}: {visual_cue}. "
        "Shot at a 45-degree angle near a natural light window with soft diffused shadows, "
        "plated on handmade ceramic tableware over a neutral warm linen background. "
        "Natural, slightly imperfect authentic food styling, vibrant fresh garnish, 85mm lens."
    )

    grid_prompt = (
        "Clean, high-contrast architectural culinary infographic diagram in the "
        f"'Cooking for Engineers' tabular block-grid style for '{title}'. "
        "Left column lists ingredients vertically in chronological order of use; "
        f"adjacent rectangular blocks to the right span the exact rows they combine ({grid_summary}), "
        "converging into a single unified full-height block on the far right. "
        "Warm cream paper background (#FAF7F2), crisp dark espresso lines (#1C1917), "
        "terracotta (#C84B31) and sage (#4A6B53) accents, legible minimalist sans-serif typography."
    )
    return hero_prompt, grid_prompt


def call_nano_banana(
    prompt: str,
    output_path: Path,
    model: str = "gemini-nano-banana-2.1",
    dry_run: bool = False,
) -> bool:
    """
    Calls the Gemini Nano Banana REST endpoint to generate an image and write it to output_path.
    Returns True if an image was saved, or False if skipped / unavailable.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if dry_run or not api_key:
        reason = "--dry-run enabled" if dry_run else "GEMINI_API_KEY not set in environment"
        print(f"[SKIP] {reason}. Skipping live Nano Banana API call for {output_path.as_posix()}.")
        print(f"  Target File : {output_path.as_posix()}")
        print(f"  Model       : {model}")
        print(f"  Prompt      : {prompt}\n")
        return False

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload: Dict[str, object] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        print(
            f"[ERROR] Nano Banana API returned HTTP {exc.code} for model '{model}': {err_body}",
            file=sys.stderr,
        )
        return False
    except urllib.error.URLError as exc:
        print(f"[ERROR] Network error calling Nano Banana API: {exc}", file=sys.stderr)
        return False

    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                img_bytes = base64.b64decode(inline["data"])
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(img_bytes)
                print(f"[OK] Saved Nano Banana image to {output_path.as_posix()}")
                return True

    print(f"[WARN] No image block returned from Nano Banana API for {output_path.as_posix()}.")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate editorial recipe hero photography and Cooking for Engineers visuals via Nano Banana."
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Recipe slug, e.g., homemade-ramen-kewpie-slaw",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Recipe title",
    )
    parser.add_argument(
        "--visual-cue",
        required=True,
        help="Key visual description of finished dish",
    )
    parser.add_argument(
        "--grid-summary",
        required=True,
        help="Text summary of the Cooking for Engineers block grid",
    )
    parser.add_argument(
        "--model",
        default="gemini-nano-banana-2.1",
        choices=SUPPORTED_MODELS,
        help="Nano Banana model ID (default: gemini-nano-banana-2.1)",
    )
    parser.add_argument(
        "--output-dir",
        default="assets/images/recipes",
        help="Output directory for generated images (default: assets/images/recipes)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prepared prompts and target paths without calling the live API",
    )

    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    hero_out = out_dir / f"{args.slug}-hero.jpg"
    grid_out = out_dir / f"{args.slug}-grid.jpg"

    hero_prompt, grid_prompt = build_prompts(
        title=args.title,
        visual_cue=args.visual_cue,
        grid_summary=args.grid_summary,
    )

    print("=" * 80)
    print(f" NANO BANANA RECIPE VISUAL ARCHITECT - {args.title} ({args.slug})")
    print("=" * 80)

    call_nano_banana(hero_prompt, hero_out, model=args.model, dry_run=args.dry_run)
    call_nano_banana(grid_prompt, grid_out, model=args.model, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
