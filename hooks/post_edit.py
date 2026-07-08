#!/usr/bin/env python3
"""PostToolUse hook: auto-fix lint after edits in launched repos. Never blocks (exit 0)."""
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path.cwd()
    if not (root / ".claude" / "fable.json").exists():
        return
    if shutil.which("ruff"):
        cmd = ["ruff", "check", "--fix", "--quiet", "."]
    elif shutil.which("poetry"):
        cmd = ["poetry", "run", "ruff", "check", "--fix", "--quiet", "."]
    else:
        return
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        # lint is best-effort; this hook must never block an edit
        print(f"post_edit: ruff skipped ({e})", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
