#!/usr/bin/env python3
"""PreToolUse hook: block rule violations BEFORE they land, in launched repos only.

Reads the Claude Code hook JSON on stdin. Exit 2 = deny (stderr goes back to the
model as feedback), exit 0 = allow. No-op without the .claude/fable.json marker.

Checks (each converts a CLAUDE-global prompt rule into a gate):
- Bash: no new-dependency installs without explicit user approval.
- Write: no regenerating an existing .py file — edit in place.
- Write/Edit: no new top-level `def` whose name already lives elsewhere (SYMBOLS.md).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_duplicates import EXEMPT_NAMES  # noqa: E402
from config import load_config  # noqa: E402

APPROVAL_TOKEN = "# user-approved"
DEF_RE = re.compile(r"^(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE)
INDEX_RE = re.compile(r"^- `(\w+)\(.*` — (\S+?):(\d+)")
ADD_DEP_RE = re.compile(r"\b(?:poetry|uv|cargo|pnpm)\s+add\b|\bnpm\s+(?:install|i)\s+[^-\s]|\byarn\s+add\b")
PIP_RE = re.compile(r"\bpip3?\s+install\b")
PIP_LOCAL_RE = re.compile(r"\s-[re]\b|\s\.\s*$")  # -r reqs / -e editable / current dir


def is_dep_install(cmd: str) -> bool:
    """True if cmd installs a NEW dependency, not a lockfile/editable/local install."""
    if PIP_RE.search(cmd) and not PIP_LOCAL_RE.search(cmd):
        return True
    return bool(ADD_DEP_RE.search(cmd))


def duplicate_defs(content: str, file_path: Path, root: Path) -> list[str]:
    """Top-level defs in `content` whose name already exists in another file per SYMBOLS.md."""
    index = root / "SYMBOLS.md"
    if not index.exists():
        return []
    try:
        rel = file_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return []  # edit outside the launched repo — not ours to police
    known: dict[str, str] = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        m = INDEX_RE.match(line)
        if m and m.group(2) != rel:
            known.setdefault(m.group(1), f"{m.group(2)}:{m.group(3)}")
    return [f"  '{name}' — already implemented at {known[name]}"
            for name in DEF_RE.findall(content)
            if name in known and not name.startswith("_") and name not in EXEMPT_NAMES]


def deny(msg: str) -> None:
    """Emit msg to stderr and exit 2 — the PreToolUse 'deny' signal."""
    print(msg, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        data = json.loads(sys.stdin.read().lstrip("\ufeff") or "{}")
    except (json.JSONDecodeError, OSError):
        return
    root = Path(data.get("cwd") or Path.cwd())
    if load_config(root) is None:  # not opted in; pre-tool guards run at every level otherwise
        return
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}

    if tool == "Bash":
        cmd = tool_input.get("command", "")
        if APPROVAL_TOKEN not in cmd and is_dep_install(cmd):
            deny("Blocked: new dependencies need explicit user approval (dependency ladder — "
                 "reuse codebase/stdlib/installed deps first). Ask the user; once approved, "
                 f"re-run the command with `{APPROVAL_TOKEN}` appended.")
        return

    if tool in ("Write", "Edit"):
        fp = tool_input.get("file_path", "")
        if not fp.endswith(".py"):
            return
        path = Path(fp)
        if tool == "Write" and path.exists():
            deny(f"Blocked: {path.name} already exists — edit in place with Edit; never regenerate "
                 "a file to change part of it. If a full rewrite is genuinely intended, delete the "
                 "file first, then Write.")
        content = tool_input.get("content") if tool == "Write" else tool_input.get("new_string")
        dupes = duplicate_defs(content or "", path, root)
        if dupes:
            deny("Blocked: duplicate function name(s) — check SYMBOLS.md and extend the existing "
                 "implementation instead of writing a new one:\n" + "\n".join(dupes))


if __name__ == "__main__":
    main()
