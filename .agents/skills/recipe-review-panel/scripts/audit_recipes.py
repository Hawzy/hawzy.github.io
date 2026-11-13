#!/usr/bin/env python3
"""
Pre-Publish Recipe Usability, Provenance & Cooking-for-Engineers Matrix Auditor.

Validates _recipes/*.md files against the 7-point Recipe Review Panel rubric:
1. Chronological ingredient ordering (matching first mention in instructions)
2. Divided ingredient clarity (', divided' in display_text + multi-row grid split)
3. Inline measurement chips (`qty unit`) + bolded control emphasis (**...**)
4. Explicit cookware vessel cues + sensory/temperature doneness cues
5. Cooking for Engineers HTML block-grid ('engineer_grid_html') rectangular matrix geometry
6. Schema.org HowToStep cleanliness (no 'Step 1:' or 'Directions:' prefixes)
7. Provenance, status, review metadata, and source URL hygiene

Uses Python 3 standard library only.
"""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

STOPWORDS = {
    "fresh", "dried", "large", "small", "medium", "whole", "finely", "thinly",
    "thick", "coarse", "pure", "raw", "cold", "warm", "hot", "cut", "into",
    "with", "and", "for", "the", "from", "about", "each", "pack", "packs",
    "packages", "package", "cup", "cups", "tbsp", "tsp", "clove", "cloves",
    "stalk", "stalks", "sprig", "sprigs", "fillet", "fillets", "steak", "steaks",
    "divided", "low", "sodium", "rich", "extra", "virgin", "unsalted", "japanese",
    "american", "european", "atlantic", "usda", "prime", "diamond", "crystal",
    "serving", "sliced", "grated", "minced", "crushed", "shredded", "peeled",
    "juiced", "zested", "wedges", "boneless", "inches", "inch", "center",
    "style", "refined", "skin", "straight", "refrigerator", "microplane",
    "bias", "lightly", "wavy", "green", "red", "dark", "white", "black",
}

VESSEL_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?-(?:inch|quart|qt|pint)|skillet|saucepan|pot|bowl|sheet pan|baking sheet|wire rack|colander|carving board|wok|griddle)\b",
    re.IGNORECASE,
)

SENSORY_PATTERN = re.compile(
    r"(\d+\s*°F|rolling boil|simmer|shimmering|smoking|wisps of|golden|mahogany|crisp|crackly|jammy|fragrant|glossy|syrupy|opaque|foaming|pellicle|springy|tacky)",
    re.IGNORECASE,
)

SCHEMA_PREFIX_PATTERN = re.compile(
    r"^\s*(?:step\s*\d+\s*[:.\-]|directions?\s*[:.\-]|\d+\s*[.)]\s+)",
    re.IGNORECASE,
)

CHIP_QTY_PATTERN = re.compile(r"`[^`]+`")
BOLD_CONTROL_PATTERN = re.compile(r"\*\*[^*]+\*\*")
INLINE_QTY_PATTERN = re.compile(r"`[^`]+`|\*\*[^*]+\*\*")
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HTTP_URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)
TODO_MARKER_PATTERN = re.compile(r"\bTODO-(?:source|ask)\b", re.IGNORECASE)


