# Experimental Program and Branching Order — 2026-08-29

Status: program-level roadmap. Not a preregistration. Does not alter frozen experiments.

## Governing principle

Sequence experiments by **dependency of interpretation**, not by novelty.

A later experiment should only be run when its result can be interpreted using earlier validated components. Interesting results trigger replication, ablation, adversarial alternatives, and transfer testing — never immediate promotion to "verified."

Every positive result should be treated as potentially explained by:
- measurement artifact;
- task-selection artifact;
- evaluator bias;
- model-specific quirk;
- prompt/context length;
- cost/latency differences;
- hidden intervention mismatch;
- regression-to-the-mean / selection effects;
- benchmark overfitting;
- uncontrolled provenance or leakage.

## Promotion ladder for any result

1. **Signal** — one experiment shows an effect.
2. **Replicated** — same design / fresh samples reproduces it.
3. **Mechanistically narrowed** — ablations and alternative explanations reduce plausible confounds.
4. **Transferred** — effect survives new items/tasks/models or environments.
5. **Execution-valid** — effect improves externally checked real work.
6. **Operational candidate** — may enter a champion procedure.
7. **General claim** — only after multiple domains/conditions support it.

Do not skip levels.

---

# Phase A — Finish the measurement foundation

## A0 — Current Stage-0 work
Finish the already-authorized exp004 statistical/preflight work.

Purpose:
- establish trustworthy inferential machinery;
- validate replicate assumptions;
- freeze selection/grading rules;
- determine n/R/power;
- prove or empirically bound critical-value behavior.

No other research branch may modify exp004.

### Branch
- If measurement remains invalid: stay here.
- If valid: proceed to intervention science.

---

# Phase B — Single-intervention science

Goal: establish whether individual procedures help, hurt, or have heterogeneous effects.

## B1 — Retrieval heterogeneity
Current first target.

Question:
Are there tasks where retrieval helps and others where it hurts enough to create exploitable policy value?

## B2 — Test-time compute / reasoning allocation
Matched-cost comparison:
- direct;
- more reasoning;
- more independent samples;
- verification;
- repair/retry.

## B3 — Context allocation
Compare:
- minimal relevant context;
- larger retrieved context;
- full-history context;
- structured compressed context later.

## B4 — Verification
Test where verification helps/hurts rather than treating it as universally beneficial.

### Rule
Do not combine interventions yet unless a single component either:
- shows a reliable effect;
- shows reliable harm;
- or creates a clearly interpretable interaction hypothesis.

---

# Phase C — Minimal world-epistemology

Run before self-modeling because a self-model itself needs an epistemic substrate if it is to be evidence-grounded rather than persona text.

## C1 — Equal-evidence representation test
A: ordinary RAG/context.
B: same evidence converted to explicit claim/provenance records.

Hold constant:
- model;
- evidence;
- retrieval budget;
- answer task.

Measure:
- correctness;
- stale-claim persistence;
- contradiction handling;
- unsupported inference;
- context/token cost.

## C2 — Temporal validity
Add:
- valid time;
- observed time;
- supersession.

Test changing facts and corrected information.

## C3 — Origin typing
Persist explicit origin:
OBSERVATION / SOURCE CLAIM / INFERENCE / MODEL HYPOTHESIS / EXECUTION RESULT.

Test whether this prevents hypotheses/summaries from fossilizing into facts.

## C4 — Dependency revision
Add dependency edges and cascading invalidation.
Deliberately falsify upstream premises.

## C5 — Evidence-lineage independence
Compare raw citation count vs lineage-aware support.

## C6 — Active epistemic routing
Allocate a fixed investigation budget to the weak/load-bearing premise rather than generic search.

### Branching discipline
At every step compare against the immediately simpler champion.

If C1 adds nothing, do not assume C2–C6 need the ledger.
If temporal validity explains the effect, keep temporal validity and ablate unnecessary graph complexity.
If a simple table/SQLite record performs as well as a graph representation, prefer the simpler implementation.

---

# Phase D — Execution grounding

This begins as soon as the measurement layer is trustworthy; it can overlap with later Phase C work.

Preferred first domain: coding.

## D1 — Objective execution baseline
Compare model-alone with the best validated procedure on real repository tasks.

External criteria:
- build;
- tests;
- runtime behavior;
- regression rate;
- repair cycles;
- human intervention;
- token/tool cost;
- latency.

## D2 — Execution-fed epistemology
Treat compiler/test/tool outcomes as privileged observations.
Test whether automatic belief revision improves repair loops.

## D3 — Novel-task execution
Use tasks authored or selected after the procedure is frozen.

Purpose: distinguish benchmark optimization from useful capability.

---

# Phase E — Persistent functional self-model

Run after at least some world-state and execution measurements exist, so "self-knowledge" can be grounded in evidence.

## E1 — No self-model vs generated self-description vs evidence-linked self-model
Conditions:
A. no persistent self-model;
B. model-written self-description;
C. externally generated self-model from actual outcomes.

Test procedure selection on unseen tasks.

This is the key first self-model experiment.

## E2 — Behavioral self-calibration
Learn:
"When task condition X occurs, procedure Y tends to help/hurt me."

Compare against:
- generic task router;
- self-reported confidence;
- episodic memory;
- no self-model.

## E3 — False self-belief challenge
Inject incorrect capability beliefs.
Test whether execution evidence overturns identity memory.

## E4 — Self-model update after capability change
Change model/tool access/prompt policy.
Test whether the agent detects stale self-beliefs.

## E5 — Failure memory vs generalized self-knowledge
Compare:
- raw episodes;
- summarized lessons;
- calibrated behavioral self-model.

