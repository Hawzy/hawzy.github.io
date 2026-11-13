#!/usr/bin/env python3
"""
Consolidation Engine for Weekly Grocery Fulfillment.

Fetches the weekly menu from the recipe blog API or local file, scales ingredient
quantities according to meal scale factors, filters out pantry staples, aggregates
identical items into consolidated line items, and maintains an idempotency ledger.

Python 3 standard library only.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple, Union
import urllib.parse
import urllib.request
import urllib.error


class AlreadyFulfilledError(Exception):
    """Raised when an order for the given week has already been fulfilled and no force override was given."""
    pass


def fetch_menu(source: str) -> Dict[str, Any]:
    """
    Fetches the weekly menu JSON payload from a HTTP/HTTPS URL, file:// URI,
    or a local filesystem path.
    """
    if source.startswith("file://"):
        parsed = urllib.parse.urlparse(source)
        file_path = urllib.request.url2pathname(parsed.path)
        if os.name == "nt" and file_path.startswith("\\") and len(file_path) > 2 and file_path[2] == ":":
            file_path = file_path.lstrip("\\")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if source.startswith("http://") or source.startswith("https://"):
        try:
            req = urllib.request.Request(
                source,
                headers={"User-Agent": "GroceryConsolidator/1.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except urllib.error.URLError as e:
            # Fallback for default local dev server when offline
            fallback_candidates = [
                Path(__file__).resolve().parents[4] / "_site" / "api" / "weekly-menu.json",
                Path.cwd() / "_site" / "api" / "weekly-menu.json",
                Path("C:/github/agy/blog/_site/api/weekly-menu.json"),
            ]
            fallback_path = next((c for c in fallback_candidates if c.exists()), fallback_candidates[0])
            if fallback_path.exists():
                sys.stderr.write(
                    f"Notice: Could not connect to {source} ({e}). Falling back to local file: {fallback_path}\n"
                )
                with open(fallback_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            raise

    # Local file path
    path = Path(source)
    if not path.is_file():
        # Try relative to repo root or sibling blog repo if path not found directly
        for root_candidate in (Path(__file__).resolve().parents[4], Path("C:/github/agy/blog")):
            candidate = root_candidate / source
            if candidate.is_file():
                path = candidate
                break
        else:
            raise FileNotFoundError(f"Cannot find menu JSON file at: {source}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_untested_warnings(menu_data: Dict[str, Any]) -> List[str]:
    """
    Returns non-blocking warning strings for any scheduled meal in `menu_data`
    whose recipe `status` is 'untested'.
    """
    if not menu_data or not isinstance(menu_data, dict):
        return []
    warnings: List[str] = []
    for meal in menu_data.get("meals") or []:
        if not meal or not isinstance(meal, dict):
            continue
        status = str(meal.get("status", "")).strip().lower()
        if status == "untested":
            day = meal.get("day") or "Scheduled meal"
            title = meal.get("recipe_title") or meal.get("recipe_slug") or "Unknown recipe"
            warnings.append(
                f"{day}: '{title}' ({meal.get('recipe_slug', '')}) has status='untested' (not yet kitchen-tested)."
            )
    return warnings


def consolidate(menu_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Consolidates non-pantry ingredients across all meals in the weekly menu:
    - Applies meal scale factor (quantity * scale_factor)
    - Filters pantry_staple items into a separate skipped list
    - Aggregates non-pantry items by (item.strip().lower(), unit.strip().lower())
    - Preserves rich item metadata
    """
    if not menu_data or not isinstance(menu_data, dict):
        menu_data = {}

    week_of = menu_data.get("week_of", "")
    postal_code = menu_data.get("postal_code", "")
    preferred_retailer_key = menu_data.get("preferred_retailer_key", "")
    default_modality = menu_data.get("default_modality", "PICKUP")

    meals = menu_data.get("meals") or []
    cart_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
    pantry_map: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for meal in meals:
        if not meal or not isinstance(meal, dict):
            continue
        raw_scale = meal.get("scale_factor", 1.0)
        try:
            scale_factor = float(raw_scale) if raw_scale is not None else 1.0
        except (ValueError, TypeError):
            scale_factor = 1.0

        ingredients = meal.get("ingredients") or []
        for ing in ingredients:
            if not ing or not isinstance(ing, dict):
                continue
            item_raw = ing.get("item", "")
            if not item_raw or not isinstance(item_raw, str):
                continue
            unit_raw = ing.get("unit", "") or ""
            raw_qty = ing.get("quantity", 0.0)
            try:
                qty = float(raw_qty) if raw_qty is not None else 0.0
            except (ValueError, TypeError):
                qty = 0.0

            scaled_qty = qty * scale_factor
            is_pantry = bool(ing.get("pantry_staple", False))

            key = (item_raw.strip().lower(), str(unit_raw).strip().lower())

            target_map = pantry_map if is_pantry else cart_map
            if key not in target_map:
                target_map[key] = {
                    "item": item_raw.strip(),
                    "display_item": item_raw.strip(),
                    "quantity": 0.0,
                    "unit": str(unit_raw).strip(),
                    "category": ing.get("category", "") or "",
                    "retailer_query": ing.get("retailer_query", "") or "",
                    "preferred_upc": ing.get("preferred_upc", "") or "",
                }
            else:
                for field in ("category", "retailer_query", "preferred_upc"):
                    if not target_map[key][field] and ing.get(field):
                        target_map[key][field] = str(ing.get(field)).strip()
            target_map[key]["quantity"] = round(target_map[key]["quantity"] + scaled_qty, 4)

    return {
        "week_of": week_of,
        "postal_code": postal_code,
        "preferred_retailer_key": preferred_retailer_key,
        "default_modality": default_modality,
        "cart": list(cart_map.values()),
        "skipped_pantry": list(pantry_map.values()),
        "warnings": collect_untested_warnings(menu_data),
    }


