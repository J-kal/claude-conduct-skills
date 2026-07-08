#!/usr/bin/env python3
"""SessionStart hook: re-inject repo state into context, in launched repos only.

Stdout is added to the model's context — this fights the real failure mode of the
instruction layer (rules and work-state decaying out of context), and fires again
after /clear and compaction. Never blocks (exit 0).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def beads_snapshot(root: Path) -> list[str]:
    """One summary line per non-empty beads status (in_progress, open); empty if bd is absent."""
    if not shutil.which("bd"):
        return []
    lines = []
    for status in ("in_progress", "open"):
        try:
            out = subprocess.run(["bd", "list", "--status", status, "--json"],
                                 capture_output=True, text=True, timeout=15, cwd=root)
            issues = json.loads(out.stdout)
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            continue
        if issues:
            shown = "; ".join(f"{i.get('id', '?')} {i.get('title', '')[:60]}" for i in issues[:10])
            lines.append(f"beads {status} ({len(issues)}): {shown}")
    return lines


def main() -> None:
    root = Path.cwd()
    if not (root / ".claude" / "fable.json").exists():
        return
    audit = subprocess.run([sys.executable, str(HERE / "audit.py"), str(root)],
                           capture_output=True, text=True)
    summary = audit.stdout.strip().splitlines()[-1] if audit.stdout.strip() else "audit produced no output"
    lines = [f"fable-os state: {summary}"]
    if audit.returncode != 0:
        lines.append("Audit has error-severity findings; the stop gate will block turn-end until they are fixed.")
    lines.extend(beads_snapshot(root))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
