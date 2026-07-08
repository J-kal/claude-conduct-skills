---
name: intake
description: Define a new task before any work starts — batched clarifying questions by priority, the five-line intake checklist (goal, done-check, blast radius, assumptions, out-of-scope), and a bead to track it. Use at the start of any non-trivial feature, bug fix, or refactor; when a request is ambiguous; or when the user says "intake", "define this task", or "plan this properly". NOT needed for trivial one-line changes.
---

# Intake

FABLE = this plugin's root directory (recorded as `plugin_root` in the repo's `.claude/fable.json`).

Follow `FABLE/patterns/task-intake.md` (and `FABLE/patterns/beads-hygiene.md` for tracker rules). Procedure:

1. **Interview first, run silent after.** Batch 2-4 questions maximum, each with a recommended default so a non-answer doesn't block. Ask ONLY what changes the build and can't be resolved from the request, the code, or a default — priority order: irreversible/outward-facing scope → architecture-changing forks → spec contradictions (flag with a concrete alternative) → missing acceptance criteria. Never ask what's discoverable, conventional, or already decided by the design specs.
2. **Fill the five lines** (one sentence each): goal, done-check, blast radius (from actual orientation — grep the callers, don't guess), assumptions taken in lieu of questions, out-of-scope. A line you can't fill IS the question to ask.
3. **Create the bead:** `bd create "<task title>" -d "<the five lines>"` with the right label — `bug` for defects (include repro in the description), `feature` for new work. Big tasks become an epic with linked children (`bd link`). Set `--status in_progress` only when work actually starts.
4. **Mid-task:** proceed on recorded assumptions; stop only for discoveries that void the plan (priority 1-2 territory). New scope discovered mid-task becomes a NEW bead, not silent expansion of this one.
5. **On completion:** close the bead with the done-check's output as the evidence note. If the task ends incomplete, the bead goes back to `open` (or `deferred` for delayed features) with a note stating exactly what's done, what's next, what's broken — future sessions only know what's written down.
