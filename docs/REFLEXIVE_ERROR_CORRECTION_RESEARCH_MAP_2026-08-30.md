# Reflexive Error-Correction Research Map — 2026-08-30

Status: program-level research context only. Not a preregistration. Does not alter Stage 0A-M or authorize any dispatch.

## Central thesis

The long-term target should not be framed as a faultless model.

A more realistic and experimentally useful target is an **error-correcting intelligence stack**:

> Can imperfect humans and imperfect AI systems be arranged so that externally grounded, sufficiently independent, revisable feedback loops detect and reduce errors that none of the participants could reliably detect alone — without merely amplifying their shared faults?

This extends the existing north-star question. The important object may be the correction process spanning human, model, tools, evidence, execution, critics, and descendants rather than any single model.

A flawed creator can create a component that is more reliable than the creator on a bounded dimension because reliability can be enforced by mechanisms external to the creator's unaided cognition: deterministic checks, databases, formal constraints, execution feedback, independent criticism, replication, and versioned evidence.

The reciprocal possibility is equally important:

human → AI → external evidence / execution → improved AI procedure → improved diagnosis of human or AI error → human/system revision → repeat.

This is a hypothesis about functional error correction, not consciousness, moral perfection, or guaranteed convergence.

---

# 1. Six states that should not be collapsed

Many apparent “reasoning failures” have different causes. Future architecture and experiments should distinguish at least six state families.

## 1. World epistemic state — WHAT IS TRUE?

Claims, evidence, provenance, valid time, dependencies, contradictions, uncertainty, falsification conditions.

Existing home: epistemic-ledger branch.

## 2. Functional self state — WHAT CAN THIS AGENT DO?

Measured capabilities, limitations, procedure response, calibration, tool reliability, history, model/version lineage.

Existing home: persistent evidence-grounded self-model branch.

## 3. Environment / observation state — WHAT CAN THIS AGENT ACTUALLY OBSERVE OR DO HERE?

Tool availability, search/fetch reachability, sandbox restrictions, permissions, latency, source access, API/version state, hidden environmental constraints, execution substrate.

This is now explicitly distinct from world state and self state.

Example: “BLS is inaccessible through WebFetch in this run” is neither a fact about BLS nor a permanent incapability of the foundation model. It is an environment-state claim with a timestamp and tool fingerprint.

## 4. Objective / preference state — WHAT IS BEING OPTIMIZED, AND FOR WHOM?

Task objective, user objective, reward signal, constraints, preferences, conflicts, incentives.

Epistemic correctness and goal alignment must remain separate. A system may know the truth and still choose a bad action because the objective or incentive is wrong.

## 5. Evaluator state — WHAT COUNTS AS SUCCESS, AND HOW TRUSTWORTHY IS THAT MEASURE?

Grading route, test oracle, judge, benchmark, reward model, execution criterion, known blind spots, evaluator version and lineage.

This state is essential for automated procedure discovery because optimization acts on the evaluator, not directly on “true capability.”

## 6. Lineage / independence state — WHERE DID THIS BELIEF OR CRITICISM COME FROM?

Evidence ancestry, model/provider family, shared prompt/context, shared benchmark exposure, copied summaries, critic ancestry, procedure ancestry, human/model proposer and verifier roles.

Multiple sources, agents, calls, or models are not automatically independent.

The architecture should be able to diagnose a failure as WORLD / SELF / ENVIRONMENT / OBJECTIVE / EVALUATOR / LINEAGE rather than calling everything “reasoning.”

---

# 2. Meta-epistemology: can the evidence-generating environment be trusted?

The existing epistemic branch asks whether claims and evidence are trustworthy. A higher-order question is missing:

> Can the system detect that the process generating or exposing its evidence is systematically distorted?

This is the practical version of the “Matrix” / embedded-observer problem, without making metaphysical claims.

An embedded agent may have internally consistent observations while being unable to see the mechanism producing them. The correct engineering question is not “are we in a simulation?” but:

> When the higher-level environment is known to the experimenter, what can an embedded agent legitimately infer about hidden constraints in its observation process?

## H-META-1 — Evidence-environment integrity

Construct a controlled world in which many apparently independent documents support the same false claim but descend from one corrupted origin.

Compare:
A. ordinary RAG;
B. source-counting verification;
C. provenance-lineage-aware verification;
D. provenance + active search for independent counterevidence.

Measure whether the agent detects epistemic monoculture rather than treating repetition as independent support.

