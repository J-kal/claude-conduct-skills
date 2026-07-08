---
name: debt
description: Reconcile the debt ledger — harvest every `# shortcut:` comment and open audit warning into beads, label bugs vs deferred features, and produce an honest state-of-work report (nothing zombie in_progress, nothing untracked). Use at end of significant sessions, weekly, before sprint planning, or when the user says "debt", "what's deferred", "what's actually in progress", or "reconcile the tracker". Read-mostly: creates/updates beads, never edits code.
---

# Debt Reconciliation

FABLE = this plugin's root directory (recorded as `plugin_root` in the repo's `.claude/fable.json`).

Three sweeps, then a report. Ground rule: **the tracker must match reality in both directions** — no debt in code that beads doesn't know about, no bead claiming a state the code contradicts.

## 1. Code → beads (harvest)

- Grep all `# shortcut:` comments. Each either carries a bead ID (`# shortcut(bc-xxxx): ...`) that resolves to an open bead, or gets one now: `bd q "<file>:<line> <ceiling>" --labels shortcut-debt`, then add the ID to the comment.
- Run `python "FABLE/hooks/audit.py"`; every warning without a covering bead gets one. Label by nature: `bug` (wrong today — swallowed exception hiding failures, diverged duplicate), `shortcut-debt` (deliberate ceiling), `rewrite` (design-level, belongs in REWRITE_PLAN.md).
- Before creating, dedup: `bd search "<key phrase>"` — update the existing bead rather than spawning a twin.

## 2. Beads → code (verify claims)

- `bd list --status in_progress`: for each, is someone/something actually working it right now? No → demote with a note: `bd update <id> --status open` + `bd note <id> "parked at <state>; next step <X>"`. An `in_progress` bead nobody is working is a lie the whole team plans around.
- `bd list --status blocked`: each must name its blocker (a linked bead or an external fact in a note). Blocker gone → back to open.
- Deferred features: delayed-but-wanted work is `--status deferred`, never silently closed and never left `open` to rot in the ready queue. A deferral note says what triggers revival.
- Spot-check closed-this-week beads: closes need evidence notes. A close without evidence gets reopened.

## 3. Bug labeling pass

Anything discovered broken during the sweeps: `bd q "<repro one-liner>" --labels bug` with file:line. Bugs are never folded into feature beads or fixed silently during reconciliation — this skill changes no code.

## Report (honest accounting)

- Counts: open / in_progress (each with owner + evidence it's live) / blocked (each with named blocker) / deferred / closed this period.
- New beads created by the harvest, zombies demoted, evidence-less closes reopened.
- Top of `bd ready` — what's genuinely workable next.
- The one-line health check: does `# shortcut:` count in code equal open `shortcut-debt` beads? If not, say which side is stale.
