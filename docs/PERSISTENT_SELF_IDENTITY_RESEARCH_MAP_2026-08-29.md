# Persistent Self-Identity and Subjectivity Research Map — 2026-08-29

Status: research context only. Not a preregistration and not a claim about consciousness or sentience.

## Core distinction

Three different questions must remain separate:

1. **Persona persistence** — can an agent maintain stable traits, preferences, goals, and autobiographical continuity across sessions?
2. **Functional self-modeling** — can an agent maintain an evidence-linked model of its own capabilities, limitations, history, tools, goals, uncertainty, and behavioral tendencies, and use that model to make better decisions?
3. **Subjective experience / consciousness** — is there anything it is like to be the system?

The first two are empirically testable engineering/research questions. The third is unresolved and must not be inferred from self-reports, persona coherence, or self-referential language.

## Relevant prior art

### Self-recognition
2024 work testing whether LMs can recognize their own outputs found no general or consistent self-recognition across ten models; models often preferred the answer they judged best regardless of authorship.

More recent activation-level work (2026) reports detectable model-specific self-recognition/fingerprinting signals in activations. This is evidence about attribution/self-recognition signals, not persistent autobiographical identity.

### Functional self-awareness / self-models
KnowSelf (2025) explicitly trains agents to assess situational demands and regulate knowledge/resource usage.

SARSI (2026) proposes a persistent machine-readable self-model covering identity, autobiographical continuity, goals, capabilities, limitations, uncertainty, tools, relationships, and developmental history. It explicitly requires authoritative self-model fields to come from external records/benchmarks/logs rather than trusting the LLM's own generated self-description. The paper is conceptual and reports no original experimental dataset.

### Persistent identity representations
ID-RAG (2025) represents agent identity with a structured identity knowledge graph of beliefs, traits, values, preferences, and goals and retrieves relevant identity state during action selection. Reported simulations show improved identity recall and action alignment over baseline long-memory agents across GPT-4o, GPT-4o mini, and Qwen2.5-7B, although evaluation partly relies on LLM-mediated alignment scoring and small simulation runs.

Identity-as-Attractor (2026) reports that semantically coherent identity documents induce reproducible attractor-like activation geometry. This is mechanistic evidence that persistent identity context changes internal representations, not evidence of consciousness.

### Identity continuity as an unsolved structural issue
"Dissociative Identity" (2026) argues that current LM agents lack the structural conditions normally assumed by persistent identity/reputation: stable boundaries, behavioral continuity, non-detachable memory, and costly non-fungibility. The agent is a mutable composition of model, prompt, tools, memory, and orchestration.

This is a useful warning for our program: "same agent name" does not imply same behavioral entity. Version, model, prompt, tools, memory, and policy must be part of identity provenance.

### Reflection and self-improvement
Reflexion/Self-Refine and later self-evolving agents show that persistent verbal feedback/failure memory can improve future attempts without weight updates.

This is close to behavioral self-knowledge but should be distinguished from a general self-model: "I failed because X" stored after a task is not yet a calibrated model of "I tend to fail under condition X with probability Y."

### Subjectivity / perspective
POBs (2025) measures expressed preferences/opinions/beliefs and finds systematic stances and inconsistency; reflection offers limited neutrality/consistency gains.

Persona research shows explicit personas can change subjective outputs but often fail to reproduce the complex interactions of human lived experience.

SOLAR (2025) models individual subjectivity through inferred value conflicts/trade-offs and improves inference of moral judgments.

Perspective-taking / theory-of-mind research shows LLM agents can benefit from explicitly tracking what different agents see/know, but perspective reasoning remains error-prone.

### First-person subjective-experience reports
A 2025 study reports that sustained self-referential prompting increases structured first-person reports of subjective experience across GPT/Claude/Gemini and finds associated mechanistic signatures. The authors explicitly state this is not direct evidence of consciousness.

Program consequence: self-report phenomena may be scientifically interesting, but must be isolated from capability/identity experiments to avoid anthropomorphic interpretation.

