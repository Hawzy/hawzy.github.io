---
layout: single
title: "Recipe Pipeline, Review Panel & Go-Live Implementation Plan"
surface: blog
sitemap: false
search: false
comments: false
---

# Recipe Pipeline, Review Panel & Go-Live Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Soft-archive the 2022 `#100DaysOfCode` blog logs and replace the monolithic `recipe-reviewer` skill with a stage-gated 7-skill recipe pipeline, per-recipe provenance dossiers, an independent 3-critic review panel, and public trust signals (`Untested` / `Kitchen-tested`, test notes, and sources) across human and B2A surfaces.

**Architecture:** Jekyll templates (`_layouts/`, `_includes/`, `sitemap.xml`, `api/*.json`, `llms.txt`, `lunr-store.js`) render dual-surface trust signals while isolating archived posts (`archived: true`) and pipeline drafts (`status: draft`) from navigation, search, sitemaps, and B2A feeds. Python 3 stdlib-only scripts under `.agents/skills/recipe-review-panel/scripts/` (`audit_recipes.py`, `review_report.py`) and `.agents/skills/recipe-visuals/scripts/` (`generate_recipe_visuals.py`) enforce frontmatter provenance invariants and Gate-2 approval rules, with thin `importlib.util` forwarding shims preserving legacy `recipe-reviewer` script paths on Windows.

**Tech Stack:** Jekyll 4.4 (`C:\Ruby33-x64\bin`), Minimal Mistakes (`dirt` skin + custom SCSS), Liquid, Schema.org `Recipe` JSON-LD, Python 3.12 standard library only (`unittest`, `html.parser`, `urllib`, `importlib.util`).

**Spec:** `docs/superpowers/specs/2026-11-08-recipe-pipeline-and-go-live-design.md`

## Global Constraints

- **Git Safety Invariant (`AGENTS.md` §3):** Autonomous agents must **NEVER** run `git push`. All commits stay strictly local on branch `feat/agentic-recipe-blog`.
- **Python Dependency Floor:** All scripts under `.agents/skills/` MUST use Python 3 standard library only (zero third-party pip packages, no `PyYAML`).
- **Windows Compatibility:** Do NOT use filesystem symlinks (Windows symlinks require elevation); use Python `importlib.util` module shims. Run Python as `python` (never `python3`), and prepend `$env:PATH = "C:\Ruby33-x64\bin;" + $env:PATH` before `bundle exec jekyll ...`.
- **Dossier Isolation:** `_drafts/` is committed to git for provenance (`_drafts/recipes/<slug>/`) and MUST be listed in `exclude:` in `_config.yml` so Jekyll never copies it to `_site/`.
- **Exact Copy & Badges:**
  - Archived post banner: `"Archived 2022 log — kept for reference."`
  - `/blog/` empty state: `"First transmission incoming"`
  - `/blog/` archive drawer summary: `"// 2022 ARCHIVE — <N> logs (#100DaysOfCode)"`
  - Recipe status badges (icon + text, never color alone): `"● Untested draft"` (amber outline) and `"✓ Kitchen-tested · <YYYY-MM-DD>"` (sage fill, anchoring `#from-my-kitchen` `<details>` `"From my kitchen"`).
  - Sources block heading: `"Sources & inspiration"` (`"Researched across <N> sources"` for `origin: research` with sources; `"Family recipe"` for `origin: family`).
- **Existing Test Invariants:** Keep `len(_recipes/*.md) == 5` and `git status --porcelain` clean at the end of every task so `tests/test_recipe_reviewer.py` and `tests/test_e2e_verification.py::test_07_git_safety_check` continue to pass.

## Review Focus

1. **Windows Jekyll glob scoping + per-post `comments: true` override on archived 2022 posts:** In Jekyll 4.4 on Windows, `scope.path` containing `*` (`_posts/2022-*`) fails because `Pathname#relative_path_from` emits backslashes against forward-slash sanitized paths, and `_posts/2022-01-01/2022-01-01-hello-world.md` sets `comments: true` in file frontmatter — use prefix `path: "_posts/2022-"` (no `*`) in `_config.yml` and guard comments, related posts, and pagination on `page.archived != true` in `_layouts/single.html` (Task 1).
2. **Alphabetically-last `status: draft` recipe or draft-linked weekly meal leaving trailing commas in JSON/JS endpoints:** If `_recipes/zzz-draft-fixture.md` sorts last in `site.recipes` or the final meal in `weekly_menu.yml` points to a draft recipe, skipping inside a raw `for` loop leaves a trailing comma before `]` that breaks `json.loads()` — pre-filter arrays with `where_exp` in `api/recipes.json` and `lunr-store.js`, and emit leading commas via an `emitted` counter in `api/weekly-menu.json` (Task 4).
3. **`jekyll-sitemap` gem ignoring layout assigns on `status: draft` recipes:** `jekyll-sitemap` reads raw `collection.docs` (`doc.sitemap != false`) without evaluating layout variables, so a draft recipe without explicit `sitemap: false` would still appear in `/sitemap.xml` — add a root `sitemap.xml` Liquid template (which `jekyll-sitemap` yields to automatically) filtering `doc.sitemap != false`, `doc.archived != true`, and `doc.status != 'draft'` (Tasks 1 & 4).
4. **Template placeholder `___` or `TBD` accepted as a BLOCKER waiver reason in `review.md`:** Unedited template text (`→ Fix | Waive (reason): ___`) must NOT count as a valid waiver — `review_report.py` must reject empty, whitespace, underscore-only (`___`), dash-only (`-`, `—`), `TBD`, `TODO`, or `N/A` waiver strings and keep verdict `CHANGES REQUESTED` (Task 3).
5. **Malformed or non-HTTP URLs in `sources:` frontmatter breaking JSON-LD `isBasedOn` and links:** `origin: research` entries with missing `title`/`url` or `javascript:` / `file://` / relative URLs must be rejected by `audit_recipes.py` unless `url` starts with `http://` or `https://` (Task 2).

---

## File Map

