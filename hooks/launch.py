#!/usr/bin/env python3
"""Launch fable-os in the current repo: opt in to the plugin's gates.

Usage: python <plugin>/hooks/launch.py [target-repo-root]   (default: cwd)

Writes .claude/fable.json (the marker that activates the plugin's hooks here,
recording the plugin root so skills can resolve gate paths) and appends the
design defaults to the repo's CLAUDE.md with {FABLE} resolved to the plugin
path. Idempotent. Judgment steps (beads init, baseline audit, tracker seeding)
belong to the launch-env skill.
"""
import json
import sys
from pathlib import Path

MARKER = "# Fable Design Defaults"


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    plugin = Path(__file__).resolve().parent.parent

    fable_json = root / ".claude" / "fable.json"
    fable_json.parent.mkdir(parents=True, exist_ok=True)
    fable_json.write_text(json.dumps({"plugin_root": plugin.as_posix()}, indent=2) + "\n", encoding="utf-8")
    print(f"  .claude/fable.json (hooks now active here; plugin_root={plugin.as_posix()})")

    defaults = (plugin / "CLAUDE-global.md").read_text(encoding="utf-8").replace("{FABLE}", plugin.as_posix())
    claude_md = root / "CLAUDE.md"
    existing = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""
    if MARKER in existing:
        # shortcut: refresh replaces everything after the marker — keep repo-specific
        # notes ABOVE the marker; add block delimiters if trailing content ever matters
        existing = existing.split(MARKER, 1)[0].rstrip()
        print("  CLAUDE.md (defaults refreshed)")
    else:
        print("  CLAUDE.md (defaults appended)")
    claude_md.write_text((existing.rstrip() + "\n\n" + defaults).lstrip(), encoding="utf-8")

    print(f"\nLaunched in {root}")
    print("Next (launch-env skill): bd init if needed; baseline audit + index; seed tracker from findings")


if __name__ == "__main__":
    main()
