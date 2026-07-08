# Ingestion Protocol

The strict procedure for taking over an existing codebase, finding every poor AI-driven design choice in it, and producing line-by-line rewrite designs. Ingestion is **documentation-first**: the sweep produces a ledger, never edits. Detection and correction are separate passes — fixing mid-sweep corrupts the inventory, biases later findings, and makes the "before" state unrecoverable.

Output artifact: `REWRITE_PLAN.md` — the remediation ledger. Execution of the ledger then follows the cleanup-protocol rules (one entry per commit, behavior preserved, evidence per claim).

## Phase 0 — Freeze and baseline

1. Clean git state (commit or stash anything loose). Record the commit hash the ingestion describes — the ledger is only valid against it.
2. `python hooks/build_index.py` — the symbol inventory.
3. `python hooks/audit.py` — mechanical baseline; record counts.
4. Run the test suite; record pass/fail per test. Failing tests are findings, not blockers.
5. **Behavior snapshot:** enumerate what the system actually does — entry points, routes/CLI commands/jobs, external services touched (from config + imports). This is the contract the rewrites must preserve; if it isn't written down, "behavior preserved" is unverifiable.

## Phase 1 — Inventory

Map before judging:

- Module map: every package/module, one line each — what it claims to do (from names/docstrings), what it imports, what imports it.
- Declared vs. actual dependencies: `pyproject.toml` against real imports. Unused deps and undeclared imports are both findings.
- Hotspots: largest files, most-imported modules, files with the most churn (git log). Slop concentrates where generation was heaviest.

## Phase 2 — Detection sweep

Two passes, in order:

**2a. Mechanical (minutes):** `python hooks/audit.py` catches the checkable signatures — duplicates, single-impl abstractions, trivial wrappers, swallowed exceptions, gamed tests, long functions, bare TODOs, stale worktrees.

**2b. Judgment sweep (the real work):** every module read in full by fresh eyes, hunting the AI-slop taxonomy below. Fan out one subagent per module cluster with non-overlapping scopes; each returns ledger-entry candidates in the exact format of Phase 3 (their output is data, not prose). The orchestrator dedups against the full set and verifies each candidate's file:line before it enters the ledger — a subagent claim is not a finding until checked.

### The AI-slop taxonomy

Signatures of AI-driven design failure, roughly in order of damage:

1. **Parallel implementations** — the same behavior written twice because generation didn't search. Includes near-duplicates that have since *diverged*: the deadliest form, because one copy has the bug fix and the other doesn't.
2. **Hallucinated integration** — code calling APIs that don't exist, exist with different signatures, or were never once exercised (no test, no caller path from any entry point). Verify against the installed package, not plausibility.
3. **Test theater** — tests that mock the thing under test, assert the mock was called, hard-code the implementation's output, or catch the failure. Coverage numbers from theater are worse than no coverage: they certify slop.
4. **Speculative abstraction** — interfaces with one implementation, factories for one product, config for constants, plugin systems with one plugin, "manager"/"handler"/"service" layers that only forward.
5. **Pass-through layering** — functions/classes whose entire body delegates unchanged to another function. Each layer is a place for future edits to miss.
6. **Defensive bloat** — try/except wrapping everything (then swallowing), the same input re-validated at every layer, None-checks on values that can't be None. Noise that hides the one check that matters.
7. **Inconsistent idiom** — three error-handling styles, mixed sync/async for the same operation, two config-loading mechanisms. Each seam is where a future generated change picks the wrong one.
8. **Dead code** — functions no entry point reaches, unused imports, commented-out blocks, feature flags nothing sets. Every dead line is context a future model reads and tries to preserve.
9. **Comment noise** — comments restating the line below, docstrings that paraphrase the signature, changelog comments ("fixed bug"). They rot instantly and train readers to skip all comments.
10. **Kitchen-sink modules** — files accreting unrelated responsibilities because generation appends where the cursor is. Detected by failure to summarize the module in one sentence.

## Phase 3 — The remediation ledger (`REWRITE_PLAN.md`)

One entry per finding. The entry must be executable by a different model with no other context — that's the bar for "clear line-by-line documentation." Format:

```markdown
## RW-014: parallel implementation of retry logic
- **Where:** services/api_client.py:88-131 and services/webhooks.py:40-77
- **Taxonomy:** 1 (parallel implementation, diverged)
- **Severity:** high — webhooks copy lacks the backoff cap added to api_client in a1b2c3d
- **Current, line by line:**
  - api_client.py:88-95 — builds retry loop, max 5 attempts, exponential backoff capped at 30s
  - webhooks.py:40-46 — same loop, uncapped backoff (divergence), max hardcoded 3
  - webhooks.py:47-60 — duplicates error classification already in api_client.py:101-115
- **Why it's wrong:** one behavior, two owners; the cap fix (a1b2c3d) missed the copy. Every future retry change has a 50% miss rate.
- **Target design:** single `retry_call(fn, *, max_attempts=5, cap=30)` in api_client.py; webhooks imports it. No new module — api_client is already the shared home (SYMBOLS.md confirms no third copy).
- **Rewrite steps:**
  1. api_client.py:88-131 — extract loop body into `retry_call`, keep existing behavior exactly (cap included).
  2. webhooks.py:40-77 — delete; replace call site at :38 with `retry_call(post_webhook, max_attempts=3)`.
  3. Grep `backoff|retry` repo-wide — confirm no third copy (checked: none).
- **Blast radius:** callers of the two current blocks: api_client.py:140, webhooks.py:38. Nothing else (grep verified).
- **Verify:** existing test_api_client retry tests pass unchanged; add one test asserting webhook retry respects the cap (the divergence this fixes).
- **Behavior change?** YES — webhook backoff becomes capped. Flagged: this is the *point*, needs sign-off.
```

Ledger rules:

- **Every claim in an entry is verified at write time** — the file:line checked, the callers grepped, the "no third copy" actually searched. An unverified entry is a guess wearing a plan's clothes.
- **Target design obeys the design specs:** the rewrite reuses before it writes (SYMBOLS.md consulted and cited), takes the dependency ladder, adds no abstraction without two consumers. Ingestion that replaces slop with new slop is churn.
- **Behavior changes are explicitly marked** and separated — the default rewrite is behavior-preserving; anything else needs the user's sign-off before execution.
- Entries end with a priority table: severity × blast radius, taxonomy classes 1-3 (parallel impls, hallucinated integration, test theater) always ranked above 4-10 — they corrupt future work, the rest merely bloat it.

## Phase 4 — Sign-off and execution

1. Present the ledger: counts by taxonomy class, the priority table, total estimated net line change (should be strongly negative), and every behavior-change entry called out for decision.
2. On approval: execute per cleanup-protocol — one ledger entry per commit, tests after each, entry marked done in the ledger with the verification output pasted in.
3. Re-run Phase 0's baseline at the end; the ledger closes with before/after counts.

## Hard limits

- **No edits during Phases 0-3.** The only files ingestion writes are the ledger and the generated index.
- **No entry without a verify step.** A rewrite that can't state its check doesn't get executed.
- **Scale honestly:** a 200-file repo is not one session's judgment sweep. Batch by module cluster, ledger grows incrementally, each batch's scope recorded so coverage is provable — "swept 40/61 modules" beats a silent partial sweep presenting as complete.