| Path | Action | Responsibility |
|---|---|---|
| `_config.yml` | Modify | Exclude `_drafts/`; scope archive defaults to `path: "_posts/2022-"` |
| `sitemap.xml` | Create | Sitemap template excluding `sitemap: false`, `archived: true`, and `status: draft` |
| `_includes/head/custom.html` | Modify | Emit `noindex` meta tag for archived posts and `status: draft` recipes |
| `_layouts/single.html` | Modify | Render amber archived post banner; suppress pagination/comments/related when archived |
| `_pages/blog.md` | Modify | Filter archived posts from main stream; render empty state + collapsed 2022 archive `<details>` |
| `assets/js/lunr/lunr-store.js` | Modify | Flatten searchable docs excluding `search: false`, `archived: true`, and `status: draft` |
| `.agents/skills/recipe-review-panel/scripts/audit_recipes.py` | Create (move+extend) | Parse `origin`/`status`/`tested_on`/`test_notes`/`sources`/`review` and validate provenance + 6-point grid/usability rules |
| `.agents/skills/recipe-reviewer/scripts/audit_recipes.py` | Modify (shim) | Backward-compatible `importlib.util` forwarding shim to `recipe-review-panel` |
| `_recipes/*.md` (5 files) | Modify | Interim grandfathered backfill (`origin: research`, `status: untested`, `review.round: 0`) |
| `.agents/skills/recipe-review-panel/scripts/review_report.py` | Create | Parse `review.md`, enforce Gate-2 verdict/waiver/PENDING rules, diff rounds, promote frontmatter |
| `_layouts/recipe.html` | Modify | Render recipe status badge in quick pills |
| `_includes/recipe-card.html` | Modify | Render card status badge, `#from-my-kitchen` `<details>` `test_notes`, `"Sources & inspiration"`, 1-line print credit |
| `_includes/recipe-catalog-grid.html` | Modify | Exclude `status: draft`; render status dot on catalog cards |
| `index.md` | Modify | Exclude `status: draft` meals; render status dot on weekly meal cards |
| `_includes/recipe-schema.html` | Modify | Add `isBasedOn` URL array to `Recipe` JSON-LD when `origin == 'research'` and `sources` non-empty |
| `api/recipes.json` | Modify | Exclude `status: draft`; emit `status`, `origin`, `tested_on`, `sources` |
| `api/weekly-menu.json` | Modify | Exclude `status: draft` meals cleanly; emit per-meal `status` |
| `llms.txt` | Modify | Exclude `status: draft`; surface recipe `status` and provenance endpoints |
| `assets/css/main.scss` | Modify | Styles for sci-fi archive/banner/empty-state + kitchen status badges, dots, notes, sources, print credit |
| `.agents/skills/weekly-grocery-order/scripts/consolidate_menu.py` | Modify | Non-blocking warning for scheduled meals with `status == "untested"` |
| `.agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py` | Create (move) | Nano Banana image generator moved to dedicated `recipe-visuals` skill |
| `.agents/skills/recipe-reviewer/scripts/generate_recipe_visuals.py` | Modify (shim) | Backward-compatible `importlib.util` forwarding shim to `recipe-visuals` |
| `.agents/skills/recipe-{research,intake,author,review-panel,visuals,test-log,pipeline}/SKILL.md` | Create (7 files) | Stage-gated modular skill instructions, rubrics, and isolated critic prompt templates |
| `.agents/skills/recipe-reviewer/SKILL.md` & `AGENTS.md` | Modify | Deprecation pointer in `recipe-reviewer` and updated pipeline docs in `AGENTS.md` |
| `tests/test_recipe_pipeline.py` | Create | Unit tests for provenance validator, `review_report.py`, skill package integrity, and shims |
| `tests/test_consolidation.py` & `tests/test_e2e_verification.py` | Modify | Untested menu warnings + E2E verification of archive, badges, `isBasedOn`, and `zzz-draft-fixture` isolation |

---

### Task 1: Blog Soft Archive & Root Sitemap Guard (Sub-project 1)

**Files:**
- Modify: `_config.yml:133-147` and `_config.yml:245-268`
- Create: `sitemap.xml`
- Modify: `_includes/head/custom.html:11-14`
- Modify: `_layouts/single.html:27-97`
- Modify: `_pages/blog.md:38-75`
- Modify: `assets/js/lunr/lunr-store.js:1-49`
- Modify: `assets/css/main.scss:2000-2266`
- Test: `tests/test_e2e_verification.py`

**Interfaces:**
- Consumes: Existing Jekyll site config and `surface-blog` layout/styles.
- Produces:
  - `_config.yml` `exclude:` entry `_drafts/` (prohibited from `_site/_drafts`).
  - `sitemap.xml` filtering `doc.sitemap != false`, `doc.archived != true`, and `doc.status != 'draft'`.
  - `_includes/head/custom.html` `<meta name="robots" content="noindex">` for `page.archived == true` or `(page.collection == 'recipes' and page.status == 'draft')`.
  - `assets/js/lunr/lunr-store.js` excluding `doc.search == false`, `doc.archived == true`, and `doc.status == 'draft'`.

- [ ] **Step 1: Update `test_01`/`test_10` and add failing `test_11_blog_soft_archive` in `tests/test_e2e_verification.py`**

Add `"_site/_drafts"` and `"_site/docs"` to `prohibited` in `test_01_build_hygiene`. In `test_10_dual_surface_room_separation_and_themes`, replace `self.assertIn("scifi-post-card", blog_html)` with `self.assertIn("scifi-archive-drawer", blog_html)`. Add `test_11_blog_soft_archive`:

```python
    def test_11_blog_soft_archive(self):
        """Soft-archived 2022 posts stay live at URLs with banner + noindex, hidden from main /blog/, sitemap, and search."""
        blog_html = (REPO_ROOT / "_site" / "blog" / "index.html").read_text(encoding="utf-8")
        self.assertIn("First transmission incoming", blog_html)
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

        lunr_js = (REPO_ROOT / "_site" / "assets" / "js" / "lunr" / "lunr-store.js").read_text(encoding="utf-8")
        self.assertNotIn("Hello World! Create a blog", lunr_js)
        self.assertIn("Crispy Mongolian Beef", lunr_js)
```

- [ ] **Step 2: Run the archive E2E test to verify it fails**

Run: `python -m unittest tests.test_e2e_verification.TestEndToEndVerification.test_11_blog_soft_archive -v`
Expected: FAIL (`"First transmission incoming"` not found in `_site/blog/index.html`).

- [ ] **Step 3: Configure `_config.yml`, `sitemap.xml`, `_includes/head/custom.html`, `_layouts/single.html`, `_pages/blog.md`, `assets/js/lunr/lunr-store.js`, and `assets/css/main.scss`**

1. `_config.yml`:
   - Add `- _drafts/` under `exclude:`.
   - Append a second `posts` scope under `defaults:` using prefix path `"_posts/2022-"` (NO `*` wildcard — avoids Windows `Pathname` backslash mismatch in Jekyll `glob_scope`):
     ```yaml
       - scope:
           path: "_posts/2022-"
           type: "posts"
         values:
           archived: true
           sitemap: false
           search: false
           related: false
           comments: false
     ```
2. `sitemap.xml` (root file with `layout: null` frontmatter):
   - Mirror `jekyll-sitemap`'s `<urlset>` structure over `site.collections` (`output != false`) and `site.html_pages` (`url != "/404.html"`), filtering every `doc` with `where_exp: "doc", "doc.sitemap != false"` + `where_exp: "doc", "doc.archived != true"` + `where_exp: "doc", "doc.status != 'draft'"`.
3. `_includes/head/custom.html`:
   - Emit `{% if page.archived == true or (page.collection == 'recipes' and page.status == 'draft') %}<meta name="robots" content="noindex">{% endif %}`.
