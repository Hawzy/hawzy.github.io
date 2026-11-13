#!/usr/bin/env python3
"""
Review Report Parser, Round Differ & Gate-2 Verdict/Promotion Engine.

Parses `_drafts/recipes/<slug>/review.md` files (Spec §5.4), computes Gate-2
verdict (`APPROVED` iff zero open BLOCKERs, valid waiver reasons, non-PENDING
visual row unless waived, and structural audit `PASS`), diffs across review
rounds, and promotes `_recipes/<slug>.md` frontmatter upon Gate-2 approval.

Uses Python 3 standard library only.
"""

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

HEADER_PATTERN = re.compile(
    r"^#\s*Review\s*[—\-]+\s*(?P<title>.+?)\s*\(round\s+(?P<round>\d+)\)\s*·\s*Verdict:\s*(?P<verdict>APPROVED|CHANGES REQUESTED)\s*$",
    re.IGNORECASE,
)

FINDING_PATTERN = re.compile(
    r"^\s*-\s*\[(?P<id>(?:CUL|EDT|VIS)-\d+)\]\s*(?P<body>.+?)\s*$"
)

WAIVER_CLAUSE_PATTERN = re.compile(
    r"(?:^|\||→|->)\s*Waived?\s*\(reason\)\s*:\s*(?P<reason>.*)$",
    re.IGNORECASE,
)

FIXED_CLAUSE_PATTERN = re.compile(
    r"(?:→|->)\s*(?:\[x\]\s*)?Fixed\b",
    re.IGNORECASE,
)

PLACEHOLDER_WAIVERS = {
    "",
    "TBD",
    "TODO",
    "NA",
    "N/A",
    "NONE",
    "FIX",
    "PENDING",
}


def _is_valid_waiver_reason(reason: str) -> bool:
    cleaned = reason.strip()
    if not cleaned:
        return False
    # Reject untouched template `Fix | Waive (reason): ___` or punctuation-only strings
    stripped_tokens = cleaned.strip("_-—. \t")
    if not stripped_tokens:
        return False
    if stripped_tokens.upper() in PLACEHOLDER_WAIVERS:
        return False
    alnum_count = sum(1 for ch in stripped_tokens if ch.isalnum())
    return alnum_count >= 4


def _classify_resolution(body: str) -> Tuple[str, str]:
    """
    Returns (resolution, waiver_reason) where resolution is one of:
    'open', 'fixed', or 'waived'.
    """
    # Split on the last arrow (`→` or `->`) if present
    arrow_parts = re.split(r"→|->", body)
    tail = arrow_parts[-1].strip() if len(arrow_parts) > 1 else body

    # If the tail still contains the untouched choice `Fix | Waive (reason):`, inspect after `Waive (reason):`
    if re.search(r"\bFix\s*\|\s*Waive", tail, re.IGNORECASE):
        m = WAIVER_CLAUSE_PATTERN.search(tail)
        if m and _is_valid_waiver_reason(m.group("reason")):
            return "waived", m.group("reason").strip()
        return "open", ""

    if FIXED_CLAUSE_PATTERN.search(body):
        return "fixed", ""

    m_waive = WAIVER_CLAUSE_PATTERN.search(tail) or WAIVER_CLAUSE_PATTERN.search(body)
    if m_waive:
        reason = m_waive.group("reason").strip()
        if _is_valid_waiver_reason(reason):
            return "waived", reason
        return "open", ""

    return "open", ""


def parse_review_markdown(md_text: str) -> Dict[str, Any]:
    """Parses a `review.md` document into structured critic rows and findings."""
    title = ""
    round_num = 1
    declared_verdict = "CHANGES REQUESTED"
    critic_rows: List[Dict[str, str]] = []
    findings: List[Dict[str, Any]] = []

    current_section: Optional[str] = None
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m_hdr = HEADER_PATTERN.match(line)
        if m_hdr:
            title = m_hdr.group("title").strip()
            round_num = int(m_hdr.group("round"))
            declared_verdict = m_hdr.group("verdict").upper().strip()
            continue

        if line.startswith("## "):
            sec_lower = line[3:].strip().lower()
            if sec_lower.startswith("blocker"):
                current_section = "BLOCKER"
            elif sec_lower.startswith("major"):
                current_section = "MAJOR"
            elif sec_lower.startswith("nit"):
                current_section = "NIT"
            else:
                current_section = None
            continue

        if line.startswith("|") and line.endswith("|") and current_section is None:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2:
                first = cells[0].lower()
                if first in ("critic", "") or set(first) <= {"-", ":"}:
                    continue
                critic_rows.append(
                    {
                        "critic": cells[0],
                        "score": cells[1],
                        "blockers": cells[2] if len(cells) > 2 else "",
                        "major": cells[3] if len(cells) > 3 else "",
                        "nit": cells[4] if len(cells) > 4 else "",
                    }
                )
            continue

        m_find = FINDING_PATTERN.match(raw_line)
        if m_find and current_section in ("BLOCKER", "MAJOR", "NIT"):
            fid = m_find.group("id").upper()
            body = m_find.group("body").strip()
            resolution, waiver_reason = _classify_resolution(body)
            findings.append(
                {
                    "id": fid,
                    "severity": current_section,
                    "text": body,
                    "resolution": resolution,
                    "waiver_reason": waiver_reason,
                }
            )

    return {
        "title": title,
        "round": round_num,
        "declared_verdict": declared_verdict,
        "critic_rows": critic_rows,
        "findings": findings,
    }


