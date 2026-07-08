# Orientation Techniques

How a model gets its bearings before touching anything. Orientation is the highest-leverage phase: a wrong mental model produces confident wrong diffs.

## Entering a codebase (cold start)

Ordered, cheapest-first:

1. **Read the map, not the territory:** `ARCHITECTURE.md`, `README.md`, `CLAUDE.md`, `pyproject.toml`. Two minutes here beats twenty minutes of file-reading.
2. **Consult `SYMBOLS.md`** for what already exists. Missing or stale → regenerate: `python hooks/build_index.py`.
3. **Trace the task's flow end to end** before editing: entry point → the function you'll touch → every caller of it (grep). You must be able to state "changing X affects A, B, C" before writing.
4. **Read spans, not files.** Open only the line ranges the task touches plus their immediate callers. Full-file reads are for files under ~200 lines only.

## During a task (staying oriented)

- Keep a live TODO for anything beyond two steps; mark items done as they finish, never in batch at the end.
- After every 3-4 edits, re-state (to yourself) what the original request was. Drift shows up as diffs the request never asked for.
- When a search comes up empty, vary the term (synonym, key operation, table/route name) before concluding "doesn't exist." Two misses on different terms = acceptable evidence; one miss = not.
- Blocked or surprised → stop and re-orient; don't push a failing approach harder.

## Verification before "done"

- Run the check: the new test, `ruff check`, and the duplicate gate.
- Re-read the final diff top to bottom AS a reviewer: does every hunk trace to the request?
- Regenerate `SYMBOLS.md` if functions were added/moved/removed.
- Report what was run and what it printed. Nothing verified = nothing claimed.

## Handing off (end of session / compaction)

Future sessions only know what's on disk. Before ending significant work, ensure:

- `ARCHITECTURE.md` reflects any structural change.
- In-progress state is written down (TODO file or PR description): what's done, what's next, what's known-broken.
- No orientation knowledge lives only in the conversation.
