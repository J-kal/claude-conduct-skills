---
name: cleanup
description: Strict pattern-compliance cleanup — audit the repo, fix every error rule-by-rule, judge warnings, verify, report, and sync results to beads. Use after merges, after any large AI-generated change lands, when the Stop-hook audit starts failing, before a release, or when the user says "cleanup", "fix the drift", or "bring the repo back in line". Behavior-preserving and net-negative lines by design. NOT for adopting an unfamiliar codebase (use ingest first) or for feature work.
---

# Cleanup

FABLE = this plugin's root directory (recorded as `plugin_root` in the repo's `.claude/fable.json`).

Follow `FABLE/patterns/cleanup-protocol.md` in full. Summary of the non-negotiables:

1. **Baseline first:** `python "FABLE/hooks/build_index.py" && python "FABLE/hooks/audit.py"`; `poetry run ruff check .`; `poetry run pytest -q`. Tests must be green before cleanup starts — failures get fixed or quarantined with user sign-off, tracked as `bd q "<failing test>" --labels bug`.
2. **Errors, one rule per commit,** in blast-radius order: duplicate-function → weakened-test → bare-except → unmarked-shortcut → stale-index. `python "FABLE/hooks/audit.py" --only <rule-id>` until clean, tests after each.
3. **Warnings are judged, not auto-fixed** (single-impl-abstraction, long-function, print-in-library, trivial-wrapper, dead-function, stale-worktree). Accepted ones get a `# shortcut(<bead-id>): <ceiling>; <upgrade path>` comment backed by a bead labeled `shortcut-debt`.
4. **Verify:** audit 0 errors, ruff clean, pytest green, index regenerated.
5. **Beads accounting (honest state):** every fix closes its bead with an evidence note (`bd close <id> --reason "<what verified>"`); every accepted-but-unfixed finding has an open bead; nothing left `in_progress` at the end — finish it, or `bd update <id> --status open` with a note saying exactly where it stands.
6. **Report:** before/after counts per rule, net lines removed, beads opened/closed, accepted warnings and why.

Hard limits: no behavior changes (a fix that changes behavior becomes a `bug`-labeled bead + separate task), no new dependencies/files/abstractions, two failed attempts on one finding → bead it, move on, report it.