4. `_layouts/single.html`:
   - Inside `<header>` (after `.scifi-post-header-bar`), when `page.archived == true`, render `<div class="scifi-archived-banner" role="status">Archived 2022 log &mdash; kept for reference.</div>`.
   - Wrap `{% include post_pagination.html %}`, the `comments.html` block, and both `page__related` branches with `{% unless page.archived %}` ... `{% endunless %}` (and filter `site.posts` / `site.related_posts` inside `page__related` with `where_exp: "p", "p.archived != true"` so future posts never recommend archived 2022 logs).
5. `_pages/blog.md`:
   - Partition `visible_posts = site.posts | where_exp: "item", "item.hidden != true"`:
     - `active_posts = visible_posts | where_exp: "item", "item.archived != true"`
     - `archived_posts = visible_posts | where_exp: "item", "item.archived == true"`
   - If `active_posts.size == 0`, render `<div class="scifi-empty-state"><span class="scifi-eyebrow">// STANDBY_CHANNEL</span><p>First transmission incoming</p></div>`; otherwise render the existing `group_by_exp` year sections over `active_posts`.
   - Below the main stream, if `archived_posts.size > 0`, render collapsed `<details class="scifi-archive-drawer">` with `<summary class="scifi-archive-drawer__summary">// 2022 ARCHIVE &mdash; {{ archived_posts.size }} logs (#100DaysOfCode)</summary>` and a compact `<ul class="scifi-archive-drawer__list">` of `<time>{{ post.date | date: "%Y.%m.%d" }}</time> <a href="{{ post.url | relative_url }}">{{ post.title }}</a>`.
6. `assets/js/lunr/lunr-store.js`:
   - Build a single `searchable_docs` Liquid array (`"" | split: ""`) concatenating `c.docs` across `site.collections` filtered by `doc.search != false`, `doc.archived != true`, and `doc.status != 'draft'`, then iterate once using `{% unless forloop.last %},{% endunless %}` so empty collections never leave trailing commas.
7. `assets/css/main.scss`:
   - Under `body.surface-blog`, style `.scifi-archived-banner` (thin amber border/tint `rgba(251, 191, 36, 0.12)`, `#FBBF24` text, monospace), `.scifi-empty-state` (dashed border panel), and `.scifi-archive-drawer` (`<details>` / `<summary>` monospace bar + compact dated list).

- [ ] **Step 4: Rebuild Jekyll site and run tests to verify they pass**

Run: `$env:PATH = "C:\Ruby33-x64\bin;" + $env:PATH; bundle exec jekyll build; python -m unittest tests.test_e2e_verification.TestEndToEndVerification.test_01_build_hygiene tests.test_e2e_verification.TestEndToEndVerification.test_10_dual_surface_room_separation_and_themes tests.test_e2e_verification.TestEndToEndVerification.test_11_blog_soft_archive -v`
Expected: Jekyll build exits `0`; all 3 test methods `OK`.

- [ ] **Step 5: Commit Task 1 locally**

```powershell
git add _config.yml sitemap.xml _includes/head/custom.html _layouts/single.html _pages/blog.md assets/js/lunr/lunr-store.js assets/css/main.scss tests/test_e2e_verification.py
git commit -m "feat(blog): soft-archive 2022 logs with noindex, drawer, and sitemap guard"
```

---

### Task 2: Provenance & Status Validator (`audit_recipes.py`), Shim & Interim Backfill

**Files:**
- Create: `.agents/skills/recipe-review-panel/scripts/audit_recipes.py`
- Modify: `.agents/skills/recipe-reviewer/scripts/audit_recipes.py` (replace with forwarding shim)
- Modify: `_recipes/blackstone-shabu-steak-fried-rice.md:1-20`
- Modify: `_recipes/citrus-chile-glazed-salmon.md:1-20`
- Modify: `_recipes/crispy-mongolian-beef-broccoli.md:1-20`
- Modify: `_recipes/homemade-ramen-kewpie-slaw.md:1-20`
- Modify: `_recipes/overnight-dry-brined-ribeye.md:1-20`
- Create: `tests/test_recipe_pipeline.py`

**Interfaces:**
- Consumes: Existing 6-point auditor logic from `.agents/skills/recipe-reviewer/scripts/audit_recipes.py`.
- Produces (in `.agents/skills/recipe-review-panel/scripts/audit_recipes.py` and re-exported by `.agents/skills/recipe-reviewer/scripts/audit_recipes.py`):
  - `parse_recipe_frontmatter(md_text: str) -> Dict[str, Any]` — additionally parses:
    - `origin: str`, `status: str`, `tested_on: str`, `test_notes: str`
    - `sources: List[Dict[str, Any]]` (each item supporting `title`, `author`, `url`)
    - `review: Dict[str, Any]` (indented mapping supporting `round: int`, `verdict: str`, `approved_on: str`)
  - `validate_provenance_and_status(data: Dict[str, Any]) -> List[str]` — enforces Spec §3.2 & §3.4 rules and returns `[Rule 7 - Provenance & Status] ...` error strings.
  - `audit_recipe_data(data: Dict[str, Any], source_name: str = "<recipe>") -> Dict[str, Any]` — includes provenance errors in `errors` and exposes `status`, `origin`, and `review_round` in the returned report dict.

- [ ] **Step 1: Write failing unit tests in `tests/test_recipe_pipeline.py` for provenance parsing, validation, grandfathering, URL hygiene, and shim imports**

Create `tests/test_recipe_pipeline.py` importing both `.agents/skills/recipe-review-panel/scripts/audit_recipes.py` (`panel_audit`) and `.agents/skills/recipe-reviewer/scripts/audit_recipes.py` (`legacy_audit`) with `TestProvenanceAndStatusAudit`:

```python
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
        parsed = panel_audit.parse_recipe_frontmatter(md)
        self.assertEqual(parsed["origin"], "research")
        self.assertEqual(parsed["status"], "tested")
        self.assertEqual(parsed["tested_on"], "2026-11-12")
        self.assertEqual(len(parsed["sources"]), 1)
        self.assertEqual(parsed["sources"][0]["author"], "RecipeTin Eats")
        self.assertEqual(parsed["review"], {"round": 2, "verdict": "approved", "approved_on": "2026-11-08"})

    def test_validator_rejects_research_without_sources_when_not_grandfathered(self):
        errs = panel_audit.validate_provenance_and_status({
            "origin": "research",
            "status": "untested",
            "sources": [],
            "review": {"round": 1, "verdict": "approved", "approved_on": "2026-11-08"},
        })
        self.assertTrue(any("sources" in e for e in errs))

    def test_validator_allows_empty_sources_only_for_round_zero_backfill_or_draft_or_family(self):
        grandfathered = panel_audit.validate_provenance_and_status({
            "origin": "research",
            "status": "untested",
            "sources": [],
            "review": {"round": 0, "verdict": "approved", "approved_on": "2026-11-08"},
        })
        self.assertEqual(grandfathered, [])

        draft_ok = panel_audit.validate_provenance_and_status({
            "origin": "research",
            "status": "draft",
            "sources": [],
        })
        self.assertEqual(draft_ok, [])

        family_ok = panel_audit.validate_provenance_and_status({
            "origin": "family",
            "status": "untested",
            "review": {"round": 1, "verdict": "approved", "approved_on": "2026-11-08"},
        })
        self.assertEqual(family_ok, [])

    def test_validator_rejects_tested_without_tested_on_and_non_draft_without_approved_review(self):
        errs_tested = panel_audit.validate_provenance_and_status({
            "origin": "family",
            "status": "tested",
            "review": {"round": 1, "verdict": "approved", "approved_on": "2026-11-08"},
        })
        self.assertTrue(any("tested_on" in e for e in errs_tested))

        errs_no_review = panel_audit.validate_provenance_and_status({
            "origin": "family",
            "status": "untested",
        })
        self.assertTrue(any("review" in e for e in errs_no_review))

    def test_validator_rejects_non_http_or_incomplete_source_entries(self):
        errs_bad_url = panel_audit.validate_provenance_and_status({
            "origin": "research",
            "status": "untested",
            "sources": [{"title": "Bad Link", "url": "javascript:alert(1)"}],
            "review": {"round": 1, "verdict": "approved", "approved_on": "2026-11-08"},
        })
        self.assertTrue(any("http" in e.lower() or "url" in e.lower() for e in errs_bad_url))

    def test_legacy_shim_resolves_to_panel_auditor(self):
        self.assertIs(legacy_audit.audit_file, panel_audit.audit_file)
        self.assertIs(legacy_audit.validate_provenance_and_status, panel_audit.validate_provenance_and_status)
```

- [ ] **Step 2: Run `tests/test_recipe_pipeline.py` to verify it fails**

Run: `python -m unittest tests/test_recipe_pipeline.py -v`
Expected: FAIL (`FileNotFoundError` / `ImportError` for `.agents/skills/recipe-review-panel/scripts/audit_recipes.py`).

- [ ] **Step 3: Implement `.agents/skills/recipe-review-panel/scripts/audit_recipes.py`, the forwarding shim, and backfill all 5 `_recipes/*.md` files**

1. Create `.agents/skills/recipe-review-panel/scripts/audit_recipes.py` from the existing auditor with:
   - Generalized list-of-dicts parsing for both `ingredients:` and `sources:` (`default` empty list `[]`), plus indented single-level mapping parsing for `review:` (`default` `{}`).
   - `ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")` and `HTTP_URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)`.
   - `validate_provenance_and_status(data: Dict[str, Any]) -> List[str]`:
     - Require `origin` in `{"research", "family"}` and `status` in `{"draft", "untested", "tested"}`.
     - Require `tested_on` matching `YYYY-MM-DD` iff `status == "tested"` (and error if `tested_on` is set when `status != "tested"`).
     - When `status in {"untested", "tested"}`: require `review` dict with integer `round >= 0`, `verdict == "approved"`, and `approved_on` matching `YYYY-MM-DD`; also reject any `TODO-source` or `TODO-ask` substring in `instructions` or `ingredients[*].display_text`.
     - Validate every item in `sources` (when non-empty) is a dict with non-empty `title` and `url` matching `HTTP_URL_PATTERN`.
     - When `origin == "research"` and `status != "draft"`: require `len(sources) >= 1` unless `review.get("round") == 0` (grandfathered interim backfill).
   - Note on existing unit test compatibility: in `audit_recipe_data(data, source_name)`, run `validate_provenance_and_status(data)` whenever `"origin"` or `"status"` is present in `data` OR when called from `audit_file(path: Path)` (which passes `require_provenance=True`), so synthetic in-memory unit-test dicts in `tests/test_recipe_reviewer.py` that test Rules 1–6 continue testing Rules 1–6 while all real `_recipes/*.md` files strictly require provenance!
2. Replace `.agents/skills/recipe-reviewer/scripts/audit_recipes.py` with a stdlib `importlib.util.spec_from_file_location` shim loading `.agents/skills/recipe-review-panel/scripts/audit_recipes.py`, registering it, re-exporting its public attributes into `globals()`, and delegating `if __name__ == "__main__": sys.exit(main())`.
3. Backfill each of the 5 files in `_recipes/` right after `cuisine:` with:
   ```yaml
   origin: "research"
   status: "untested"
   review:
     round: 0
     verdict: "approved"
     approved_on: "2026-11-08"
   ```

- [ ] **Step 4: Run `tests/test_recipe_pipeline.py`, `tests/test_recipe_reviewer.py`, and CLI audit to verify all pass**

Run: `python -m unittest tests/test_recipe_pipeline.py tests/test_recipe_reviewer.py -v; python .agents/skills/recipe-review-panel/scripts/audit_recipes.py; python .agents/skills/recipe-reviewer/scripts/audit_recipes.py`
Expected: All unit tests `OK`; both new and shimmed CLI paths report `[PASS]` on all 5 recipes with exit code `0`.

- [ ] **Step 5: Commit Task 2 locally**

```powershell
git add .agents/skills/recipe-review-panel/scripts/audit_recipes.py .agents/skills/recipe-reviewer/scripts/audit_recipes.py _recipes/*.md tests/test_recipe_pipeline.py
git commit -m "feat(audit): add provenance/status validator, shim, and round-0 recipe backfill"
```

---

### Task 3: Review Report Parser, Diff & Gate-2 Promotion Engine (`review_report.py`)

**Files:**
- Create: `.agents/skills/recipe-review-panel/scripts/review_report.py`
- Modify: `tests/test_recipe_pipeline.py`

**Interfaces:**
- Consumes: `review.md` Markdown format (Spec §5.4) and `_recipes/<slug>.md` YAML frontmatter.
- Produces (in `.agents/skills/recipe-review-panel/scripts/review_report.py`):
  - `parse_review_markdown(md_text: str) -> Dict[str, Any]`
  - `compute_verdict(report: Dict[str, Any]) -> Tuple[str, List[str]]` -> `("APPROVED" | "CHANGES REQUESTED", blocking_reasons)`
  - `diff_rounds(prev_report: Dict[str, Any], curr_report: Dict[str, Any]) -> Dict[str, List[str]]`
  - `format_diff_markdown(diff: Dict[str, List[str]], prev_round: int) -> str`
  - `promote_recipe_frontmatter(recipe_md_text: str, round_num: int, approved_on: str) -> str`
  - CLI flags: `--check <review.md> [--json]`, `--diff <prev.md> <curr.md>`, `--approve <review.md> --recipe <_recipes/slug.md> [--date YYYY-MM-DD]`

- [ ] **Step 1: Write failing tests in `tests/test_recipe_pipeline.py` (`TestReviewReportEngine`)**

