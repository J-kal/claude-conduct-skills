#!/usr/bin/env python3
"""Keep a Claude Code run alive: auto-restart after usage-limit exhaustion or a crash.

Usage (from the launched repo root):
    python <plugin>/hooks/keepalive.py "/cleanup"     # start a task, restart until it exits clean
    python <plugin>/hooks/keepalive.py                # no prompt: resume the last session here

Runs `claude -p <prompt>`; on a nonzero exit it resumes the SAME conversation with
`claude --continue`, waiting long (default 30 min) when the output looks like a
usage/rate limit and with exponential backoff for crashes. Stops on the first clean
exit. Recovery works because the system keeps state on disk: beads + the SessionStart
hook re-inject where things stood, so the resumed session re-orients itself.
"""
import argparse
import re
import shutil
import subprocess
import sys
import time

LIMIT_RE = re.compile(r"usage limit|rate limit|overloaded|429", re.I)
RESUME_PROMPT = ("You were interrupted (crash or usage limit). Re-orient from beads "
                 "(bd list) and on-disk state, then continue where you left off.")


def attempt(cmd: list[str]) -> tuple[int, bool]:
    res = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(res.stdout)
    sys.stderr.write(res.stderr)
    return res.returncode, bool(LIMIT_RE.search(res.stdout + res.stderr))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prompt", nargs="?", default="", help="initial prompt; empty = resume last session")
    ap.add_argument("--max-restarts", type=int, default=20)
    ap.add_argument("--limit-wait", type=int, default=1800, help="seconds to wait after a usage/rate limit")
    args = ap.parse_args()
    claude = shutil.which("claude")
    if not claude:
        sys.exit("keepalive: claude CLI not on PATH")

    cmd = [claude, "-p", args.prompt] if args.prompt else [claude, "--continue", "-p", RESUME_PROMPT]
    for restart in range(args.max_restarts + 1):
        code, hit_limit = attempt(cmd)
        if code == 0:
            print("keepalive: clean exit", file=sys.stderr)
            return
        if restart == args.max_restarts:
            break
        wait = args.limit_wait if hit_limit else min(60 * 2 ** restart, 900)
        print(f"keepalive: exit={code} limit={hit_limit}; restart {restart + 1}/{args.max_restarts} "
              f"in {wait // 60} min", file=sys.stderr)
        time.sleep(wait)
        cmd = [claude, "--continue", "-p", RESUME_PROMPT]
    sys.exit(f"keepalive: gave up after {args.max_restarts} restarts")


if __name__ == "__main__":
    main()
