# Fable Design Defaults

These rules govern every coding and research task. They are defaults, not suggestions; deviate only when the user explicitly overrides.

## Package management
Use poetry to set up and isolate every project. `poetry add` for dependencies, `poetry run` for scripts. Never bare `pip install`.

## Defining a task (before any work)
- Interview first, run silent after: batch 2-4 questions at task start, each with a recommended default; mid-task, proceed on recorded assumptions. Ask only what changes the build AND can't be resolved from the request, the code, or a default — in priority order: irreversible/outward-facing scope, architecture-changing forks, spec contradictions (flag with an alternative), missing acceptance criteria. Never ask what's discoverable or conventional.
- Before the first edit, state: goal, done-check, blast radius, assumptions, out-of-scope. A line you can't fill is the question to ask.

## Worktrees
- Use one only for parallel writers or high-risk changes; single-threaded or read-only work gets none. One task, one worktree, one branch; created and removed as one unit of work (`git worktree remove` + `prune` after landing). Never leave uncommitted work in one at session end.

## Before writing code (orientation — always)
1. Read `ARCHITECTURE.md` and `SYMBOLS.md` if present. If `SYMBOLS.md` is missing or stale, regenerate: `python "{FABLE}/hooks/build_index.py"`.
2. Before writing ANY new function, check `SYMBOLS.md` and grep for the behavior. Something close exists → extend it, don't duplicate it.
3. Trace the change end to end: grep every caller of anything you're about to modify. State the blast radius before editing.
4. Read line spans, not whole files (full reads only under ~200 lines). Delegate broad sweeps to subagents.

## Writing code
- Smallest diff that fixes the root cause. Edit in place; never regenerate a file to change part of it. Fix bugs at the shared choke point all callers route through.
- Dependency ladder, first rung that holds: doesn't need to exist → already in codebase → stdlib → installed dep → minimal new code. New dependencies need explicit user approval.
- No abstraction with fewer than two real consumers today. No scaffolding for later. Boring over clever.
- Touch only what the request touches. Improvements you notice go in a note at the end, never in the diff.
- Never call an internal function without having seen its definition. Verify unfamiliar library APIs against the installed version.
- Deliberate shortcuts get a comment naming the ceiling and upgrade path: `# shortcut: O(n²) scan; index it if lists exceed ~10k`.

## Quality control (every non-trivial change)
- One focused test — the smallest thing that fails if the logic breaks. Trivial one-liners exempt.
- `ruff check` and `ruff format --check` must pass.
- `python "{FABLE}/hooks/check_duplicates.py"` must pass (no duplicate function names or bodies).
- Regenerate `SYMBOLS.md` after adding/removing/moving functions; update `ARCHITECTURE.md` (keep it under 60 lines) only when system shape changes.
- Report only what was verified, with command output. Tests unrun = say unrun; failed = paste the failure. Never weaken a test to make it pass — a wrong test gets flagged, not gamed.
- Gate cost is tunable via the audit level (light | standard | strict) in `.claude/fable.json` or `FABLE_AUDIT_LEVEL`. Error rules block at every level; lower levels only drop advisory/token-costly work. Use `light` for cheap mechanical sessions, `strict` when a diff warrants the LLM review.

## Task accounting (beads)
The `bd` tracker is the source of truth for work state; keep it honest (`{FABLE}/patterns/beads-hygiene.md`). Every non-trivial task, every discovered bug (`--labels bug`, with repro), every deliberate shortcut (`# shortcut(<bead-id>):` in code + `shortcut-debt` bead), every delayed feature (`--status deferred`, with a revival trigger). `in_progress` only while actively worked — at session end, finish it or demote to open with a where-it-stands note. Close only with evidence (`bd close <id> --reason "<verification output>"`). Dedup before creating (`bd search`). Fixed label vocabulary: bug, feature, shortcut-debt, rewrite, chore.

## Working style
- Keep a live TODO for anything beyond two steps.
- A spec that looks wrong or self-contradictory gets flagged with a concrete alternative BEFORE implementation.
- Blocked or surprised → re-orient, don't push harder.
- Before ending significant work: in-progress state written to disk (what's done, what's next, what's broken). Future sessions only know what's on disk.

## Taking over an existing codebase
See `{FABLE}/patterns/ingestion-protocol.md`: documentation-first — sweep against the AI-slop taxonomy, produce a REWRITE_PLAN.md ledger (per finding: location, current behavior line by line, why it's wrong, verified target design, numbered rewrite steps, blast radius, verify step, behavior-change flag). No edits until the ledger is signed off; then execute one entry per commit.

## Research tasks
See `{FABLE}/patterns/research-strategy.md`: breadth-first sweep → prioritize → deep-read → adversarially verify load-bearing claims → synthesize with citations. Never present a single-source claim as settled.

## Subagents / orchestration
See `{FABLE}/patterns/orchestration.md`: fan out only for independent work; every subagent prompt states the deliverable format; subagent output is data to verify, not truth to relay.

## Model allocation (strict)
Every delegated task runs on the smallest/cheapest model that can do it — escalate only on demonstrated failure, never preemptively. Full ladder in `{FABLE}/patterns/orchestration.md`: prefer deterministic code (no model) → Haiku-class for mechanical rubric/extraction/sweep work → Sonnet-class for cross-file judgment → Opus/Fable only for the hardest synthesis a smaller tier has actually failed. Split sweeps by difficulty (cheap workers find, one careful pass verifies), and state the model + why in every spawn. This plugin's own diff review runs on the smallest model by default (`review_model` in `.claude/fable.json`).
