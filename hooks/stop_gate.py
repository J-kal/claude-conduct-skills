#!/usr/bin/env python3
"""Stop hook: in launched repos only, block turn-end until the audit passes, then reindex.

No-op (exit 0) unless .claude/fable.json exists in the cwd — repos opt in via the
launch-env skill, so the plugin's hooks never fire in unrelated folders.
Exit 2 (blocking) with the findings on stderr when the audit fails.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main() -> None:
    root = Path.cwd()
    if not (root / ".claude" / "fable.json").exists():
        return
    # index first so a fresh repo can't deadlock on stale-index
    subprocess.run([sys.executable, str(HERE / "build_index.py"), str(root)], capture_output=True)
    audit = subprocess.run(
        [sys.executable, str(HERE / "audit.py"), str(root),
         "--skip", "long-function,print-in-library,single-impl-abstraction,trivial-wrapper,dead-function,stale-worktree"],
        capture_output=True, text=True)
    if audit.returncode != 0:
        print(audit.stdout + audit.stderr, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
