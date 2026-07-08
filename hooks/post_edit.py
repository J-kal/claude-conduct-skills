#!/usr/bin/env python3
"""PostToolUse hook: after edits in launched repos, auto-fix lint, then surface
error-severity audit findings back to the model while the context is hot.

Exit 2 does not undo the edit — it feeds stderr to the model as feedback, so
violations get corrected at edit time instead of batched at the stop gate.
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import audit_level, load_config  # noqa: E402

HERE = Path(__file__).parent
FAST_RULES = "duplicate-function,bare-except,unmarked-shortcut,weakened-test"


def main() -> None:
    root = Path.cwd()
    cfg = load_config(root)
    if cfg is None:
        return
    if shutil.which("ruff"):
        cmd = ["ruff", "check", "--fix", "--quiet", "."]
    elif shutil.which("poetry"):
        cmd = ["poetry", "run", "ruff", "check", "--fix", "--quiet", "."]
    else:
        cmd = None
    if cmd:
        try:
            subprocess.run(cmd, capture_output=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as e:
            # lint is best-effort; only audit findings below may exit 2
            print(f"post_edit: ruff skipped ({e})", file=sys.stderr)
    if audit_level(cfg) == "light":
        return  # light: lint only — defer the audit to the turn-end stop gate
    try:
        audit = subprocess.run(
            [sys.executable, str(HERE / "audit.py"), str(root), "--only", FAST_RULES],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return
    if audit.returncode != 0:
        print(audit.stdout + audit.stderr, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