def compute_verdict(report: Dict[str, Any]) -> Tuple[str, List[str]]:
    """
    Computes Gate-2 verdict per Spec §5.3 & §5.4:
    APPROVED iff:
    1. Structural audit (script) row is present and == 'PASS'
    2. Visual (rendered) row is not 'PENDING' unless waived by a valid VIS-* blocker waiver
    3. Zero BLOCKER findings have resolution == 'open'
    """
    reasons: List[str] = []
    critic_rows = report.get("critic_rows") or []
    findings = report.get("findings") or []

    structural_status: Optional[str] = None
    visual_score: Optional[str] = None
    culinary_score: Optional[str] = None
    editorial_score: Optional[str] = None
    for row in critic_rows:
        cname = row.get("critic", "").lower()
        if "structural" in cname:
            structural_status = row.get("score", "").strip().upper()
        elif "visual" in cname:
            visual_score = row.get("score", "").strip()
        elif "culinary" in cname:
            culinary_score = row.get("score", "").strip()
        elif "editorial" in cname:
            editorial_score = row.get("score", "").strip()

    if structural_status != "PASS":
        reasons.append(
            f"Structural audit row must be 'PASS' (found '{structural_status or 'MISSING'}')."
        )
    if not culinary_score:
        reasons.append("Culinary & Safety critic row is missing from the scorecard.")
    if not editorial_score:
        reasons.append("Editorial & Usability critic row is missing from the scorecard.")
    if not visual_score:
        reasons.append("Visual (rendered) critic row is missing from the scorecard.")

    vis_waived = any(
        f.get("id", "").startswith("VIS-")
        and f.get("severity") == "BLOCKER"
        and f.get("resolution") == "waived"
        for f in findings
    )
    if visual_score and "PENDING" in visual_score.upper() and not vis_waived:
        reasons.append(
            f"Visual critic row is '{visual_score}' without a waived VIS-* blocker."
        )

    for f in findings:
        if f.get("severity") == "BLOCKER" and f.get("resolution") == "open":
            reasons.append(f"Open BLOCKER [{f.get('id')}]: {f.get('text')}")

    verdict = "APPROVED" if len(reasons) == 0 else "CHANGES REQUESTED"
    return verdict, reasons


def diff_rounds(prev_report: Dict[str, Any], curr_report: Dict[str, Any]) -> Dict[str, List[str]]:
    """Compares finding IDs between round N-1 and round N."""
    prev_map = {f["id"]: f for f in (prev_report.get("findings") or [])}
    curr_map = {f["id"]: f for f in (curr_report.get("findings") or [])}

    resolved: List[str] = []
    waived: List[str] = []
    persisting: List[str] = []
    new_ids: List[str] = []

    for fid, pf in prev_map.items():
        if fid not in curr_map:
            resolved.append(fid)
        else:
            cf = curr_map[fid]
            if cf.get("resolution") == "fixed":
                resolved.append(fid)
            elif cf.get("resolution") == "waived":
                waived.append(fid)
            else:
                persisting.append(fid)

    for fid, cf in curr_map.items():
        if fid not in prev_map:
            if cf.get("resolution") == "waived":
                waived.append(fid)
            elif cf.get("resolution") == "fixed":
                resolved.append(fid)
            else:
                new_ids.append(fid)

    return {
        "resolved": sorted(resolved),
        "waived": sorted(waived),
        "persisting": sorted(persisting),
        "new": sorted(new_ids),
    }


def format_diff_markdown(diff: Dict[str, List[str]], prev_round: int) -> str:
    """Formats round diff summary for `## Changes since round N-1`."""
    lines = [f"## Changes since round {prev_round}"]
    lines.append(f"- Resolved: {', '.join(diff['resolved']) if diff['resolved'] else 'none'}")
    lines.append(f"- Waived: {', '.join(diff['waived']) if diff['waived'] else 'none'}")
    lines.append(f"- Persisting: {', '.join(diff['persisting']) if diff['persisting'] else 'none'}")
    lines.append(f"- New: {', '.join(diff['new']) if diff['new'] else 'none'}")
    return "\n".join(lines)