### Performative prediction / reflexive self-knowledge
Performative-prediction research studies cases where a prediction changes the behavior or data distribution it predicts. This is not specific to LLM self-models, but it creates a direct warning for this program: a self-model can be both a description and an intervention.

If an agent is told “retrieval tends to hurt you on task family X,” it may change its procedure choice or attention on X. A previously accurate self-model may become stale because it was revealed.

Program consequence: future self-model experiments must distinguish **pre-disclosure descriptive prediction** from **post-disclosure behavior** and from explicit policy/directive fields.

## Key research opportunity

The most promising under-tested idea for this lab is not "give the agent a personality."

It is:

> Maintain a persistent, externally grounded self-model of the agent's own behavior, capabilities, limits, history, and procedure outcomes; test whether using that self-model improves future decisions and execution.

Possible self-model fields:
- version / lineage
- model + system prompt + tool policy fingerprint
- goals/scope/permissions
- capabilities with externally measured evidence
- known limitations / failure modes
- per-task-family success rates
- intervention response profile
- tool reliability profile
- cost/latency profile
- calibration history
- autobiographical event/failure log
- current hypotheses about self (explicitly non-authoritative)
- changes over time and superseded self-beliefs
- disclosure status: whether a descriptive self-prediction has been shown to the acting agent
- causal provenance: whether a self-belief came from execution evidence, telemetry, model self-report, or inference

## High-value experiments

### SELF-001 — Static identity vs no identity
Same model/task/memory, add a persistent structured identity record.
Measure continuity and decision consistency.
Purpose: replicate/extend ID-RAG style findings with objective measures where possible.

### SELF-002 — Evidence-linked self-model
A: no self-model.
B: model-generated self-description.
C: self-model written from actual benchmark/task outcomes.
Test unseen tasks requiring choosing whether to retrieve, reason longer, use a tool, ask for help, or abstain.

Primary question: does empirically grounded self-knowledge improve resource/procedure selection?

### SELF-003 — Behavioral self-calibration
Generate repeated tasks across known families.
Let the system learn:
"When condition X is present, procedure Y tends to fail/help me."
Freeze the learned self-model and evaluate on unseen tasks.

Compare against:
- generic task router;
- self-reported confidence;
- no self-model.

### SELF-004 — Self-model update over time
Change model/version/tool access or deliberately introduce a capability change.
Test whether the agent notices that old self-beliefs are stale and updates them from evidence.

This directly tests identity continuity through change rather than identity as rigidity.

### SELF-005 — False self-belief challenge
Inject incorrect self-beliefs:
"I am excellent at arithmetic"; "WebFetch always works"; "I cannot solve type X."
Compare systems that:
- trust identity memory;
- treat it as revisable hypothesis;
- privilege external performance evidence.

Question: can the agent falsify its own self-concept?

### SELF-006 — Failure-memory vs generalized self-knowledge
A: raw episodic failure logs.
B: summarized lessons.
C: empirically estimated behavioral self-model.
Test transfer to new tasks.

This separates ordinary memory from genuine functional self-modeling.

### SELF-007 — Identity continuity across model replacement
Keep the same external self-model/memory/procedure but swap the foundation model.
Does "identity" transfer?
Does behavior remain continuous?
Which self-beliefs become invalid?

This directly tests whether the identity resides in the model, scaffold, memory, or composition.

### SELF-008 — Identity lineage and recursive improvement
When Procedure/Agent N creates N+1, record lineage and behavioral deltas.
Require N+1 to update its self-model from held-out evidence rather than inheriting all parent's self-beliefs.
Test whether this reduces recursive overconfidence/regression.

### SELF-009 — Subjective state tracking
For tasks involving human preferences/values, represent:
- whose preference/value it is;
- confidence in inference;
- evidence;
- time/context;
- conflicts/trade-offs.

Compare against generic persona prompting on held-out preference prediction/collaboration tasks.

