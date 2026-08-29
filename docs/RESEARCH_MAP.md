# Research Map

## North-star question

Can we experimentally discover procedures that make an existing AI model measurably more reliable, useful, and efficient — and can those procedures themselves be improved automatically without changing model weights?

This repository should distinguish five levels of claim at all times:

1. **Proven / exactly established** — mathematical proof or exact enumeration.
2. **Measured** — observed in a committed experiment or audit.
3. **Supported** — evidence exists, but the claim is not yet established generally.
4. **Hypothesis** — worth testing; not evidence.
5. **Engineering idea** — build only when an upstream hypothesis earns it.

## Detailed experimental ordering

See [`docs/EXPERIMENTAL_PROGRAM_2026-08-29.md`](EXPERIMENTAL_PROGRAM_2026-08-29.md) for the dependency-ordered experiment program, branch points, interaction tests, alternative-explanation protocol, and promotion ladder for provisional findings.

Related research branches:
- [`docs/EPISTEMIC_SYSTEMS_PRIOR_ART_MAP_2026-08-29.md`](EPISTEMIC_SYSTEMS_PRIOR_ART_MAP_2026-08-29.md)
- [`docs/PERSISTENT_SELF_IDENTITY_RESEARCH_MAP_2026-08-29.md`](PERSISTENT_SELF_IDENTITY_RESEARCH_MAP_2026-08-29.md)
- [`docs/PRIOR_ART_AND_DESIGN_SIGNALS_2026-08-29.md`](PRIOR_ART_AND_DESIGN_SIGNALS_2026-08-29.md)

## Program structure

### Stage 0 — Validate the laboratory
Goal: make sure the measurement system is not lying.

Required before production experiments:
- identifiable estimand
- valid null and test
- demonstrated Type-I control
- adequate replication
- treatment-blind selection
- grading-route symmetry
- telemetry and environment state
- frozen answer keys / prompts / analysis
- explicit stop rules

### Stage 1 — Establish intervention effects
First target: retrieval.

Question: are there tasks where retrieval helps and tasks where retrieval hurts enough that a non-constant policy has exploitable value?

Do not interpret a negative result on one battery as “retrieval controllers do not work.”

### Stage 2 — Establish controllability
Question: can observable task/model signals predict which procedure should be used before the action is chosen?

Begin with the smallest action space that the Stage-1 result justifies.

### Stage 3 — Establish execution value
Move beyond judged benchmark answers.

Every claimed capability improvement should eventually survive an execution test whose success criterion exists outside the evaluating model.

Preferred first domain: coding, because outcomes can be grounded in builds, tests, runtime behavior, regressions, repair count, latency, token/tool cost, and required human intervention.

Compare at minimum:
- model alone
- model + human-designed validated procedure
- later: model + automatically discovered procedure

### Stage 4 — Generalization
Freeze procedures, then evaluate on tasks/repositories not used to discover them.

Separate:
- discovery set
- validation set
- held-out / later-authored tasks
- real-world execution tasks

### Stage 5 — Automated procedure discovery
Given the frozen current champion procedure, allow an AI researcher role to propose candidate procedures.

Candidates do not replace the champion until they pass the same experimental and holdout rules.

### Stage 6 — Recursive procedure improvement
Loop:

current champion → candidate generation → controlled test → red-team → independent validation → promote or reject.

Primary risk: optimizing the benchmark rather than real capability.

### Stage 7 — Model-agnostic execution runtime
Only after the preceding stages earn it.

Long-term runtime may choose:
- model
- context
- retrieval policy
- reasoning/decomposition strategy
- tool use
- verification
- retry/repair
- stopping

The product is the empirically validated procedure/control layer, not necessarily a new model.

## Execution lane

Research and execution should develop together once Stage 0 is trustworthy.

Research lane:
measure → discover → validate → generalize.

Execution lane:
choose real task → execute → observe external outcome → measure usefulness → feed failures back into research.

Do not commercialize first. Use the system internally on useful work and generate evidence that it accomplishes something valuable before abstracting it into an API or platform.

## Permanent guardrails

- GitHub is canonical project memory; chat sessions are working contexts.
- Frozen artifacts are never silently changed after outcome visibility.
- Re-grades are not replications.
- Model self-report is not authoritative telemetry where observed telemetry exists.
- Unreachable environment states are NOT MEASURED, not failures.
- Judged effects must remain separated from deterministic effects when the measurement process can itself create arm differences.
- Procedure improvements must eventually generalize to unseen tasks.
- Real execution evidence outranks a model judging another model’s usefulness.
- An interesting result is a signal to investigate, not permission to call a mechanism verified.
