#!/usr/bin/env python3
"""Shared hook config: the opt-in marker check and audit-level resolution.

One place decides (a) whether a repo opted in and (b) how much the hooks do, so the
cost of the gates can be dialed down without turning them off. Levels, cheapest first:

    light     lint + block on error-severity rules only. No per-edit audit, no beads
              lookups, no LLM review. The floor that still keeps code clean.
    standard  light + per-edit audit feedback + beads state. The default.
    strict    standard + an LLM judgment review of the working diff at turn end (tokens).

Selection is dynamic: FABLE_AUDIT_LEVEL (env, per-session) overrides the repo default
in .claude/fable.json ("level": "..."), which overrides the built-in default.
"""
import json
import os
from pathlib import Path

LEVELS = ("light", "standard", "strict")
DEFAULT_LEVEL = "standard"


def load_config(root: Path):
    """Return the .claude/fable.json dict, or None if the repo hasn't opted in."""
    marker = root / ".claude" / "fable.json"
    if not marker.exists():
        return None
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def audit_level(cfg) -> str:
    """Resolve the active level: env FABLE_AUDIT_LEVEL > fable.json 'level' > default."""
    level = os.environ.get("FABLE_AUDIT_LEVEL") or (cfg or {}).get("level") or DEFAULT_LEVEL
    return level if level in LEVELS else DEFAULT_LEVEL