def promote_recipe_frontmatter(
    recipe_md_text: str,
    round_num: int,
    approved_on: str,
) -> str:
    """
    Updates or inserts top-level `status:` ('draft' -> 'untested', preserving 'tested')
    and `review:` ({round, verdict: 'approved', approved_on}) inside the YAML frontmatter
    of a recipe Markdown file without modifying ingredients, instructions, or engineer_grid_html.
    """
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(approved_on).strip()):
        raise ValueError(f"Invalid approved_on date '{approved_on}': expected YYYY-MM-DD")
    lines = recipe_md_text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("Missing opening YAML frontmatter delimiter '---'")

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        raise ValueError("Missing closing YAML frontmatter delimiter '---'")

    newline = "\r\n" if lines[0].endswith("\r\n") else "\n"
    fm_lines = lines[1:end_idx]
    new_fm: List[str] = []
    status_written = False
    review_written = False

    review_block = [
        f"review:{newline}",
        f"  round: {int(round_num)}{newline}",
        f'  verdict: "approved"{newline}',
        f'  approved_on: "{approved_on}"{newline}',
    ]

    i = 0
    n = len(fm_lines)
    while i < n:
        line = fm_lines[i]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        if indent == 0 and stripped.startswith("status:"):
            _, val = stripped.split(":", 1)
            cur_status = val.strip().strip("\"'")
            target_status = "tested" if cur_status == "tested" else "untested"
            new_fm.append(f'status: "{target_status}"{newline}')
            status_written = True
            i += 1
            continue

        if indent == 0 and (stripped == "review:" or stripped.startswith("review:")):
            new_fm.extend(review_block)
            review_written = True
            i += 1
            while i < n:
                nxt = fm_lines[i]
                if not nxt.strip():
                    i += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                if nxt_indent == 0:
                    break
                i += 1
            continue

        new_fm.append(line)
        i += 1

    if not status_written:
        new_fm.insert(0, f'status: "untested"{newline}')
    if not review_written:
        new_fm.extend(review_block)

    return "".join([lines[0]] + new_fm + lines[end_idx:])


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description="Parse review.md reports, compute Gate-2 verdicts, diff rounds, and promote recipe frontmatter."
    )
    parser.add_argument("--check", metavar="REVIEW_MD", help="Check a review.md file and exit 0 iff APPROVED.")
    parser.add_argument("--diff", nargs=2, metavar=("PREV_MD", "CURR_MD"), help="Print markdown diff between two review rounds.")
    parser.add_argument("--approve", metavar="REVIEW_MD", help="Approve Gate 2 using REVIEW_MD and promote --recipe frontmatter.")
    parser.add_argument("--recipe", metavar="RECIPE_MD", help="Target _recipes/<slug>.md file for --approve.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Approval date YYYY-MM-DD (default: today).")
    parser.add_argument("--json", action="store_true", dest="json_only", help="Output JSON summary.")
    args = parser.parse_args()

    if args.diff:
        prev_rep = parse_review_markdown(Path(args.diff[0]).read_text(encoding="utf-8"))
        curr_rep = parse_review_markdown(Path(args.diff[1]).read_text(encoding="utf-8"))
        diff = diff_rounds(prev_rep, curr_rep)
        if args.json_only:
            print(json.dumps(diff, indent=2))
        else:
            print(format_diff_markdown(diff, prev_round=prev_rep.get("round", 1)))
        return 0

    target_review = args.check or args.approve
    if not target_review:
        parser.print_help()
        return 2

    review_path = Path(target_review)
    report = parse_review_markdown(review_path.read_text(encoding="utf-8"))
    verdict, reasons = compute_verdict(report)

    if args.approve:
        if not args.recipe:
            print("Error: --approve requires --recipe <_recipes/slug.md>.", file=sys.stderr)
            return 2
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(args.date).strip()):
            print(f"Error: --date must be YYYY-MM-DD (got '{args.date}').", file=sys.stderr)
            return 2
        if verdict != "APPROVED":
            print(f"[GATE-2 BLOCKED] Cannot promote {args.recipe}: verdict is {verdict}.", file=sys.stderr)
            for r in reasons:
                print(f"  - {r}", file=sys.stderr)
            return 1
        recipe_path = Path(args.recipe)
        updated = promote_recipe_frontmatter(
            recipe_path.read_text(encoding="utf-8"),
            round_num=report.get("round", 1),
            approved_on=args.date,
        )
        recipe_path.write_text(updated, encoding="utf-8")
        print(f"[GATE-2 APPROVED] Promoted {recipe_path.as_posix()} (round {report.get('round', 1)}, {args.date}).")
        return 0

    if args.json_only:
        print(
            json.dumps(
                {
                    "title": report["title"],
                    "round": report["round"],
                    "verdict": verdict,
                    "reasons": reasons,
                    "findings": report["findings"],
                },
                indent=2,
            )
        )
    else:
        print(f"Review: {report['title']} (round {report['round']}) -> {verdict}")
        for r in reasons:
            print(f"  - {r}")

    return 0 if verdict == "APPROVED" else 1


if __name__ == "__main__":
    sys.exit(main())
