# Current Prior Art and Design Signals — 2026-08-29

Status: program-level research context, not a preregistration. These are external signals to inform future experiments; they do not alter frozen experiments.

## Why this exists

The project should stand on current external evidence rather than rediscovering known failure modes. The relevant frontier is broader than prompt engineering: model performance is increasingly understood as a property of the model plus harness, tools, inference budget, elicitation, evaluation, and execution procedure.

## Signals to incorporate

### 1. Treat the procedure/harness as a first-class research object
Current evaluation work increasingly distinguishes underlying model capability from elicited system performance. This supports the lab's broader question: how much capability/reliability can be extracted from a fixed model by changing the procedure around it?

Program consequence: retrieval is one intervention, not the final action space.

### 2. Broaden routing into resource/procedure allocation
Relevant actions eventually include retrieval, verification, reasoning/test-time compute, sampling, decomposition, context allocation, tool use, retries, stopping, and model choice.

Program consequence: after the binary retrieval experiment is understood, future controllers should allocate procedures/resources rather than merely choose SEARCH/NO SEARCH.

### 3. Automated prompt/workflow search is plausible, but benchmark overfitting is the central risk
Recent work explores evolutionary and automated optimization of prompts and agent workflows.

Program consequence: before automated procedure search, establish separate discovery, validation, held-out/later-authored, and real-execution task sets. Preserve candidate diversity and prevent failed hypotheses from polluting the active champion context.

### 4. LLM judges are measurement instruments, not ground truth
External work continues to find judge sensitivity to presentation and other surface properties. This agrees with exp003c's measured rubric-boundary sensitivity.

Program consequence: whenever an executable/objective criterion exists, it outranks an LLM judge. Judge-mediated results prove performance under that measurement process unless independently grounded.

### 5. Benchmark/task defects can masquerade as model failures
Audits of coding benchmarks have found broken, underspecified, overly strict, or low-coverage tasks.

Program consequence: add a permanent task-validity gate before serious battery freeze:
prompt <-> key/gold <-> evaluator/tests <-> intended capability.
All four must align.

### 6. Move real execution earlier
Long-horizon agent benchmarks and coding-agent studies increasingly evaluate functional task completion, tool use, self-correction, tests, and committed work rather than answer quality alone.

Program consequence: once Stage 0 measurement is trustworthy, begin a parallel execution track rather than waiting for recursive procedure optimization.

Preferred first execution domain: coding/repository tasks with builds, tests, runtime behavior, regressions, repair cycles, latency, token/tool cost, and human intervention.

### 7. Cost is part of capability
Adaptive routing/test-time-compute work shows that the best policy depends on budget and that extra inference is not uniformly valuable.

Program consequence: retain tokens, latency, tool calls, retries, and monetary/compute cost as first-class telemetry. Compare quality at matched cost and cost at matched quality where identifiable.

### 8. More verification is not automatically better
External work suggests that under some budgets, additional independent generation/sampling can outperform spending the same compute on generative verification.

Future experiment candidate: compare matched additional compute allocated to:
- more independent candidate solutions;
- deeper verification;
- repair/retry;
- retrieval;
- decomposition.

Do not assume VERIFY is intrinsically the highest-value use of compute.

## Added research branch: explicit epistemic state

A separate hypothesis worth investigating is whether a useful AI system benefits from an explicit, persistent representation of what it claims to know about the world rather than relying only on latent model weights, prompt context, or fresh search.

Candidate distinction:

- **model memory / parametric knowledge** — patterns encoded in weights;
- **retrieved evidence** — information returned by a tool at a point in time;
- **epistemic state** — explicit claims with provenance, scope, time, confidence/status, dependencies, contradictions, and update rules.

This is not yet an architecture decision. It is a research question.

Potential state object:

CLAIM
- proposition
- claim type
- entities/scope
- valid time / observed time
- provenance/evidence
- evidence independence
- status: observed / supported / disputed / inferred / unknown / superseded
- confidence or evidential strength (only if calibrated)
- dependencies
- contradiction links
- falsification/update conditions

Important constraint: the system must not convert repetition, model confidence, or multiple derivative sources into independent evidence.

Potential value:
1. distinguish “the model says X” from “evidence E supports X”;
2. prevent stale facts from silently persisting;
3. expose contradictions instead of averaging them away;
4. permit targeted re-verification when a downstream conclusion depends on a weak/stale claim;
5. make uncertainty and unknowns machine-actionable;
6. support execution decisions whose premises can be audited;
7. provide a structured substrate for procedure routing.

Major risks:
- building a knowledge graph that merely fossilizes hallucinations;
- false numerical precision in confidence scores;
- provenance laundering through derivative sources;
- runaway state/context growth;
- ontology complexity before demonstrated value;
- confusing coherence with truth.

Research rule: do not build a large world model now. Test the smallest useful epistemic ledger against a baseline on tasks where provenance, contradiction, freshness, or dependency tracking should matter.

## Candidate future experiment

Question: does an explicit epistemic ledger improve downstream factual/execution reliability over an otherwise identical procedure with the same evidence budget?

Possible controlled conditions:
A. ordinary context + retrieval;
B. same retrieval/evidence, converted into explicit claim/evidence/state records;
C. later, state + targeted re-verification/update policy.

Use objective/deterministic outcomes where possible. Measure not only final correctness but stale-claim persistence, contradiction detection, unsupported inference, unnecessary retrieval, and cost.

This experiment belongs after the current Stage-0 measurement work; it should not alter exp004 midstream.
