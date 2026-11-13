import base64
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEWER_SCRIPTS = REPO_ROOT / ".agents" / "skills" / "recipe-reviewer" / "scripts"
if str(REVIEWER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REVIEWER_SCRIPTS))

import audit_recipes
import generate_recipe_visuals


class TestRecipeReviewerSkill(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_all_seed_recipes_pass_pre_publish_audit(self):
        recipe_files = sorted((REPO_ROOT / "_recipes").glob("*.md"))
        self.assertEqual(len(recipe_files), 6)
        for rf in recipe_files:
            rep = audit_recipes.audit_file(rf)
            self.assertTrue(
                rep["passed"],
                f"Seed recipe {rf.name} failed pre_publish audit: {rep['errors']}",
            )
            self.assertGreaterEqual(rep["chip_steps"], 3)
            self.assertGreaterEqual(rep["bold_control_steps"], 3)
            self.assertGreaterEqual(rep["grid_rows"], rep["ingredient_count"])

    def test_auditor_catches_chronology_inline_bold_and_schema_prefix_flaws(self):
        flawed_data = {
            "title": "Flawed Draft",
            "slug": "flawed-draft",
            "ingredients": [
                {"item": "noodles", "display_text": "2 packs noodles"},
                {"item": "eggs", "display_text": "2 large eggs"},
            ],
            "instructions": [
                "Step 1: Boil the eggs in a 2-quart pot until jammy.",
                "Boil the noodles in a 4-quart pot until springy.",
            ],
            "engineer_grid_html": "",
        }
        rep = audit_recipes.audit_recipe_data(flawed_data, source_name="flawed.md")
        self.assertFalse(rep["passed"])
        joined = "\n".join(rep["errors"])
        self.assertIn("Rule 6 - Schema Hygiene", joined)
        self.assertIn("Rule 3 - Inline Measurements", joined)
        self.assertIn("Rule 1 - Chronology", joined)
        self.assertIn("Rule 5 - Engineer Block Grid", joined)

    def test_block_grid_validator_catches_jagged_or_colliding_spans(self):
        # Row 0 spans 2 rows at col 3, AND Row 1 adds an extra cell that makes Row 1 wider than Row 0
        jagged_html = """
        <table class="engineer-grid-table">
          <tbody>
            <tr>
              <td class="ing-qty">2</td>
              <td class="ing-unit">cup</td>
              <td class="ing-name">broth</td>
              <td class="action-cell" rowspan="2">Simmer</td>
            </tr>
            <tr>
              <td class="ing-qty">1</td>
              <td class="ing-unit">tsp</td>
              <td class="ing-name">soy sauce</td>
              <td class="action-cell">Extra</td>
            </tr>
          </tbody>
        </table>
        """
        errors, _ = audit_recipes.validate_engineer_grid(jagged_html, expected_min_rows=2)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Jagged" in e or "Final assembly" in e for e in errors))

    def test_block_grid_validator_accepts_stretched_downstream_ing_name(self):
        stretched_html = """
        <table class="engineer-grid-table">
          <thead>
            <tr>
              <th scope="col">Qty</th>
              <th scope="col">Unit</th>
              <th scope="col">Ingredient</th>
              <th scope="col" colspan="2">Order of Operations (Read Left to Right)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="ing-qty">4</td>
              <td class="ing-unit">cup</td>
              <td class="ing-name">broth</td>
              <td class="action-cell action-cell--heat">Simmer 5m</td>
              <td class="action-cell action-cell--finish" rowspan="2">Top with scallions &amp; serve</td>
            </tr>
            <tr>
              <td class="ing-qty">1</td>
              <td class="ing-unit">stalk</td>
              <td class="ing-name" colspan="2">scallions, sliced</td>
            </tr>
          </tbody>
        </table>
        """
        errors, ing_names = audit_recipes.validate_engineer_grid(stretched_html, expected_min_rows=2)
        self.assertEqual(errors, [])
        self.assertEqual(len(ing_names), 2)

    def test_block_grid_validator_supports_multi_table_subgrids(self):
        multi_html = """
        <div class="engineer-subgrid">
          <table class="engineer-grid-table">
            <caption class="engineer-subgrid__caption">Part 1 &mdash; Sauce</caption>
            <thead>
              <tr>
                <th scope="col">Qty</th>
                <th scope="col">Unit</th>
                <th scope="col">Ingredient</th>
                <th scope="col" colspan="2">Order of Operations (Read Left to Right)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="ing-qty">1/3</td>
                <td class="ing-unit">cup</td>
                <td class="ing-name">chicken broth</td>
                <td class="action-cell action-cell--prep" rowspan="2">Whisk together</td>
                <td class="action-cell action-cell--finish" rowspan="2">Stage sauce for Part 2</td>
              </tr>
              <tr>
                <td class="ing-qty">1</td>
                <td class="ing-unit">tsp</td>
                <td class="ing-name">dark soy sauce</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="engineer-subgrid">
          <table class="engineer-grid-table">
            <caption class="engineer-subgrid__caption">Part 2 &mdash; Stir-Fry</caption>
            <thead>
              <tr>
                <th scope="col">Qty</th>
                <th scope="col">Unit</th>
                <th scope="col">Ingredient</th>
                <th scope="col" colspan="3">Order of Operations (Read Left to Right)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="ing-qty">1</td>
                <td class="ing-unit">lb</td>
                <td class="ing-name">flank steak</td>
                <td class="action-cell action-cell--heat">Sear crisp</td>
                <td class="action-cell action-cell--heat" rowspan="2">Toss with Part 1 sauce</td>
                <td class="action-cell action-cell--finish" rowspan="2">Serve over rice</td>
              </tr>
              <tr>
                <td class="ing-qty">&mdash;</td>
                <td class="ing-unit">Part 1</td>
                <td class="ing-name engineer-subgrid-ref" colspan="2">prepared sauce</td>
              </tr>
            </tbody>
          </table>
        </div>
        """
        errors, ing_names = audit_recipes.validate_engineer_grid(multi_html, expected_min_rows=3)
        self.assertEqual(errors, [])
        self.assertEqual(len(ing_names), 4)

    def test_tiered_ingredient_matching_avoids_generic_head_collisions(self):
        steps = [
            "Marinate flank steak `1 lb` with low-sodium soy sauce `1 tbsp` and neutral oil `1 tbsp`.",
            "Whisk low-sodium soy sauce `1/4 cup`, dark soy sauce `1 1/2 tsp`, and toasted sesame oil `1 tsp`.",
            "Stir-fry white onion `1 medium` and scallion whites `6 whites`, then finish with scallion greens `6 greens`.",
        ]
        dark_soy = {"item": "dark soy sauce", "display_text": "1 1/2 tsp Chinese dark soy sauce"}
        sesame_oil = {"item": "toasted sesame oil", "display_text": "1 tsp pure toasted sesame oil"}
        scallion = {
            "item": "scallion",
            "display_text": "6 fresh scallions, whites and greens divided",
        }
        self.assertEqual([m[0] for m in audit_recipes.find_ingredient_mentions(dark_soy, steps)], [1])
        self.assertEqual([m[0] for m in audit_recipes.find_ingredient_mentions(sesame_oil, steps)], [1])
        self.assertEqual([m[0] for m in audit_recipes.find_ingredient_mentions(scallion, steps)], [2])

    def test_generate_recipe_visuals_graceful_skip_without_api_key(self):
        env = dict(os.environ)
        env.pop("GEMINI_API_KEY", None)
        script_path = REVIEWER_SCRIPTS / "generate_recipe_visuals.py"
        res = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--slug",
                "homemade-ramen-kewpie-slaw",
                "--title",
                "Weeknight Shoyu Ramen",
                "--visual-cue",
                "Rich shoyu broth, jammy 6.5-minute egg halves",
                "--grid-summary",
                "Boil eggs 6.5m; simmer broth 5m; assemble all",
                "--output-dir",
                self.temp_dir,
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("[SKIP]", res.stdout)
        self.assertIn("Editorial food photography of Weeknight Shoyu Ramen", res.stdout)
        self.assertIn("Cooking for Engineers", res.stdout)

    def test_generate_recipe_visuals_writes_images_with_mocked_api(self):
        fake_jpeg = b"\xff\xd8\xff\xe0MOCK_NANO_BANANA_JPEG\xff\xd9"
        mock_payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": "image/jpeg",
                                    "data": base64.b64encode(fake_jpeg).decode("utf-8"),
                                }
                            }
                        ]
                    }
                }
            ]
        }

        class FakeHTTPResponse(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()

        out_path = Path(self.temp_dir) / "test-hero.jpg"
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-dummy-key"}):
            with mock.patch(
                "urllib.request.urlopen",
                return_value=FakeHTTPResponse(json.dumps(mock_payload).encode("utf-8")),
            ) as mocked_open:
                ok = generate_recipe_visuals.call_nano_banana(
                    prompt="Test prompt",
                    output_path=out_path,
                    model="gemini-nano-banana-2.1",
                )
                self.assertTrue(ok)
                self.assertTrue(out_path.is_file())
                self.assertEqual(out_path.read_bytes(), fake_jpeg)
                sent_req = mocked_open.call_args[0][0]
                self.assertEqual(sent_req.get_header("X-goog-api-key"), "test-dummy-key")


if __name__ == "__main__":
    unittest.main()
