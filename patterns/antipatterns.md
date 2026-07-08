# Antipatterns

What the model must NOT do. Each entry: the failure, why it happens, the counter-move.

## Rewriting instead of editing
The model regenerates a whole file to change a few lines, silently dropping comments, edge-case handling, or someone else's in-flight work.
**Counter:** targeted edits only. If a rewrite genuinely is needed, say so and get approval first.

## Duplicate implementation
A second `parse_date()` three files from the first, because searching felt slower than writing.
**Counter:** SYMBOLS.md check + grep before any new function. The duplicate-check hook blocks it if it slips through.

## Speculative abstraction
Base classes, plugin systems, and config options for futures nobody requested. Flexibility that is never exercised is pure maintenance cost.
**Counter:** abstraction requires two real consumers existing today.

## Scope creep in a diff
Asked to fix a bug, the model also renames variables, reorders imports, and "improves" adjacent functions. Review cost explodes; regressions hide in the noise.
**Counter:** the diff answers the request and nothing else. Improvements go in a list at the end of the response, not in the diff.

## Hallucinated APIs
Calling methods that don't exist on a library, or on this codebase's own modules, because the name is plausible.
**Counter:** never call an internal function without seeing its definition (SYMBOLS.md line or source). For libraries, verify the API against the installed version when at all unsure.

## Symptom-patching
Guarding one call site the ticket named while every sibling caller stays broken.
**Counter:** before fixing, grep every caller of the function being touched; fix at the shared choke point.

## Test-gaming
Making tests pass by weakening asserts, adding skips, hardcoding expected values, or catching the exception the test was checking for.
**Counter:** a failing test is information about the code, not an obstacle. If the test itself is wrong, say so explicitly and show why.

## Sycophantic spec agreement
Implementing a spec the model can see is wrong or self-contradictory, because pushing back feels impolite.
**Counter:** contradictions and likely mistakes get flagged BEFORE implementation, with a concrete alternative. Then follow the user's call.

## Index rot
Hand-maintained docs drift from reality within weeks, then actively mislead every future session.
**Counter:** anything enumerable is generated (SYMBOLS.md); the hand-maintained layer (ARCHITECTURE.md) stays short enough to verify at a glance.

## Confident completion claims
"Done and all tests pass" when tests were never run, or failed.
**Counter:** report only what was verified, with the command output. Unrun = say unrun. Failed = paste the failure.

## Context hoarding
Reading entire files (or the whole repo) into context "for safety," burning the context window before the real work starts, then losing earlier instructions to truncation.
**Counter:** search first, read only the relevant spans, delegate broad sweeps to subagents that return conclusions.

## Dependency reflex
`poetry add somelib` for what three lines of stdlib do. Every dependency is a supply-chain, upgrade, and audit liability.
**Counter:** the dependency ladder in code-patterns.md. New deps need explicit approval.
