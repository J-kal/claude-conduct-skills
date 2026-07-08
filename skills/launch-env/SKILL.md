---
name: launch-env
description: Activate fable-os in the current repo — write the opt-in marker that turns on the plugin's quality gates here, append the design defaults to CLAUDE.md, init beads, run the baseline audit, and seed the tracker. Use when adopting the system in a new codebase/environment, or when the user says "launch env", "set this repo up", or "activate fable here". Run once per repo; re-running is safe (idempotent) and refreshes the defaults after plugin updates.
---

# Launch Environment

FABLE = this plugin's root directory (this file lives at `FABLE/skills/launch-env/SKILL.md`). Run everything from the target repo root.

## 1. Activate

`python "FABLE/hooks/launch.py"` — writes `.claude/fable.json` (the marker that makes the plugin's PostToolUse/Stop hooks fire in this repo, recording `plugin_root` for other skills) and appends the design defaults to CLAUDE.md with paths resolved. Without the marker the plugin's hooks no-op here.

## 2. Beads init (task platform — part of every launch)

- `bd list` works → already initialized, skip. Otherwise `bd init` (accept defaults; `.beads/` travels with the repo — verify the .gitignore bd sets up keeps the issue db and excludes lock/server files).

## 3. Baseline

- `python "FABLE/hooks/build_index.py"` → SYMBOLS.md exists.
- `python "FABLE/hooks/audit.py"` → record counts in a bead: `bd q "launch baseline: <N> errors, <M> warnings" --labels chore`.
- Poetry env check: `poetry install` clean; ruff and pytest available (`poetry add --group dev ruff pytest` if missing — the only dependency addition this package may make).

## 4. Seed the tracker

- Every baseline audit **error** becomes a bead (label `bug` if broken-today, else `shortcut-debt`).
- Repo predates the package or contains inherited AI-generated code → recommend running **ingest** next; launch installs the guardrails, ingest maps what got in before them.

## 5. Verify + handoff

- Make one trivial edit and end the turn: the Stop hook should run the audit (confirm in the transcript).
- Report: marker written, baseline counts, beads created, recommended next step (ingest for legacy repos, intake for the first task on fresh ones).