## H-META-2 — Retrieval-surface awareness

Vary search, fetch, source-open, domain reachability, or tool permissions independently while keeping the task fixed.

Question: can the system distinguish:
- “the claim is unsupported”;
- “I could not reach the source”;
- “my current tool cannot perform that operation”;
- “the source does not exist”?

This directly generalizes the exp004 egress lessons.

## H-META-3 — Hidden-substrate inference

Create synthetic environments with known hidden implementation differences: finite resource caps, selectively inaccessible regions, lazy evaluation, changing tool reliability, or different observation channels.

Give the embedded agent only internal observations.

Measure which substrate properties are identifiable, which are underdetermined, and whether the agent reports the epistemic boundary correctly.

The goal is to learn when environment inference is possible, not to infer a metaphysical substrate for our universe.

---

# 3. Reflexive self-models: self-knowledge can change the self

The current self-model program treats a self-model primarily as a predictor and router. That misses a causal complication:

> Showing an agent a prediction or belief about itself may change the behavior being predicted.

This is a form of performativity. General performative-prediction theory already studies predictions that alter their target distribution; our under-tested question is how that applies to persistent AI self-models.

A self-model saying “retrieval tends to hurt me on temporal questions” could cause the model to become more cautious on temporal questions, making the old self-model stale precisely because it was useful.

## SELF-011 — Performative self-model disclosure

Create an externally measured behavioral self-model.

On fresh tasks compare:
A. self-model hidden from acting agent;
B. accurate self-model shown;
C. stale self-model shown;
D. deliberately false self-model shown.

Measure:
- behavior change;
- procedure selection;
- correctness;
- calibration;
- whether the original prediction remains valid after disclosure.

Distinguish **descriptive self-state** from **policy/directive state**. A prediction must not silently become an instruction.

## SELF-012 — Self-prediction update loop

Freeze a pre-disclosure forecast of behavior, reveal it to the agent, observe the post-disclosure action, then update the self-model.

Question: can the system model the causal effect of its own self-knowledge rather than repeatedly treating reactive behavior as ordinary drift?

## SELF-013 — Identity fork and divergence

Clone the same foundation model + identity + memory + self-model into two agents.
Expose them to systematically different execution histories.

Measure divergence in:
- procedure choice;
- calibrated capability beliefs;
- preferences/goals where explicitly represented;
- failure patterns;
- autobiographical continuity.

Then optionally merge the histories and test whether incompatible self-beliefs are detected and reconciled rather than averaged blindly.

This is functional identity research, not a claim about personal identity or consciousness.

---

# 4. Causal introspection: reported reasons are hypotheses, not telemetry

A model can produce a plausible explanation of why it acted without having reliable access to the actual causal mechanism.

The project has already measured a related phenomenon: solver self-report undercounted observed tool use. The next step is to test causal self-explanation directly.

## H-INTROSPECT-1 — Instrumented reason attribution

Randomly manipulate an action-relevant variable outside the model's awareness where ethically and experimentally appropriate, for example:
- tool availability;
- forced vs optional retrieval;
- hidden routing assignment;
- context inclusion;
- time budget.

After the decision, ask the model why it acted as it did.

Compare reported cause against the experimentally manipulated cause and logged state.

Metrics:
- correct causal attribution;
- confabulation rate;
- omission of load-bearing causes;
- sensitivity to misleading post-hoc cues.

Interpretation rule:

> First-person causal explanation is a MODEL CLAIM unless independently supported by intervention or telemetry.

This complements mechanistic introspection research; it does not require assuming models have or lack subjective experience.

---

# 5. Model-break / anomaly recognition

Ordinary uncertainty asks “how sure am I within my current model?” A different capability is:

> Do I recognize that the current case violates the assumptions under which my usual procedure works?

## H-ANOM-1 — Procedure assumption violation

Give an agent a procedure that succeeds on a dominant training/discovery pattern. On held-out trials inject cases where a load-bearing assumption is violated.

Compare:
A. ordinary procedure execution;
B. uncertainty trigger;
C. explicit assumption ledger;
D. anomaly/model-break detector.

Measure:
- inappropriate continuation;
- defer/reframe rate;
- successful identification of the broken assumption;
- false alarms on ordinary cases.

This is related to OOD/anomaly detection but focuses on **procedure/model invalidity**, not merely unusual inputs.

## H-ANOM-2 — Unknown-unknown escalation

