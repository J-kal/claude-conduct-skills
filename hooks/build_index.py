#!/usr/bin/env python3
"""Generate SYMBOLS.md: one line per function/class in the repo.

Run from repo root: python hooks/build_index.py [root]
The index is generated, never hand-edited, so it cannot rot.
"""
import ast
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache", "build", "dist", ".eggs", ".claude", "migrations", "alembic"}


def first_line(doc: str | None) -> str:
    return (doc or "").strip().splitlines()[0] if doc and doc.strip() else ""


def index_file(path: Path, root: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    rel = path.relative_to(root).as_posix()
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ", ".join(a.arg for a in node.args.args)
            lines.append(f"- `{node.name}({args})` — {rel}:{node.lineno} — {first_line(ast.get_docstring(node))}")
        elif isinstance(node, ast.ClassDef):
            lines.append(f"- `class {node.name}` — {rel}:{node.lineno} — {first_line(ast.get_docstring(node))}")
    return lines


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    entries: list[str] = []
    for py in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIRS for part in py.parts):
            continue
        entries.extend(index_file(py, root))
    out = root / "SYMBOLS.md"
    header = (
        "# Symbol Index (generated — do not edit)\n\n"
        "Regenerate: `python hooks/build_index.py`\n"
        "Consult this BEFORE writing any new function. If it already exists, reuse it.\n\n"
    )
    out.write_text(header + "\n".join(entries) + "\n", encoding="utf-8")
    print(f"SYMBOLS.md: {len(entries)} symbols indexed")


if __name__ == "__main__":
    main()
