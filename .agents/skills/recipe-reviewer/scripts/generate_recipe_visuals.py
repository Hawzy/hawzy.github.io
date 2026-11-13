#!/usr/bin/env python3
"""Backward-compatible forwarding shim to .agents/skills/recipe-visuals/scripts/generate_recipe_visuals.py."""
import importlib.util
from pathlib import Path
import sys

_CANONICAL = (
    Path(__file__).resolve().parents[2]
    / "recipe-visuals"
    / "scripts"
    / "generate_recipe_visuals.py"
)
_SPEC = importlib.util.spec_from_file_location("_canonical_generate_recipe_visuals", _CANONICAL)
assert _SPEC and _SPEC.loader
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MOD
_SPEC.loader.exec_module(_MOD)

for _k, _v in _MOD.__dict__.items():
    if not _k.startswith("__") or _k == "__all__":
        globals()[_k] = _v

if __name__ == "__main__":
    sys.exit(_MOD.main())
