"""
End-to-End Verification and Safety Audit Suite.

Covers all 7 Definition of Done requirements:
1. Build hygiene check
2. Server HTTP status check
3. JSON API validation (weekly-menu.json and recipes.json)
4. llms.txt validation
5. Schema.org JSON-LD linked data validation
6. Agent consolidation engine dry-run and ingredient summation check
7. Git safety invariant check
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest
import urllib.request

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".agents" / "skills" / "weekly-grocery-order" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import consolidate_menu


class TestEndToEndVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_url = "http://127.0.0.1:4000"
        cls.expected_menu_slugs = {
            "crispy-mongolian-beef-broccoli",
            "blackstone-shabu-steak-fried-rice",
        }
        cls.expected_catalog_slugs = {
            "crispy-mongolian-beef-broccoli",
            "blackstone-shabu-steak-fried-rice",
            "homemade-pork-napa-cabbage-dumplings",
        }
        try:
            with urllib.request.urlopen(f"{cls.server_url}/", timeout=1):
                cls.server_available = True
        except Exception:
            cls.server_available = False

    def test_01_build_hygiene(self):
        """Requirement 1: Verify prohibited files do not leak into _site/."""
        self.assertTrue((REPO_ROOT / "_site").is_dir(), "_site directory does not exist or is not a directory")
        prohibited = [
            "_site/.agents",
            "_site/.agent",
            "_site/agent",
            "_site/.cache",
            "_site/.venv",
            "_site/AGENTS.md",
            "_site/Gemfile",
            "_site/Gemfile.lock",
            "_site/tests",
            "_site/_drafts",
        ]
        for path_str in prohibited:
            full_path = REPO_ROOT / path_str
            self.assertFalse(
                full_path.exists(),
                f"Prohibited path leaked into site build: {path_str}"
            )

    def test_02_server_http_status(self):
        """Requirement 2: Local server responds with 200 on root."""
        if not self.server_available:
            self.skipTest("Jekyll server is not running on port 4000. Start with: bundle exec jekyll serve --port 4000")
        req = urllib.request.Request(
            f"{self.server_url}/",
            headers={"User-Agent": "E2ETester/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)

    def test_03_json_api_validation(self):
        """Requirement 3: Validate weekly-menu.json and recipes.json APIs."""
        if not self.server_available:
            self.skipTest("Jekyll server is not running on port 4000. Start with: bundle exec jekyll serve --port 4000")
        # Validate weekly-menu.json
        with urllib.request.urlopen(f"{self.server_url}/api/weekly-menu.json", timeout=5) as r:
            menu = json.loads(r.read().decode("utf-8"))
        self.assertIn("week_of", menu)
        self.assertIn("default_modality", menu)
        self.assertIn("meals", menu)

        menu_slugs = {m["recipe_slug"] for m in menu["meals"]}
        self.assertEqual(menu_slugs, self.expected_menu_slugs)

        # Validate recipes.json
        with urllib.request.urlopen(f"{self.server_url}/api/recipes.json", timeout=5) as r:
            recipes = json.loads(r.read().decode("utf-8"))
        self.assertIsInstance(recipes, list)
        self.assertEqual(len(recipes), len(self.expected_catalog_slugs))

        recipes_slugs = {rec["slug"] for rec in recipes}
        self.assertEqual(recipes_slugs, self.expected_catalog_slugs)

        for rec in recipes:
            self.assertTrue(rec.get("title"))
            self.assertTrue(rec.get("slug"))
            self.assertTrue(rec.get("excerpt"))
            self.assertIsInstance(rec.get("categories"), list)
            self.assertIsInstance(rec.get("tags"), list)
            self.assertIsInstance(rec.get("ingredients"), list)
            self.assertGreater(len(rec["ingredients"]), 0)
            self.assertIsInstance(rec.get("instructions"), list)
            self.assertGreater(len(rec["instructions"]), 0)

            for ing in rec["ingredients"]:
                for field in [
                    "item",
                    "quantity",
                    "unit",
                    "display_text",
                    "category",
                    "pantry_staple",
                    "retailer_query",
                    "preferred_upc",
                ]:
                    self.assertIn(field, ing, f"Missing {field} in {ing} of {rec['slug']}")

    def test_04_llms_txt_validation(self):
        """Requirement 4: Validate /llms.txt formatting and links."""
        if not self.server_available:
            self.skipTest("Jekyll server is not running on port 4000. Start with: bundle exec jekyll serve --port 4000")
        with urllib.request.urlopen(f"{self.server_url}/llms.txt", timeout=5) as r:
            content = r.read().decode("utf-8")

        self.assertTrue(content.startswith("# "), "llms.txt must start with '# '")
        self.assertIn("\n> ", content, "llms.txt must contain a '> ' blockquote")
        self.assertIn("/api/weekly-menu.json", content)
        self.assertIn("/api/recipes.json", content)

        for slug in self.expected_catalog_slugs:
            self.assertIn(slug, content, f"Missing recipe slug link for {slug} in llms.txt")

    def test_05_json_ld_schema_validation(self):
        """Requirement 5: Extract and parse JSON-LD from all 3 recipe pages."""
        pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)

        for slug in self.expected_catalog_slugs:
            html_path = REPO_ROOT / "_site" / "recipes" / slug / "index.html"
            self.assertTrue(html_path.exists(), f"Recipe HTML not found: {html_path}")

            content = html_path.read_text(encoding="utf-8")
            matches = pattern.findall(content)
            self.assertGreater(len(matches), 0, f"No JSON-LD script found in {html_path}")

            recipe_schema = None
            for m in matches:
                try:
                    parsed = json.loads(m.strip())
                    if parsed.get("@type") == "Recipe":
                        recipe_schema = parsed
                        break
                except json.JSONDecodeError:
                    continue

            self.assertIsNotNone(recipe_schema, f"No Recipe @type JSON-LD found in {html_path}")
            self.assertEqual(recipe_schema.get("@context"), "https://schema.org")
            self.assertEqual(recipe_schema.get("@type"), "Recipe")
            self.assertTrue(recipe_schema.get("name"))
            self.assertIsNotNone(recipe_schema.get("recipeYield"))
            self.assertTrue(recipe_schema.get("prepTime", "").startswith("PT"))
            self.assertTrue(recipe_schema.get("cookTime", "").startswith("PT"))

            instructions = recipe_schema.get("recipeInstructions")
            self.assertIsInstance(instructions, list)
            self.assertGreater(len(instructions), 0)
            for step in instructions:
                self.assertEqual(step.get("@type"), "HowToStep")
                self.assertTrue(step.get("text"))

    def test_06_agent_consolidation_dry_run(self):
        """Requirement 6: Run consolidation engine against live server and verify math."""
        if not self.server_available:
            self.skipTest("Jekyll server is not running on port 4000. Start with: bundle exec jekyll serve --port 4000")
        menu_data = consolidate_menu.fetch_menu(f"{self.server_url}/api/weekly-menu.json")
        consolidated = consolidate_menu.consolidate(menu_data)

        cart = consolidated["cart"]
        cart_dict = {(item["item"].lower(), item["unit"].lower()): item for item in cart}

        # 1. garlic clove: Tue (4 * 1.0) + Fri (4 * 1.5) = 4 + 6 = 10.0
        self.assertIn(("garlic clove", "clove"), cart_dict)
        self.assertAlmostEqual(cart_dict[("garlic clove", "clove")]["quantity"], 10.0)

        # 2. scallion: Tue (6 * 1.0) + Fri (6 * 1.5) = 6 + 9 = 15.0
        self.assertIn(("scallion", "stalk"), cart_dict)
        self.assertAlmostEqual(cart_dict[("scallion", "stalk")]["quantity"], 15.0)

        # 3. flank steak: Tue (1 * 1.0) = 1.0
        self.assertIn(("flank steak", "lb"), cart_dict)
        self.assertAlmostEqual(cart_dict[("flank steak", "lb")]["quantity"], 1.0)

        # 4. shabu-shabu beef: Fri (1 * 1.5) = 1.5
        self.assertIn(("shabu-shabu beef", "lb"), cart_dict)
        self.assertAlmostEqual(cart_dict[("shabu-shabu beef", "lb")]["quantity"], 1.5)

        # 5. Verify pantry staples are excluded from cart and placed in skipped_pantry
        cart_item_names = {c["item"].lower() for c in cart}
        skipped_names = {s["item"].lower() for s in consolidated["skipped_pantry"]}

        for staple in ["kosher salt", "unsalted butter", "low-sodium soy sauce", "neutral oil", "toasted sesame oil"]:
            self.assertNotIn(staple, cart_item_names, f"{staple} unexpectedly in active cart")
            self.assertIn(staple, skipped_names, f"{staple} missing from skipped pantry list")

    def test_07_git_safety_check(self):
        """Requirement 7: Verify local branch is main or feat/agentic-recipe-blog, feature branches unpushed, and working tree clean."""
        res_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(REPO_ROOT),
        )
        current_branch = res_branch.stdout.strip()
        self.assertIn(current_branch, ("main", "feat/agentic-recipe-blog"))

        # Verify non-main feature branches have not been pushed upstream
        if current_branch != "main":
            res_remote = subprocess.run(
                ["git", "branch", "-r", "--list", f"origin/{current_branch}"],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(REPO_ROOT),
            )
            self.assertEqual(
                res_remote.stdout.strip(),
                "",
                f"Remote branch origin/{current_branch} unexpectedly exists! Autonomous agents must never push."
            )

        # Verify git status --porcelain is empty (no uncommitted/dirty files)
        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(
            res_status.stdout.strip(),
            "",
            f"Working tree is dirty:\n{res_status.stdout.strip()}"
        )

    def test_08_editorial_recipe_card_and_print_styles(self):
        """Requirement 8: Verify elevated recipe card, Jump/Print bar, scaling attributes, and @media print CSS."""
        if not self.server_available:
            self.skipTest("Jekyll server is not running on port 4000. Start with: bundle exec jekyll serve --port 4000")

        with urllib.request.urlopen(f"{self.server_url}/recipes/homemade-ramen-kewpie-slaw/", timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            html = resp.read().decode("utf-8")

        # Action bar & Jump/Print controls
        self.assertIn('class="recipe-top-actions"', html)
        self.assertIn('href="#recipe-card"', html)
        self.assertIn("Jump to Recipe", html)
        self.assertIn('onclick="window.print()"', html)

        # Elevated recipe card container & metadata grid
        self.assertIn('id="recipe-card"', html)
        self.assertIn("PREP TIME", html)
        self.assertIn("COOK TIME", html)
        self.assertIn("TOTAL TIME", html)
        self.assertIn("YIELD / CALORIES", html)

        # Interactive 1x/2x/3x scaler & Cook Mode wakeLock
        self.assertIn('data-scale="1"', html)
        self.assertIn('data-scale="2"', html)
        self.assertIn('data-scale="3"', html)
        self.assertIn('data-base-qty="', html)
        self.assertIn("navigator.wakeLock", html)

        # Optional image resilience: zero broken or empty <img src=""> tags when image is omitted
        self.assertNotIn('src=""', html)
        self.assertNotIn('class="recipe-hero-figure"', html)
        self.assertNotIn('class="recipe-card__thumb"', html)

        # Dedicated single-page print stylesheet in /assets/css/main.css
        with urllib.request.urlopen(f"{self.server_url}/assets/css/main.css", timeout=5) as css_resp:
            self.assertEqual(css_resp.status, 200)
            css = css_resp.read().decode("utf-8")

        self.assertIn("@media print", css)
        self.assertIn("#recipe-card", css)
        self.assertIn("page-break-inside:avoid", css.replace(" ", ""))
        self.assertIn("#FAF7F2", css.upper())
        self.assertIn("#C84B31", css.upper())

    def test_09_recipe_reviewer_block_grid_and_inline_measurements(self):
        """Requirement 9: Verify all 3 compiled recipe pages contain .engineer-grid-table, rowspan, and bolded inline measurements."""
        step_block_re = re.compile(
            r'<div class="recipe-step-content">(.*?)</div>', re.DOTALL
        )
        json_ld_re = re.compile(
            r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL
        )

        for slug in self.expected_catalog_slugs:
            html_path = REPO_ROOT / "_site" / "recipes" / slug / "index.html"
            self.assertTrue(html_path.exists(), f"Missing built recipe HTML: {html_path}")
            html = html_path.read_text(encoding="utf-8")

            # Cooking for Engineers block grid checks
            self.assertIn("Recipe Block Grid (Order of Operations)", html)
            self.assertIn("Order of Operations (Read Left to Right)", html)
            self.assertIn('class="engineer-grid-table"', html)
            self.assertIn('id="engineer-grid-dialog"', html)
            self.assertIn('closedby="any"', html)
            self.assertIn("openEngineerGridModal()", html)
            self.assertIn('rowspan="', html)
            self.assertIn('class="ing-qty"', html)
            self.assertIn('class="ing-unit"', html)
            self.assertIn('class="ing-name', html)
            self.assertIn("action-cell", html)

            # 3-Tier Instruction Typography: <code> chips for ingredients + <strong> for heat/timers/temps
            step_blocks = step_block_re.findall(html)
            self.assertGreater(len(step_blocks), 0, f"No .recipe-step-content blocks in {slug}")
            chip_steps = 0
            bold_steps = 0
            for idx, sb in enumerate(step_blocks, start=1):
                if "<code" in sb:
                    chip_steps += 1
                if "<strong>" in sb:
                    bold_steps += 1
                self.assertNotIn(
                    "`",
                    sb,
                    f"Raw unrendered Markdown '`' leaked into step {idx} of {slug}",
                )
                self.assertNotIn(
                    "**",
                    sb,
                    f"Raw unrendered Markdown '**' leaked into step {idx} of {slug}",
                )
            self.assertGreaterEqual(
                chip_steps,
                3,
                f"Expected >= 3 ingredient chip steps in {slug}, found {chip_steps}",
            )
            self.assertGreaterEqual(
                bold_steps,
                3,
                f"Expected >= 3 bold heat/timer/temp steps in {slug}, found {bold_steps}",
            )

            # Verify JSON-LD HowToStep text has no raw Markdown '**' or '`' artifacts
            for match in json_ld_re.findall(html):
                try:
                    parsed = json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
                if parsed.get("@type") == "Recipe":
                    for step_obj in parsed.get("recipeInstructions", []):
                        self.assertNotIn("**", step_obj.get("text", ""))
                        self.assertNotIn("`", step_obj.get("text", ""))

        css_path = REPO_ROOT / "_site" / "assets" / "css" / "main.css"
        css_text = css_path.read_text(encoding="utf-8").replace(" ", "")
        self.assertIn(".engineer-grid-table", css_text)
        self.assertIn(".engineer-grid-dialog", css_text)
        self.assertIn(".layout--recipe.page", css_text)
        self.assertIn("border-collapse:collapse", css_text)
        self.assertIn("#f5f0e6", css_text.lower())

    def test_10_dual_surface_room_separation_and_themes(self):
        """Requirement 10: Verify Layout C Blog Home (/), Kitchen (/recipes/), Projects (/projects/), and themes."""
        home_html = (REPO_ROOT / "_site" / "index.html").read_text(encoding="utf-8")
        self.assertIn("surface-blog", home_html)
        self.assertIn('data-default-theme="gruvbox"', home_html)
        self.assertIn("hz-hub", home_html)
        self.assertIn("hz-project-shelf", home_html)
        self.assertIn("scifi-archive-drawer", home_html)

        recipes_html = (REPO_ROOT / "_site" / "recipes" / "index.html").read_text(encoding="utf-8")
        self.assertIn("surface-kitchen", recipes_html)
        self.assertIn('data-default-theme="kitchen"', recipes_html)
        self.assertIn("Active Weekly Dinner Plan", recipes_html)
        self.assertIn("recipe-catalog-card", recipes_html)
        for slug in self.expected_catalog_slugs:
            self.assertIn(f"/recipes/{slug}/", recipes_html)

        projects_html = (REPO_ROOT / "_site" / "projects" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="blog-relaunch"', projects_html)
        self.assertIn('id="dinner-planner"', projects_html)
        self.assertIn("hz-project-card__posts", projects_html)
        self.assertIn("/blog/2026/rebuilding-my-blog-with-antigravity-and-view-loops.html", projects_html)
        self.assertIn("hz-project-card__surface-link", projects_html)
        for hidden_slug in ("board-game-" + "copilot", "fantasy-" + "bot"):
            self.assertNotIn(hidden_slug, projects_html)
            self.assertNotIn(hidden_slug, home_html)

        blog_html = (REPO_ROOT / "_site" / "blog" / "index.html").read_text(encoding="utf-8")
        self.assertIn("surface-blog", blog_html)
        self.assertIn('data-default-theme="gruvbox"', blog_html)
        self.assertIn("hz-hub", blog_html)
        self.assertIn("hz-tag-chip", blog_html)
        self.assertIn("hz-tag-filter-status", blog_html)
        self.assertIn('data-filter-tag="antigravity"', blog_html)
        self.assertIn("data-tags=", blog_html)
        self.assertIn("scifi-archive-drawer", blog_html)
        self.assertIn("Hello World! Create a blog", blog_html)

        about_html = (REPO_ROOT / "_site" / "about" / "index.html").read_text(encoding="utf-8")
        self.assertIn("surface-blog", about_html)
        self.assertIn("/recipes/", about_html)

        for rel_doc in (
            "docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html",
            "docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html",
        ):
            doc_path = REPO_ROOT / "_site" / rel_doc
            self.assertTrue(doc_path.exists(), f"Missing rendered doc HTML: {doc_path}")
            doc_html = doc_path.read_text(encoding="utf-8")
            self.assertIn("surface-blog", doc_html)
            self.assertIn('data-default-theme="gruvbox"', doc_html)

        sitemap_xml = (REPO_ROOT / "_site" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/docs/superpowers/", sitemap_xml)

        sample_post = REPO_ROOT / "_site" / "blog" / "2022" / "hello-world.html"
        self.assertTrue(sample_post.exists(), f"Missing built post HTML: {sample_post}")
        post_html = sample_post.read_text(encoding="utf-8")
        self.assertIn("surface-blog", post_html)
        self.assertIn("scifi-post-header-bar", post_html)
        self.assertIn("all posts", post_html)
        self.assertNotIn('class="author__avatar"', post_html)

        for token in (
            "hz-theme-btn",
            "hz-theme-menu",
            'data-theme-opt="gruvbox"',
            'data-theme-opt="telemetry"',
            'data-theme-opt="catppuccin"',
            'data-theme-opt="kitchen"',
            'data-theme-opt="paper"',
            "hv-diamond",
            "hv-plain",
            "hv-powerline",
            "hv-serif",
            "hv-robby",
            'localStorage.getItem("hawzy-theme")',
        ):
            self.assertIn(token, home_html)

        css_lower = (REPO_ROOT / "_site" / "assets" / "css" / "main.css").read_text(encoding="utf-8").lower()
        self.assertIn("body.surface-blog", css_lower)
        self.assertIn("color-scheme:onlydark", css_lower.replace(" ", ""))
        for css_token in (
            "#141617",
            "#080c14",
            "#1e1e2e",
            "#faf7f2",
            "#ffffff",
            ".hz-feature-card",
            ".hz-theme-menu",
            "@view-transition",
        ):
            self.assertIn(css_token, css_lower)

        ads_txt = (REPO_ROOT / "_site" / "ads.txt").read_text(encoding="utf-8")
        self.assertIn("google.com, pub-3188913102212071, DIRECT, f08c47fec0942fa0", ads_txt)
        self.assertIn("select_theme", home_html)
        analytics_tpl = (REPO_ROOT / "_includes" / "analytics-providers" / "custom.html").read_text(encoding="utf-8")
        self.assertIn("jekyll.environment == 'production'", analytics_tpl)

        if self.server_available:
            for route in [
                "/recipes/",
                "/blog/",
                "/projects/",
                "/about/",
                "/ads.txt",
                "/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html",
                "/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html",
            ]:
                with urllib.request.urlopen(f"{self.server_url}{route}", timeout=5) as resp:
                    self.assertEqual(resp.status, 200, f"Route {route} did not return 200")

    def test_11_blog_soft_archive(self):
        """Soft-archived 2022 posts stay live at URLs with banner + noindex, hidden from main /blog/, sitemap, and search."""
        blog_html = (REPO_ROOT / "_site" / "blog" / "index.html").read_text(encoding="utf-8")
        self.assertIn("hz-feature-card", blog_html)
        self.assertNotIn('class="scifi-post-card"', blog_html)
        self.assertRegex(blog_html, r"// 2022 ARCHIVE\s*(?:&mdash;|—)\s*17 logs \(#100DaysOfCode\)")
        self.assertIn('<details class="scifi-archive-drawer"', blog_html)
        self.assertIn("/blog/2022/hello-world.html", blog_html)

        post_html = (REPO_ROOT / "_site" / "blog" / "2022" / "hello-world.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex">', post_html)
        self.assertIn("Archived 2022 log", post_html)
        self.assertIn("kept for reference.", post_html)
        # Verify explicit `comments: true` in 2022-01-01-hello-world.md does not render related/disqus blocks
        self.assertNotIn('class="page__related"', post_html)
        self.assertNotIn("disqus_thread", post_html)

        sitemap_xml = (REPO_ROOT / "_site" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/blog/2022/", sitemap_xml)
        self.assertIn("/recipes/crispy-mongolian-beef-broccoli/", sitemap_xml)

        tags_html = (REPO_ROOT / "_site" / "tags" / "index.html").read_text(encoding="utf-8")
        self.assertIn("antigravity", tags_html)
        self.assertNotIn("100DaysOfCode", tags_html)
        self.assertNotIn("/blog/2022/", tags_html)
        self.assertNotIn("Index //", tags_html)

        lunr_js = (REPO_ROOT / "_site" / "assets" / "js" / "lunr" / "lunr-store.js").read_text(encoding="utf-8")
        self.assertNotIn("Hello World! Create a blog", lunr_js)
        self.assertIn("Crispy Mongolian Beef", lunr_js)

    def test_12_draft_isolation_and_tested_rendering(self):
        """Verify trust signals, B2A status/sources fields, JSON-LD isBasedOn, and strict isolation of status=draft recipes."""
        recipes_json = json.loads((REPO_ROOT / "_site" / "api" / "recipes.json").read_text(encoding="utf-8"))
        for rec in recipes_json:
            self.assertIn("status", rec)
            self.assertIn("origin", rec)
            self.assertIn("tested_on", rec)
            self.assertIn("sources", rec)

        menu_json = json.loads((REPO_ROOT / "_site" / "api" / "weekly-menu.json").read_text(encoding="utf-8"))
        for meal in menu_json["meals"]:
            self.assertIn("status", meal)

        mongolian_html = (REPO_ROOT / "_site" / "recipes" / "crispy-mongolian-beef-broccoli" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Untested draft", mongolian_html)
        self.assertIn("Sources &amp; inspiration", mongolian_html)

        llms_txt = (REPO_ROOT / "_site" / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("[untested]", llms_txt)

        # Fixture test: alphabetically-last draft recipe + draft meal in weekly_menu.yml + tested recipe with source
        base_md = (REPO_ROOT / "_recipes" / "citrus-chile-glazed-salmon.md").read_text(encoding="utf-8")
        draft_path = REPO_ROOT / "_recipes" / "zzz-draft-fixture.md"
        tested_path = REPO_ROOT / "_recipes" / "aaa-tested-fixture.md"
        weekly_menu_path = REPO_ROOT / "_data" / "weekly_menu.yml"
        orig_weekly_menu_bytes = weekly_menu_path.read_bytes()
        orig_weekly_menu = orig_weekly_menu_bytes.decode("utf-8")

        jekyll_env = dict(os.environ)
        jekyll_env["PATH"] = r"C:\Ruby33-x64\bin;" + jekyll_env.get("PATH", "")
        bundle_exe = r"C:\Ruby33-x64\bin\bundle.bat"

        try:
            draft_md = (
                base_md.replace('title: "Pan-Seared Salmon with Citrus-Chile Glaze"', 'title: "ZZZ Secret Draft Recipe"', 1)
                .replace('slug: "citrus-chile-glazed-salmon"', 'slug: "zzz-draft-fixture"', 1)
                .replace('status: "untested"', 'status: "draft"', 1)
            )
            tested_md = (
                base_md.replace('title: "Pan-Seared Salmon with Citrus-Chile Glaze"', 'title: "AAA Kitchen Tested Fixture"', 1)
                .replace('slug: "citrus-chile-glazed-salmon"', 'slug: "aaa-tested-fixture"', 1)
                .replace(
                    'status: "draft"',
                    'status: "tested"\ntested_on: "2026-11-08"\ntest_notes: "Crisped beautifully in 12-inch wok."\nsources:\n  - title: "Serious Eats Sear Guide"\n    author: "J. Kenji Lopez-Alt"\n    url: "https://www.seriouseats.com/pan-seared-salmon"\nreview:\n  round: 1\n  verdict: "approved"\n  approved_on: "2026-11-08"',
                    1,
                )
            )
            draft_path.write_text(draft_md, encoding="utf-8")
            tested_path.write_text(tested_md, encoding="utf-8")
            weekly_menu_path.write_text(
                orig_weekly_menu.rstrip()
                + '\n  - day: "Sunday"\n    recipe_slug: "zzz-draft-fixture"\n    scale_factor: 1.0\n    notes: "Draft test"\n',
                encoding="utf-8",
            )

            subprocess.run(
                [bundle_exe, "exec", "jekyll", "build"],
                cwd=str(REPO_ROOT),
                env=jekyll_env,
                check=True,
                capture_output=True,
                text=True,
            )

            # 1. Draft page still builds with noindex
            draft_built = (REPO_ROOT / "_site" / "recipes" / "zzz-draft-fixture" / "index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', draft_built)

            # 2. Draft excluded from all discovery and B2A surfaces (and JSON remains strictly valid)
            for rel in [
                "_site/index.html",
                "_site/recipes/index.html",
                "_site/sitemap.xml",
                "_site/assets/js/lunr/lunr-store.js",
                "_site/llms.txt",
            ]:
                text = (REPO_ROOT / rel).read_text(encoding="utf-8")
                self.assertNotIn("zzz-draft-fixture", text, f"Draft slug leaked into {rel}")
                self.assertNotIn("ZZZ Secret Draft Recipe", text, f"Draft title leaked into {rel}")

            built_recipes_json = json.loads((REPO_ROOT / "_site" / "api" / "recipes.json").read_text(encoding="utf-8"))
            built_slugs = {r["slug"] for r in built_recipes_json}
            self.assertNotIn("zzz-draft-fixture", built_slugs)
            self.assertIn("aaa-tested-fixture", built_slugs)

            built_menu_json = json.loads((REPO_ROOT / "_site" / "api" / "weekly-menu.json").read_text(encoding="utf-8"))
            built_meal_slugs = {m["recipe_slug"] for m in built_menu_json["meals"]}
            self.assertNotIn("zzz-draft-fixture", built_meal_slugs)

            # 3. Tested fixture renders badge, test_notes details, sources count, and JSON-LD isBasedOn
            tested_built = (REPO_ROOT / "_site" / "recipes" / "aaa-tested-fixture" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Kitchen-tested", tested_built)
            self.assertIn("2026-11-08", tested_built)
            self.assertIn("From my kitchen", tested_built)
            self.assertIn("Crisped beautifully in 12-inch wok.", tested_built)
            self.assertIn("Researched across 1 source", tested_built)
            self.assertIn("https://www.seriouseats.com/pan-seared-salmon", tested_built)

            pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
            recipe_ld = None
            for m in pattern.findall(tested_built):
                try:
                    parsed = json.loads(m.strip())
                    if parsed.get("@type") == "Recipe":
                        recipe_ld = parsed
                        break
                except json.JSONDecodeError:
                    continue
            self.assertIsNotNone(recipe_ld)
            self.assertEqual(recipe_ld.get("isBasedOn"), ["https://www.seriouseats.com/pan-seared-salmon"])
        finally:
            if draft_path.exists():
                draft_path.unlink()
            if tested_path.exists():
                tested_path.unlink()
            weekly_menu_path.write_bytes(orig_weekly_menu_bytes)
            subprocess.run(
                [bundle_exe, "exec", "jekyll", "build"],
                cwd=str(REPO_ROOT),
                env=jekyll_env,
                check=True,
                capture_output=True,
                text=True,
            )


if __name__ == "__main__":
    unittest.main()
