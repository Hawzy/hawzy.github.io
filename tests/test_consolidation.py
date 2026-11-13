import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add the script directory to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".agents" / "skills" / "weekly-grocery-order" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import consolidate_menu


class TestGroceryConsolidation(unittest.TestCase):
    def setUp(self):
        self.sample_menu = {
            "week_of": "2026-10-25",
            "default_modality": "PICKUP",
            "postal_code": "99223",
            "preferred_retailer_key": "fred-meyer",
            "meals": [
                {
                    "day": "Monday",
                    "recipe_slug": "overnight-dry-brined-ribeye",
                    "scale_factor": 1.0,
                    "notes": "Family dinner kick-off",
                    "recipe_title": "Overnight Dry-Brined Cast-Iron Ribeye Steak",
                    "recipe_url": "https://hawzy.github.io/recipes/overnight-dry-brined-ribeye/",
                    "ingredients": [
                        {
                            "item": "ribeye steak",
                            "quantity": 2,
                            "unit": "steak",
                            "category": "Meat & Seafood",
                            "pantry_staple": False,
                            "retailer_query": "bone-in ribeye steak",
                            "preferred_upc": "0001111041523"
                        },
                        {
                            "item": "kosher salt",
                            "quantity": 2,
                            "unit": "tsp",
                            "category": "Spices & Seasonings",
                            "pantry_staple": True,
                            "retailer_query": "diamond crystal kosher salt",
                            "preferred_upc": "0001360001005"
                        },
                        {
                            "item": "garlic clove",
                            "quantity": 4,
                            "unit": "clove",
                            "category": "Produce",
                            "pantry_staple": False,
                            "retailer_query": "fresh garlic bulb",
                            "preferred_upc": "0003338311001"
                        }
                    ]
                },
                {
                    "day": "Wednesday",
                    "recipe_slug": "citrus-chile-glazed-salmon",
                    "scale_factor": 1.5,
                    "notes": "Extra portions for lunch prep",
                    "recipe_title": "Pan-Seared Salmon with Citrus-Chile Glaze",
                    "recipe_url": "https://hawzy.github.io/recipes/citrus-chile-glazed-salmon/",
                    "ingredients": [
                        {
                            "item": "salmon fillet",
                            "quantity": 4,
                            "unit": "fillet",
                            "category": "Meat & Seafood",
                            "pantry_staple": False,
                            "retailer_query": "fresh atlantic salmon fillets",
                            "preferred_upc": "0001111041999"
                        },
                        {
                            "item": "garlic clove",
                            "quantity": 3,
                            "unit": "clove",
                            "category": "Produce",
                            "pantry_staple": False,
                            "retailer_query": "fresh garlic bulb",
                            "preferred_upc": "0003338311001"
                        },
                        {
                            "item": "lime",
                            "quantity": 2,
                            "unit": "lime",
                            "category": "Produce",
                            "pantry_staple": False,
                            "retailer_query": "fresh limes",
                            "preferred_upc": "0003338311018"
                        },
                        {
                            "item": "honey",
                            "quantity": 2,
                            "unit": "tbsp",
                            "category": "Pantry",
                            "pantry_staple": True,
                            "retailer_query": "wildflower honey 12oz",
                            "preferred_upc": "0001111082050"
                        }
                    ]
                },
                {
                    "day": "Friday",
                    "recipe_slug": "homemade-ramen-kewpie-slaw",
                    "scale_factor": 1.0,
                    "notes": "Fun Friday family dinner",
                    "recipe_title": "Weeknight Shoyu Ramen with Japanese Kewpie Slaw",
                    "recipe_url": "https://hawzy.github.io/recipes/homemade-ramen-kewpie-slaw/",
                    "ingredients": [
                        {
                            "item": "garlic clove",
                            "quantity": 2,
                            "unit": "clove",
                            "category": "Produce",
                            "pantry_staple": False,
                            "retailer_query": "fresh garlic bulb",
                            "preferred_upc": "0003338311001"
                        },
                        {
                            "item": "lime",
                            "quantity": 1,
                            "unit": "lime",
                            "category": "Produce",
                            "pantry_staple": False,
                            "retailer_query": "fresh limes",
                            "preferred_upc": "0003338311018"
                        },
                        {
                            "item": "soy sauce",
                            "quantity": 2,
                            "unit": "tbsp",
                            "category": "Condiments",
                            "pantry_staple": True,
                            "retailer_query": "kikkoman soy sauce",
                            "preferred_upc": "0001111082160"
                        }
                    ]
                }
            ]
        }
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scale_factor_multiplication(self):
        single_meal_menu = {
            "week_of": "2026-10-25",
            "meals": [
                {
                    "scale_factor": 1.5,
                    "ingredients": [
                        {
                            "item": "salmon fillet",
                            "quantity": 4,
                            "unit": "fillet",
                            "category": "Meat & Seafood",
                            "pantry_staple": False,
                            "retailer_query": "fresh atlantic salmon fillets",
                            "preferred_upc": "0001111041999"
                        }
                    ]
                }
            ]
        }
        result = consolidate_menu.consolidate(single_meal_menu)
        cart = result["cart"]
        self.assertEqual(len(cart), 1)
        # 4 * 1.5 = 6.0
        self.assertEqual(cart[0]["quantity"], 6.0)
        self.assertEqual(cart[0]["item"], "salmon fillet")
        self.assertEqual(cart[0]["unit"], "fillet")

    def test_skipping_pantry_staple_items(self):
        result = consolidate_menu.consolidate(self.sample_menu)
        cart = result["cart"]
        skipped = result["skipped_pantry"]

        # Ensure no pantry staples in cart
        cart_items = [c["item"].lower() for c in cart]
        self.assertNotIn("kosher salt", cart_items)
        self.assertNotIn("honey", cart_items)
        self.assertNotIn("soy sauce", cart_items)

        # Ensure pantry staples are captured in skipped list with scaled quantities
        skipped_dict = {(s["item"].lower(), s["unit"].lower()): s["quantity"] for s in skipped}
        self.assertIn(("kosher salt", "tsp"), skipped_dict)
        self.assertEqual(skipped_dict[("kosher salt", "tsp")], 2.0 * 1.0)
        self.assertIn(("honey", "tbsp"), skipped_dict)
        self.assertEqual(skipped_dict[("honey", "tbsp")], 2.0 * 1.5)  # 3.0
        self.assertIn(("soy sauce", "tbsp"), skipped_dict)
        self.assertEqual(skipped_dict[("soy sauce", "tbsp")], 2.0 * 1.0)

    def test_aggregation_of_identical_pairs(self):
        result = consolidate_menu.consolidate(self.sample_menu)
        cart = result["cart"]
        cart_dict = {(c["item"].lower(), c["unit"].lower()): c for c in cart}

        # garlic clove:
        # Meal 1: 4 * 1.0 = 4.0
        # Meal 2: 3 * 1.5 = 4.5
        # Meal 3: 2 * 1.0 = 2.0
        # Total: 10.5
        self.assertIn(("garlic clove", "clove"), cart_dict)
        self.assertAlmostEqual(cart_dict[("garlic clove", "clove")]["quantity"], 10.5)

        # lime:
        # Meal 2: 2 * 1.5 = 3.0
        # Meal 3: 1 * 1.0 = 1.0
        # Total: 4.0
        self.assertIn(("lime", "lime"), cart_dict)
        self.assertAlmostEqual(cart_dict[("lime", "lime")]["quantity"], 4.0)

        # ribeye steak:
        # Meal 1: 2 * 1.0 = 2.0
        self.assertIn(("ribeye steak", "steak"), cart_dict)
        self.assertAlmostEqual(cart_dict[("ribeye steak", "steak")]["quantity"], 2.0)

        # salmon fillet:
        # Meal 2: 4 * 1.5 = 6.0
        self.assertIn(("salmon fillet", "fillet"), cart_dict)
        self.assertAlmostEqual(cart_dict[("salmon fillet", "fillet")]["quantity"], 6.0)

    def test_idempotency_ledger(self):
        ledger_path = Path(self.temp_dir) / "cart_ledger.json"

        # 1. In dry-run mode, ledger should NOT be created or written to
        warn_msg = consolidate_menu.process_ledger(
            ledger_path=ledger_path,
            week_of="2026-10-25",
            cart=consolidate_menu.consolidate(self.sample_menu)["cart"],
            dry_run=True
        )
        self.assertFalse(ledger_path.exists())
        self.assertIsNone(warn_msg)

        # 2. Live run creates the ledger entry
        consolidate_menu.process_ledger(
            ledger_path=ledger_path,
            week_of="2026-10-25",
            cart=consolidate_menu.consolidate(self.sample_menu)["cart"],
            dry_run=False
        )
        self.assertTrue(ledger_path.exists())
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger_data = json.load(f)
        self.assertIn("2026-10-25", ledger_data)
        self.assertIn("fulfilled_at", ledger_data["2026-10-25"])

        # 3. Subsequent dry-run warns of prior fulfillment
        dry_run_warn = consolidate_menu.process_ledger(
            ledger_path=ledger_path,
            week_of="2026-10-25",
            cart=consolidate_menu.consolidate(self.sample_menu)["cart"],
            dry_run=True
        )
        self.assertIsNotNone(dry_run_warn)
        self.assertIn("Week of 2026-10-25 was previously fulfilled at", dry_run_warn)

        # 4. Subsequent live run raises error/prevent rerun unless forced
        with self.assertRaises(consolidate_menu.AlreadyFulfilledError):
            consolidate_menu.process_ledger(
                ledger_path=ledger_path,
                week_of="2026-10-25",
                cart=consolidate_menu.consolidate(self.sample_menu)["cart"],
                dry_run=False,
                force=False
            )

        # 5. Live run with force succeeds and updates timestamp
        consolidate_menu.process_ledger(
            ledger_path=ledger_path,
            week_of="2026-10-25",
            cart=consolidate_menu.consolidate(self.sample_menu)["cart"],
            dry_run=False,
            force=True
        )
        with open(ledger_path, "r", encoding="utf-8") as f:
            updated_data = json.load(f)
        self.assertIn("2026-10-25", updated_data)

    def test_fetch_menu_local_file(self):
        menu_path = Path(self.temp_dir) / "menu.json"
        with open(menu_path, "w", encoding="utf-8") as f:
            json.dump(self.sample_menu, f)

        # Direct path
        loaded = consolidate_menu.fetch_menu(str(menu_path))
        self.assertEqual(loaded["week_of"], "2026-10-25")

        # file:// URI
        file_uri = menu_path.as_uri()
        loaded_uri = consolidate_menu.fetch_menu(file_uri)
        self.assertEqual(loaded_uri["week_of"], "2026-10-25")

    def test_scale_factor_default_missing(self):
        menu_missing_scale = {
            "week_of": "2026-10-25",
            "meals": [
                {
                    "ingredients": [
                        {
                            "item": "lime",
                            "quantity": 3,
                            "unit": "lime",
                            "pantry_staple": False
                        }
                    ]
                }
            ]
        }
        res = consolidate_menu.consolidate(menu_missing_scale)
        self.assertEqual(res["cart"][0]["quantity"], 3.0)

    def test_format_table(self):
        cart = consolidate_menu.consolidate(self.sample_menu)["cart"]
        table_output = consolidate_menu.format_table(cart, "Test Cart")
        self.assertIn("TEST CART", table_output)
        self.assertIn("garlic clove", table_output)
        self.assertIn("salmon fillet", table_output)

    def test_handle_none_meals_and_ingredients(self):
        # meals is None
        menu_none_meals = {"week_of": "2026-10-25", "meals": None}
        res1 = consolidate_menu.consolidate(menu_none_meals)
        self.assertEqual(res1["cart"], [])
        self.assertEqual(res1["skipped_pantry"], [])

        # meals has None or ingredients is None
        menu_none_ingredients = {
            "week_of": "2026-10-25",
            "meals": [
                None,
                {"scale_factor": 1.0, "ingredients": None},
                {
                    "scale_factor": 1.0,
                    "ingredients": [
                        None,
                        {
                            "item": "garlic clove",
                            "quantity": 2,
                            "unit": "clove",
                            "pantry_staple": False
                        }
                    ]
                }
            ]
        }
        res2 = consolidate_menu.consolidate(menu_none_ingredients)
        self.assertEqual(len(res2["cart"]), 1)
        self.assertEqual(res2["cart"][0]["item"], "garlic clove")
        self.assertEqual(res2["cart"][0]["quantity"], 2.0)

    def test_handle_none_or_invalid_menu_data(self):
        # None or non-dict input
        res_none = consolidate_menu.consolidate(None)
        self.assertEqual(res_none["cart"], [])
        self.assertEqual(res_none["skipped_pantry"], [])

        res_str = consolidate_menu.consolidate("not-a-dict")
        self.assertEqual(res_str["cart"], [])
        self.assertEqual(res_str["skipped_pantry"], [])

    def test_untested_meal_emits_non_blocking_warning(self):
        menu = {
            "week_of": "2026-11-08",
            "meals": [
                {
                    "day": "Monday",
                    "recipe_slug": "ribeye",
                    "recipe_title": "Ribeye",
                    "status": "untested",
                    "scale_factor": 1.0,
                    "ingredients": [],
                },
                {
                    "day": "Tuesday",
                    "recipe_slug": "ramen",
                    "recipe_title": "Ramen",
                    "status": "tested",
                    "scale_factor": 1.0,
                    "ingredients": [],
                },
            ],
        }
        warnings = consolidate_menu.collect_untested_warnings(menu)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Ribeye", warnings[0])
        self.assertIn("untested", warnings[0].lower())


if __name__ == "__main__":
    unittest.main()

