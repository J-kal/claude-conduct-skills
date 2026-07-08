#!/usr/bin/env python3
"""Stop hook: in launched repos only, block turn-end until the gates pass, then reindex.

No-op (exit 0) unless .claude/fable.json exists in the cwd — repos opt in via the
launch-env skill, so the plugin's hooks never fire in unrelated folders.
Exit 2 (blocking) with the findings on stderr when any gate fails.

Gates, in order:
1. Mechanical audit (error-severity rules).
2. Beads honesty: no bead left in_progress at turn end — finish it or demote with a note.
3. Optional LLM judgment review of the working diff — opt in per repo with
   "llm_review": true in .claude/fable.json (adds latency + token cost per turn).

Gates 2 and 3 skip when stop_hook_active (the turn already continued from this hook)
so a converging fix loop can't nag or re-bill.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent

JUDGMENT_PROMPT = """You are a strict reviewer gating an automated coding agent's diff. Review ONLY for:
1. smallest-diff violations: changes beyond what one task plausibly required
2. symptom patches: a guard added in one caller when a shared choke point should own the fix
3. new abstractions with fewer than two real consumers
4. new dependencies introduced

If none apply, reply with exactly: OK
Otherwise list findings, one line each: file:line — problem — the smaller alternative.

Diff:
"""


def dangling_beads(root: Path) -> list[str]:
    if not shutil.which("bd"):
        return []
    try:
        out = subprocess.run(["bd", "list", "--status", "in_progress", "--json"],
                             capture_output=True, text=True, timeout=15, cwd=root)
        issues = json.loads(out.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return []  # no tracker or unparseable output — nothing to enforce
    if not issues:
        return []
    ids = ", ".join(i.get("id", "?") for i in issues)
    return [f"Beads left in_progress at turn end ({ids}). Either continue the work now, "
            "or demote to open with a where-it-stands note (what's done, what's next, what's broken)."]


def llm_review(root: Path) -> list[str]:
    claude = shutil.which("claude")
    if not claude:
        return []
    diff = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, cwd=root).stdout
    if not diff.strip():
        return []
    try:
        # cwd = temp dir: no fable.json marker there, so the inner session's hooks no-op
        # shortcut: untracked new files aren't in `git diff HEAD`; add --intent-to-add staging if that gap matters
        res = subprocess.run([claude, "-p", JUDGMENT_PROMPT + diff[:20000]],
                             capture_output=True, text=True, timeout=240,
                             cwd=tempfile.gettempdir())
    except (OSError, subprocess.TimeoutExpired):
        return []
    verdict = res.stdout.strip()
    if res.returncode == 0 and verdict and not verdict.upper().startswith("OK"):
        return ["LLM judgment review found issues in the working diff — fix or justify to the user:\n" + verdict]
    return []


def main() -> None:
    root = Path.cwd()
    if not (root / ".claude" / "fable.json").exists():
        return
    try:
        hook_input = json.loads(sys.stdin.read().lstrip("\ufeff") or "{}")
    except (json.JSONDecodeError, OSError):
        hook_input = {}
    repeat = bool(hook_input.get("stop_hook_active"))

    # index first so a fresh repo can't deadlock on stale-index
    subprocess.run([sys.executable, str(HERE / "build_index.py"), str(root)], capture_output=True)
    problems = []
    audit = subprocess.run(
        [sys.executable, str(HERE / "audit.py"), str(root),
         "--skip", "long-function,print-in-library,single-impl-abstraction,trivial-wrapper,dead-function,stale-worktree"],
        capture_output=True, text=True)
    if audit.returncode != 0:
        problems.append(audit.stdout + audit.stderr)

    if not repeat:
        problems.extend(dangling_beads(root))
        try:
            cfg = json.loads((root / ".claude" / "fable.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cfg = {}
        if cfg.get("llm_review"):
            problems.extend(llm_review(root))

    if problems:
        print("\n\n".join(problems), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