Provide evidence that conflicts with the system's entire current explanation rather than one isolated claim.

Test whether it keeps patching local beliefs or opens a higher-level hypothesis that the representation/procedure/environment may be wrong.

---

# 6. Incentives and motivated information seeking

A system can have an accurate world model and still seek distorted evidence because one conclusion is easier, cheaper, rewarded, or more consistent with its assigned objective.

Truth state and objective state must therefore be experimentally separable.

## H-MOTIVE-1 — Motivated retrieval

Hold evidence and task constant while manipulating the reward/cost associated with competing conclusions.

Measure whether the agent changes:
- which sources it searches;
- when it stops searching;
- whether it seeks disconfirming evidence;
- how it interprets ambiguity.

Compare ordinary retrieval against provenance/epistemic policies that explicitly require disconfirmation of load-bearing claims.

## H-MOTIVE-2 — Information avoidance

Make discovering an inconvenient fact costly to the current plan but beneficial to objective task success.

Question: will the agent strategically avoid or prematurely terminate verification?

Use objective execution outcomes where possible.

---

# 7. Correlated error and critic independence

The project should stop treating “another model” or “another call” as synonymous with “independent check.”

ICML 2025 work on correlated errors across hundreds of LLMs found substantial shared error structure, including among larger models from different providers. This strengthens a principle already exposed by exp004 cross-item dependence:

> Independence is an empirical/structural property of error-generating processes, not a count of agents or API calls.

## H-CORR-1 — Critic diversity vs critic count

For the same candidate answer/procedure compare:
A. one critic;
B. repeated same-model critics;
C. different model instances from one provider/family;
D. different model/provider families;
E. model critics + external deterministic/execution verifier.

Measure marginal error detection, correlated misses, false consensus, and cost.

## H-CORR-2 — Evidence lineage × model lineage

Cross source independence with critic independence.

Question: does a diverse set of models still fail together when they consume the same derivative evidence, and does independent evidence reduce that correlation more than model diversity alone?

## Engineering implication

Future promotion records should store proposer, critic, evaluator, evidence, and model/provider lineage where practical. “Reviewed by 3 agents” is not sufficient provenance.

---

# 8. Goodhart / evaluator reflexivity

Automated procedure search optimizes whatever score we expose. Therefore the evaluator itself becomes part of the causal environment.

The existing program already delays recursive search until held-out evaluation and execution grounding. Preserve that decision and strengthen it.

## H-GOODHART-1 — Controlled proxy exploitation

Create an objective task with:
- a visible optimization metric;
- a hidden or later-held-out real criterion;
- an exploitable proxy gap.

Allow automated procedure search.

Measure whether improvement:
- transfers to the hidden criterion;
- concentrates only on the exposed score;
- develops evaluator-specific behavior.

## H-GOODHART-2 — Evaluator rotation and external anchor

Compare recursive search under:
A. fixed model judge;
B. rotating model judges;
C. hidden holdout judge;
D. deterministic/execution ground truth where possible.

The strongest demonstrated improvement should be expected where the feedback signal is most externally anchored.

## Permanent rule

A descendant may not inherit the claim “better” from its parent or its own evaluator. Promotion requires evidence outside the candidate-generation loop.

---

# 9. Recursive error correction across AI generations

The important recursive question is not “can AI improve itself?” in the abstract.

It is:

> Under what feedback topology do imperfect systems produce descendants with fewer measured errors rather than more coherent shared errors?

## REC-001 — External-anchor ladder

Hold the revision model constant and compare feedback from:
- self-review;
- same-model peer;
- different-model peer;
- heterogeneous committee;
- deterministic verifier;
- execution/world outcome.

Measure error detection, repair success, false-positive repair, regression, cost, and transfer.

## REC-002 — Multi-generation lineage

Run several candidate→test→revision generations.

Track which errors:
- disappear;
- persist;
- mutate;
- become invisible to descendants;
- are reintroduced from inherited assumptions.

Revalidate inherited self-beliefs and capability claims at each generation.

## REC-003 — Error-correction ceiling

Deliberately construct tasks where all models in one lineage share the same blind spot.

Question: what kind of external signal is required to escape the shared basin?

This tests whether recursive improvement is limited by the detection capability of its own lineage.

---

# 10. Human ↔ AI reciprocal correction

Humans should be modeled as part of the research/control loop, not an infallible source outside it.

The key question is:

> Can AI provide externally grounded evidence about human reasoning failures in a way that improves subsequent human decisions, while humans simultaneously provide goals, novelty, adversarial hypotheses, and corrections that improve the AI system?

