# Worktree Behavior

Git worktrees give an agent an isolated copy of the repo. Isolation is cheap; abandoned isolation is expensive — a stale worktree is a full shadow copy of the codebase that pollutes search, duplicate detection, and indexing. (Observed: backchannel's leftover `.claude/worktrees/ri-resume` doubled every symbol in the first audit run.)

## When a worktree is required

- Two or more agents mutating files in the same repo at the same time. Parallel writers without isolation = silent overwrites.
- Experimental or high-risk changes (large refactor, dependency upgrade) where the main checkout must stay deployable.
- Long-running work that must survive alongside day-to-day changes on the main checkout.

## When a worktree is waste

- Single-threaded edits, however large. One writer needs no isolation.
- Read-only work (research, review, audit). Readers can't conflict.
- "Just to be safe." Safety without a concurrent writer is pure overhead plus a cleanup liability.

## Lifecycle — every worktree, no exceptions

1. **Create** one worktree per task, named for the task, on its own branch.
2. **Work** entirely inside it. Gates run against the worktree root: `python hooks/audit.py <worktree-root>`, tests via the worktree's own environment. Never mix edits across the worktree and the main checkout in one task.
3. **Land** the result: merge or PR the branch. An unmerged worktree at task end is a decision, not a default — say why it's parked and when it dies.
4. **Remove**: `git worktree remove <path>` immediately after landing, then `git worktree prune`. Creation and removal are one unit of work; a task that created a worktree isn't done until the worktree is gone.

## Hard rules

- **Never leave uncommitted work in a worktree at session end.** Future sessions only know what's committed or written down. Commit to the branch, or write the state to HANDOFF.md and say so.
- **One task, one worktree, one branch.** No reusing a stale worktree for a new task — orientation inside it is poisoned by the old task's leftovers.
- **Tooling ignores worktree litter defensively:** the index and audit skip `.claude/` so an abandoned worktree can't corrupt results — but that's the seatbelt, not the license. `git worktree list` at cleanup time; anything unexplained gets removed or reported.
- Worktrees live where the tool puts them (`.claude/worktrees/`) or outside the repo — never loose inside the source tree.
