# fable-os

A Claude Code plugin that acts as an operating system for AI-driven codebases: deterministic quality gates, five lifecycle skills, pattern docs models follow, and beads-based honest task accounting. Install it once at user level; activate it per repo with one command.

Two layers, because instructions are advisory and hooks are deterministic:

- **Instructions** (`CLAUDE-global.md`, `patterns/`) tell the model how to work.
- **Gates** (`hooks/`) block output that breaks the rules anyway.

## Install (once, any machine)

From GitHub:

```
/plugin marketplace add J-kal/claude-conduct-skills
/plugin install fable-os@fable
```

Or from a local clone: `/plugin marketplace add <path-to-this-folder>` then install the same way. Updating everywhere = `git push` here, `/plugin update fable-os` there (or re-add the marketplace) — nothing is copied into repos, so every environment tracks the same version.

## Activate (once per repo)

In any folder, say **"launch env"** (the launch-env skill), or run its mechanical step directly:

```
python "<plugin-root>/hooks/launch.py"
```

This writes `.claude/fable.json` — the opt-in marker. **The plugin's hooks no-op in folders without the marker**, so installing user-wide is safe; only launched repos get gated. The skill then finishes the judgment steps: `bd init`, baseline audit, tracker seeding, and appends the design defaults (with resolved plugin paths) to the repo's CLAUDE.md.

## The skills — what to trigger, when

Each SKILL.md description tells future models when to reach for it; this table is the human map. "Rated for" = the development-process stage each is designed for.

| Skill | Rated for | What it does |
|---|---|---|
| **launch-env** | New repo/environment adoption (once, idempotent) | Marker + CLAUDE.md defaults + beads init + baseline audit + tracker seeding |
| **ingest** | Taking over existing/inherited AI-generated code | Sweep against the AI-slop taxonomy → REWRITE_PLAN.md ledger + beads mirror. Writes no code |
| **intake** | Start of any non-trivial task | Batched priority questions, five-line task definition, tracking bead |
| **cleanup** | After merges, after big AI changes land, failing audit, pre-release | Fix audit errors rule-by-rule, judge warnings, verify, sync beads. Behavior-preserving, net-negative lines |
| **debt** | End of significant sessions; weekly; before planning | Two-way reconcile: `# shortcut:` comments + audit warnings ↔ beads; verify every claimed status against reality |

Typical lifecycle: **launch-env** once → **ingest** if the repo predates the plugin → **intake** per task → **cleanup** after things land → **debt** on cadence.

## Pseudo-independent operation

Three tiers, most-automatic first:

1. **Every turn (hooks, deterministic):** in launched repos —
   - `session_start.py` re-injects repo state (audit summary + open/in-progress beads) at session start, after `/clear`, and after compaction, so rules and work-state survive context loss.
   - `pre_tool.py` blocks violations *before* they land: unapproved dependency installs, regenerating an existing `.py` instead of editing, and new functions duplicating a name already in `SYMBOLS.md`.
   - `post_edit.py` ruff-auto-fixes after each edit, then feeds error-severity audit findings straight back to the model while the context is hot.
   - `stop_gate.py` blocks turn-end until the audit passes and no bead is left `in_progress` (finish or demote with a note); rebuilds the index each turn.
2. **Per turn, judgment (`strict` level):** the stop gate also runs a narrow `claude -p` review of the working diff for the un-mechanizable rules (smallest diff, symptom patches, speculative abstraction, new deps). Adds latency and token cost per turn — on only at `strict` (or the legacy `"llm_review": true`).
3. **On demand (skills):** any tier-1 failure or human trigger invokes the skill by name.
4. **Async/scheduled (headless):** `claude -p "/cleanup"` or `claude -p "/debt"` from cron, CI, or a Claude Code scheduled routine. Safe to automate because both are bounded by design: cleanup is behavior-preserving with hard limits and evidence-gated closes; debt changes no code. Findings needing judgment land as beads for a human instead of being auto-resolved.
   - Crash/limit resilience: wrap any run in `python <plugin>/hooks/keepalive.py "/cleanup"` — on a crash or usage-limit exit it waits (30 min for limits, backoff for crashes) and resumes the same conversation with `claude --continue`; beads + the SessionStart hook re-orient the resumed session. Run it with no prompt to resume the last session after an interactive one dies.

Beads is the interface between autonomous runs and humans: an async run's output is opened/closed issues with evidence notes — queryable via `bd ready` / `bd list` — not chat that scrolls away.