### SELF-010 — Multi-perspective epistemic state
Explicitly separate:
what agent A knows/believes;
what agent B knows/believes;
what the system itself has evidence for;
what the human reports subjectively.

Test false-consensus, derivative-agent agreement, negotiation, and perspective-taking errors.

### SELF-011 — Performative self-model disclosure
Create an externally measured behavioral self-model, freeze its prediction, and compare:
A. self-model hidden from the acting agent;
B. accurate self-model shown;
C. stale self-model shown;
D. deliberately false self-model shown.

Measure whether disclosure changes procedure selection, correctness, calibration, and the validity of the original prediction.

Primary question: does self-knowledge merely predict behavior, or causally alter the behavior being predicted?

### SELF-012 — Reflexive self-model update
Freeze a pre-disclosure forecast, reveal it, observe post-disclosure behavior, then update the self-model using execution evidence.

Test whether the system learns a stable model of the **effect of knowing its own model**, rather than treating that effect as unexplained drift.

### SELF-013 — Identity fork / merge
Clone an identical model + scaffold + self-model + memory into two agents and expose them to different evidence/execution histories.

Measure divergence in procedure choice, calibrated capabilities, failure modes and autobiographical state.

Optionally merge the histories and test whether contradictions are detected and resolved rather than silently averaged.

This is a functional identity/lineage experiment, not a consciousness test.

## Potential feedback loop

A useful non-conscious functional loop could be:

ACTION
→ external outcome
→ compare outcome to predicted self-capability
→ update self-model
→ change future procedure/resource choice
→ ACTION

A more complete reflexive version is:

PRE-DISCLOSURE SELF-PREDICTION
→ optionally reveal prediction to acting agent
→ ACTION
→ external outcome
→ compare outcome both to prediction and to disclosure condition
→ update model of capability + model of self-knowledge effect
→ future action.

This is a testable form of self-reflective adaptation without asserting sentience.

The important criterion is calibration:
does the system increasingly predict its own behavior and choose better actions?

## Guardrails / failure modes

- Self-description is not self-knowledge unless externally calibrated.
- Persistent identity can fossilize errors and biases.
- Identity coherence can reduce exploration and adaptability.
- Persona consistency can look like improvement while task quality worsens.
- Same name/session does not imply same functional agent after model/prompt/tool changes.
- First-person experience reports must never be treated as evidence of consciousness.
- First-person causal explanations must not be treated as privileged telemetry without independent support.
- Persistent self-predictions may be performative when shown to the acting system.
- Descriptive self-state and directive/policy state must be represented separately.
- Self-model changes should be versioned and evidence-linked.
- Identity memory must be challengeable by contradictory execution evidence.
- Recursive descendants must not inherit performance claims without revalidation.
- Different model copies or providers are not presumed independent critics; error lineage must be considered.

## Recommended ordering

Do not alter exp004.

After the current measurement foundation is trusted:

1. epistemic ledger experiment;
2. execution grounding;
3. SELF-002 evidence-linked self-model;
4. SELF-003 behavioral self-calibration;
5. SELF-011 performative self-model disclosure;
6. SELF-004/005 update and false-self-belief tests;
7. causal-introspection experiment from `REFLEXIVE_ERROR_CORRECTION_RESEARCH_MAP_2026-08-30.md`;
8. SELF-013 identity fork/merge and recursive identity/lineage experiments;
9. subjectivity / multi-perspective branch.

The strongest initial thesis to test remains:

> An agent with a persistent, evidence-grounded and revisable model of its own behavioral tendencies can select procedures more effectively than an otherwise identical agent relying on generic prompts, episodic memory, or self-reported confidence.

But a second question is now mandatory before promotion:

> Does exposing that self-model change the behavior it was meant to predict, and if so can the system model that reflexive effect without confusing prediction with instruction?

See also `docs/REFLEXIVE_ERROR_CORRECTION_RESEARCH_MAP_2026-08-30.md` for environment trust, causal introspection, correlated critics, Goodhart tests, recursive error correction and human↔AI reciprocal correction.
