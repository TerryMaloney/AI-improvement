# Epistemic Systems Prior-Art Map — 2026-08-29

Status: research context only. Not a novelty claim, not a preregistration, and does not alter frozen experiments.

## Research question

Can an explicit epistemic state around an LLM — claims, provenance, temporal validity, contradiction/dependency structure, uncertainty, and revision rules — improve reliability or execution beyond ordinary prompt context / RAG / memory?

## Existing traditions we should not reinvent

### 1. Truth Maintenance Systems (TMS / ATMS)
Classical symbolic AI already formalized justification-based belief maintenance and cascading retraction when assumptions fail.

Lesson for this project: dependency-aware invalidation is old and useful. The new question is whether it improves LLM-agent reliability in realistic workflows.

### 2. AGM belief revision / non-monotonic reasoning
AGM formalizes rational belief revision/contraction. Recent 2025–2026 work continues to connect AGM-style semantics with machine learning and versioned agent memory.

Lesson: do not invent ad hoc contradiction-resolution rules if a known belief-revision formalism can provide invariants.

### 3. Epistemic / dynamic epistemic logic
Formal systems represent what agents know/believe and how information updates those states.

Lesson: useful for multi-agent knowledge-state reasoning, but likely too heavy as the first implementation. Treat as a source of formal properties, not necessarily the storage format.

### 4. Temporal knowledge graphs and agent memory
Recent systems such as Zep/Graphiti and temporal-KG reasoning agents explicitly preserve time-evolving relations instead of treating memory as static chunks. Published work reports meaningful gains on temporal/long-term memory tasks.

Lesson: valid-time and historical state should be explicit if the system stores facts.

### 5. Claim verification + evidence graphs
Recent claim-verification systems decompose claims, resolve entities, retrieve graph/text evidence, and verify structured subclaims.

Lesson: claim decomposition + provenance is established prior art; our experiment should ask what extra benefit comes from persistent state, revision, dependencies, or active control.

### 6. Evidence tracing / execution provenance
2026 survey work frames agent trust in terms of links between retrieved evidence, intermediate claims, memory, tool outputs, actions, and final answers.

Lesson: provenance should include execution observations, not only documents/citations.

### 7. Uncertainty-aware retrieval / calibration
Recent work uses uncertainty estimates to choose retrieval or data acquisition and reports gains in retrieval/QA settings.

Lesson: uncertainty can be a routing signal, but self-confidence must not be treated as truth. Calibrate it against outcomes.

### 8. Long-term memory benchmarks
LongMemEval / LongMemEval-V2 test knowledge updates, temporal reasoning, workflow knowledge, environment gotchas, and premise awareness. Memory systems increasingly beat naive full-context approaches.

Lesson: more context is not automatically better; structured memory can outperform context stuffing while using fewer tokens.

### 9. Self-evolving memory/procedure search
2026 work such as EvolveMem uses failure logs and guarded optimization loops to change retrieval configurations automatically, with rollback on regression and transfer tests across benchmarks.

Lesson: recursive procedure improvement is not hypothetical prior art anymore. Our differentiation must come from stronger measurement validity, negative-effect detection, execution grounding, or a broader epistemic/control action space.

## Recent design signals

- Structured/temporal memory can improve temporal and cross-session reasoning relative to naive full-context approaches.
- Knowledge-graph + web-search hybrids can improve claim verification and interpretability.
- Simple interpretable verification components can sometimes outperform heavier LLM-centric verification pipelines.
- Memory/update benchmarks repeatedly show that stale/corrected information is a distinct capability, not ordinary retrieval.
- Agent provenance is emerging as its own research area because final-answer accuracy cannot explain whether evidence/tool use was justified.
- Recursive optimization must have regression guards and held-out transfer tests or it risks benchmark overfitting.

## Underexplored combinations worth testing

These are hypotheses, not novelty claims.

### H-EPI-1 — Evidence-backed belief state vs equal-evidence RAG
Hold model, evidence, retrieval budget, and answer prompt constant.
A: ordinary retrieved context.
B: same evidence normalized into explicit claims + provenance + temporal validity + status.
Question: does representation alone improve contradiction/staleness/multi-hop reliability?

### H-EPI-2 — Dependency-aware cascading invalidation
Add explicit dependency edges between claims/inferences.
Change/falsify an upstream premise mid-task.
Question: does automatic downstream invalidation reduce stale conclusions and unnecessary re-reasoning compared with ordinary memory?

