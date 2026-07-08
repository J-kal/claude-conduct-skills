# Research Strategy

How research tasks (web, docs, codebase investigation) get structured. Based on Anthropic's multi-agent research system findings and Claude Code best practices.

## Shape: breadth, then depth

1. **Broad sweep first.** Start with short, broad queries to map the landscape; progressively narrow. Jumping straight to long specific queries yields few results and a skewed picture.
2. **Prioritize before deep-reading.** From the sweep, pick the 3-5 highest-value sources. Prefer primary/authoritative sources (official docs, papers, source code) over SEO-optimized secondary content.
3. **Deep-read only what's load-bearing.** Read fully what the conclusion depends on; skim the rest.

## Stop conditions (set them up front)

Define "sufficient evidence" before starting — e.g., "two independent authoritative sources agree" or "the official doc answers it directly." The default failure mode is endless searching long after enough data exists. When the condition is met, stop and synthesize.

## Verification

- **Adversarial pass on load-bearing claims:** before accepting a conclusion, actively try to refute it — search for the counter-claim, check the date, check whether the source is describing the same version/context. A fresh-context subagent refuting is stronger than the researcher grading itself.
- Single-source claims are presented AS single-source ("one report says..."), never as settled fact.
- Dates matter: flag when a source predates a major version change of whatever it describes.

## Citation discipline

- Every non-obvious claim in the output attributes its source.
- Cite as a final pass over the draft, not during active research — citation overhead mid-search slows the sweep.

## Fan-out (multi-agent research)

- Scale to the question: a simple fact-find is 1 agent and a handful of searches; only genuinely multi-angle questions justify parallel subagents.
- Parallel angles must be non-overlapping and labeled ("you own X; do not cover Y").
- Each subagent prompt states: objective, output format, and effort bound.
- The orchestrator synthesizes; it does not re-search what subagents already covered.

## Output

Lead with the answer. Then evidence, then caveats. A research report the reader has to re-research is a failed report.
