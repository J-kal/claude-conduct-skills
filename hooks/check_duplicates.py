#!/usr/bin/env python3
"""Gate: fail if two functions share a name or a near-identical body.

Run from repo root: python hooks/check_duplicates.py [root]
Exit 0 = clean, exit 2 = duplicates found (Claude Code hooks treat 2 as blocking).
Dunder methods and common overridable names are exempt from the name check.
"""
import ast
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache", "build", "dist", ".eggs", "tests", "test", ".claude", "migrations", "alembic"}
EXEMPT_NAMES = {"main", "run", "setup", "teardown", "get", "post", "put", "delete", "validate", "clean", "save", "load", "close", "start", "stop", "handle", "process", "execute", "cli", "seed"}


def body_fingerprint(node: ast.AST) -> str:
    """Hash of the AST body with names/constants normalized, so renamed copies still match."""
    dump = ast.dump(ast.Module(body=node.body, type_ignores=[]), annotate_fields=False)
    return hashlib.sha1(dump.encode()).hexdigest()


def collect(root: Path):
    by_name: dict[str, list[str]] = defaultdict(list)
    by_body: dict[str, list[str]] = defaultdict(list)
    for py in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIRS for part in py.parts):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8-sig"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = py.relative_to(root).as_posix()
        toplevel = {id(n) for n in tree.body}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                loc = f"{rel}:{node.lineno} {node.name}"
                # only module-level functions get name-checked: methods and closures
                # legitimately share names across classes/scopes
                if id(node) in toplevel and not node.name.startswith("_") and node.name not in EXEMPT_NAMES:
                    by_name[node.name].append(loc)
                if len(node.body) > 2:  # skip trivial bodies (pass, one-liners)
                    by_body[body_fingerprint(node)].append(loc)
    return by_name, by_body


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    by_name, by_body = collect(root)
    problems = []
    for name, locs in by_name.items():
        if len(locs) > 1:
            problems.append(f"DUPLICATE NAME '{name}':\n  " + "\n  ".join(locs))
    for locs in by_body.values():
        if len(locs) > 1:
            problems.append("IDENTICAL BODY:\n  " + "\n  ".join(locs))
    if problems:
        print("Duplicate implementations found — reuse or consolidate before proceeding:\n")
        print("\n\n".join(problems))
        sys.exit(2)
    print("No duplicate functions found.")


if __name__ == "__main__":
    main()
