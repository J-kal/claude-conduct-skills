# Cleanup Protocol

The strict, repeatable task that brings a repo back in line after agents drifted from the patterns. Run it on demand (`/cleanup`), after merges, or when the audit starts failing.

The audit is the single source of truth for what "out of line" means. Patterns are added, removed, and identified in ONE place: `hooks/audit.py` — one decorated function per pattern, `--list` to enumerate them, `--only`/`--skip` to scope a run.

## Phase 0 — Baseline (never skip)

```
python hooks/build_index.py
python hooks/audit.py
poetry run ruff check .
poetry run pytest -q
```

Record the counts. The test suite must pass BEFORE cleanup starts — otherwise you can't tell what cleanup broke. Failing tests get fixed (or explicitly quarantined with the user's sign-off) first.

## Phase 1 — Fix errors, one rule at a time

Work rule by rule, not file by file: `python hooks/audit.py --only <rule-id>`, fix every finding, re-run the rule, then run the tests. One rule per commit.

Order (highest blast radius first):

1. **duplicate-function** — for each duplicate: read both, keep the better one, point all callers at it, delete the other. Never keep both "to be safe."
2. **weakened-test** — restore the assert, give the skip a reason, or delete a test that tests nothing. Never fix by deleting a failing-but-correct test.
3. **bare-except** — catch the specific exception; if the swallow was intentional, log it and mark `# shortcut: swallowing X because Y; handle when Z`.
4. **unmarked-shortcut** — each bare TODO/FIXME either gets done now (< 10 lines) or converted to `# shortcut: <ceiling>; <upgrade path>`.
5. **stale-index** — regenerate.

## Phase 2 — Judge warnings, don't auto-fix them

Warnings are candidates, not verdicts. For each:

- **single-impl-abstraction** — inline it UNLESS a second implementation is on the visible roadmap (ask if unsure). Zero-implementation protocols are dead code: delete.
- **long-function** — extract only along real seams (a nameable sub-task used or testable on its own). Never split a coherent 80-line function into three 27-line fragments just to satisfy the number — that trade is worse.
- **print-in-library** — convert to logging, matching the repo's existing logger setup.

A warning judged acceptable gets a one-line `# shortcut:` comment at the site so it stops being re-litigated every cleanup.

## Phase 3 — Verify and report

```
python hooks/audit.py        # errors must be 0
poetry run ruff check .
poetry run pytest -q
python hooks/build_index.py
```

Report: before/after counts per rule, what was deleted (lines removed is the headline metric), which warnings were accepted and why. Nothing verified = nothing claimed.

## Hard limits

- Cleanup NEVER changes behavior. Any fix that alters output/API is a bug fix — separate change, flagged to the user.
- Cleanup never adds dependencies, files, or abstractions. Its diff should be net-negative lines.
- Two failed attempts at the same finding → mark it, move on, report it. Don't thrash.

## Evolving the rule set

- **Add a pattern:** one `@rule("id", "description", severity)` function in `hooks/audit.py` yielding `(path, line, message)`. New rules start as `severity="warn"`; promote to `error` after one clean cleanup cycle proves the signal.
- **Remove a pattern:** delete the function (or `--skip` it while deciding).
- **Identify patterns:** `python hooks/audit.py --list`.
- A rule that keeps producing accepted warnings is a bad rule — tune it or delete it rather than training everyone to ignore the audit.
