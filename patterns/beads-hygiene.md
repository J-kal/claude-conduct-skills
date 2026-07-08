# Beads Hygiene

Beads (`bd`) is the task platform installed with every environment launch. It is the single source of truth for work state — the honest answer to "what's done, what's in flight, what's deferred, what's broken." A tracker that's 90% accurate is worse than none: people plan around its lies. These rules keep it truthful.

## What gets a bead

- Every non-trivial task at intake (the five-line definition goes in the description).
- Every bug the moment it's discovered — `bd q "<repro one-liner>" --labels bug` with file:line — even (especially) when found mid-task on something else. Never fixed silently, never folded into an unrelated bead.
- Every deliberate shortcut: the `# shortcut(<bead-id>): ...` comment in code and its `shortcut-debt` bead are created together and reference each other. Code marks the site; the bead makes it plannable.
- Every delayed feature — status `deferred`, with a note naming what triggers revival. Deferred ≠ closed (it's still wanted) and ≠ open (it's not workable now); using the wrong state either loses the feature or clogs the ready queue.
- Every ingest ledger entry (label `rewrite`, linked in dependency order).

## Labels (fixed vocabulary — don't invent per-repo synonyms)

| Label | Means |
|---|---|
| `bug` | Wrong today; description contains a repro |
| `feature` | New capability |
| `shortcut-debt` | Deliberate ceiling, marked in code |
| `rewrite` | Design-level fix from an ingest ledger |
| `chore` | Maintenance, baselines, upgrades |

Priority: P1 = corrupts future work or user-visible breakage; P2 = should land this cycle; P3 = accepted debt. Priority is set at creation and changed deliberately, not re-derived per session.

## Status discipline (the honesty rules)

- **`in_progress` means actively being worked right now.** Set it when work starts, not at intake. At session end nothing you touched stays `in_progress`: finish it, or demote to `open` with a note stating exactly where it stands (done, next step, known-broken). Zombie in_progress is the single most corrosive tracker lie.
- **`blocked` names its blocker** — a linked bead (`bd link`) or an external fact in a note. Unblocked → back to open the moment it's noticed.
- **Closing requires evidence.** `bd close <id> --reason "<the verification output>"` — the done-check's result, not "done". A close without evidence gets reopened at the next debt reconciliation.
- **One bead, one unit of work.** Scope discovered mid-task becomes a new linked bead, never silent expansion. Epics hold children via links; work happens on children.

## Sync and dedup

- `.beads/` (the issue database) travels with the repo; commit it alongside the code it describes. Lock/server/log files stay ignored (bd init's .gitignore handles this — verify at launch).
- Before creating: `bd search "<key phrase>"`. Update the existing bead over spawning a twin; `bd find-duplicates` at reconciliation catches what slipped through.
- `bd ready` is the source of truth for "what next" — if the genuinely-next task isn't in it, the tracker is wrong; fix the tracker, then start the task.

## Reconciliation cadence

The **debt** skill runs the two-way check (code→beads harvest, beads→code claim verification) at end of significant sessions and at least weekly. Its health metric: `# shortcut:` count in code == open `shortcut-debt` beads. Drift in either direction is a finding.
