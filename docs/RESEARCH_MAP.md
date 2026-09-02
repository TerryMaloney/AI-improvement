# Research Map

## North-star question

Can we experimentally discover procedures that make an existing AI model measurably more reliable, useful, and efficient — and can those procedures themselves be improved automatically without changing model weights?

Higher-order extension:

> Can a mixed human–AI system recursively improve its own error-detection and correction procedures using externally grounded evidence, while detecting when shared assumptions, self-models, evidence environments, incentives, evaluators, or critic lineages are themselves the source of error?

The long-run target is therefore not assumed to be a faultless model. A potentially stronger target is an **error-correcting intelligence stack** in which faults become increasingly observable, diagnosable, challengeable, and correctable across humans, models, tools, evidence, execution, evaluators, and descendants.

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
- [`docs/REFLEXIVE_ERROR_CORRECTION_RESEARCH_MAP_2026-08-30.md`](REFLEXIVE_ERROR_CORRECTION_RESEARCH_MAP_2026-08-30.md)
- [`docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`](EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md)
- [`docs/PRIOR_ART_AND_DESIGN_SIGNALS_2026-08-29.md`](PRIOR_ART_AND_DESIGN_SIGNALS_2026-08-29.md)
- [`docs/FABLE_5_1_RESEARCH_DISCOVERY_2026-09-01.md`](FABLE_5_1_RESEARCH_DISCOVERY_2026-09-01.md) — failure taxonomy (G1–G7, two roots), EGP-perturbation compression of the six states, ranked portfolio, kill/merge list, novelty-engine proposal. **Proposal pending review; changes no frozen artifact.**
- [`docs/EGP_AND_PREDICTION_FRONTIER_SYNTHESIS_2026-09-01.md`](EGP_AND_PREDICTION_FRONTIER_SYNTHESIS_2026-09-01.md) — red-team of the EGP synthesis (count ceiling REJECTED; robust-EVOI-with-reliability-learning adopted, not new); R1/R2 narrowed to falsifiable R1′/R2′ with a churn rival and a frozen forward prediction (P4); `EXPERIMENT_CAUSAL_CONTRACT` template for future families; NOVELTY-ENGINE-003 (prediction-frontier expansion: KNOWN theory, EXTENSION as generation objective) with a ≈280-call kill test; reviewed kill/merge list (nothing deleted). **Proposal; changes no frozen artifact.**
- [`docs/EXPERIMENT_CAUSAL_CONTRACT.md`](EXPERIMENT_CAUSAL_CONTRACT.md) — **implemented** (validator, tests, Stage 0B draft). Prospective rule for future families.
- [`docs/results/ZERO_DISPATCH_TESTS_2026-09-02.md`](results/ZERO_DISPATCH_TESTS_2026-09-02.md) — P1 not testable, P7 not testable mechanically, M2 downgraded after a false premise was found; R1′/R2′ unchanged, prospective table frozen at `experiments/meta_r1r2/`.

The reflexive error-correction branch adds six state families that future architecture should avoid collapsing:
- world epistemic state;
- functional self state;
- environment / observation state;
- objective / preference state;
- evaluator state;
- lineage / independence state.

These are program-level hypotheses. They do not alter frozen experiment-specific artifacts.

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

Future controllability work should distinguish task signals from self-state, environment-state, evaluator-state and incentive-state signals rather than treating every predictor as a generic feature.

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

Generalization should eventually vary not only model/task family but also environment/tool state and evaluator lineage, because a procedure that works only under one retrieval surface or judge is a local procedure.

### Stage 5 — Automated procedure discovery
Given the frozen current champion procedure, allow an AI researcher role to propose candidate procedures.

Candidates do not replace the champion until they pass the same experimental and holdout rules.

Automated search must treat evaluator quality as part of the experiment. Improving the exposed score is not sufficient evidence of improving the underlying capability.

