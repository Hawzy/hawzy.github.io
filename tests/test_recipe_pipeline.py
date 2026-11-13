import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
PANEL_SCRIPTS = REPO_ROOT / ".agents" / "skills" / "recipe-review-panel" / "scripts"
LEGACY_SCRIPTS = REPO_ROOT / ".agents" / "skills" / "recipe-reviewer" / "scripts"


def _load_module(name: str, path: Path):
    resolved = path.resolve()
    for existing in list(sys.modules.values()):
        existing_file = getattr(existing, "__file__", None)
        if existing_file and Path(existing_file).resolve() == resolved:
            sys.modules[name] = existing
            return existing
    spec = importlib.util.spec_from_file_location(name, str(resolved))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return sys.modules.get(name, mod)


class TestProvenanceAndStatusAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel_audit = _load_module(
            "panel_audit_recipes", PANEL_SCRIPTS / "audit_recipes.py"
        )
        cls.legacy_audit = _load_module(
            "legacy_audit_recipes", LEGACY_SCRIPTS / "audit_recipes.py"
        )

    def test_parse_frontmatter_sources_and_review_mapping(self):
        md = (
            "---\n"
            'title: "Test Dish"\n'
            'slug: "test-dish"\n'
            'origin: "research"\n'
            'status: "tested"\n'
            "tested_on: 2026-11-12\n"
            'test_notes: "Cut soy to 3 tbsp."\n'
            "sources:\n"
            '  - title: "Mongolian Beef"\n'
            '    author: "RecipeTin Eats"\n'
            '    url: "https://www.recipetineats.com/mongolian-beef/"\n'
            "review:\n"
            "  round: 2\n"
            '  verdict: "approved"\n'
            "  approved_on: 2026-11-08\n"
            "---\n"
        )
        parsed = self.panel_audit.parse_recipe_frontmatter(md)
        self.assertEqual(parsed["origin"], "research")
        self.assertEqual(parsed["status"], "tested")
        self.assertEqual(parsed["tested_on"], "2026-11-12")
        self.assertEqual(len(parsed["sources"]), 1)
        self.assertEqual(parsed["sources"][0]["author"], "RecipeTin Eats")
        self.assertEqual(
            parsed["review"],
            {"round": 2, "verdict": "approved", "approved_on": "2026-11-08"},
        )

    def test_validator_rejects_research_without_sources_when_not_grandfathered(self):
        errs = self.panel_audit.validate_provenance_and_status(
            {
                "origin": "research",
                "status": "untested",
                "sources": [],
                "review": {
                    "round": 1,
                    "verdict": "approved",
                    "approved_on": "2026-11-08",
                },
            }
        )
        self.assertTrue(any("sources" in e for e in errs))

    def test_validator_allows_empty_sources_only_for_round_zero_backfill_or_draft_or_family(self):
        grandfathered = self.panel_audit.validate_provenance_and_status(
            {
                "origin": "research",
                "status": "untested",
                "sources": [],
                "review": {
                    "round": 0,
                    "verdict": "approved",
                    "approved_on": "2026-11-08",
                },
            }
        )
        self.assertEqual(grandfathered, [])

        draft_ok = self.panel_audit.validate_provenance_and_status(
            {
                "origin": "research",
                "status": "draft",
                "sources": [],
            }
        )
        self.assertEqual(draft_ok, [])

        family_ok = self.panel_audit.validate_provenance_and_status(
            {
                "origin": "family",
                "status": "untested",
                "review": {
                    "round": 1,
                    "verdict": "approved",
                    "approved_on": "2026-11-08",
                },
            }
        )
        self.assertEqual(family_ok, [])

    def test_validator_rejects_tested_without_tested_on_and_non_draft_without_approved_review(self):
        errs_tested = self.panel_audit.validate_provenance_and_status(
            {
                "origin": "family",
                "status": "tested",
                "review": {
                    "round": 1,
                    "verdict": "approved",
                    "approved_on": "2026-11-08",
                },
            }
        )
        self.assertTrue(any("tested_on" in e for e in errs_tested))

        errs_no_review = self.panel_audit.validate_provenance_and_status(
            {
                "origin": "family",
                "status": "untested",
            }
        )
        self.assertTrue(any("review" in e for e in errs_no_review))

    def test_validator_rejects_non_http_or_incomplete_source_entries(self):
        errs_bad_url = self.panel_audit.validate_provenance_and_status(
            {
                "origin": "research",
                "status": "untested",
                "sources": [{"title": "Bad Link", "url": "javascript:alert(1)"}],
                "review": {
                    "round": 1,
                    "verdict": "approved",
                    "approved_on": "2026-11-08",
                },
            }
        )
        self.assertTrue(
            any("http" in e.lower() or "url" in e.lower() for e in errs_bad_url)
        )

    def test_legacy_shim_resolves_to_panel_auditor(self):
        self.assertIs(self.legacy_audit.audit_file, self.panel_audit.audit_file)
        self.assertIs(
            self.legacy_audit.validate_provenance_and_status,
            self.panel_audit.validate_provenance_and_status,
        )


class TestReviewReportEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review_report = _load_module(
            "review_report", PANEL_SCRIPTS / "review_report.py"
        )
        cls.panel_audit = _load_module(
            "panel_audit_recipes", PANEL_SCRIPTS / "audit_recipes.py"
        )

    def test_open_blocker_and_placeholder_waiver_yield_changes_requested(self):
        md_open = (
            "# Review — Crispy Mongolian Beef (round 1) · Verdict: CHANGES REQUESTED\n"
            "| Critic | Score | Blockers | Major | Nit |\n"
            "|---|---|---|---|---|\n"
            "| Culinary & Safety | 4/5 | 1 | 0 | 0 |\n"
            "| Editorial & Usability | 5/5 | 0 | 0 | 0 |\n"
            "| Visual (rendered) | 4/5 | 0 | 0 | 0 |\n"
            "| Structural audit (script) | PASS | — | — | — |\n\n"
            "## Blockers\n"
            "- [CUL-1] Step 4: Missing doneness temp — evidence: research.md → Fix | Waive (reason): ___\n"
        )
        rep1 = self.review_report.parse_review_markdown(md_open)
        verdict1, reasons1 = self.review_report.compute_verdict(rep1)
        self.assertEqual(verdict1, "CHANGES REQUESTED")
        self.assertTrue(any("CUL-1" in r for r in reasons1))

        md_tbd = md_open.replace("Waive (reason): ___", "Waive (reason): TBD")
        rep2 = self.review_report.parse_review_markdown(md_tbd)
        verdict2, reasons2 = self.review_report.compute_verdict(rep2)
        self.assertEqual(verdict2, "CHANGES REQUESTED")
        self.assertTrue(any("CUL-1" in r for r in reasons2))

    def test_valid_waiver_reason_and_fixed_blocker_yield_approved(self):
        md = (
            "# Review — Crispy Mongolian Beef (round 2) · Verdict: APPROVED\n"
            "| Critic | Score | Blockers | Major | Nit |\n"
            "|---|---|---|---|---|\n"
            "| Culinary & Safety | 5/5 | 0 | 0 | 1 |\n"
            "| Editorial & Usability | 5/5 | 0 | 0 | 0 |\n"
            "| Visual (rendered) | 4/5 | 0 | 0 | 0 |\n"
            "| Structural audit (script) | PASS | — | — | — |\n\n"
            "## Blockers\n"
            "- [CUL-1] Step 4: Medium-rare 125°F steak — evidence: brief.md → Waive (reason): Explicit chef's-choice sear temp noted in step 4\n"
            "- [EDT-1] Step 2: Extra bold clause — evidence: SKILL.md → Fixed\n"
        )
        rep = self.review_report.parse_review_markdown(md)
        verdict, reasons = self.review_report.compute_verdict(rep)
        self.assertEqual(verdict, "APPROVED")
        self.assertEqual(reasons, [])

    def test_pending_visual_critic_blocks_approval_until_confirmed_or_waived(self):
        md_pending = (
            "# Review — Crispy Mongolian Beef (round 1) · Verdict: CHANGES REQUESTED\n"
            "| Critic | Score | Blockers | Major | Nit |\n"
            "|---|---|---|---|---|\n"
            "| Culinary & Safety | 5/5 | 0 | 0 | 0 |\n"
            "| Editorial & Usability | 5/5 | 0 | 0 | 0 |\n"
            "| Visual (rendered) | PENDING — run /browser | — | — | — |\n"
            "| Structural audit (script) | PASS | — | — | — |\n\n"
            "## Blockers\n"
        )
        rep_pending = self.review_report.parse_review_markdown(md_pending)
        v_pending, r_pending = self.review_report.compute_verdict(rep_pending)
        self.assertEqual(v_pending, "CHANGES REQUESTED")
        self.assertTrue(any("Visual" in r or "PENDING" in r for r in r_pending))

        md_waived = (
            md_pending
            + "- [VIS-1] Rendered check: Chrome port 9222 offline — evidence: local build → Waive (reason): Verified manually in local browser at 1280px and 390px\n"
        )
        rep_waived = self.review_report.parse_review_markdown(md_waived)
        v_waived, r_waived = self.review_report.compute_verdict(rep_waived)
        self.assertEqual(v_waived, "APPROVED")
        self.assertEqual(r_waived, [])

    def test_structural_audit_fail_blocks_approval(self):
        md = (
            "# Review — Crispy Mongolian Beef (round 1) · Verdict: CHANGES REQUESTED\n"
            "| Critic | Score | Blockers | Major | Nit |\n"
            "|---|---|---|---|---|\n"
            "| Culinary & Safety | 5/5 | 0 | 0 | 0 |\n"
            "| Editorial & Usability | 5/5 | 0 | 0 | 0 |\n"
            "| Visual (rendered) | 5/5 | 0 | 0 | 0 |\n"
            "| Structural audit (script) | FAIL | — | — | — |\n\n"
            "## Blockers\n"
        )
        rep = self.review_report.parse_review_markdown(md)
        verdict, reasons = self.review_report.compute_verdict(rep)
        self.assertEqual(verdict, "CHANGES REQUESTED")
        self.assertTrue(any("Structural audit" in r for r in reasons))

    def test_diff_rounds_tracks_resolved_persisting_waived_and_new_ids(self):
        r1 = self.review_report.parse_review_markdown(
            "# Review — Dish (round 1) · Verdict: CHANGES REQUESTED\n"
            "| Critic | Score | Blockers | Major | Nit |\n"
            "|---|---|---|---|---|\n"
            "| Culinary & Safety | 3/5 | 1 | 0 | 0 |\n"
            "| Editorial & Usability | 4/5 | 1 | 1 | 0 |\n"
            "| Visual (rendered) | 4/5 | 0 | 0 | 0 |\n"
            "| Structural audit (script) | PASS | — | — | — |\n\n"
            "## Blockers\n"
            "- [CUL-1] Step 3: Temp mismatch — evidence: research.md → Fix | Waive (reason): ___\n"
            "- [EDT-1] Step 2: Three bolds — evidence: SKILL.md → Fix | Waive (reason): ___\n"
            "## Major\n"
            "- [EDT-2] Step 5: Wordy step — evidence: SKILL.md → Fix | Waive (reason): ___\n"
        )
        r2 = self.review_report.parse_review_markdown(
            "# Review — Dish (round 2) · Verdict: CHANGES REQUESTED\n"
            "| Critic | Score | Blockers | Major | Nit |\n"
            "|---|---|---|---|---|\n"
            "| Culinary & Safety | 5/5 | 0 | 0 | 0 |\n"
            "| Editorial & Usability | 4/5 | 0 | 1 | 0 |\n"
            "| Visual (rendered) | 4/5 | 0 | 1 | 0 |\n"
            "| Structural audit (script) | PASS | — | — | — |\n\n"
            "## Blockers\n"
            "- [CUL-1] Step 3: Temp mismatch — evidence: research.md → Waive (reason): Carryover heat reaches 135°F during rest\n"
            "## Major\n"
            "- [EDT-2] Step 5: Wordy step — evidence: SKILL.md → Fix | Waive (reason): ___\n"
            "- [VIS-1] Grid: Tight mobile padding — evidence: 390px → Fix | Waive (reason): ___\n"
        )
        diff = self.review_report.diff_rounds(r1, r2)
        self.assertIn("EDT-1", diff["resolved"])
        self.assertIn("CUL-1", diff["waived"])
        self.assertIn("EDT-2", diff["persisting"])
        self.assertIn("VIS-1", diff["new"])
        md_diff = self.review_report.format_diff_markdown(diff, prev_round=1)
        self.assertIn("EDT-1", md_diff)
        self.assertIn("CUL-1", md_diff)

    def test_promote_recipe_frontmatter_updates_status_and_review_preserving_grid(self):
        sample_recipe = (
            REPO_ROOT / "_recipes" / "crispy-mongolian-beef-broccoli.md"
        ).read_text(encoding="utf-8")
        draft_recipe = sample_recipe.replace('status: "untested"', 'status: "draft"', 1)
        promoted = self.review_report.promote_recipe_frontmatter(
            draft_recipe, round_num=2, approved_on="2026-11-08"
        )
        parsed = self.panel_audit.parse_recipe_frontmatter(promoted)
        self.assertEqual(parsed["status"], "untested")
        self.assertEqual(
            parsed["review"],
            {"round": 2, "verdict": "approved", "approved_on": "2026-11-08"},
        )
        orig_parsed = self.panel_audit.parse_recipe_frontmatter(sample_recipe)
        self.assertEqual(parsed["engineer_grid_html"], orig_parsed["engineer_grid_html"])

        with tempfile.TemporaryDirectory() as tmp:
            unapproved_path = Path(tmp) / "review.md"
            recipe_path = Path(tmp) / "recipe.md"
            unapproved_path.write_text(
                "# Review — Dish (round 1) · Verdict: CHANGES REQUESTED\n"
                "| Critic | Score | Blockers | Major | Nit |\n"
                "|---|---|---|---|---|\n"
                "| Structural audit (script) | FAIL | — | — | — |\n",
                encoding="utf-8",
            )
            recipe_path.write_text(draft_recipe, encoding="utf-8")
            res = subprocess.run(
                [
                    sys.executable,
                    str(PANEL_SCRIPTS / "review_report.py"),
                    "--approve",
                    str(unapproved_path),
                    "--recipe",
                    str(recipe_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res.returncode, 0)

    def test_missing_critic_row_and_invalid_approve_date_rejected(self):
        md_missing_visual = (
            "# Review — Dish (round 1) · Verdict: APPROVED\n"
            "| Critic | Score | Blockers | Major | Nit |\n"
            "|---|---|---|---|---|\n"
            "| Culinary & Safety | 5/5 | 0 | 0 | 0 |\n"
            "| Editorial & Usability | 5/5 | 0 | 0 | 0 |\n"
            "| Structural audit (script) | PASS | — | — | — |\n\n"
            "## Blockers\n"
        )
        rep = self.review_report.parse_review_markdown(md_missing_visual)
        verdict, reasons = self.review_report.compute_verdict(rep)
        self.assertEqual(verdict, "CHANGES REQUESTED")
        self.assertTrue(any("Visual" in r for r in reasons))

        with self.assertRaises(ValueError):
            self.review_report.promote_recipe_frontmatter(
                "---\ntitle: \"Dish\"\nstatus: \"draft\"\n---\nBody\n",
                round_num=1,
                approved_on="2026/11/08",
            )


class TestSkillPackageIntegrity(unittest.TestCase):
    SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
    NEW_SKILLS = [
        "recipe-research",
        "recipe-intake",
        "recipe-author",
        "recipe-review-panel",
        "recipe-visuals",
        "recipe-test-log",
        "recipe-pipeline",
    ]

    @staticmethod
    def _parse_skill_frontmatter(text: str):
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return None
        meta = {}
        for line in lines[1:]:
            if line.strip() == "---":
                return meta
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
        return None

    def test_all_pipeline_skills_have_valid_frontmatter(self):
        for skill_name in self.NEW_SKILLS + ["recipe-reviewer"]:
            skill_md = self.SKILLS_DIR / skill_name / "SKILL.md"
            self.assertTrue(skill_md.exists(), f"Missing SKILL.md for {skill_name}")
            text = skill_md.read_text(encoding="utf-8")
            meta = self._parse_skill_frontmatter(text)
            self.assertIsNotNone(meta, f"Invalid frontmatter in {skill_md}")
            self.assertEqual(meta.get("name"), skill_name)
            self.assertTrue(meta.get("description", "").strip(), f"Empty description in {skill_md}")

    def test_recipe_research_skill_covers_research_and_import_modes(self):
        text = (self.SKILLS_DIR / "recipe-research" / "SKILL.md").read_text(encoding="utf-8")
        for token in ["Research mode", "Import mode", "research-raw", "sources.yml", "[s", "USDA", "FDA", "15"]:
            self.assertIn(token, text, f"Missing '{token}' in recipe-research/SKILL.md")

    def test_recipe_author_skill_covers_draft_grammar_grid_and_todo_source(self):
        text = (self.SKILLS_DIR / "recipe-author" / "SKILL.md").read_text(encoding="utf-8")
        for token in ["status: draft", "3-tier", "Cooking for Engineers", "TODO-source", "audit_recipes.py"]:
            self.assertIn(token, text, f"Missing '{token}' in recipe-author/SKILL.md")

    def test_recipe_review_panel_skill_covers_3_critics_isolation_and_cli(self):
        text = (self.SKILLS_DIR / "recipe-review-panel" / "SKILL.md").read_text(encoding="utf-8")
        for token in [
            "Culinary",
            "Editorial",
            "Visual",
            "no author context",
            "PENDING — run /browser",
            "review_report.py",
        ]:
            self.assertIn(token, text, f"Missing '{token}' in recipe-review-panel/SKILL.md")

    def test_recipe_pipeline_skill_covers_3_gates_and_brief_stages(self):
        text = (self.SKILLS_DIR / "recipe-pipeline" / "SKILL.md").read_text(encoding="utf-8")
        for token in ["Gate 1", "Gate 2", "Gate 3", "brief.md", "research-import", "published", "tested"]:
            self.assertIn(token, text, f"Missing '{token}' in recipe-pipeline/SKILL.md")

    def test_visuals_shim_and_all_five_script_entrypoints(self):
        canonical_vis_path = self.SKILLS_DIR / "recipe-visuals" / "scripts" / "generate_recipe_visuals.py"
        shim_vis_path = self.SKILLS_DIR / "recipe-reviewer" / "scripts" / "generate_recipe_visuals.py"
        self.assertTrue(canonical_vis_path.exists())
        self.assertTrue(shim_vis_path.exists())

        canonical_vis = _load_module("canonical_visuals", canonical_vis_path)
        shim_vis = _load_module("shim_visuals", shim_vis_path)
        self.assertIs(shim_vis.build_prompts, canonical_vis.build_prompts)
        self.assertIs(shim_vis.call_nano_banana, canonical_vis.call_nano_banana)

        scripts = [
            self.SKILLS_DIR / "recipe-review-panel" / "scripts" / "audit_recipes.py",
            self.SKILLS_DIR / "recipe-reviewer" / "scripts" / "audit_recipes.py",
            self.SKILLS_DIR / "recipe-review-panel" / "scripts" / "review_report.py",
            canonical_vis_path,
            shim_vis_path,
        ]
        for script_path in scripts:
            res = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"--help failed on {script_path}: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
