# Architecture

fable-os is a Claude Code plugin — a marker-gated set of hooks + skills that enforce
design discipline in *other* repos. This repo is both the plugin source and the
marketplace listing. No server, no runtime state: every entry point is a short Python
script a Claude Code hook runs.

## The gate: `.claude/fable.json`

One marker file, written into a target repo by `hooks/launch.py`, decides everything.
Every hook's first act is to check for it in the cwd; without it they exit 0 (no-op).
That is why the plugin is safe to install user-wide — it only acts in repos that opted
in. The file also records `plugin_root` so skills can resolve gate paths, and a `level`
(light | standard | strict) that scales how much the hooks do. `hooks/config.py` is the
one place that reads the marker and resolves the level (env `FABLE_AUDIT_LEVEL` >
`fable.json` > default), so every hook agrees on both.

## Hook lifecycle (launched repos only)

Wired in `hooks/hooks.json` via `${CLAUDE_PLUGIN_ROOT}`:

- **SessionStart** → `session_start.py`: prints the audit summary + beads state into
  context, fighting context loss after `/clear` and compaction.
- **PreToolUse** (Bash|Write|Edit) → `pre_tool.py`: denies (exit 2), *before* they land,
  unapproved dependency installs, regenerating an existing `.py`, and new functions whose
  name already exists in SYMBOLS.md.
- **PostToolUse** (Write|Edit) → `post_edit.py`: ruff auto-fix, then feeds fast
  error-severity audit findings back to the model while the context is hot.
- **Stop** → `stop_gate.py`: rebuilds the index, blocks turn-end on audit errors or beads
  left `in_progress`; optional `claude -p` review of the working diff.

## The rule engine: `hooks/audit.py`

A decorator registry — `@rule(id, desc, severity)` adds a check; each yields
`(file, line, message)`. Errors exit 2 (block); warns advise. `hooks/check_duplicates.py`
holds the dup-detection logic that both audit and `pre_tool` reuse. Adding a pattern is
one decorated function; `--list` / `--only` / `--skip` select which run.

## Generated maps (never hand-edited)

`hooks/build_index.py` writes two files, regenerated every turn by the stop gate so they
cannot rot: `SYMBOLS.md` (what exists — name, location, one-line docstring) and
`CALLERS.md` (who references what — for blast radius). The `stale-index` rule fails if
SYMBOLS.md lags its sources; the `missing-docstring` rule keeps the index's docstring
column populated.

## Judgment layer (models read it, hooks don't enforce it)

`CLAUDE-global.md` (appended to each launched repo's CLAUDE.md) and `patterns/*.md` state
the rules a hook can't check — the AI-slop taxonomy, orientation, cleanup and ingestion
protocols. `skills/*/SKILL.md` are the five lifecycle procedures (launch-env, ingest,
intake, cleanup, debt). Beads (`bd`) is the on-disk source of truth for task state, and
the interface between headless runs and humans.

## Resilience

`hooks/keepalive.py` wraps a run: on a crash or usage-limit exit it waits and resumes the
same conversation with `claude --continue`; beads + SessionStart re-orient the resumed
session.