### H-EPI-3 — Observation > inference > model-output typing
Force every persisted item to carry epistemic origin:
OBSERVATION / SOURCE CLAIM / INFERENCE / MODEL HYPOTHESIS / EXECUTION RESULT.
Question: does preventing model-generated hypotheses from silently becoming facts improve later execution accuracy?

### H-EPI-4 — Temporal + provenance + revision together
Temporal graphs exist; provenance systems exist; AGM-style revision exists. Test the combined minimal ledger against temporal memory alone.

### H-EPI-5 — Active epistemic control
Route tool budget based on the dependency graph:
verify the weak premise whose resolution has highest expected effect on downstream conclusions.
Compare against generic uncertainty-based search and always-search.

### H-EPI-6 — Execution-fed epistemology
For coding/scientific tasks, treat test/build/tool outcomes as privileged observations that update or falsify claims automatically.
Question: does grounding belief revision in execution evidence improve repair loops?

### H-EPI-7 — Provenance independence
Track whether multiple evidence items are truly independent or merely derivative/duplicated.
Question: does independence-aware support prevent citation-count/repetition from becoming false confidence?

### H-EPI-8 — Counterfactual falsification conditions at write time
When storing an important hypothesis, require “what observation would make this false?”
Question: does this make later verification/revision more efficient and reduce belief persistence after disconfirmation?

### H-EPI-9 — Epistemic compression instead of context maximization
Retrieve only the minimal claim/evidence/dependency slice needed for a decision.
Question: can an epistemic graph preserve quality while using less context than full-history or large-RAG baselines?

### H-EPI-10 — Procedure search over epistemic operations
Let automated procedure search choose operations such as:
retrieve / verify / revise / invalidate / execute / ask / defer / stop.
Use frozen discovery/validation/holdout splits and a champion-regression policy.

### H-EPI-11 — Explicit epistemic structure as a protective intervention
This hypothesis emerged from the exp004 grading problem and must remain separate from exp004 itself.

Compare ordinary answering against an otherwise matched condition that requires explicit fields such as:
- premise status;
- temporal scope;
- definition scope;
- source/evidence status;
- uncertainty / unresolved status.

Primary questions:
1. Does explicit epistemic structure improve objective correctness?
2. Does it specifically reduce retrieval-induced displacement?
3. Is there a retrieval × epistemic-structure interaction?
4. Does any benefit survive unseen tasks and naturalistic/execution settings?

Important interpretation rule: structured epistemic output is an intervention on cognition, not a neutral grading device. If it improves performance, that is a procedure effect to be independently validated, not evidence that the original free-form measurement was unbiased.

## Likely avoid / do not build first

- giant general-purpose knowledge graph;
- arbitrary confidence numbers with no calibration;
- treating repeated/derivative sources as independent evidence;
- allowing model-generated summaries to overwrite raw evidence;
- using coherence as a proxy for truth;
- permanent memory without supersession / valid-time semantics;
- recursive self-improvement before held-out evaluation exists;
- evaluating the epistemic layer primarily with another LLM judge when objective outcomes are possible.

## Minimal architecture worth eventually testing

Claim record:
- proposition
- type/origin
- scope/entities
- valid_time / observed_time
- evidence bindings
- provenance lineage / independence
- status
- dependencies
- contradictions
- supersedes / superseded_by
- falsification condition
- execution observations

Important: start with a small ledger backed by SQLite/JSON, not a graph database. Promote to graph storage only if dependency/temporal queries prove useful.

## Candidate experimental progression

1. Equal-evidence RAG vs explicit claim ledger.
2. Explicit epistemic-structure intervention (H-EPI-11) as a small isolated test where objective grading is available.
3. Add temporal validity.
4. Add dependency invalidation / belief revision.
5. Add execution observations.
6. Add active routing based on epistemic state.
7. Compare against uncertainty-only and generic controller baselines.
8. Generalize to unseen tasks.
9. Only then allow automated procedure search over epistemic operations.

## Novelty posture

The ingredients are not novel individually. TMS, AGM belief revision, knowledge graphs, temporal memory, provenance, uncertainty-aware retrieval, and self-evolving memory all have substantial prior art.

The potentially interesting research question is whether a **minimal, externally grounded synthesis** of these mechanisms produces measurable downstream gains at fixed model/evidence/cost, especially on execution tasks and negative-intervention cases.

Treat that as an empirical hypothesis until a dedicated prior-art review establishes otherwise.