### Stage 6 — Recursive procedure improvement
Loop:

current champion → candidate generation → controlled test → red-team → independent validation → promote or reject.

Primary risk: optimizing the benchmark rather than real capability.

Additional recursive risks:
- self-confirming evaluator loops;
- inherited false self-beliefs;
- correlated critic blind spots;
- environmental limitations misread as model traits;
- a prediction about the agent changing the agent once revealed;
- objective/incentive distortion of information seeking.

Recursive descendants inherit artifacts and lineage, not validated capability claims. Claims must be re-earned against external evidence.

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

Additional experimentally earned inputs/actions may eventually include:
- environment/tool reachability state;
- evidence-lineage independence;
- evaluator reliability/state;
- descriptive self-model state;
- objective/incentive state;
- anomaly / model-break escalation;
- independent critic selection;
- stronger external-verifier escalation.

The product is the empirically validated procedure/control layer, not necessarily a new model.

## Execution lane

Research and execution should develop together once Stage 0 is trustworthy.

Research lane:
measure → discover → validate → generalize.

Execution lane:
choose real task → execute → observe external outcome → measure usefulness → feed failures back into research.

A later reciprocal-correction lane may explicitly test:
human proposal → AI criticism → external evidence/execution → human/system revision → future decision.

Do not commercialize first. Use the system internally on useful work and generate evidence that it accomplishes something valuable before abstracting it into an API or platform.

## Permanent guardrails

- A paired exact test spends DISCORDANT PAIRS, not sample size. Size on expected
  discordance and record, before dispatch, the discordant count below which
  rejection is arithmetically impossible.
- Retrieval AVAILABILITY, retrieval USE, and QUERY QUALITY are three different
  treatments. A result about one licenses nothing about the others.
- A deterministic, fingerprinted, golden-corpus-tested evaluator is not thereby a
  correct one. Every check that reads only the rule and never a realized output
  can pass while the rule mis-scores the run.
- An evaluator whose verdict can be changed by trailing elaboration is an
  arm-correlated instrument, because elaboration length plausibly correlates with
  the treatment.
- Ceiling in BOTH arms is a measurement of the effect, not an absence of
  measurement. Ceiling in the BASELINE arm alone is a favourable condition, not a
  defect.
- Harder items do not automatically buy power. In a one-sided paired test,
  genuine repairs cancel genuine harms.
- Prefer repairing the instrument over increasing n, and demonstrate the
  preference by computing both.
- A reported quantity computed from a field that was never populated is not a
  measurement, however plausible its value looks.
- The freeze/grade/analyse driver is itself a load-bearing construct and belongs
  in the pre-dispatch freeze.
- Structured output formats may alter the cognition being measured; when format
  compliance could interact with the arm, a structured field is a robustness
  check, never the primary route.
- GitHub is canonical project memory; chat sessions are working contexts.
- Frozen artifacts are never silently changed after outcome visibility.
- Re-grades are not replications.
- Model self-report is not authoritative telemetry where observed telemetry exists.
- A model's explanation of why it acted is a claim, not privileged causal telemetry.
- A self-prediction shown to the acting agent may become an intervention; disclosure effects must be tested rather than assumed away.
- Unreachable environment states are NOT MEASURED, not failures.
- Tool access is an environment-state property with time/tool/version scope, not a permanent model capability.
- Multiple sources, calls, agents, or model providers are not automatically independent; lineage and correlated errors matter.
- Judged effects must remain separated from deterministic effects when the measurement process can itself create arm differences.
- Truth state, objective/preference state, environment state, and evaluator state must not be collapsed.
- Procedure improvements must eventually generalize to unseen tasks.
- Real execution evidence outranks a model judging another model’s usefulness.
- Recursive descendants do not inherit validated performance claims without revalidation.
- Human judgments are revisable inputs to the research loop, not an infallible oracle.
- An interesting result is a signal to investigate, not permission to call a mechanism verified.