Add test cases covering:
1. `test_open_blocker_and_placeholder_waiver_yield_changes_requested`: a `review.md` containing `- [CUL-1] Step 4: ... → Fix | Waive (reason): ___` or `Waive (reason): TBD` returns `("CHANGES REQUESTED", [...])`.
2. `test_valid_waiver_reason_and_fixed_blocker_yield_approved`: `- [CUL-1] Step 4: Medium-rare 125°F steak — evidence: brief.md → Waive (reason): Explicit chef's-choice sear temp noted in step 4` with `Structural audit (script) | PASS` and `Visual (rendered) | 4/5` returns `("APPROVED", [])`.
3. `test_pending_visual_critic_blocks_approval_until_confirmed_or_waived`: `| Visual (rendered) | PENDING — run /browser | — | — | — |` without a valid `[VIS-*]` waiver returns `("CHANGES REQUESTED", [...])`, and flips to `("APPROVED", [])` when a `[VIS-1] ... → Waive (reason): Verified manually in local browser at 1280px and 390px` is recorded.
4. `test_structural_audit_fail_blocks_approval`: `| Structural audit (script) | FAIL | — | — | — |` returns `("CHANGES REQUESTED", [...])`.
5. `test_diff_rounds_tracks_resolved_persisting_waived_and_new_ids`: compares Round 1 (`CUL-1`, `EDT-1`) against Round 2 (`CUL-1` waived, `EDT-1` absent/resolved, `VIS-1` new).
6. `test_promote_recipe_frontmatter_updates_status_and_review_preserving_grid`: promotes `status: "draft"` to `status: "untested"` with `review: {round: 2, verdict: "approved", approved_on: "2026-11-08"}` while leaving `engineer_grid_html` and Markdown body byte-identical; CLI `--approve` exits non-zero if `compute_verdict` != `"APPROVED"`.

- [ ] **Step 2: Run `TestReviewReportEngine` to verify it fails**

Run: `python -m unittest tests.test_recipe_pipeline.TestReviewReportEngine -v`
Expected: FAIL (`ImportError` / `FileNotFoundError` for `review_report.py`).

- [ ] **Step 3: Implement `.agents/skills/recipe-review-panel/scripts/review_report.py`**

Implement using Python 3 stdlib (`re`, `argparse`, `json`, `datetime`, `pathlib`, `sys`):
- Header regex `# Review\s*[—-]\s*(?P<title>.+?)\s*\(round\s+(?P<round>\d+)\)\s*·\s*Verdict:\s*(?P<verdict>APPROVED|CHANGES REQUESTED)`.
- Markdown table parser extracting each critic row (`critic`, `score_or_status`, `blockers`, `major`, `nit`).
- Section-aware finding parser (`## Blockers`, `## Major`, `## Nits`) matching `- \[(?P<id>(?:CUL|EDT|VIS)-\d+)\]\s*(?P<body>.+)`:
  - Resolution parsing on the trailing `→` / `->` clause:
    - Fixed if marked `→ Fixed` / `[x] Fixed` (with optional note).
    - Waived ONLY if marked `Waive (reason): <reason>` or `Waived (reason): <reason>` where `<reason>.strip()` is non-empty, contains at least 4 alphanumeric characters, and `.strip("_-—. ").upper()` is not in `{"", "TBD", "TODO", "NA", "N/A", "NONE", "FIX"}`. Note: the untouched template string `Fix | Waive (reason): ___` is classified as `resolution = "open"`.
- `compute_verdict(report)` enforces:
  1. `Structural audit` row present and equal to `"PASS"` (case-insensitive).
  2. `Visual` row not containing `"PENDING"` unless a `VIS-*` finding in `## Blockers` carries `resolution == "waived"` with a valid `waiver_reason`.
  3. Zero `BLOCKER` findings with `resolution == "open"`.
- `promote_recipe_frontmatter(recipe_md_text, round_num, approved_on)` splices only the top-level `status:` and `review:` YAML lines inside the opening `--- ... ---` block (converting `draft` -> `untested`, keeping `tested` if already `tested`), preserving exact line content of `ingredients`, `instructions`, `engineer_grid_html`, and narrative body.

- [ ] **Step 4: Run `tests/test_recipe_pipeline.py` to verify all tests pass**

Run: `python -m unittest tests/test_recipe_pipeline.py -v`
Expected: All tests in `TestProvenanceAndStatusAudit` and `TestReviewReportEngine` `OK`.

- [ ] **Step 5: Commit Task 3 locally**

```powershell
git add .agents/skills/recipe-review-panel/scripts/review_report.py tests/test_recipe_pipeline.py
git commit -m "feat(review-panel): add review.md parser, round differ, and Gate-2 promoter"
```

---

### Task 4: Recipe Trust Signals, Draft Isolation & B2A Surface Updates

**Files:**
- Modify: `_layouts/recipe.html:23-40`
- Modify: `_includes/recipe-card.html:6-26` and `_includes/recipe-card.html:180-198`
- Modify: `_includes/recipe-catalog-grid.html:1-37`
- Modify: `index.md:22-48`
- Modify: `_includes/recipe-schema.html:1-41`
- Modify: `api/recipes.json:1-25`
- Modify: `api/weekly-menu.json:1-24`
- Modify: `llms.txt:1-16`
- Modify: `assets/css/main.scss:1100-1595`
- Modify: `.agents/skills/weekly-grocery-order/scripts/consolidate_menu.py:77-150` and `263-299`
- Test: `tests/test_consolidation.py` and `tests/test_e2e_verification.py`

**Interfaces:**
- Consumes: Frontmatter fields `origin`, `status`, `tested_on`, `test_notes`, `sources` validated in Task 2; `sitemap.xml`, `noindex`, and `lunr-store.js` guards from Task 1.
- Produces:
  - Human badges (`● Untested draft`, `✓ Kitchen-tested · <date>`), `#from-my-kitchen` `<details>` `"From my kitchen"`, `"Sources & inspiration"` block + 1-line `.recipe-print-credit`, status dots on `/` and `/recipes/`, and `Schema.org` `isBasedOn` array.
  - B2A fields: `status`, `origin`, `tested_on`, `sources` in `/api/recipes.json`; per-meal `status` in `/api/weekly-menu.json`; `[<status>]` tag in `/llms.txt`.
  - `collect_untested_warnings(menu_data: Dict[str, Any]) -> List[str]` in `consolidate_menu.py` emitting non-blocking warnings to `stderr` when any scheduled meal has `status == "untested"`.

- [ ] **Step 1: Add failing unit tests in `tests/test_consolidation.py` and E2E tests in `tests/test_e2e_verification.py`**