## E6 — Identity continuity across model replacement
Hold scaffold/memory/goals constant while swapping foundation model.

Measure functional continuity, not consciousness.

---

# Phase F — Subjectivity and multi-perspective epistemology

Keep separate from objective world-state claims.

## F1 — Subject-relative claims
Represent explicitly:
- whose preference/experience/value;
- evidence;
- context/time;
- confidence;
- conflicts/trade-offs.

Compare with ordinary persona prompting.

## F2 — Multi-agent perspective state
Track separately:
- what agent A observed;
- what agent B inferred;
- what the system itself supports;
- what the human reports subjectively.

Test:
- false consensus;
- derivative-agent agreement;
- theory-of-mind/perspective mistakes;
- negotiation/collaboration.

## F3 — Human preference execution
Use real interaction outcomes where feasible rather than judge-only preference scores.

---

# Phase G — Interaction experiments

Only after individual components have earned inclusion.

Use factorial/ablation designs instead of giant "everything on" comparisons.

## High-priority combinations

### G1 — Epistemic ledger × retrieval
Does explicit state improve when/what to retrieve?

### G2 — Epistemic ledger × execution
Does execution evidence + belief revision outperform execution feedback in prose?

### G3 — Self-model × task router
Does behavioral self-knowledge add predictive value beyond task features?

### G4 — Self-model × epistemic ledger
Can the same evidence rules govern beliefs about the world and beliefs about self?

### G5 — Self-model × execution
Does calibrated knowledge of one's own failure modes improve recovery/tool choice?

### G6 — Subjectivity × epistemic ledger
Does subject-relative typing prevent objective/subjective category errors?

### G7 — Epistemic compression × context size
Can minimal dependency-grounded state beat context maximization at matched quality/cost?

### G8 — Multiple agents × provenance independence
Does lineage-aware identity prevent derivative agents from creating false consensus?

## Combination rule

For k components, do not start with a 2^k full factorial unless power/cost justify it.

Preferred progression:
single effects → plausible pairwise interactions → targeted triples → champion architecture.

---

# Phase H — Generalization

Any component/procedure that survives earlier phases must be frozen and tested on:
- fresh item sets;
- later-authored tasks;
- different task families;
- at least one different model when relevant;
- real execution tasks.

Classify failures:
- model-specific;
- task-specific;
- environment-specific;
- evaluator-specific;
- general.

A result that does not transfer remains a local procedure, not a general principle.

---

# Phase I — Automated procedure discovery

Only now authorize automatic search.

## I1 — Candidate generation
AI researcher receives:
- frozen champion;
- prior experimental results;
- failure taxonomy;
- allowed operations.

It proposes alternatives.

## I2 — Champion protocol
Candidate must beat champion on discovery data, then survive validation and holdout before promotion.

## I3 — Diversity protection
Maintain multiple candidate families.
Do not allow one early strategy family to dominate search merely because it exploits evaluator quirks.

## I4 — Failure-memory hygiene
Store rejected hypotheses and failure evidence, but do not inject the entire failure archive into every candidate-generation context.

---

# Phase J — Recursive procedure improvement

Loop:
champion N → candidate generation → controlled evaluation → red-team → holdout execution → champion N+1 or reject.

Track:
- ancestry/lineage;
- changed components;
- evidence supporting promotion;
- regressions;
- transfer performance.

Descendants do not inherit capability claims without revalidation.

---

# Phase K — Model-agnostic runtime

Only after evidence supports the preceding layers.

Potential controller inputs:
- task features;
- world epistemic state;
- self-model state;
- human/subjective state;
- environment/tool state;
- cost/latency constraints.

Potential actions:
- answer;
- retrieve;
- verify;
- reason more;
- sample alternatives;
- execute;
- revise;
- ask;
- defer;
- switch model;
- stop.

The runtime should be the consequence of experimentally earned components, not a preconceived architecture.

---

# Cross-cutting experimental matrix

Every promising component should eventually be tested along these axes where relevant:

- model family;
- task family;
- difficulty;
- deterministic vs judged evaluation;
- context size;
- evidence freshness;
- cost;
- latency;
- tool availability;
- execution environment;
- single vs multi-agent;
- familiar vs held-out tasks.

Do not attempt all axes in the discovery experiment. Use them for staged transfer testing.

---

# Alternative-explanation protocol

For every interesting positive result, before architecture promotion ask:

1. Could output length explain it?
2. Could evaluator/grading route explain it?
3. Could selection/screening explain it?
4. Could extra tokens/tool calls explain it?
5. Could prompt wording or added instructions explain it?
6. Could task leakage/familiarity explain it?
7. Could one or two load-bearing items explain it?
8. Could the effect disappear under equal cost?
9. Could the effect be model-specific?
10. Could a simpler component reproduce it?

At least the most plausible alternatives must be tested before calling a mechanism established.

---

# Highest-value near-term queue after exp004

1. Finish exp004 measurement/retrieval work.
2. Begin objective coding execution baseline.
3. C1 equal-evidence epistemic-ledger experiment.
4. C2 temporal validity.
5. D2 execution-fed epistemology.
6. E1 evidence-linked self-model.
7. E2 behavioral self-calibration.
8. C6 active epistemic routing.
9. Pairwise interaction tests among the surviving components.
10. Generalization.
11. Automated procedure discovery.
12. Recursive improvement.

Why this order:
- execution starts early so research remains tied to usefulness;
- epistemology precedes self-modeling so self-beliefs can be evidence-grounded;
- self-modeling precedes recursive search so the optimizer can potentially learn its own behavioral limits;
- combinations are delayed until component effects are interpretable;
- recursive improvement is last because it amplifies both genuine improvements and measurement mistakes.
