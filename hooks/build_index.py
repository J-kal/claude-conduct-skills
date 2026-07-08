#!/usr/bin/env python3
"""Generate the repo's readability maps: SYMBOLS.md and CALLERS.md.

Run from repo root: python hooks/build_index.py [root]
Both are generated, never hand-edited, so they cannot rot.

- SYMBOLS.md — one line per function/class: name, location, one-line docstring.
- CALLERS.md — who references each function (crude name match), for blast radius.
"""
import ast
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache", "build", "dist", ".eggs", ".claude", "migrations", "alembic"}


def first_line(doc: str | None) -> str:
    """First non-empty line of a docstring, or '' when there is none."""
    return (doc or "").strip().splitlines()[0] if doc and doc.strip() else ""


def source_files(root: Path):
    """Yield (relpath, parsed AST) for every non-skipped, parseable .py under root."""
    for py in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIRS for part in py.parts):
            continue
        try:
            yield py.relative_to(root).as_posix(), ast.parse(py.read_text(encoding="utf-8-sig"))
        except (SyntaxError, UnicodeDecodeError):
            continue


def index_lines(rel: str, tree: ast.AST) -> list[str]:
    """One SYMBOLS.md line per top-level function/class in a parsed file."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ", ".join(a.arg for a in node.args.args)
            lines.append(f"- `{node.name}({args})` — {rel}:{node.lineno} — {first_line(ast.get_docstring(node))}")
        elif isinstance(node, ast.ClassDef):
            lines.append(f"- `class {node.name}` — {rel}:{node.lineno} — {first_line(ast.get_docstring(node))}")
    return lines


def caller_lines(files: list[tuple[str, ast.AST]]) -> list[str]:
    """One CALLERS.md line per module-level function: where its name is referenced elsewhere.

    Crude by design — matches on name only, so `x.run()` counts as a reference to any
    top-level `run`. Good enough to state blast radius before editing.
    # shortcut: name-match, not scope-aware resolution; upgrade if false matches mislead
    """
    defined: dict[str, str] = {}
    for rel, tree in files:
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined.setdefault(node.name, f"{rel}:{node.lineno}")
    refs: dict[str, list[str]] = defaultdict(list)
    for rel, tree in files:
        for node in ast.walk(tree):
            name = node.id if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) else \
                node.attr if isinstance(node, ast.Attribute) else None
            if name in defined:
                site = f"{rel}:{node.lineno}"
                if site != defined[name] and site not in refs[name]:
                    refs[name].append(site)
    out = []
    for name in sorted(defined):
        sites = ", ".join(refs[name]) if refs[name] else "no references found"
        out.append(f"- `{name}` — defined at {defined[name]} — called by: {sites}")
    return out


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    files = list(source_files(root))
    entries = [line for rel, tree in files for line in index_lines(rel, tree)]
    (root / "SYMBOLS.md").write_text(
        "# Symbol Index (generated — do not edit)\n\n"
        "Regenerate: `python hooks/build_index.py`\n"
        "Consult this BEFORE writing any new function. If it already exists, reuse it.\n\n"
        + "\n".join(entries) + "\n", encoding="utf-8")
    callers = caller_lines(files)
    (root / "CALLERS.md").write_text(
        "# Caller Index (generated — do not edit)\n\n"
        "Regenerate: `python hooks/build_index.py`\n"
        "Who references each function (crude name match). Read this to state blast radius before editing.\n\n"
        + "\n".join(callers) + "\n", encoding="utf-8")
    print(f"SYMBOLS.md: {len(entries)} symbols; CALLERS.md: {len(callers)} functions")


if __name__ == "__main__":
    main()