1. In `tests/test_consolidation.py`, add `test_untested_meal_emits_non_blocking_warning`:
   ```python
    def test_untested_meal_emits_non_blocking_warning(self):
        menu = {
            "week_of": "2026-11-08",
            "meals": [
                {"day": "Monday", "recipe_slug": "ribeye", "recipe_title": "Ribeye", "status": "untested", "scale_factor": 1.0, "ingredients": []},
                {"day": "Tuesday", "recipe_slug": "ramen", "recipe_title": "Ramen", "status": "tested", "scale_factor": 1.0, "ingredients": []},
            ],
        }
        warnings = consolidate_menu.collect_untested_warnings(menu)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Ribeye", warnings[0])
        self.assertIn("untested", warnings[0].lower())
   ```
2. In `tests/test_e2e_verification.py`:
   - Extend `test_03_json_api_validation` (or add `test_12_trust_signals_and_draft_isolation`) checking `_site/api/recipes.json` has `status`, `origin`, `tested_on`, `sources` on every recipe, `_site/api/weekly-menu.json` has per-meal `status`, `_site/llms.txt` mentions status, and `_site/recipes/crispy-mongolian-beef-broccoli/index.html` renders `"Untested draft"` and `"Sources & inspiration"`.
   - Add `test_12_draft_isolation_and_tested_rendering` which writes TWO temporary fixtures inside a `try / finally` block (`_recipes/zzz-draft-fixture.md` with `status: "draft"` sorting alphabetically LAST, plus temporarily appending `zzz-draft-fixture` as the final meal in `_data/weekly_menu.yml` to exercise Review Focus #2 across both JSON endpoints, and `_recipes/aaa-tested-fixture.md` with `status: "tested"`, `tested_on: "2026-11-08"`, `test_notes: "Crisped beautifully in 12-inch wok."`, `origin: "research"`, and 1 `https://` source), runs `bundle exec jekyll build`:
     - Asserts `zzz-draft-fixture` HTML exists with `<meta name="robots" content="noindex">`, and `zzz-draft-fixture` is ABSENT from `_site/index.html` (both weekly-menu cards and catalog grid), `_site/recipes/index.html`, `_site/sitemap.xml`, `_site/assets/js/lunr/lunr-store.js`, `_site/api/recipes.json` and `_site/api/weekly-menu.json` (both parsed cleanly with `json.loads` — zero trailing comma!), and `_site/llms.txt`.
     - Asserts `aaa-tested-fixture` HTML renders `Kitchen-tested`, `2026-11-08`, `From my kitchen`, `Crisped beautifully in 12-inch wok.`, `Researched across 1 source`, and `isBasedOn` in its `Recipe` JSON-LD.
     - In `finally:`, restores the original `_data/weekly_menu.yml` bytes, deletes both fixture files, and re-runs `bundle exec jekyll build` so `_site/` and `git status --porcelain` return to clean 5-recipe state.

- [ ] **Step 2: Run the new consolidation and E2E tests to verify they fail**

Run: `python -m unittest tests.test_consolidation.TestGroceryConsolidation.test_untested_meal_emits_non_blocking_warning tests.test_e2e_verification.TestEndToEndVerification.test_12_draft_isolation_and_tested_rendering -v`
Expected: FAIL (`AttributeError: module 'consolidate_menu' has no attribute 'collect_untested_warnings'` and missing badges/draft filtering).

- [ ] **Step 3: Implement template updates, SCSS styles, B2A JSON/llms filters, and `consolidate_menu.py` warning**

1. `_layouts/recipe.html` & `_includes/recipe-card.html`:
   - Render `.recipe-status-badge`:
     - `page.status == 'tested'`: `<a href="#from-my-kitchen" class="recipe-status-badge recipe-status-badge--tested"><span aria-hidden="true">&#10003;</span> Kitchen-tested &middot; {{ page.tested_on }}</a>` (or `<span>` if no `test_notes`).
     - `page.status == 'draft'`: `<span class="recipe-status-badge recipe-status-badge--draft"><span aria-hidden="true">&#9676;</span> Pipeline draft</span>`.
     - Default / `'untested'`: `<span class="recipe-status-badge recipe-status-badge--untested"><span aria-hidden="true">&#9679;</span> Untested draft</span>`.
   - In `_includes/recipe-card.html` after `.recipe-card__toolbar` (or above `.recipe-card__body`), when `page.test_notes and page.test_notes != ""`, render `<details id="from-my-kitchen" class="recipe-kitchen-notes"><summary>From my kitchen</summary><p>{{ page.test_notes | escape }}</p></details>`.
   - Below `.recipe-card__engineer-grid` inside `<section id="recipe-card">`, render `<footer class="recipe-card__sources">`:
     - Heading `<h3 class="recipe-card__sources-title">Sources &amp; inspiration</h3>`.
     - If `page.origin == 'family'`: `<p class="recipe-card__sources-summary">Family recipe</p>` and `<p class="recipe-print-credit">Source: Family recipe</p>`.
     - Else if `page.sources and page.sources.size > 0`: `<p class="recipe-card__sources-summary">Researched across {{ page.sources.size }} {% if page.sources.size == 1 %}source{% else %}sources{% endif %}</p>`, `<ul class="recipe-card__sources-list">` with `<a href="{{ src.url }}" rel="noopener noreferrer" target="_blank">{{ src.title }}</a>{% if src.author %} &mdash; {{ src.author }}{% endif %}`, and `<p class="recipe-print-credit">Sources ({{ page.sources.size }}): {{ page.sources | map: "title" | join: "; " }}</p>`.
     - Else (`review.round == 0` grandfathered research recipe): `<p class="recipe-card__sources-summary">Research synthesis &mdash; source citations backfilling</p>` and `<p class="recipe-print-credit">Source: Research synthesis</p>`.
2. `_includes/recipe-catalog-grid.html` & `index.md`:
   - In `_includes/recipe-catalog-grid.html`, assign `live_recipes = site.recipes | where_exp: "r", "r.status != 'draft'"` and iterate `live_recipes`; add `<span class="recipe-status-dot recipe-status-dot--{{ recipe.status | default: 'untested' }}" title="{% if recipe.status == 'tested' %}Kitchen-tested{% else %}Untested draft{% endif %}">{% if recipe.status == 'tested' %}&#10003; Tested{% else %}&#9679; Untested{% endif %}</span>` in `.recipe-catalog-card__eyebrow`.
   - In `index.md`, skip meal cards when `matched_recipe and matched_recipe.status == 'draft'`, and render the same compact status indicator in `.weekly-meal-card__meta`.
3. `_includes/recipe-schema.html`:
   - When `page.origin == 'research' and page.sources and page.sources.size > 0`, emit `"isBasedOn": [{% for s in page.sources %}{{ s.url | jsonify }}{% unless forloop.last %},{% endunless %}{% endfor %}],` above `"recipeIngredient"`.
4. `api/recipes.json`, `api/weekly-menu.json`, and `llms.txt`:
   - `api/recipes.json`: iterate `live_recipes = site.recipes | where_exp: "r", "r.status != 'draft'"` and add `"origin": {{ recipe.origin | default: "research" | jsonify }}`, `"status": {{ recipe.status | default: "untested" | jsonify }}`, `"tested_on": {{ recipe.tested_on | jsonify }}`, `"sources": {{ recipe.sources | default: empty_array | jsonify }}` (`{% assign empty_array = "" | split: "" %}`).
   - `api/weekly-menu.json`: track `{% assign emitted = 0 %}`, skip any meal where `matched_recipe == nil` or `matched_recipe.status == 'draft'`, prepend `{% if emitted > 0 %},{% endif %}{% assign emitted = emitted | plus: 1 %}`, and include `"status": {{ matched_recipe.status | default: "untested" | jsonify }}`.
   - `llms.txt`: iterate `live_recipes = site.recipes | where_exp: "r", "r.status != 'draft'"`, append `[{{ recipe.status | default: "untested" }}]` to each recipe line, and mention `status`/`origin`/`sources` in the `All Recipes JSON` bullet.
5. `assets/css/main.scss`:
   - Style `.recipe-status-badge` (`--untested`: `#FFFBEB` / `#B45309` amber border & text; `--tested`: `#4A6B53` sage fill with `#FAF7F2` text; `--draft`: `#F5F5F4` muted), `.recipe-status-dot`, `.recipe-kitchen-notes`, `.recipe-card__sources`, and `.recipe-print-credit` (`display: none` on screen; in `@media print`, hide `.recipe-card__sources-title`, `.recipe-card__sources-summary`, `.recipe-card__sources-list`, and `.recipe-kitchen-notes` toggle chrome while showing `.recipe-print-credit` as a compact 1-line footer).
6. `.agents/skills/weekly-grocery-order/scripts/consolidate_menu.py`:
   - Implement `collect_untested_warnings(menu_data: Dict[str, Any]) -> List[str]` inspecting `menu_data.get("meals") or []` for `meal.get("status") == "untested"`.
   - Include `"warnings": collect_untested_warnings(menu_data)` in `consolidate(menu_data)` output (preserving all existing keys `cart` and `skipped_pantry`), and write `[UNTESTED RECIPE NOTICE] <msg>` lines to `sys.stderr` in `main()` without changing exit code `0`.

- [ ] **Step 4: Rebuild Jekyll site and run consolidation + E2E tests to verify all pass**

Run: `$env:PATH = "C:\Ruby33-x64\bin;" + $env:PATH; bundle exec jekyll build; python -m unittest tests/test_consolidation.py tests/test_e2e_verification.py -v`
Expected: Jekyll build exits `0`; all unit and E2E tests (including `test_12_draft_isolation_and_tested_rendering`, JSON-LD validation, and `test_07` if clean or non-dirty checks) pass.

- [ ] **Step 5: Commit Task 4 locally**

```powershell
git add _layouts/recipe.html _includes/recipe-card.html _includes/recipe-catalog-grid.html _includes/recipe-schema.html index.md api/recipes.json api/weekly-menu.json llms.txt assets/css/main.scss .agents/skills/weekly-grocery-order/scripts/consolidate_menu.py tests/test_consolidation.py tests/test_e2e_verification.py
git commit -m "feat(site,b2a): surface recipe status badges, sources, draft isolation, and menu warnings"
```

---

### Task 5: Modular Pipeline Skills (`recipe-*`), Visuals Split & Shim, Deprecation Pointer & `AGENTS.md`

**Files:**
- Create: `.agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py`
- Modify: `.agents/skills/recipe-reviewer/scripts/generate_recipe_visuals.py` (replace with forwarding shim)
- Create: `.agents/skills/recipe-research/SKILL.md`
- Create: `.agents/skills/recipe-intake/SKILL.md`
- Create: `.agents/skills/recipe-author/SKILL.md`
- Create: `.agents/skills/recipe-review-panel/SKILL.md`
- Create: `.agents/skills/recipe-visuals/SKILL.md`
- Create: `.agents/skills/recipe-test-log/SKILL.md`
- Create: `.agents/skills/recipe-pipeline/SKILL.md`
- Modify: `.agents/skills/recipe-reviewer/SKILL.md`
- Modify: `AGENTS.md:18-26` and `AGENTS.md:36-74` and `AGENTS.md:116-135`
- Modify: `tests/test_recipe_pipeline.py`

**Interfaces:**
- Consumes: `.agents/skills/recipe-review-panel/scripts/audit_recipes.py` (Task 2) and `.agents/skills/recipe-review-panel/scripts/review_report.py` (Task 3).
- Produces:
  - 7 discoverable skill packages under `.agents/skills/` + deprecated `recipe-reviewer` pointer.
  - `.agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py` + backward-compatible shim at `.agents/skills/recipe-reviewer/scripts/generate_recipe_visuals.py`.

- [ ] **Step 1: Add failing `TestSkillPackageIntegrity` tests in `tests/test_recipe_pipeline.py`**

Add tests asserting:
1. All 7 new skills (`recipe-research`, `recipe-intake`, `recipe-author`, `recipe-review-panel`, `recipe-visuals`, `recipe-test-log`, `recipe-pipeline`) + `recipe-reviewer` exist under `.agents/skills/<name>/SKILL.md` with valid `---` YAML frontmatter containing non-empty `name:` (matching directory name) and `description:`.
2. `recipe-research/SKILL.md` documents both **Research mode** (`>=3` independent sources, `USDA`/`FDA` food-safety rule) and **Import mode** (`research-raw`), `sources.yml`, `[sN]` citations, and the `<=15`-line Gate-1 summary.
3. `recipe-author/SKILL.md` documents `status: draft`, 3-tier grammar, *Cooking for Engineers* block grid, and `TODO-source` (never inventing numbers).
4. `recipe-review-panel/SKILL.md` documents all 3 critics (`Culinary`, `Editorial`, `Visual`), explicit **no author context** isolation rule, `PENDING — run /browser` Chrome fallback, and `review_report.py` CLI usage.
5. `recipe-pipeline/SKILL.md` documents all 3 human gates (`Gate 1`, `Gate 2`, `Gate 3`) and `brief.md` stage transitions.
6. `.agents/skills/recipe-reviewer/scripts/generate_recipe_visuals.py` shim resolves `build_prompts` and `call_nano_banana` identically to `.agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py`, and `--help` exits `0` on all 5 script paths (3 canonical + 2 shims).

- [ ] **Step 2: Run `TestSkillPackageIntegrity` to verify it fails**

Run: `python -m unittest tests.test_recipe_pipeline.TestSkillPackageIntegrity -v`
Expected: FAIL (missing `SKILL.md` files and `recipe-visuals/scripts/generate_recipe_visuals.py`).

- [ ] **Step 3: Move `generate_recipe_visuals.py` with shim, author the 7 `SKILL.md` files, replace `recipe-reviewer/SKILL.md` with deprecation pointer, and update `AGENTS.md`**

1. Copy `.agents/skills/recipe-reviewer/scripts/generate_recipe_visuals.py` to `.agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py`, then replace `.agents/skills/recipe-reviewer/scripts/generate_recipe_visuals.py` with the same `importlib.util` forwarding shim pattern used in Task 2.
2. Author focused, self-contained `SKILL.md` files per Spec §§4–6:
   - `recipe-research/SKILL.md`: Research mode (`>=3` independent sources for core ratios/temps/times; USDA/FDA only for food-safety minimums; disagreements table with chosen resolution + rationale) and Import mode (normalizing `_drafts/recipes/<slug>/research-raw.<md|pdf|docx|txt>` into `sources.yml` + `[sN]`-cited `research.md`, searching web only for uncited numbers); outputs `<=15`-line Gate-1 brief.
   - `recipe-intake/SKILL.md`: Family recipe intake (`origin: family`) into `_drafts/recipes/<slug>/brief.md`; asks only missing yield/pan/heat/doneness questions; preserves family quirks; marks unknowns `TODO-ask`; outputs `<=15`-line Gate-1 brief.
   - `recipe-author/SKILL.md`: Reads dossier (`brief.md` + `research.md` + `sources.yml`), writes `_recipes/<slug>.md` with `status: "draft"`, enforces all 6 usability + *Cooking for Engineers* rectangular matrix rules, never invents numbers (emits `TODO-source` if absent from dossier), and runs `python .agents/skills/recipe-review-panel/scripts/audit_recipes.py _recipes/<slug>.md`.
   - `recipe-review-panel/SKILL.md`: Runs `audit_recipes.py`, archives prior `review.md` as `review-r<N-1>.md`, dispatches 3 parallel subagents passing ONLY file paths (`_recipes/<slug>.md`, `_drafts/recipes/<slug>/{brief.md,research.md,sources.yml}`) with zero authoring conversation context, embeds exact critic rubrics & prompt templates from Spec §§5.1–5.3 (including `chrome-devtools` 1280px/390px/lightbox/print checks and `PENDING — run /browser` fallback), merges stable IDs (`CUL-n`, `EDT-n`, `VIS-n`), runs `review_report.py --diff` and `review_report.py --check`.
   - `recipe-visuals/SKILL.md`: Runs `python .agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py ...`, verifies generated dish image matches actual recipe protein/garnish/cookware before wiring `image:`, or skips cleanly (visuals optional for publish).
   - `recipe-test-log/SKILL.md`: Prepends dated cook notes to `_drafts/recipes/<slug>/test-log.md`, updates `status: "tested"`, `tested_on: YYYY-MM-DD`, and optional 1–2 line `test_notes`, and runs a scoped critic pass if recipe quantities/steps were edited.
   - `recipe-pipeline/SKILL.md`: Stage router (`intake` -> `research` / `research-import` -> `gate-1` -> `authoring` -> `review` -> `gate-2` -> `published` -> `tested` in `brief.md`), halting for explicit user sign-off at Gate 1, Gate 2 (`review_report.py --approve`), and Gate 3.
3. Replace `.agents/skills/recipe-reviewer/SKILL.md` with a concise deprecation pointer mapping authoring rules -> `recipe-author`, auditing/panel -> `recipe-review-panel`, visuals -> `recipe-visuals`, and end-to-end flow -> `recipe-pipeline`.
4. Update `AGENTS.md` §1, §2.A, and §2.D to document the new provenance frontmatter fields, `_drafts/recipes/<slug>/` dossiers, the 7-skill pipeline, and preserved shim paths.

- [ ] **Step 4: Run `tests/test_recipe_pipeline.py` and `tests/test_recipe_reviewer.py` to verify all pass**

Run: `python -m unittest tests/test_recipe_pipeline.py tests/test_recipe_reviewer.py -v`
Expected: All tests in both suites `OK`.

- [ ] **Step 5: Commit Task 5 locally**

```powershell
git add .agents/skills/ AGENTS.md tests/test_recipe_pipeline.py
git commit -m "feat(skills): split recipe-reviewer into 7-skill stage-gated pipeline with shims"
```

---

### Task 6: Full Build, Live Server E2E Verification & Handoff Readiness Check

**Files:**
- Verify only (no new source edits unless verification uncovers a regression; if `_drafts/recipes/*/research-raw.*` files have been dropped by the user, run import + panel on `crispy-mongolian-beef-broccoli` and halt at Gate 2).

**Interfaces:**
- Consumes: All deliverables from Tasks 1–5.
- Produces: Clean `_site/` build, running local server check on `http://127.0.0.1:4000`, 100% green `unittest` suite, verified CLI dry runs, and clean local git status ready for `research-raw.*` backfill and Sub-project 3 (launch blog post).

- [ ] **Step 1: Run clean Jekyll production build**

Run: `$env:PATH = "C:\Ruby33-x64\bin;" + $env:PATH; bundle exec jekyll build`
Expected: Exit code `0` with zero Liquid or SCSS errors.

- [ ] **Step 2: Ensure local Jekyll server is serving on `http://127.0.0.1:4000` for HTTP E2E tests**

Start `bundle exec jekyll serve --port 4000 --no-watch` as a background daemon (`IsDaemon: true`) if port `4000` is not already listening, and verify `http://127.0.0.1:4000/` returns HTTP `200`.

- [ ] **Step 3: Run the complete Python test suite and CLI skill scripts**

Run: `python -m unittest discover -s tests -v; python .agents/skills/recipe-review-panel/scripts/audit_recipes.py; python .agents/skills/weekly-grocery-order/scripts/consolidate_menu.py --url _site/api/weekly-menu.json --dry-run`
Expected:
- Every test in `test_consolidation.py`, `test_e2e_verification.py` (with zero skipped server tests!), `test_recipe_reviewer.py`, and `test_recipe_pipeline.py` reports `OK`.
- `audit_recipes.py` exits `0` (`[PASS]` across all 5 recipes).
- `consolidate_menu.py --dry-run` exits `0`, prints consolidated cart + `[UNTESTED RECIPE NOTICE]` lines on `stderr`, and leaves `.cache/cart_ledger.json` untouched.

- [ ] **Step 4: Check git safety invariant and `_drafts/recipes/*/research-raw.*` handoff state**

Run: `git status --porcelain; git branch -r --list "origin/feat/agentic-recipe-blog"; Get-ChildItem -Path _drafts/recipes -Recurse -Filter "research-raw*"`
Expected:
- `git status --porcelain` output is empty.
- `origin/feat/agentic-recipe-blog` output is empty (unpushed).
- If any `research-raw.*` files are present in `_drafts/recipes/`, invoke `recipe-research` (import mode) + `recipe-review-panel` starting with `crispy-mongolian-beef-broccoli` and halt at Gate 2; otherwise report the 5 staging folders ready for the user's `research-raw.*` drop and offer to outline Sub-project 3 (the launch blog post).
