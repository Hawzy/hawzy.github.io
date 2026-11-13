import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
AUDIT_SCRIPT_PATH = SKILLS_ROOT / "blog-author" / "scripts" / "audit_posts.py"


def load_audit_posts():
    if not AUDIT_SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Missing blog auditor script: {AUDIT_SCRIPT_PATH}")
    spec = importlib.util.spec_from_file_location("audit_posts", AUDIT_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestBlogPipeline(unittest.TestCase):
    def test_blog_skills_frontmatter_and_voice_handoff_exist(self):
        for skill_name in ("blog-voice", "blog-research", "blog-author"):
            skill_md = SKILLS_ROOT / skill_name / "SKILL.md"
            self.assertTrue(skill_md.exists(), f"Missing {skill_md}")
            text = skill_md.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), f"{skill_md} missing YAML frontmatter")
            self.assertIn(f"name: {skill_name}", text)
            self.assertIn("description:", text)

        voice_profile = SKILLS_ROOT / "blog-voice" / "voice-profile.md"
        self.assertTrue(voice_profile.exists(), "Missing voice-profile.md")
        vp_text = voice_profile.read_text(encoding="utf-8")
        self.assertIn("## Banned Phrases", vp_text)
        self.assertIn("- delve", vp_text)

        handoff = SKILLS_ROOT / "blog-voice" / "prompts" / "gemini-personal-intelligence-handoff.md"
        self.assertTrue(handoff.exists(), "Missing gemini-personal-intelligence-handoff.md")
        handoff_text = handoff.read_text(encoding="utf-8")
        self.assertIn("@Gmail", handoff_text)
        self.assertIn("voice-profile.md", handoff_text)

    def test_audit_skips_archived_2022_posts(self):
        audit_posts = load_audit_posts()
        archived_post = REPO_ROOT / "_posts" / "2022-01-01" / "2022-01-01-hello-world.md"
        self.assertTrue(archived_post.exists())
        errors = audit_posts.audit_post_file(archived_post, REPO_ROOT)
        self.assertEqual(errors, [])

    def test_audit_flags_banned_slop_in_prose_but_allows_inside_code_blocks(self):
        audit_posts = load_audit_posts()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            bad_post = tmp_path / "2026-11-10-bad-post.md"
            bad_post.write_text(
                "---\n"
                'title: "Test Post"\n'
                'excerpt: "A clean test post excerpt that meets the length check."\n'
                "categories:\n  - Blog\n"
                "tags:\n  - antigravity\n"
                "---\n\n"
                "Let's delve into this tapestry of code. Also it’s not just a test.\n",
                encoding="utf-8",
            )
            bad_errors = audit_posts.audit_post_file(bad_post, REPO_ROOT)
            self.assertTrue(
                any("delve" in e.lower() for e in bad_errors),
                f"Expected banned phrase 'delve' error, got {bad_errors}",
            )
            self.assertTrue(
                any("it's not just" in e.lower() for e in bad_errors),
                f"Expected smart-quote banned phrase 'it\\'s not just' error, got {bad_errors}",
            )

            good_post = tmp_path / "2026-11-10-good-post.md"
            good_post.write_text(
                "---\n"
                'title: "Test Post"\n'
                'excerpt: "A clean test post excerpt that meets the length check."\n'
                "categories:\n  - Blog\n"
                "tags:\n  - antigravity\n"
                "---\n\n"
                "The auditor rejects inline words like `delve` and `tapestry` when used in prose:\n\n"
                "```markdown\n"
                "Let's delve into this tapestry of code.\n"
                "```\n",
                encoding="utf-8",
            )
            good_errors = audit_posts.audit_post_file(good_post, REPO_ROOT)
            self.assertEqual(good_errors, [])

    def test_audit_flags_missing_frontmatter_todo_markers_and_broken_links(self):
        audit_posts = load_audit_posts()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            post = tmp_path / "2026-11-10-flawed.md"
            post.write_text(
                "---\n"
                'title: "Flawed Post"\n'
                "categories:\n  - Blog\n"
                "---\n\n"
                "Here is an unverified number TODO-source and a [broken link](/assets/does-not-exist.png).\n",
                encoding="utf-8",
            )
            errors = audit_posts.audit_post_file(post, REPO_ROOT)
            joined = "\n".join(errors)
            self.assertIn("excerpt", joined)
            self.assertIn("tags", joined)
            self.assertIn("TODO-", joined)
            self.assertIn("/assets/does-not-exist.png", joined)

    def test_twitter_thread_validator_uses_23_char_tco_url_accounting(self):
        audit_posts = load_audit_posts()
        long_url = "https://hawzy.github.io/blog/rebuilding-my-blog-with-antigravity-and-view-loops-very-long-slug/"
        tweet_body = "A" * 245 + " " + long_url
        # Raw length is 246 + 95 = 341 > 280, but t.co adjusted length is 246 + 23 = 269 <= 280
        self.assertGreater(len(tweet_body), 280)
        self.assertEqual(audit_posts.compute_tweet_length(tweet_body), 246 + 23)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            ok_thread = tmp_path / "twitter-thread.md"
            ok_thread.write_text(
                f"1/ {tweet_body}\n\n2/ Short follow-up tweet on the 5 themes.\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_posts.audit_twitter_thread(ok_thread), [])

            over_thread = tmp_path / "over-thread.md"
            over_thread.write_text(
                "1/ " + ("B" * 285) + "\n",
                encoding="utf-8",
            )
            over_errors = audit_posts.audit_twitter_thread(over_thread)
            self.assertEqual(len(over_errors), 1)
            self.assertIn("280", over_errors[0])

    def test_relaunch_post_1_and_dossier_pass_audit(self):
        audit_posts = load_audit_posts()
        post_1 = (
            REPO_ROOT
            / "_posts"
            / "2026-11-10-rebuilding-my-blog-with-antigravity-and-view-loops.md"
        )
        self.assertTrue(post_1.exists(), f"Missing Post #1: {post_1}")
        self.assertEqual(audit_posts.audit_post_file(post_1, REPO_ROOT), [])
        post_1_text = post_1.read_text(encoding="utf-8")
        for expected_token in ("seventeen", "#080C14", "#FAF7F2", "#C84B31", "#1A7F37"):
            self.assertIn(expected_token, post_1_text)

        dossier_dir = (
            REPO_ROOT
            / "_drafts"
            / "posts"
            / "rebuilding-my-blog-with-antigravity-and-view-loops"
        )
        for req in ("notes.md", "facts.md", "twitter-thread.md", "review.md"):
            self.assertTrue((dossier_dir / req).exists(), f"Missing {dossier_dir / req}")

        self.assertEqual(
            audit_posts.audit_twitter_thread(dossier_dir / "twitter-thread.md"), []
        )

        backlog = REPO_ROOT / "_drafts" / "posts" / "BACKLOG.md"
        self.assertFalse(backlog.exists(), f"Public repo must not track {backlog}")

        for expected_link in (
            "https://github.com/obra/superpowers",
            "/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html",
            "/docs/superpowers/plans/2026-11-10-blog-relaunch-themes-and-writing-skills.html",
        ):
            self.assertIn(expected_link, post_1_text)

    def test_no_unannounced_projects_or_private_info_in_tracked_files(self):
        import subprocess

        tracked = subprocess.check_output(
            ["git", "ls-files"], cwd=REPO_ROOT, text=True
        ).splitlines()
        forbidden_tokens = (
            "board-game-copilot",
            "bga-bot",
            "fantasy-bot",
            "mfl-recap",
            "3d-prints",
            "openscad",
            "freecad",
            "govee",
            "local swarm",
            "gemma 4",
            "rtx 3090",
            "sweat-bot",
            "stream deck",
            "arnak",
            "nickh",
            "@gmail.com",
        )
        text_exts = {".md", ".html", ".yml", ".yaml", ".py", ".txt", ".json", ".scss", ".js"}
        leaks: list[str] = []
        for rel in tracked:
            if rel == "tests/test_blog_pipeline.py" or rel.startswith("_posts/2022-"):
                continue
            path = REPO_ROOT / rel
            if not path.is_file() or path.suffix.lower() not in text_exts:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore").lower()
            for token in forbidden_tokens:
                if token in content:
                    leaks.append(f"{rel}: contains '{token}'")
        self.assertEqual(leaks, [], f"Public repo leaks found:\n" + "\n".join(leaks))

    def test_public_blog_seo_handle_og_card_and_voice_privacy(self):
        import struct

        voice_profile = SKILLS_ROOT / "blog-voice" / "voice-profile.md"
        vp_text = voice_profile.read_text(encoding="utf-8")
        self.assertNotIn("@gmail.com", vp_text.lower())
        self.assertNotIn("jessie", vp_text.lower())
        for phrase in ("- seamlessly", "- unlock value", "- it's not about"):
            self.assertIn(phrase, vp_text)

        config_text = (REPO_ROOT / "_config.yml").read_text(encoding="utf-8")
        self.assertIn('username               : "hawzzy"', config_text)
        self.assertIn("og_image                 : /assets/images/og-default.png", config_text)

        nav_text = (REPO_ROOT / "_data" / "navigation.yml").read_text(encoding="utf-8")
        self.assertIn("@hawzzy", nav_text)
        self.assertIn("https://x.com/hawzzy", nav_text)

        og_png = REPO_ROOT / "assets" / "images" / "og-default.png"
        self.assertTrue(og_png.exists(), f"Missing {og_png}")
        raw_png = og_png.read_bytes()
        self.assertTrue(raw_png.startswith(b"\x89PNG\r\n\x1a\n"))
        width, height = struct.unpack(">II", raw_png[16:24])
        self.assertEqual((width, height), (1200, 630))

        built_post = (
            REPO_ROOT
            / "_site"
            / "blog"
            / "2026"
            / "rebuilding-my-blog-with-antigravity-and-view-loops.html"
        )
        self.assertTrue(built_post.exists(), f"Missing built post {built_post}")
        built_html = built_post.read_text(encoding="utf-8")
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', built_html)
        self.assertIn('<meta name="twitter:site" content="@hawzzy">', built_html)
        self.assertIn("/assets/images/og-default.png", built_html)

    def test_load_banned_phrases_falls_back_to_sibling_skill_dir_when_repo_root_lacks_voice_profile(self):
        audit_posts = load_audit_posts()
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_root = Path(tmpdir)
            phrases = audit_posts.load_banned_phrases(empty_root)
            self.assertIn("delve", phrases)
            self.assertIn("seamlessly", phrases)

    def test_audit_accepts_rendered_docs_html_links_when_md_exists(self):
        audit_posts = load_audit_posts()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            post = tmp_path / "2026-11-12-doc-link.md"
            post.write_text(
                "---\n"
                'title: "Doc Link Test"\n'
                'excerpt: "Verifies rendered docs/superpowers HTML links resolve against .md sources."\n'
                "categories:\n  - Blog\n"
                "tags:\n  - antigravity\n"
                "---\n\n"
                "See [the spec](/docs/superpowers/specs/2026-11-10-blog-relaunch-themes-and-writing-skills-design.html) "
                "and [missing](/docs/superpowers/specs/does-not-exist.html).\n",
                encoding="utf-8",
            )
            errors = audit_posts.audit_post_file(post, REPO_ROOT)
            self.assertEqual(len(errors), 1, f"Expected only missing doc to fail, got {errors}")
            self.assertIn("does-not-exist.html", errors[0])


if __name__ == "__main__":
    unittest.main()
