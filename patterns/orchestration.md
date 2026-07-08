# Orchestration

When and how to control other models/subagents. Based on Anthropic's multi-agent research system and Claude Code best practices.

## When to fan out — and when not to

- **Fan out** for breadth-first, independent work: parallel research angles, multi-file audits, mass migrations, searching many locations.
- **Stay single-threaded** for tightly coupled edits. Multi-agent beat single-agent by ~90% on research tasks; it does NOT win on sequential coding, where shared context is the whole game.
- Scale explicitly: simple fact-find = 1 agent, 3-10 tool calls. Only genuinely divisible work gets 5+. Never spawn agents for work you could finish in the time it takes to write their prompts.

## Writing subagent prompts

Every delegation states four things:

1. **Objective** — the question or task, self-contained (the subagent sees none of your context).
2. **Output format** — exactly what to return: "raw markdown list of file:line + one-line finding", "JSON matching this schema". A subagent's reply is data for the orchestrator, not user-facing prose — say so.
3. **Tool guidance** — where to look, what to skip, which tools to prefer.
4. **Boundaries** — scope it owns, scope it must NOT touch (prevents duplicate work across parallel agents), and an effort bound.

## Subagents as context hygiene

The main context is for decisions and implementation. Anything that would flood it — reading fifteen files to answer one question, a broad grep across naming conventions — goes to a subagent that returns a short conclusion. Delegate the reading, keep the deciding.

## Writer/reviewer separation

A fresh-context subagent reviews the finished diff against the request, unbiased by the reasoning that produced it. Instruct reviewers to report **only correctness and requirement gaps** — a reviewer told to "find issues" will invent some, and chasing invented issues produces over-engineering.

## Trust model

- Subagent output is a claim, not a fact. Verify anything load-bearing (spot-check the cited file:line, re-run the reported command) before building on it.
- A subagent that returns nothing useful gets ONE refined retry with a sharper prompt; after that, do it yourself or report the gap.
- The orchestrator owns the final answer. "The subagent said so" is not a justification the user can act on.

## Handoff between sessions/models

Future sessions and other models only know what's on disk. Any state the next agent needs — decisions made, work remaining, known-broken items — gets written to a file (HANDOFF.md, PR description, TODO file) before the session ends. The generated SYMBOLS.md + short ARCHITECTURE.md are the standing handoff for code structure.
