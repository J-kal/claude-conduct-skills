#!/usr/bin/env python3
"""Strict design-pattern audit: evaluate the repo against every registered rule.

Usage (from repo root):
    python hooks/audit.py                 # run all rules
    python hooks/audit.py --list          # identify registered rules
    python hooks/audit.py --only bare-except,duplicate-function
    python hooks/audit.py --skip long-function
    python hooks/audit.py path/to/repo    # audit another root

Exit 0 = clean, exit 2 = error-severity findings (Claude Code hooks block on 2).
Warnings print but never fail the run.

Adding a pattern = one decorated function below. Removing = delete it (or --skip).
Each rule receives the list of parsed files and yields (relpath, lineno, message).
"""
import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_duplicates import EXEMPT_NAMES, collect as collect_duplicates  # noqa: E402

SKIP_DIRS = {".venv", "venv", ".git", "__pycache__", "node_modules", ".pytest_cache", "build", "dist", ".eggs", ".claude", "migrations", "alembic"}

RULES = {}


@dataclass
class PyFile:
    rel: str
    path: Path
    source: str
    tree: ast.AST

    @property
    def is_test(self) -> bool:
        return "test" in Path(self.rel).parts[0:1] or Path(self.rel).name.startswith("test_")

    @property
    def is_script(self) -> bool:
        return (Path(self.rel).parts[0:1] in (("scripts",), ("hooks",))
                or 'if __name__ == "__main__"' in self.source)


def rule(rule_id: str, description: str, severity: str = "error"):
    def register(fn):
        RULES[rule_id] = (description, severity, fn)
        return fn
    return register


# ---------------------------------------------------------------- rules --

@rule("duplicate-function", "No function implemented twice (name or body)")
def r_duplicates(files, root):
    by_name, by_body = collect_duplicates(root)
    for name, locs in by_name.items():
        if len(locs) > 1:
            rel, line, _ = locs[0].replace(" ", ":", 1).split(":", 2)
            yield rel, int(line), f"'{name}' defined in {len(locs)} places: " + "; ".join(locs)
    for locs in by_body.values():
        if len(locs) > 1:
            rel, line, _ = locs[0].replace(" ", ":", 1).split(":", 2)
            yield rel, int(line), "identical body: " + "; ".join(locs)


@rule("stale-index", "SYMBOLS.md exists and is newer than every source file")
def r_stale_index(files, root):
    index = root / "SYMBOLS.md"
    if not index.exists():
        yield "SYMBOLS.md", 0, "missing — run: python hooks/build_index.py"
        return
    stamp = index.stat().st_mtime
    stale = [f.rel for f in files if f.path.stat().st_mtime > stamp]
    if stale:
        yield "SYMBOLS.md", 0, f"stale ({len(stale)} newer source files) — run: python hooks/build_index.py"


@rule("bare-except", "No swallowed exceptions: bare except, or except-with-only-pass")
def r_bare_except(files, root):
    for f in files:
        for node in ast.walk(f.tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    yield f.rel, node.lineno, "bare 'except:' — catch the specific exception"
                elif all(isinstance(s, ast.Pass) for s in node.body):
                    yield f.rel, node.lineno, "exception swallowed with 'pass' — handle it or let it raise"


@rule("unmarked-shortcut", "Deferred work uses '# shortcut:' with ceiling + upgrade path, not bare TODO/FIXME/HACK")
def r_todo(files, root):
    # built dynamically so this file doesn't flag itself
    tags = tuple("#" + sep + word for word in ("TODO", "FIXME", "HACK", "XXX") for sep in ("", " "))
    for f in files:
        for i, line in enumerate(f.source.splitlines(), 1):
            if any(t.lower() in line.lower() for t in tags):
                yield f.rel, i, "bare TODO/FIXME/HACK — convert to '# shortcut: <ceiling>; <upgrade path>' or do it now"


@rule("single-impl-abstraction", "No abstract base with fewer than two concrete implementations", severity="warn")
def r_abstraction(files, root):
    bases_of = {}   # class name -> set of base names it inherits
    abstract = {}   # class name -> (rel, lineno)
    for f in files:
        for node in ast.walk(f.tree):
            if isinstance(node, ast.ClassDef):
                base_names = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases}
                bases_of[node.name] = base_names
                if base_names & {"ABC", "Protocol"}:
                    abstract[node.name] = (f.rel, node.lineno)
    for name, (rel, lineno) in abstract.items():
        impls = sum(1 for bases in bases_of.values() if name in bases)
        if impls < 2:
            yield rel, lineno, f"abstract '{name}' has {impls} implementation(s) — inline it until a second consumer exists"


