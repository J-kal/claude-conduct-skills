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

## Model allocation — smallest tier that holds

Strict design guideline: **every delegated task runs on the smallest/cheapest model that can do it.** The orchestrator may be a large model; its fan-out workers are not by default. Match the model to the task's actual difficulty, escalating only on demonstrated failure — never preemptively "to be safe."

The ladder, cheapest rung first:

1. **No model** — counting, grepping, formatting, listing files, running a script. If deterministic code (an audit rule, `build_index.py`, ripgrep) produces the answer, no agent is spawned at all. This is the real minimum; reach for it before any model.
2. **Smallest model (Haiku-class)** — mechanical, bounded work against an explicit rubric: single-file reads, structured extraction, pattern-matching to a given taxonomy, "does this file contain X", per-module sweep passes that report candidates for the orchestrator to verify.
3. **Mid model (Sonnet-class)** — judgment needing cross-file reasoning: is this abstraction warranted, does this fix address the root cause, tradeoffs with no obvious answer, the stop-gate diff review.
4. **Large model (Opus/Fable-class)** — only the hardest synthesis, architecture, and adversarial verification where a smaller tier has *demonstrably* failed the specific task. The exception, not the default.

(Current tier→model mapping: Haiku 4.5, Sonnet 5, Opus 4.8 / Fable 5. The rung is the principle; the names are just today's fill-ins — reassess when the model lineup changes.)

Rules:
- **State the model and why in every spawn**: "Haiku — mechanical rubric match" / "escalated to Sonnet: Haiku missed the cross-file divergence." An unstated model choice defaults to the smallest that fits the rung above.
- **Split by difficulty, not just by scope.** A sweep is usually Haiku workers finding candidates + one Sonnet pass verifying the hard ones — not one big model doing all of it. Cheap-find, careful-verify.
- **Escalate on evidence, downgrade by default.** If a Haiku worker returns something plainly wrong, retry that item one tier up — don't upgrade the whole fleet.

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