def process_ledger(
    ledger_path: Union[str, Path],
    week_of: str,
    cart: List[Dict[str, Any]],
    dry_run: bool = False,
    force: bool = False,
) -> Optional[str]:
    """
    Checks the cart ledger for previous fulfillments and updates the ledger on live runs.
    Returns a warning message string if previous fulfillment detected during dry run.
    Raises AlreadyFulfilledError if previously fulfilled during non-dry run without force.
    """
    ledger_file = Path(ledger_path)
    ledger_data: Dict[str, Any] = {}

    if ledger_file.exists():
        try:
            with open(ledger_file, "r", encoding="utf-8") as f:
                ledger_data = json.load(f)
        except Exception:
            ledger_data = {}

    if week_of in ledger_data:
        prior_entry = ledger_data[week_of]
        timestamp = (
            prior_entry.get("fulfilled_at", "unknown")
            if isinstance(prior_entry, dict)
            else str(prior_entry)
        )
        warn_msg = f"Week of {week_of} was previously fulfilled at {timestamp}"
        if dry_run:
            return warn_msg
        if not force:
            raise AlreadyFulfilledError(
                f"{warn_msg}. Use --force to override."
            )

    if not dry_run:
        now_iso = datetime.now(timezone.utc).isoformat()
        ledger_data[week_of] = {
            "fulfilled_at": now_iso,
            "item_count": len(cart),
            "cart": cart,
        }
        ledger_file.parent.mkdir(parents=True, exist_ok=True)
        with open(ledger_file, "w", encoding="utf-8") as f:
            json.dump(ledger_data, f, indent=2)

    return None


def format_table(items: List[Dict[str, Any]], title: str) -> str:
    """Formats an ingredient list into a clean ASCII table."""
    lines = []
    lines.append("=" * 80)
    lines.append(f" {title.upper()}")
    lines.append("=" * 80)
    lines.append(f"{'ITEM':<25} {'QTY':<8} {'UNIT':<10} {'CATEGORY':<18} {'RETAILER QUERY / UPC'}")
    lines.append("-" * 80)
    for it in items:
        qty_str = f"{it['quantity']:g}"
        upc_info = it.get('retailer_query', '')
        if it.get('preferred_upc'):
            upc_info += f" ({it['preferred_upc']})"
        lines.append(
            f"{it['display_item']:<25} {qty_str:<8} {it['unit']:<10} {it.get('category', ''):<18} {upc_info}"
        )
    lines.append("-" * 80)
    lines.append(f"Total Line Items: {len(items)}\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity Weekly Grocery Fulfillment & Consolidation Engine"
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:4000/api/weekly-menu.json",
        help="URL or local path to weekly-menu.json (default: http://127.0.0.1:4000/api/weekly-menu.json)",
    )
    parser.add_argument(
        "--ledger",
        default=".cache/cart_ledger.json",
        help="Path to idempotency ledger JSON (default: .cache/cart_ledger.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run consolidation without modifying the cart ledger",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force fulfillment even if week was already recorded in ledger",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_only",
        help="Output raw JSON summary only (suitable for piping)",
    )

    args = parser.parse_args()

    try:
        menu_data = fetch_menu(args.url)
    except Exception as e:
        sys.stderr.write(f"Error fetching menu: {e}\n")
        sys.exit(1)

    consolidated = consolidate(menu_data)
    week_of = consolidated.get("week_of") or "unknown"
    for untested_msg in consolidated.get("warnings") or []:
        sys.stderr.write(f"[UNTESTED RECIPE NOTICE] {untested_msg}\n")

    try:
        warn = process_ledger(
            ledger_path=args.ledger,
            week_of=week_of,
            cart=consolidated["cart"],
            dry_run=args.dry_run,
            force=args.force,
        )
        if warn:
            sys.stderr.write(f"[IDEMPOTENCY WARNING] {warn}\n\n")
    except AlreadyFulfilledError as afe:
        sys.stderr.write(f"[IDEMPOTENCY ERROR] {afe}\n")
        sys.exit(2)

    if args.json_only:
        print(json.dumps(consolidated, indent=2))
        return

    # Human-readable summary output
    print("=" * 80)
    print(f" GROCERY FULFILLMENT ORDER SUMMARY")
    print(f" Week Of: {week_of} | Modality: {consolidated.get('default_modality')} | Retailer: {consolidated.get('preferred_retailer_key')} ({consolidated.get('postal_code')})")
    if args.dry_run:
        print(" MODE: DRY RUN (Ledger will not be updated)")
    print("=" * 80 + "\n")

    print(format_table(consolidated["cart"], "Consolidated Shopping Cart (To Order)"))
    print(format_table(consolidated["skipped_pantry"], "Skipped Pantry Staples (Scale-Adjusted)"))

    print("=" * 80)
    print(" CONSOLIDATED CART JSON PAYLOAD")
    print("=" * 80)
    print(json.dumps(consolidated, indent=2))


if __name__ == "__main__":
    main()
