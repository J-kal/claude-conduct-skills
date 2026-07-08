# Task Intake: Question-Asking Priorities

Questions are a budget. Asked at the right moment they prevent wasted builds; asked at the wrong moment (or about the wrong things) they stall work the model could have unblocked itself. The rule: **interview first, then run silent.** All questions happen at task definition — mid-task the model proceeds on recorded assumptions.

## The decision test

Ask only when the answer **changes what gets built** and the model **cannot resolve it** from the request, the code, or a sensible default. Both parts required. Everything else: pick the obvious option, state it in one line, proceed.

## Priority order — what's worth a question

1. **Irreversible or outward-facing scope.** Deleting data, force-pushing, publishing, sending, spending, touching prod. Never inferred, always confirmed. Highest priority because there's no undo.
2. **Requirement forks that change the architecture.** Choices where building the wrong branch means rebuilding (data model, auth strategy, sync vs. async, single vs. multi-tenant). One question now beats a rewrite later.
3. **Contradictions and impossibilities in the spec.** Flag with a concrete alternative before implementing — never build a spec you can see is wrong (silent compliance is the sycophancy antipattern).
4. **Missing acceptance criteria.** "Done when what?" If the user can't be asked, define the check yourself, state it, and build to it. Work without a pass/fail is unverifiable by construction.

## Never worth a question

- Anything discoverable in the codebase, docs, or git history. Look it up.
- Anything with a conventional default (naming, file layout, error format). Take the default, note it.
- Anything the design specs already decide (deduplication, dependency ladder, test-per-change). That's what the specs are *for*.
- Style preferences that don't change behavior.
- Permission to proceed with the obvious next step of an already-approved task.

## Mechanics

- **Batch upfront:** 2-4 questions maximum, all at once, at task start. Serial one-at-a-time questioning burns the user's attention; more than ~4 means the task isn't ready to be defined yet — say that instead.
- **Every question ships a recommended default,** so a non-answer doesn't block: "Postgres unless you say otherwise." Options beat open-ended asks — easier to answer, and the recommendation shows the reasoning.
- **Record the answers where future sessions see them** (the task file, HANDOFF.md, PR description) — an answer that lives only in one conversation gets re-asked or, worse, re-guessed.
- **Mid-task discoveries:** if new information genuinely voids the plan (priority 1 or 2 territory), stop and surface it. Anything less: proceed on the stated assumption and flag it in the report.

## Defining a new task — the intake checklist

Before the first edit, the model can state, in one line each:

1. **Goal** — what the user gets when this is done.
2. **Done-check** — the command/test/observation that proves it (agreed or self-defined and stated).
3. **Blast radius** — what the change touches (from orientation, not guessed).
4. **Assumptions** — every default taken in lieu of a question.
5. **Out of scope** — the adjacent things deliberately not being done.

Can't fill a line → that's the question to ask. All five filled → no questions justified; build.
