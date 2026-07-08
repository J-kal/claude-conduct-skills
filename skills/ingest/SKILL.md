---
name: ingest
description: Take over an existing codebase — sweep it against the AI-slop taxonomy and produce REWRITE_PLAN.md, a line-by-line rewrite ledger, with every finding mirrored as a beads issue. Documentation only, writes no code. Use once when adopting a repo this package is newly installed into, after inheriting AI-generated code, or when the user says "ingest", "audit this codebase for AI slop", or "what needs rewriting". NOT for routine drift (use cleanup) or for executing fixes (cleanup executes approved ledger entries).
---

# Ingest

FABLE = this plugin's root directory (recorded as `plugin_root` in the repo's `.claude/fable.json`).

Follow `FABLE/patterns/ingestion-protocol.md` in full. Non-negotiables:

1. **No edits.** Outputs are REWRITE_PLAN.md, regenerated SYMBOLS.md, and beads issues. Detection and correction are separate passes.
2. **Freeze/baseline:** record the commit hash the ledger describes; index, audit, run tests (failures are findings), write the behavior snapshot (entry points, routes/CLI/jobs, external services).
3. **Sweep:** mechanical (`python "FABLE/hooks/audit.py"`) then judgment — every module read against the taxonomy: parallel/diverged implementations, hallucinated integration, test theater, speculative abstraction, pass-through layering, defensive bloat, inconsistent idiom, dead code, comment noise, kitchen-sink modules. Fan out subagents per module cluster on large repos; verify every candidate's file:line before it enters the ledger. Report coverage honestly ("swept N/M modules").
4. **Ledger entries** must be executable by a different model with no other context: location, taxonomy class, severity, current behavior line by line, why wrong, target design citing SYMBOLS.md for reuse, numbered line-level rewrite steps, grep-verified blast radius, verify step, explicit behavior-change flag.
5. **Beads mirror:** one bead per ledger entry — `bd q "RW-NNN: <title>" --labels rewrite` (add `bug` if it's broken today, not just poorly designed); priority from severity × blast radius (taxonomy 1-3 → P1); `bd link` entries that must land in dependency order. The ledger holds the design; the bead holds the state.
6. **Sign-off gate:** present counts by taxonomy class, the priority table, net line estimate, and every behavior-change entry for explicit user approval before anything is executed (via the cleanup skill).