def _unquote(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")):
        inner = val[1:-1]
        if val[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return val


def _parse_scalar(val: str) -> Any:
    raw = val.strip()
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return _unquote(raw)


def parse_recipe_frontmatter(md_text: str) -> Dict[str, Any]:
    """Parses the YAML frontmatter subset used in _recipes/*.md using Python stdlib."""
    lines = md_text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Missing opening YAML frontmatter delimiter '---'")

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        raise ValueError("Missing closing YAML frontmatter delimiter '---'")

    fm_lines = lines[1:end_idx]
    data: Dict[str, Any] = {
        "ingredients": [],
        "instructions": [],
        "sources": [],
        "review": {},
        "engineer_grid_html": "",
    }

    i = 0
    n = len(fm_lines)
    while i < n:
        line = fm_lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent == 0 and ":" in line:
            key, rest = line.split(":", 1)
            key = key.strip()
            rest_stripped = rest.strip()

            if rest_stripped in ("|", "|-", "|+"):
                i += 1
                block_lines: List[str] = []
                base_block_indent: Optional[int] = None
                while i < n:
                    bline = fm_lines[i]
                    if not bline.strip():
                        block_lines.append("")
                        i += 1
                        continue
                    bindent = len(bline) - len(bline.lstrip(" "))
                    if bindent == 0:
                        break
                    if base_block_indent is None:
                        base_block_indent = bindent
                    block_lines.append(bline[min(base_block_indent, bindent):])
                    i += 1
                data[key] = "\n".join(block_lines).strip()
                continue

            if key in ("ingredients", "sources") and rest_stripped in ("", "[]"):
                if rest_stripped == "[]":
                    data[key] = []
                    i += 1
                    continue
                i += 1
                items: List[Dict[str, Any]] = []
                current_item: Optional[Dict[str, Any]] = None
                while i < n:
                    iline = fm_lines[i]
                    istripped = iline.strip()
                    if not istripped or istripped.startswith("#"):
                        i += 1
                        continue
                    iindent = len(iline) - len(iline.lstrip(" "))
                    if iindent == 0:
                        break
                    if istripped.startswith("- "):
                        if current_item is not None:
                            items.append(current_item)
                        current_item = {}
                        kv_part = istripped[2:].strip()
                        if ":" in kv_part:
                            ik, iv = kv_part.split(":", 1)
                            current_item[ik.strip()] = _parse_scalar(iv)
                    elif current_item is not None and ":" in istripped:
                        ik, iv = istripped.split(":", 1)
                        current_item[ik.strip()] = _parse_scalar(iv)
                    i += 1
                if current_item is not None:
                    items.append(current_item)
                data[key] = items
                continue

            if key == "review" and rest_stripped in ("", "{}"):
                if rest_stripped == "{}":
                    data["review"] = {}
                    i += 1
                    continue
                i += 1
                rev_map: Dict[str, Any] = {}
                while i < n:
                    rline = fm_lines[i]
                    rstripped = rline.strip()
                    if not rstripped or rstripped.startswith("#"):
                        i += 1
                        continue
                    rindent = len(rline) - len(rline.lstrip(" "))
                    if rindent == 0:
                        break
                    if ":" in rstripped:
                        rk, rv = rstripped.split(":", 1)
                        rev_map[rk.strip()] = _parse_scalar(rv)
                    i += 1
                data["review"] = rev_map
                continue

            if key == "instructions" and rest_stripped == "":
                i += 1
                steps: List[str] = []
                while i < n:
                    sline = fm_lines[i]
                    sstripped = sline.strip()
                    if not sstripped or sstripped.startswith("#"):
                        i += 1
                        continue
                    sindent = len(sline) - len(sline.lstrip(" "))
                    if sindent == 0:
                        break
                    if sstripped.startswith("- "):
                        steps.append(str(_unquote(sstripped[2:].strip())))
                    i += 1
                data["instructions"] = steps
                continue

            data[key] = _parse_scalar(rest_stripped)
        i += 1

    return data


def validate_provenance_and_status(data: Dict[str, Any]) -> List[str]:
    """
    Validates provenance, lifecycle status, review metadata, and source URL hygiene:
    - origin in {'research', 'family'}
    - status in {'draft', 'untested', 'tested'}
    - tested_on (YYYY-MM-DD) required iff status == 'tested'
    - review ({round >= 0, verdict == 'approved', approved_on: YYYY-MM-DD}) required when status != 'draft'
    - sources: valid http(s) URLs + titles; >= 1 required when origin == 'research' and status != 'draft'
      unless grandfathered with review.round == 0
    - no unresolved TODO-source / TODO-ask markers when status != 'draft'
    """
    errors: List[str] = []
    origin = str(data.get("origin", "")).strip()
    status = str(data.get("status", "")).strip()
    tested_on = str(data.get("tested_on", "")).strip()
    sources = data.get("sources")
    review = data.get("review")

    if origin not in ("research", "family"):
        errors.append(
            f"[Rule 7 - Provenance & Status] Invalid or missing 'origin': '{origin}' (expected 'research' or 'family')."
        )
    if status not in ("draft", "untested", "tested"):
        errors.append(
            f"[Rule 7 - Provenance & Status] Invalid or missing 'status': '{status}' (expected 'draft', 'untested', or 'tested')."
        )

    if status == "tested":
        if not tested_on or not ISO_DATE_PATTERN.match(tested_on):
            errors.append(
                "[Rule 7 - Provenance & Status] Recipe with status='tested' requires 'tested_on' in YYYY-MM-DD format."
            )
    elif tested_on:
        errors.append(
            f"[Rule 7 - Provenance & Status] 'tested_on' ('{tested_on}') is only valid when status='tested' (current status='{status}')."
        )

    review_round: Optional[int] = None
    if status in ("untested", "tested"):
        if not isinstance(review, dict) or not review:
            errors.append(
                f"[Rule 7 - Provenance & Status] Non-draft recipe (status='{status}') requires a 'review' block."
            )
        else:
            raw_round = review.get("round")
            verdict = str(review.get("verdict", "")).strip()
            approved_on = str(review.get("approved_on", "")).strip()
            if not isinstance(raw_round, int) or isinstance(raw_round, bool) or raw_round < 0:
                errors.append(
                    f"[Rule 7 - Provenance & Status] 'review.round' must be an integer >= 0 (got {raw_round!r})."
                )
            else:
                review_round = raw_round
            if verdict != "approved":
                errors.append(
                    f"[Rule 7 - Provenance & Status] Non-draft recipe requires review.verdict='approved' (got '{verdict}')."
                )
            if not approved_on or not ISO_DATE_PATTERN.match(approved_on):
                errors.append(
                    f"[Rule 7 - Provenance & Status] 'review.approved_on' must be YYYY-MM-DD (got '{approved_on}')."
                )

    if sources is None:
        sources_list: List[Any] = []
    elif isinstance(sources, list):
        sources_list = sources
    else:
        errors.append("[Rule 7 - Provenance & Status] 'sources' must be a YAML list.")
        sources_list = []

    for idx, src in enumerate(sources_list, start=1):
        if not isinstance(src, dict):
            errors.append(f"[Rule 7 - Provenance & Status] Source #{idx} must be a mapping.")
            continue
        title = str(src.get("title", "")).strip()
        url = str(src.get("url", "")).strip()
        if not title:
            errors.append(f"[Rule 7 - Provenance & Status] Source #{idx} is missing a non-empty 'title'.")
        if not url or not HTTP_URL_PATTERN.match(url):
            errors.append(
                f"[Rule 7 - Provenance & Status] Source #{idx} has invalid or non-HTTP(S) 'url': '{url}'."
            )

    if origin == "research" and status in ("untested", "tested"):
        is_grandfathered = review_round == 0
        if len(sources_list) == 0 and not is_grandfathered:
            errors.append(
                "[Rule 7 - Provenance & Status] Recipe with origin='research' and review.round >= 1 requires at least 1 entry in 'sources'."
            )

    if status in ("untested", "tested"):
        for step_idx, step in enumerate(data.get("instructions") or [], start=1):
            if TODO_MARKER_PATTERN.search(str(step)):
                errors.append(
                    f"[Rule 7 - Provenance & Status] Unresolved TODO-source/TODO-ask marker in step {step_idx} of non-draft recipe."
                )
        for ing in data.get("ingredients") or []:
            if isinstance(ing, dict) and TODO_MARKER_PATTERN.search(str(ing.get("display_text", ""))):
                errors.append(
                    f"[Rule 7 - Provenance & Status] Unresolved TODO-source/TODO-ask marker in ingredient '{ing.get('item', '')}'."
                )

    return errors


class _EngineerGridParser(HTMLParser):
    """Extracts one or more <table> elements with <thead>/<tbody> cell structure for 2D span verification."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: List[Dict[str, Any]] = []
        self._current_table: Optional[Dict[str, Any]] = None
        self.in_thead = False
        self.in_tbody = False
        self._current_row: Optional[List[Dict[str, Any]]] = None
        self._current_cell: Optional[Dict[str, Any]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_dict = {k: (v or "") for k, v in attrs}
        classes = set(attr_dict.get("class", "").split())

        if tag == "table":
            self._current_table = {
                "classes": classes,
                "thead_rows": [],
                "tbody_rows": [],
            }
            self.tables.append(self._current_table)
        elif tag == "thead":
            self.in_thead = True
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "tr":
            self._current_row = []
        elif tag in ("td", "th") and self._current_row is not None:
            try:
                rowspan = int(attr_dict.get("rowspan", "1") or "1")
            except ValueError:
                rowspan = -1
            try:
                colspan = int(attr_dict.get("colspan", "1") or "1")
            except ValueError:
                colspan = -1
            self._current_cell = {
                "tag": tag,
                "classes": classes,
                "rowspan": rowspan,
                "colspan": colspan,
                "data_base_qty": attr_dict.get("data-base-qty"),
                "text": "",
            }

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._current_cell["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._current_cell is not None and self._current_row is not None:
            self._current_cell["text"] = " ".join(self._current_cell["text"].split())
            self._current_row.append(self._current_cell)
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            if self.in_thead:
                self._current_table["thead_rows"].append(self._current_row)
            else:
                self._current_table["tbody_rows"].append(self._current_row)
            self._current_row = None
        elif tag == "thead":
            self.in_thead = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "table":
            self._current_table = None


def _validate_single_grid_table(
    table: Dict[str, Any], prefix: str = ""
) -> Tuple[List[str], List[str]]:
    """Validates rectangular R x C occupancy and column roles for a single <table class='engineer-grid-table'>."""
    errors: List[str] = []
    ing_names: List[str] = []

    if "engineer-grid-table" not in table["classes"]:
        errors.append(f"{prefix}<table> in 'engineer_grid_html' must have class 'engineer-grid-table'.")

    rows = table["tbody_rows"]
    num_rows = len(rows)
    if num_rows == 0:
        errors.append(f"{prefix}Block-grid <table> has 0 tbody rows.")
        return errors, ing_names

    occupied: Dict[Tuple[int, int], str] = {}
    placed_cells: List[Dict[str, Any]] = []
    row_max_cols: List[int] = [0] * num_rows

    for r_idx, row in enumerate(rows):
        c_idx = 0
        for cell in row:
            while (r_idx, c_idx) in occupied:
                c_idx += 1

            rs = cell["rowspan"]
            cs = cell["colspan"]
            if rs < 1 or cs < 1:
                errors.append(f"{prefix}Invalid rowspan={rs} or colspan={cs} at row {r_idx}, col {c_idx}.")
                continue

            if r_idx + rs > num_rows:
                errors.append(
                    f"{prefix}Cell '{cell['text'][:30]}' at row {r_idx}, col {c_idx} has rowspan={rs}, overflowing total tbody rows ({num_rows})."
                )

            for rr in range(r_idx, min(num_rows, r_idx + rs)):
                for cc in range(c_idx, c_idx + cs):
                    if (rr, cc) in occupied:
                        errors.append(
                            f"{prefix}Matrix collision at (row={rr}, col={cc}) between '{occupied[(rr, cc)]}' and '{cell['text'][:30]}'."
                        )
                    occupied[(rr, cc)] = cell["text"][:30] or f"r{r_idx}c{c_idx}"
                    if cc + 1 > row_max_cols[rr]:
                        row_max_cols[rr] = cc + 1

            placed_cells.append(
                {
                    "r": r_idx,
                    "c": c_idx,
                    "rs": rs,
                    "cs": cs,
                    "classes": cell["classes"],
                    "text": cell["text"],
                }
            )
            c_idx += cs

        while (r_idx, c_idx) in occupied:
            if c_idx + 1 > row_max_cols[r_idx]:
                row_max_cols[r_idx] = c_idx + 1
            c_idx += 1

    if len(set(row_max_cols)) != 1:
        errors.append(f"{prefix}Jagged block-grid row widths detected across tbody rows: {row_max_cols}.")
        return errors, ing_names

    num_cols = row_max_cols[0]
    if num_cols < 4:
        errors.append(
            f"{prefix}Block grid must have at least 4 columns (3 ingredient cols + >=1 action col), found {num_cols}."
        )

    for rr in range(num_rows):
        for cc in range(num_cols):
            if (rr, cc) not in occupied:
                errors.append(f"{prefix}Unfilled hole in block-grid matrix at (row={rr}, col={cc}).")

    # Verify thead column width if present
    for h_idx, hrow in enumerate(table["thead_rows"]):
        h_width = sum(max(1, hc["colspan"]) for hc in hrow)
        if h_width != num_cols:
            errors.append(
                f"{prefix}<thead> row {h_idx} spans {h_width} columns, which does not match <tbody> width {num_cols}."
            )

    # Check ingredient columns 0..2 and action cells >= 3
    final_col_cells = []
    for p in placed_cells:
        c = p["c"]
        cls = p["classes"]
        if c == 0:
            if "ing-qty" not in cls or p["rs"] != 1 or p["cs"] != 1:
                errors.append(f"{prefix}Row {p['r']} col 0 must be a 1x1 'td.ing-qty' cell.")
        elif c == 1:
            if "ing-unit" not in cls or p["rs"] != 1 or p["cs"] != 1:
                errors.append(f"{prefix}Row {p['r']} col 1 must be a 1x1 'td.ing-unit' cell.")
        elif c == 2:
            if "ing-name" not in cls or p["rs"] != 1 or p["cs"] < 1:
                errors.append(f"{prefix}Row {p['r']} col 2 must be a 1-row 'td.ing-name' cell.")
            elif c + p["cs"] >= num_cols:
                errors.append(
                    f"{prefix}Row {p['r']} 'td.ing-name' colspan={p['cs']} spans into the final assembly column without an action cell."
                )
            ing_names.append(p["text"].lower())
        else:
            if "action-cell" not in cls:
                errors.append(
                    f"{prefix}Cell at (row={p['r']}, col={c}) must include class 'action-cell' (found {sorted(cls)})."
                )
        if p["c"] + p["cs"] == num_cols and p["c"] >= 3:
            final_col_cells.append(p)

    # Progressive convergence check: rightmost column should merge all rows (rowspan == num_rows)
    if len(final_col_cells) != 1 or final_col_cells[0]["r"] != 0 or final_col_cells[0]["rs"] != num_rows:
        errors.append(
            f"{prefix}Final assembly column (col {num_cols - 1}) must be a single full-height cell spanning all {num_rows} rows."
        )

    return errors, ing_names


def validate_engineer_grid(grid_html: str, expected_min_rows: int) -> Tuple[List[str], List[str]]:
    """
    Mathematically validates one or more Cooking for Engineers 2D HTML tables:
    - Supports single-table recipes or multi-part sub-grids (e.g., Part 1 Sauce + Part 2 Stir-Fry)
    - Verifies .engineer-grid-table class and independent R x C rectangular geometry per table
    - Ensures total tbody rows across all sub-grids >= expected_min_rows.
    Returns (errors, body_ing_names).
    """
    errors: List[str] = []
    ing_names: List[str] = []

    if not grid_html or not grid_html.strip():
        return ["Missing 'engineer_grid_html' frontmatter table."], ing_names

    parser = _EngineerGridParser()
    parser.feed(grid_html)

    if not parser.tables:
        return ["'engineer_grid_html' does not contain a <table> element."], ing_names

    multi = len(parser.tables) > 1
    total_tbody_rows = sum(len(t["tbody_rows"]) for t in parser.tables)
    if total_tbody_rows < expected_min_rows:
        errors.append(
            f"Block grid has {total_tbody_rows} tbody rows, expected at least {expected_min_rows} (one per ingredient + divided splits)."
        )

    for idx, table in enumerate(parser.tables, start=1):
        prefix = f"Sub-grid {idx}: " if multi else ""
        t_errors, t_ings = _validate_single_grid_table(table, prefix=prefix)
        errors.extend(t_errors)
        ing_names.extend(t_ings)

    return errors, ing_names


GENERIC_INGREDIENT_HEADS = {
    "oil", "oils", "sauce", "sauces", "soy", "wine", "wines",
    "broth", "stock", "vinegar", "salt", "sugar", "pepper", "peppers",
    "onion", "onions", "whites", "greens",
}


def _ingredient_token_tiers(ing: Dict[str, Any]) -> List[List[str]]:
    """
    Builds prioritized token tiers for locating an ingredient in instruction prose without
    false-positive collisions across generic head nouns (e.g., 'dark soy sauce' vs 'low-sodium soy sauce',
    'toasted sesame oil' vs 'neutral oil', 'white onion' vs 'scallion').
    """
    item = str(ing.get("item", "")).lower().strip()
    display = str(ing.get("display_text", "")).lower().strip()

    tier1_phrases: List[str] = []
    if item:
        tier1_phrases.append(item)
        if item.endswith("y") and len(item) > 2 and item[-2] not in "aeiou":
            tier1_phrases.append(item[:-1] + "ies")
        elif item.endswith("s"):
            if len(item) > 3:
                tier1_phrases.append(item[:-1])
        else:
            tier1_phrases.append(item + "s")

    tier2_distinctive: List[str] = []
    for w in re.findall(r"[a-z]{3,}", item):
        if w not in STOPWORDS and w not in GENERIC_INGREDIENT_HEADS and w not in tier2_distinctive:
            tier2_distinctive.append(w)
            if w.endswith("s") and len(w) > 4 and w[:-1] not in tier2_distinctive:
                tier2_distinctive.append(w[:-1])

    tier3_fallback: List[str] = []
    for w in re.findall(r"[a-z]{3,}", f"{item} {display}"):
        if w not in STOPWORDS and w not in tier1_phrases and w not in tier2_distinctive and w not in tier3_fallback:
            tier3_fallback.append(w)
            if w.endswith("s") and len(w) > 4 and w[:-1] not in tier3_fallback:
                tier3_fallback.append(w[:-1])

    return [t for t in (tier1_phrases, tier2_distinctive, tier3_fallback) if t]


def _scan_steps_for_tokens(tokens: List[str], instructions: List[str]) -> List[Tuple[int, int]]:
    hits: List[Tuple[int, int]] = []
    for s_idx, step in enumerate(instructions):
        step_lower = step.lower()
        best_pos: Optional[int] = None
        for tok in tokens:
            m = re.search(r"\b" + re.escape(tok) + r"\b", step_lower)
            if m:
                if best_pos is None or m.start() < best_pos:
                    best_pos = m.start()
        if best_pos is not None:
            hits.append((s_idx, best_pos))
    return hits


def find_ingredient_mentions(ing: Dict[str, Any], instructions: List[str]) -> List[Tuple[int, int]]:
    """Returns list of (step_idx, char_offset) where the ingredient is mentioned."""
    for tier_tokens in _ingredient_token_tiers(ing):
        hits = _scan_steps_for_tokens(tier_tokens, instructions)
        if hits:
            return hits
    return []


def audit_recipe_data(
    data: Dict[str, Any],
    source_name: str = "<recipe>",
    require_provenance: bool = False,
) -> Dict[str, Any]:
    """Runs usability, block-grid, and provenance checks on parsed recipe frontmatter."""
    errors: List[str] = []
    ingredients: List[Dict[str, Any]] = data.get("ingredients") or []
    instructions: List[str] = data.get("instructions") or []
    grid_html: str = data.get("engineer_grid_html") or ""

    if not ingredients:
        errors.append("Recipe has an empty 'ingredients' list.")
    if not instructions:
        errors.append("Recipe has an empty 'instructions' list.")

    # Rule 6: Schema.org Cleanliness (no 'Step 1:' or 'Directions:' prefixes)
    for idx, step in enumerate(instructions, start=1):
        if SCHEMA_PREFIX_PATTERN.search(step):
            errors.append(
                f"[Rule 6 - Schema Hygiene] Step {idx} starts with a prohibited prefix ('Step N' / 'Directions'): '{step[:50]}...'"
            )

    # Rule 3: 3-Tier Instruction Typography (`qty` chips for ingredients + **bold** for heat/time/temp)
    annotated_step_count = 0
    chip_step_count = 0
    bold_control_step_count = 0
    for step in instructions:
        has_chip = bool(CHIP_QTY_PATTERN.search(step))
        has_bold = bool(BOLD_CONTROL_PATTERN.search(step))
        if has_chip:
            chip_step_count += 1
        if has_bold:
            bold_control_step_count += 1
        if has_chip or has_bold:
            annotated_step_count += 1
    if instructions and chip_step_count == 0:
        errors.append("[Rule 3 - Inline Measurements] Zero instruction steps contain inline measurement chips (`...`).")
    if instructions and bold_control_step_count == 0:
        errors.append("[Rule 3 - Control Emphasis] Zero instruction steps highlight stove/timer/temp controls with **bold**.")

    # Rule 1 & Rule 2: Chronological Ingredient Order & Divided Clarity
    first_positions: List[Tuple[int, int, str]] = []
    divided_count = 0
    for ing in ingredients:
        item_name = str(ing.get("item", "unknown"))
        display_text = str(ing.get("display_text", ""))
        mentions = find_ingredient_mentions(ing, instructions)
        if not mentions:
            errors.append(f"[Rule 1 - Chronology] Ingredient '{item_name}' is never mentioned in 'instructions'.")
            continue

        first_step, first_char = mentions[0]
        first_positions.append((first_step, first_char, item_name))

        # Verify the step introducing this ingredient has a backtick measurement chip (`qty unit`)
        intro_step_text = instructions[first_step]
        if not CHIP_QTY_PATTERN.search(intro_step_text):
            errors.append(
                f"[Rule 3 - Inline Measurements] Step {first_step + 1} introduces '{item_name}' without inline measurement chip (`...`)."
            )

        is_marked_divided = "divided" in display_text.lower()
        if is_marked_divided:
            divided_count += 1
            if len(mentions) < 2:
                errors.append(
                    f"[Rule 2 - Divided Ingredients] '{item_name}' is marked ', divided' in display_text but only appears in 1 instruction step."
                )

    for idx in range(len(first_positions) - 1):
        curr_step, curr_char, curr_name = first_positions[idx]
        next_step, next_char, next_name = first_positions[idx + 1]
        if (curr_step, curr_char) > (next_step, next_char):
            errors.append(
                f"[Rule 1 - Chronology] Out-of-order ingredient: '{curr_name}' (first used in step {curr_step + 1}) "
                f"is listed before '{next_name}' (first used earlier in step {next_step + 1})."
            )

    # Rule 4: Sensory Cues + Vessel Sizes
    joined_steps = " ".join(instructions)
    if not VESSEL_PATTERN.search(joined_steps):
        errors.append("[Rule 4 - Vessel Sizes] Instructions lack explicit cookware/vessel sizes.")
    if not SENSORY_PATTERN.search(joined_steps):
        errors.append("[Rule 4 - Sensory Cues] Instructions lack sensory or thermal doneness cues.")

    # Rule 5: Cooking for Engineers Block Grid Matrix
    expected_rows = len(ingredients) + divided_count
    grid_errors, grid_ing_names = validate_engineer_grid(grid_html, expected_min_rows=expected_rows)
    for gerr in grid_errors:
        errors.append(f"[Rule 5 - Engineer Block Grid] {gerr}")

    # Rule 7: Provenance & Status
    if require_provenance or "origin" in data or "status" in data:
        errors.extend(validate_provenance_and_status(data))

    review_obj = data.get("review") if isinstance(data.get("review"), dict) else {}
    return {
        "source": source_name,
        "slug": data.get("slug", ""),
        "title": data.get("title", ""),
        "origin": data.get("origin", ""),
        "status": data.get("status", ""),
        "review_round": review_obj.get("round"),
        "passed": len(errors) == 0,
        "ingredient_count": len(ingredients),
        "divided_ingredients": divided_count,
        "instruction_count": len(instructions),
        "bolded_steps": annotated_step_count,
        "chip_steps": chip_step_count,
        "bold_control_steps": bold_control_step_count,
        "grid_rows": len(grid_ing_names),
        "errors": errors,
    }


def audit_file(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = parse_recipe_frontmatter(text)
    return audit_recipe_data(data, source_name=path.as_posix(), require_provenance=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit _recipes/*.md files against the 7-point Culinary Usability, Provenance & Block Grid rubric."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional recipe Markdown file path(s). Defaults to all _recipes/*.md files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_only",
        help="Emit machine-parseable JSON output only.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[4]
    if args.paths:
        target_files = [Path(p) for p in args.paths]
    else:
        candidates = [
            repo_root / "_recipes",
            Path.cwd() / "_recipes",
            Path("C:/github/agy/blog/_recipes"),
        ]
        recipes_dir = next((c for c in candidates if c.is_dir()), repo_root / "_recipes")
        target_files = sorted(recipes_dir.glob("*.md"))

    if not target_files:
        print("No recipe files found to audit.", file=sys.stderr)
        return 1

    reports = [audit_file(p) for p in target_files]
    all_passed = all(r["passed"] for r in reports)

    if args.json_only:
        print(json.dumps({"all_passed": all_passed, "reports": reports}, indent=2))
        return 0 if all_passed else 1

    print("=" * 80)
    print(" RECIPE REVIEW PANEL & BLOCK-GRID PRE-PUBLISH AUDIT")
    print("=" * 80)
    for rep in reports:
        status = "PASS" if rep["passed"] else "FAIL"
        print(
            f"[{status}] {rep['title']} ({rep['source']}) - "
            f"origin={rep['origin']}, status={rep['status']}, "
            f"{rep['ingredient_count']} ingredients, {rep['grid_rows']} grid rows, "
            f"{rep['chip_steps']} chip steps, {rep['bold_control_steps']} bold-control steps"
        )
        for err in rep["errors"]:
            print(f"    - {err}")
    print("=" * 80)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