### Audit levels (dialing cost)

Every per-turn cost scales with one knob — pick the cheapest level that keeps the repo clean:

| Level | Per-edit audit | Beads state | LLM diff review | Turn-end block |
|---|---|---|---|---|
| `light` | — (lint only) | — | — | error rules only |
| `standard` (default) | error rules | ✓ | — | error rules only |
| `strict` | error rules | ✓ | ✓ (`claude -p`) | error rules only |

Errors always block at every level (the floor); levels only trade away the *advisory* work that costs time or tokens. Selection is dynamic, most-specific wins:

1. `FABLE_AUDIT_LEVEL=light` — env var, per-session/per-command (e.g. `FABLE_AUDIT_LEVEL=light claude ...`).
2. `"level": "strict"` in `.claude/fable.json` — the repo's default.
3. built-in default: `standard`.

`hooks/audit.py --level light` runs the same errors-only pass by hand.

### Model allocation (strict guideline)

Minimum-viable model is a design rule, not a preference: **every delegated task runs on the smallest tier that can do it**, escalating only on demonstrated failure. The ladder — deterministic code (no model) → Haiku-class for mechanical sweep/extract/rubric work → Sonnet-class for cross-file judgment → Opus/Fable only for the hardest synthesis — lives in `patterns/orchestration.md` and is restated in every launched repo's CLAUDE.md, so orchestrating models pick cheap by default and split sweeps into cheap-find + careful-verify.

The one model call the plugin makes itself — the `strict` stop-gate diff review — obeys the same rule: it runs on `review_model` (default `haiku`; `FABLE_REVIEW_MODEL` env or `"review_model"` in `.claude/fable.json` to override). Headless skill runs should pass the smallest sufficient model too, e.g. `claude --model haiku -p "/cleanup"`.

## Contents

| Path | What it is |
|---|---|
| `.claude-plugin/plugin.json`, `marketplace.json` | Plugin manifest + marketplace listing (this repo is both) |
| `skills/{launch-env,ingest,intake,cleanup,debt}/SKILL.md` | The five procedures, each with when-to-use triggers in its description |
| `hooks/hooks.json` | Plugin hook wiring (PreToolUse gate, PostToolUse lint+audit, Stop gate, SessionStart state) via `${CLAUDE_PLUGIN_ROOT}` |
| `hooks/pre_tool.py`, `hooks/post_edit.py`, `hooks/stop_gate.py`, `hooks/session_start.py` | Marker-gated hook entry points — no-ops outside launched repos |
| `hooks/config.py` | Shared marker check + audit-level resolution (`FABLE_AUDIT_LEVEL` > `fable.json` > default) |
| `hooks/keepalive.py` | Restart wrapper: resume a run after crashes or usage-limit exhaustion (`claude --continue` + backoff) |
| `hooks/launch.py` | Per-repo activation: marker + CLAUDE.md defaults (idempotent) |
| `hooks/audit.py` | Rule registry: 12 pattern checks, `--list` / `--only` / `--skip`, exit 2 on errors |
| `hooks/build_index.py` | Generates `SYMBOLS.md` (symbols + docstrings) and `CALLERS.md` (who-calls-what) — can't rot |
| `ARCHITECTURE.md` | Short model-maintained map of the system's shape and data flow |
| `hooks/check_duplicates.py` | Gate: duplicate module-level names or copy-pasted bodies |
| `CLAUDE-global.md` | Design defaults appended to each launched repo's CLAUDE.md (`{FABLE}` resolves to the plugin path) |
| `patterns/*.md` | The judgment layer: code patterns, antipatterns, orientation, task intake, worktrees, cleanup protocol, ingestion protocol + AI-slop taxonomy, beads hygiene, research strategy, orchestration |

## Evolving the system

- Add an enforcement pattern: one `@rule(...)` function in `hooks/audit.py` (start `warn`, promote to `error` after a clean cycle proves the signal). Remove: delete it. Identify: `--list`.
- Add a procedure: new `skills/<name>/SKILL.md` whose description states its triggers and development-process stage.
- Ship to the company: push here; each machine runs `/plugin update fable-os`.

Design decisions locked in: instructions + hard gates, Python-first with portable principles, generated maps (`SYMBOLS.md` + `CALLERS.md`) + short model-maintained `ARCHITECTURE.md`, docstrings enforced so the index describes not just names, one test + lint per non-trivial change, beads as the single source of work-state truth, per-repo opt-in via marker.
