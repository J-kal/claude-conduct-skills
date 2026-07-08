#!/usr/bin/env python3
"""Stop hook: in launched repos only, block turn-end until the gates pass, then reindex.

No-op (exit 0) unless .claude/fable.json exists in the cwd — repos opt in via the
launch-env skill, so the plugin's hooks never fire in unrelated folders.
Exit 2 (blocking) with the findings on stderr when any gate fails.

Gates, in order:
1. Mechanical audit (error-severity rules). Every level.
2. Beads honesty: no bead left in_progress at turn end. standard + strict.
3. LLM judgment review of the working diff (adds latency + token cost per turn).
   strict level, or legacy "llm_review": true in .claude/fable.json.

Gates 2 and 3 skip when stop_hook_active (the turn already continued from this hook)
so a converging fix loop can't nag or re-bill.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import audit_level, load_config  # noqa: E402

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
    """Findings for any bead left in_progress at turn end; empty if bd is absent or all clear."""
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
    """Run a narrow claude -p judgment review of the working diff; findings, or empty on OK/unavailable."""
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
    cfg = load_config(root)
    if cfg is None:
        return
    level = audit_level(cfg)
    try:
        hook_input = json.loads(sys.stdin.read().lstrip("\ufeff") or "{}")
    except (json.JSONDecodeError, OSError):
        hook_input = {}
    repeat = bool(hook_input.get("stop_hook_active"))

    # index first so a fresh repo can't deadlock on stale-index
    subprocess.run([sys.executable, str(HERE / "build_index.py"), str(root)], capture_output=True)
    problems = []
    # errors-only at every level: warns never block, so computing them here just burns time
    audit = subprocess.run(
        [sys.executable, str(HERE / "audit.py"), str(root), "--level", "light"],
        capture_output=True, text=True)
    if audit.returncode != 0:
        problems.append(audit.stdout + audit.stderr)

    if not repeat and level != "light":
        problems.extend(dangling_beads(root))
        if level == "strict" or cfg.get("llm_review"):
            problems.extend(llm_review(root))

    if problems:
        print("\n\n".join(problems), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