@rule("long-function", "Functions stay under 60 lines", severity="warn")
def r_long(files, root):
    for f in files:
        for node in ast.walk(f.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = (node.end_lineno or node.lineno) - node.lineno
                if length > 60:
                    yield f.rel, node.lineno, f"'{node.name}' is {length} lines — extract or simplify"


@rule("print-in-library", "No print() in library code (scripts and tests exempt) — use logging", severity="warn")
def r_print(files, root):
    for f in files:
        if f.is_script or f.is_test:
            continue
        for node in ast.walk(f.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                yield f.rel, node.lineno, "print() in library code — use logging"


@rule("weakened-test", "Tests are not gamed: no reasonless skips, no assert-True, no swallowed assertion errors")
def r_test_gaming(files, root):
    for f in files:
        if not f.is_test:
            continue
        for node in ast.walk(f.tree):
            if isinstance(node, ast.Assert) and isinstance(node.test, ast.Constant) and node.test.value is True:
                yield f.rel, node.lineno, "'assert True' — test asserts nothing"
            if isinstance(node, ast.Call):
                name = ast.dump(node.func)
                if "skip" in getattr(node.func, "attr", "") and not node.args and not node.keywords:
                    yield f.rel, node.lineno, "skip without a reason — give the reason or unskip"
            if isinstance(node, ast.ExceptHandler) and node.type is not None:
                t = node.type
                names = {t.id} if isinstance(t, ast.Name) else {getattr(e, "id", "") for e in getattr(t, "elts", [])}
                if "AssertionError" in names:
                    yield f.rel, node.lineno, "except AssertionError — the test failure is being swallowed"


@rule("trivial-wrapper", "No pass-through layers: a function whose whole body forwards to one call", severity="warn")
def r_wrapper(files, root):
    for f in files:
        if f.is_test:
            continue
        for node in ast.walk(f.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.decorator_list:
                continue
            body = [s for s in node.body if not isinstance(s, ast.Expr) or not isinstance(s.value, ast.Constant)]
            if len(body) != 1 or not isinstance(body[0], ast.Return) or not isinstance(body[0].value, ast.Call):
                continue
            call = body[0].value
            params = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
            passed = [a.id for a in call.args if isinstance(a, ast.Name)]
            if len(call.args) == len(passed) and passed == params and not call.keywords:
                yield f.rel, node.lineno, f"'{node.name}' only forwards to another call — inline it at the call sites"


@rule("dead-function", "No unreachable code: module-level functions someone actually references", severity="warn")
def r_dead(files, root):
    defined = {}   # name -> (rel, lineno)
    referenced = set()
    for f in files:
        for node in ast.walk(f.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if (id(node) in {id(n) for n in f.tree.body} and not node.decorator_list
                        and not node.name.startswith("_") and node.name not in EXEMPT_NAMES
                        and not f.is_test and not f.is_script):
                    defined.setdefault(node.name, (f.rel, node.lineno))
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                referenced.add(node.id)
            elif isinstance(node, ast.Attribute):
                referenced.add(node.attr)
        referenced.update(a.name for node in ast.walk(f.tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                          for a in node.names)
        if "__all__" in f.source:
            referenced.update(n.value for node in ast.walk(f.tree) if isinstance(node, ast.Assign)
                              for t in node.targets if isinstance(t, ast.Name) and t.id == "__all__"
                              for n in ast.walk(node.value) if isinstance(n, ast.Constant) and isinstance(n.value, str))
    dead = {n: loc for n, loc in defined.items() if n not in referenced}
    if dead:
        # rescue pass: skipped dirs (migrations, alembic, scripts) may still reference library code
        env_dirs = {".venv", "venv", ".git", "__pycache__", "node_modules", ".claude", "build", "dist", ".eggs"}
        for py in root.rglob("*.py"):
            if any(p in env_dirs for p in py.parts):
                continue
            try:
                src = py.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError):
                continue
            for name in [n for n in dead if n in src and py.relative_to(root).as_posix() != dead[n][0]]:
                del dead[name]
    for name, (rel, lineno) in dead.items():
        yield rel, lineno, f"'{name}' is never referenced anywhere — delete it (or wire it up)"


@rule("stale-worktree", "No leftover worktrees: .claude/worktrees is empty once tasks land", severity="warn")
def r_stale_worktree(files, root):
    wt = root / ".claude" / "worktrees"
    if wt.is_dir():
        for entry in wt.iterdir():
            yield f".claude/worktrees/{entry.name}", 0, "leftover worktree — land or remove it (git worktree remove + prune)"


# ------------------------------------------------------------- runner --

def load_files(root: Path) -> list[PyFile]:
    out = []
    for py in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIRS for part in py.parts):
            continue
        try:
            src = py.read_text(encoding="utf-8-sig")
            out.append(PyFile(py.relative_to(root).as_posix(), py, src, ast.parse(src)))
        except (SyntaxError, UnicodeDecodeError):
            continue
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--list", action="store_true", help="list registered rules and exit")
    ap.add_argument("--only", default="", help="comma-separated rule ids to run")
    ap.add_argument("--skip", default="", help="comma-separated rule ids to skip")
    args = ap.parse_args()

    if args.list:
        for rid, (desc, sev, _) in RULES.items():
            print(f"  {rid:26} [{sev:5}] {desc}")
        return

    only = set(filter(None, args.only.split(",")))
    skip = set(filter(None, args.skip.split(",")))
    unknown = (only | skip) - RULES.keys()
    if unknown:
        sys.exit(f"unknown rule id(s): {', '.join(unknown)} — see --list")

    root = Path(args.root).resolve()
    files = load_files(root)
    errors = warnings = 0
    for rid, (desc, sev, fn) in RULES.items():
        if only and rid not in only or rid in skip:
            continue
        for rel, lineno, msg in fn(files, root):
            print(f"[{sev.upper()}] {rid}: {rel}:{lineno} — {msg}")
            if sev == "error":
                errors += 1
            else:
                warnings += 1
    print(f"\naudit: {errors} error(s), {warnings} warning(s) across {len(files)} files, {len(RULES)} rules")
    if errors:
        sys.exit(2)


if __name__ == "__main__":
    main()
