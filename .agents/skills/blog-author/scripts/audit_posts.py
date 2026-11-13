#!/usr/bin/env python3
"""Deterministic auditor for hawzy.github.io blog posts and X/Twitter threads.

Uses Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TCO_URL_LENGTH = 23
MAX_TWEET_LENGTH = 280
URL_RE = re.compile(r"https?://\S+")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
TODO_MARKER_RE = re.compile(r"\bTODO-[A-Za-z0-9_-]+")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\((/[^)\s#?]+)")
TAG_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
X_POST_URL_RE = re.compile(r"^https://(?:x|twitter)\.com/[A-Za-z0-9_]{1,15}/status/\d+$")

KNOWN_SITE_ROUTES = (
    "/blog/",
    "/recipes/",
    "/projects/",
    "/about/",
    "/tags/",
    "/categories/",
    "/search/",
    "/api/",
    "/llms.txt",
)


def load_known_project_slugs(repo_root: Path) -> set[str]:
    """Load declared project slugs from _data/projects.yml using stdlib only."""
    projects_file = repo_root / "_data" / "projects.yml"
    if not projects_file.exists():
        return set()
    slugs: set[str] = set()
    for raw_line in projects_file.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if stripped.startswith("slug:"):
            val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            if val:
                slugs.add(val)
    return slugs


def load_banned_phrases(repo_root: Path) -> list[str]:
    """Load bullet items under '## Banned Phrases' from voice-profile.md."""
    voice_profile = repo_root / ".agents" / "skills" / "blog-voice" / "voice-profile.md"
    if not voice_profile.exists():
        voice_profile = Path(__file__).resolve().parents[2] / "blog-voice" / "voice-profile.md"
    if not voice_profile.exists():
        return []
    lines = voice_profile.read_text(encoding="utf-8").splitlines()
    in_section = False
    phrases: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("## "):
            if line.lower() == "## banned phrases":
                in_section = True
                continue
            if in_section:
                break
        elif in_section and line.startswith("- "):
            phrase = line[2:].strip()
            if phrase:
                phrases.append(phrase)
    return phrases


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str, list[str]]:
    """Minimal stdlib YAML frontmatter parser for Jekyll blog posts."""
    errors: list[str] = []
    if not text.startswith("---"):
        return {}, text, ["Missing YAML frontmatter opening '---'"]
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text, ["Missing YAML frontmatter closing '---'"]
    fm_raw = parts[1]
    body = parts[2]
    data: dict[str, object] = {}
    current_list_key: str | None = None

    for raw_line in fm_raw.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key is not None:
            item_val = stripped[2:].strip().strip('"').strip("'")
            existing = data.get(current_list_key)
            if isinstance(existing, list):
                existing.append(item_val)
            continue

        if ":" in raw_line and not raw_line.startswith((" ", "\t")):
            key, val_part = raw_line.split(":", 1)
            key = key.strip()
            val = val_part.strip()
            if not val:
                data[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                items = [
                    x.strip().strip('"').strip("'")
                    for x in inner.split(",")
                    if x.strip()
                ]
                data[key] = items
                current_list_key = None
            else:
                clean_val = val.strip('"').strip("'")
                if clean_val.lower() == "true":
                    data[key] = True
                elif clean_val.lower() == "false":
                    data[key] = False
                else:
                    data[key] = clean_val
                current_list_key = None

    return data, body, errors


def strip_code_blocks_and_spans(markdown_body: str) -> str:
    """Remove fenced code blocks and inline code spans before prose checks."""
    without_fenced = FENCED_CODE_RE.sub(" ", markdown_body)
    return INLINE_CODE_RE.sub(" ", without_fenced)


def audit_post_file(
    post_path: Path,
    repo_root: Path,
    banned_phrases: list[str] | None = None,
    require_additive_asset: bool | None = None,
) -> list[str]:
    """Audit a single Jekyll post file. Returns a list of error strings."""
    text = post_path.read_text(encoding="utf-8")
    fm, body, errors = _parse_frontmatter(text)
    if errors:
        return [f"{post_path.name}: {err}" for err in errors]

    try:
        rel_post = post_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        rel_post = post_path.as_posix()

    is_archived = fm.get("archived") is True or (
        rel_post.startswith("_posts/2022-") and fm.get("archived") is not False
    )
    if is_archived:
        return []

    title = fm.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append(f"{post_path.name}: missing non-empty 'title' in frontmatter")

    excerpt = fm.get("excerpt")
    if not isinstance(excerpt, str) or not excerpt.strip():
        errors.append(f"{post_path.name}: missing 'excerpt' in frontmatter")
    elif not (20 <= len(excerpt.strip()) <= 220):
        errors.append(
            f"{post_path.name}: 'excerpt' length ({len(excerpt.strip())}) must be between 20 and 220 chars"
        )

    categories = fm.get("categories")
    if not isinstance(categories, list) or len(categories) == 0:
        errors.append(f"{post_path.name}: missing non-empty 'categories' list in frontmatter")

    enforce_additive = (
        require_additive_asset
        if require_additive_asset is not None
        else rel_post.startswith("_posts/")
    )
    if enforce_additive or "additive_asset" in fm:
        additive_asset = fm.get("additive_asset")
        if not isinstance(additive_asset, str) or len(additive_asset.strip()) < 15:
            errors.append(
                f"{post_path.name}: missing or too-short 'additive_asset' in frontmatter (min 15 chars describing the blog-exclusive table/code/diagram)"
            )

    if "x_post_url" in fm:
        x_post_url = fm.get("x_post_url")
        if isinstance(x_post_url, str) and x_post_url.strip():
            if not X_POST_URL_RE.match(x_post_url.strip()):
                errors.append(
                    f"{post_path.name}: 'x_post_url' must match https://x.com/<handle>/status/<id>"
                )
        elif x_post_url is not None and x_post_url != "":
            errors.append(
                f"{post_path.name}: 'x_post_url' must match https://x.com/<handle>/status/<id>"
            )

    tags = fm.get("tags")
    if not isinstance(tags, list) or len(tags) == 0:
        errors.append(f"{post_path.name}: missing non-empty 'tags' list in frontmatter")
    else:
        for tag in tags:
            if not isinstance(tag, str) or not TAG_SLUG_RE.match(tag):
                errors.append(
                    f"{post_path.name}: tag '{tag}' must be lowercase hyphenated slug"
                )

    post_projects: list[str] = []
    if "projects" in fm:
        projects_val = fm.get("projects")
        if not isinstance(projects_val, list):
            errors.append(f"{post_path.name}: 'projects' frontmatter must be a list of slugs")
        else:
            for proj in projects_val:
                if not isinstance(proj, str) or not TAG_SLUG_RE.match(proj):
                    errors.append(
                        f"{post_path.name}: project '{proj}' must be lowercase hyphenated slug"
                    )
                else:
                    post_projects.append(proj)
    if "project" in fm:
        project_val = fm.get("project")
        if not isinstance(project_val, str) or not TAG_SLUG_RE.match(project_val):
            errors.append(
                f"{post_path.name}: project '{project_val}' must be lowercase hyphenated slug"
            )
        else:
            post_projects.append(project_val)

    known_projects = load_known_project_slugs(repo_root)
    if known_projects:
        for proj in post_projects:
            if proj not in known_projects:
                errors.append(
                    f"{post_path.name}: unknown project slug '{proj}' not found in _data/projects.yml"
                )

    prose = strip_code_blocks_and_spans(body)
    normalized_prose = prose.replace("\u2019", "'").replace("\u2018", "'")

    if banned_phrases is None:
        banned_phrases = load_banned_phrases(repo_root)

    for phrase in banned_phrases:
        norm_phrase = phrase.replace("\u2019", "'").replace("\u2018", "'")
        pattern = re.compile(r"\b" + re.escape(norm_phrase) + r"\b", re.IGNORECASE)
        if pattern.search(normalized_prose):
            errors.append(
                f"{post_path.name}: banned AI-slop phrase '{phrase}' found in prose"
            )

    for todo_match in TODO_MARKER_RE.findall(prose):
        errors.append(
            f"{post_path.name}: unresolved marker '{todo_match}' found in prose"
        )

    for rel_target in MARKDOWN_LINK_RE.findall(prose):
        if rel_target == "/" or any(
            rel_target == route.rstrip("/") or rel_target.startswith(route)
            for route in KNOWN_SITE_ROUTES
        ):
            continue
        candidate = repo_root / rel_target.lstrip("/")
        if not candidate.exists() and candidate.suffix == ".html":
            md_candidate = candidate.with_suffix(".md")
            if md_candidate.exists():
                continue
        if not candidate.exists():
            errors.append(
                f"{post_path.name}: broken internal asset/path link '{rel_target}'"
            )

    return errors


def compute_tweet_length(text: str) -> int:
    """Compute X/Twitter character length where every URL counts as 23 chars."""
    normalized = URL_RE.sub("X" * TCO_URL_LENGTH, text.strip())
    return len(normalized)


def audit_twitter_thread(thread_path: Path) -> list[str]:
    """Audit numbered tweets ('1/ ...', '2/ ...') in a twitter-thread.md file."""
    if not thread_path.exists():
        return [f"{thread_path}: file does not exist"]

    raw = thread_path.read_text(encoding="utf-8")
    # Split into numbered tweet blocks starting at line start with '<num>/ '
    matches = list(re.finditer(r"(?m)^(\d+)/\s+", raw))
    if not matches:
        return [f"{thread_path.name}: no numbered tweets ('1/ ...') found"]

    errors: list[str] = []
    for idx, match in enumerate(matches):
        tweet_num = match.group(1)
        body_start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw)
        tweet_body = raw[body_start:end].strip()
        full_tweet = raw[match.start() : end].strip()
        length = compute_tweet_length(full_tweet)
        if length > MAX_TWEET_LENGTH:
            errors.append(
                f"{thread_path.name}: tweet {tweet_num}/ exceeds {MAX_TWEET_LENGTH} chars (t.co-adjusted length: {length})"
            )
        if not tweet_body:
            errors.append(f"{thread_path.name}: tweet {tweet_num}/ is empty")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit blog posts and X/Twitter threads.")
    parser.add_argument("--post", type=Path, help="Specific _posts/<file>.md to audit")
    parser.add_argument(
        "--dossier",
        type=Path,
        help="Specific _drafts/posts/<slug> dossier directory to audit",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[4]
    if not (repo_root / "_posts").exists():
        if args.post and args.post.resolve().parent.name == "_posts":
            repo_root = args.post.resolve().parents[1]
        else:
            repo_root = Path.cwd()
    banned = load_banned_phrases(repo_root)
    all_errors: list[str] = []

    if args.post:
        post_path = args.post if args.post.is_absolute() else (repo_root / args.post)
        all_errors.extend(audit_post_file(post_path, repo_root, banned))
    else:
        posts_dir = repo_root / "_posts"
        for post_path in sorted(posts_dir.rglob("*.md")):
            all_errors.extend(audit_post_file(post_path, repo_root, banned))

    if args.dossier:
        dossier_dir = (
            args.dossier if args.dossier.is_absolute() else (repo_root / args.dossier)
        )
        for required_file in ("notes.md", "facts.md"):
            req_path = dossier_dir / required_file
            if not req_path.exists():
                all_errors.append(f"{dossier_dir.name}: missing required {required_file}")
        thread_path = dossier_dir / "twitter-thread.md"
        if thread_path.exists():
            all_errors.extend(audit_twitter_thread(thread_path))

    if all_errors:
        for err in all_errors:
            print(f"[FAIL] {err}", file=sys.stderr)
        return 1

    print("[OK] Blog post and thread audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
