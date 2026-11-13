#!/usr/bin/env python3
"""
Backward-compatible forwarding shim for `.agents/skills/recipe-reviewer/scripts/audit_recipes.py`.
Canonical location: `.agents/skills/recipe-review-panel/scripts/audit_recipes.py`.
"""

import importlib.util
from pathlib import Path
import sys

_TARGET = (
    Path(__file__).resolve().parents[2]
    / "recipe-review-panel"
    / "scripts"
    / "audit_recipes.py"
).resolve()

_mod = None
for _existing in list(sys.modules.values()):
    _f = getattr(_existing, "__file__", None)
    if _f and Path(_f).resolve() == _TARGET:
        _mod = _existing
        break

if _mod is None:
    _spec = importlib.util.spec_from_file_location("_canonical_audit_recipes", str(_TARGET))
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Cannot load canonical audit_recipes from {_TARGET}")
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["_canonical_audit_recipes"] = _mod
    _spec.loader.exec_module(_mod)

for _k, _v in _mod.__dict__.items():
    if not _k.startswith("__") or _k in ("__doc__", "__all__"):
        globals()[_k] = _v

if __name__ == "__main__":
    sys.exit(_mod.main())