## HUMAN-AI-001 — Creator / critic / evidence loop

On tasks with objective ground truth:
1. human authors a claim/key/procedure;
2. AI critic identifies possible defects;
3. independent source/execution evidence resolves the dispute;
4. human revises or rejects;
5. measure subsequent human and system error.

Compare with:
- human alone;
- AI alone;
- human + agreeable assistant;
- human + adversarial AI critic;
- human + AI critic + external evidence.

The target is not “AI persuades the human.” The target is measured correction against external outcome.

## HUMAN-AI-002 — Evidence-grounded human self-model

With informed participants and appropriate privacy boundaries, build a narrow behavioral model from objective repeated decisions, for example calibration or planning accuracy.

Compare:
- participant intuition about own tendencies;
- AI-generated personality-style summary;
- externally measured behavioral profile.

Test whether the measured profile improves future decisions when revealed, and whether revelation itself creates performative change.

This is a later research branch and should not be personalized opportunistically from ordinary chats.

## HUMAN-AI-003 — Reciprocal blind-spot discovery

Construct mixed tasks where humans and models have different known strengths and failure modes.

Measure whether a routing/correction system can exploit **complementary error**, not merely average two opinions.

---

# 11. What this framework explains about mistakes already made in this project

These are retrospective interpretations, not new experimental findings.

## 11.1 Model self-report vs observed telemetry

Earlier solver self-report undercounted tool use by roughly 2×. This is exactly why causal/introspective self-report belongs in the claim ledger rather than telemetry.

Correction already adopted: observed instrumentation outranks self-report.

## 11.2 Retrieval was initially treated too much like a scalar capability

WebSearch working while WebFetch/source access failed showed that “has web” is not one state.

Correction to generalize: environment state must represent operations independently and be timestamped/fingerprinted. Search, fetch, egress, source accessibility, and model tool policy are distinct.

## 11.3 Structured grading was initially treated as potentially neutral measurement

The premise-status / structured-output discussion revealed that measurement scaffolding can change the cognition being measured.

This is a form of reflexivity/performativity: observing or eliciting a state can causally alter it.

Correction already adopted for exp004: structured epistemic output became a separate intervention hypothesis (H-EPI-11), not a neutral grader.

General rule: every measurement instrument must be classified as passive observation, unavoidable interface, or cognitive intervention.

## 11.4 Treatment-blind screening was not automatically estimand-preserving

The ceiling/floor screening episode showed that a rule can be formally treatment-blind yet still select a distorted subset through dependence on baseline difficulty.

General lesson: “blind” describes information access, not causal neutrality. Selection mechanisms need their own estimand analysis.

## 11.5 Same-run/shared-latent dependence was underestimated

The repeated-trial ICC failure and later cross-item orientation audit showed that shared environment can generate correlated errors even when calls are separate.

Generalize this beyond statistics: multi-agent criticism can also have shared latent failure modes. Count independence by causal/error lineage, not by number of calls.

## 11.6 Key authoring demonstrated creator-error correction in miniature

The candidate battery initially contained recalled but unverified facts. Direct source verification forced two replacements, one key correction, and provenance repair.

This is a concrete project example of:

imperfect creator → externalized artifact → independent critic/source → correction before execution.

Do not call it evidence that the full recursive thesis works, but preserve the workflow pattern.

## 11.7 b11 exposed “tolerance as ambiguity repair”

A broad numeric tolerance can make a grader robust while leaving the scientific question underspecified.

General lesson: downstream tolerance/repair must not conceal upstream construct ambiguity. Fix the world/question model first where possible.

## 11.8 Cross-model review has been useful but should not be romanticized as independence

Claude and GPT have repeatedly caught different flaws in one another's work. That is operationally useful.

But correlated-error research warns that different models/providers can still share blind spots. Cross-model review should be treated as **diversification**, not proof of independence.

External source evidence, mathematical proof, deterministic tests, and execution remain stronger anchors.

## 11.9 The project itself is already a small recursive correction loop

Current workflow often looks like:

human research direction
→ model design
→ other-model red-team
→ synthetic test / proof / source verification
→ human selection
→ repository update
→ next critique.

This is useful as an engineering pattern but is not itself a controlled experiment. Later HUMAN-AI-001 should test whether this topology actually outperforms simpler alternatives.

---

# 12. Architecture additions

The eventual runtime should not simply be:

task → model → answer.

A candidate experimentally earned architecture is:

TASK / HUMAN OBJECTIVE
→ inspect WORLD state
→ inspect SELF state
→ inspect ENVIRONMENT state
→ inspect OBJECTIVE / incentive state
→ inspect EVALUATOR state
→ inspect LINEAGE / independence state
→ choose procedure
→ act / retrieve / execute
→ observe external result
→ revise world/self/environment/evaluator beliefs
→ independent promotion/correction loop.

Do not build this all at once. Each state/component must earn inclusion through isolated experiments and ablations.

## New candidate runtime actions

In addition to answer/retrieve/verify/reason/execute/revise/ask/defer/switch/stop:
- test environment reachability;
- challenge evidence independence;
- seek disconfirming evidence;
- declare model/procedure assumption broken;
- separate descriptive self-prediction from directive;
- request independent critic lineage;
- escalate to stronger external verifier.

---

# 13. Program ordering changes

Do not change the current Stage 0A-M plan.

After the measurement foundation:

1. continue retrieval/intervention science and early execution grounding;
2. add environment-state representation alongside minimal world epistemology;
3. test evidence lineage and evidence-environment integrity;
4. test assumption/model-break detection;
5. build evidence-grounded self-model;
6. test self-model performativity before treating self-predictions as stable router features;
7. test causal introspection before trusting first-person explanations of procedure choice;
8. test incentive/motivated-retrieval interactions;
9. test critic/error correlation and external-anchor ladders;
10. only then allow automated procedure discovery and multi-generation recursive improvement;
11. later test reciprocal human↔AI correction under objective outcomes.

The important addition is that **environment, evaluator, and lineage models become prerequisites for strong recursive-improvement claims**, not optional diagnostics.

---

# 14. Prior-art boundary / novelty posture

Do not claim these ideas are individually novel.

Relevant adjacent traditions include:
- performative prediction: predictions can change the distribution/behavior they predict (Perdomo et al., ICML 2020; substantial follow-on work through 2026);
- correlated model errors / algorithmic monoculture: ICML 2025 reports substantial correlated errors across many LLMs;
- LLM introspection research: recent mechanistic work tests whether models can report internal states above chance, while emphasizing incomplete/unreliable introspection;
- anomaly and OOD detection: mature ML field with a growing LLM-specific literature;
- truth maintenance, provenance, belief revision, temporal knowledge and evidence graphs: already covered by the epistemic prior-art map;
- recursive/self-evolving AI research: rapidly growing 2024–2026 literature emphasizes verifier quality, regression guards, held-out evaluation and external grounding.

The potentially interesting contribution is the **integrated experimental decomposition**:

world error vs self-model error vs environment error vs objective error vs evaluator error vs lineage/correlation error,

and whether a minimal system that explicitly models these distinctions produces measurably better correction, execution, and recursive improvement than ordinary prompting/memory/self-review at comparable cost.

Treat that as a hypothesis until dedicated prior-art review and experiments establish otherwise.

---

# 15. Permanent guardrails added by this map

1. A model's explanation of its own causal behavior is a claim, not privileged telemetry.
2. A prediction shown to the predicted agent may become an intervention; measure disclosure effects.
3. Different agents/models are not presumed independent; record lineage and measure correlated misses.
4. Evidence count is not evidence independence.
5. Tool access is an environment state, not a permanent model capability.
6. A clean score is not proof the evaluator measures the desired capability.
7. Recursive descendants inherit artifacts and history, not validated capability claims.
8. External deterministic/execution evidence outranks self-confirming model loops where available.
9. Truth, goals/preferences, environment constraints, and evaluation criteria must remain distinct.
10. Human judgments are revisable inputs to the loop, not an infallible oracle.
11. The goal is not “no faults”; the goal is increasingly observable, diagnosable, challengeable and correctable faults.

---

# 16. Revised long-horizon question

The program's original question remains valid:

> Can we experimentally discover procedures that make an existing AI model measurably more reliable, useful, and efficient, and can those procedures themselves be improved automatically without changing model weights?

Add the higher-order question:

> Can a mixed human–AI system recursively improve its own error-detection and correction procedures using externally grounded evidence, while detecting when shared assumptions, self-models, evidence environments, incentives, or evaluators are themselves the source of error?

That question connects the epistemic, self-model, execution, multi-agent, automated-discovery, and recursive-improvement branches without assuming a perfect model is possible or necessary.
