# Code Patterns

Rules for how code gets written under this system. Python-first; the principles are language-agnostic.

## 1. One function, one existence

Every behavior lives in exactly one function. Before writing ANY new function:

1. Check `SYMBOLS.md` (the generated index) for an existing implementation.
2. Grep for the behavior, not just the name — search for the key operation (`rglob`, `requests.post`, the table name), since a duplicate rarely shares your naming.
3. If something close exists, extend or parameterize it. Only write new when nothing fits.

A function that "almost" does what you need gets a parameter, not a sibling.

## 2. Smallest diff that solves the root cause

- Edit in place; never rewrite a file to change ten lines.
- A bug fix goes where all callers route through — one guard in the shared function, not a patch at each call site.
- Never reformat, rename, or reorganize code you weren't asked to touch. Drive-by cleanup belongs in its own change.
- If the diff is growing past the problem, stop and re-scope.

## 3. Dependency ladder

Take the first rung that holds:

1. Does it need to exist? Speculative need = skip.
2. Already in this codebase? Reuse it.
3. Standard library? Use it.
4. Already-installed dependency? Use it.
5. Only then: minimal new code. New dependencies require explicit user approval.

## 4. Structure

- Fewest files that stay readable. New file only when an existing module is the wrong home, not to "organize."
- Flat over nested: no package hierarchy until a flat layout actually hurts.
- No abstraction with one consumer: no interface with one implementation, no factory for one product, no config for a constant.
- Boring over clever. Optimize for the reader at 3am, not the writer.

## 5. Quality control per change (default gate)

Every non-trivial change (a branch, a loop, a parser, anything touching money/security/data):

- Ships with ONE focused test — the smallest thing that fails if the logic breaks. `pytest`, no fixtures unless needed.
- Passes `ruff check` and `ruff format --check`.
- Trivial one-liners need no test.

Deliberate shortcuts get a marker comment naming the ceiling and upgrade path:
`# shortcut: global lock; move to per-account locks if throughput matters`

## 6. The index stays current

- `SYMBOLS.md` is generated (`python hooks/build_index.py`) — regenerate after any change that adds/removes/moves functions. Never hand-edit it.
- `ARCHITECTURE.md` is model-maintained and SHORT (< 60 lines): what each module is for, key data flows, where things live. Update it only when the shape of the system changes, not per function.

## 7. Poetry everywhere

Every project uses poetry for environment isolation and dependencies. `poetry add`, never bare `pip install`. Scripts run via `poetry run`.
