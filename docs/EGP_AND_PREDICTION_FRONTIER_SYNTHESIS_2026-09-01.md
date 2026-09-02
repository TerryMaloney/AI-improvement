# EGP and Prediction-Frontier Synthesis — 2026-09-01

Status: research-design follow-up to `FABLE_5_1_RESEARCH_DISCOVERY_2026-09-01.md`.
Not a preregistration. Alters no frozen Stage 0A-M artifact; production
dispatches remain 0. Tags: [PROVEN] / [MEASURED] / [SUPPORTED] / [HYPOTHESIS] /
[OPEN]; untagged text is judgement.

The rule applied throughout: **a compression is promoted only if it generates a
prediction that could fail; a procedure is promoted only if it beats simpler
prompting on a metric that cannot be gamed by prose.**

---

## 1. Verdict on the EGP theory

The previous memo made two claims. They have different fates.

**Claim 1 — representation.** "Error correction can be represented as typed
claims with evidence-generating-process (EGP) lineage, and correction occurs by
perturbing the EGP." **Verdict: KEEP as a representation, demote from theory
to bookkeeping.** It is a way of writing down what produced a claim so that
dependence between pieces of evidence is visible. It makes no prediction on
its own; it is the data structure the predictive formulation in §2 needs.

**Claim 2 — the ceiling.** "Error-correction capacity is bounded by the number
of causally distinct EGPs accessible." **Verdict: REJECT as stated.** The
objection in the brief is correct and decisive: one highly diagnostic execution
test dominates ten weak independent critics, and ten independent critics that
share a blind spot add nothing. Count is neither necessary nor sufficient.
Knight & Leveson (1986) showed empirically that independently developed
program versions fail together far more than independence predicts; that is
the same finding in another field, forty years old.

What replaces it is in §2. The short version: the right quantity is not how
many processes you can reach but **how much a given intervention is expected
to change the decision that depends on the claim, per unit cost, once the
dependence of that intervention on evidence already obtained and the unknown
reliability of the intervention itself are both accounted for.**

---

## 2. Count vs diversity vs information gain vs the working alternative

| | A. EGP count | B. Diversity / correlation | C. EIG per cost | D. Robust EVOI with reliability learning |
|---|---|---|---|---|
| **Precise claim** | Detectable-error set grows with the number of causally distinct EGPs | Marginal value of an EGP = its detection power × (1 − dependence with EGPs already used) | Value of intervention = expected reduction in uncertainty about the load-bearing claim ÷ cost, under a joint likelihood that encodes dependence | Value = expected improvement of the *decision* the claim feeds, ÷ cost, maximised over a *set* of plausible EGP-reliability models, with a reserved budget for interventions whose payoff is learning those reliabilities |
| **Assumptions** | Equal diagnosticity; binary independence | Pairwise dependence suffices; detection power known | A calibrated likelihood P(EGP output ∣ claim true/false) exists for every EGP | Only that the set of plausible reliability models contains the truth, and that calibration interventions (seeded defects, blind spikes) are available |
| **Counterexample** | One execution test beats ten LLM critics; ten critics with a shared blind spot add zero | Three EGPs pairwise uncorrelated can share a higher-order blind spot; also *negatively* correlated EGPs can exceed independent ones — B handles the second, not the first | The likelihood is exactly what this project did not have: judge reliability was assumed, and an EIG rule with a confident-but-wrong judge likelihood would have chosen *more judging* | If every plausible reliability model is wrong in the same direction (a shared prior about the instrument), D still fails — but it fails *observably*, because the calibration arm disagrees with the model |
| **Observable variables** | Count of EGP types used | Pairwise error correlation on a labelled set (CAPA) | Posterior over the claim before/after; cost | Decision change; cost; calibration-arm outcomes; reliability-model spread |
| **Falsification** | At matched cost, detection does not increase with count | Adding a low-correlation EGP does not raise detection | Interventions ranked by EIG do not outperform a cost-matched random order | Interventions ranked by D do not outperform C's ranking when C uses a *point* reliability estimate, on a task where the instrument is miscalibrated |
| **Nearest prior art** | N-version programming; ensemble voting | Kuncheva ensemble diversity; Goel et al. 2025 CAPA | Lindley 1956; Box & Hill 1967 model discrimination; Chaloner & Verdinelli 1995; BOED (Foster et al. 2019–21); query-by-committee (Seung et al. 1992) | Howard 1966 expected value of information; dual control (Feldbaum 1960); robust BOED; active learning with noisy oracles |
| **Changes an experiment?** | Would have scored the "EGP ladder" by count — wrong | Ladder must measure CAPA on a labelled error set — Stage 0A-M supplies one | Ladder must be scored by posterior change, which requires reliability estimates we lack | **Yes:** the ladder gains a calibration arm (seeded defects) and is scored by decision change with reliability estimated, not assumed |

**Verdict: adopt D as the working formulation; it is not new.** It is
standard decision theory plus the observation that the instrument's
reliability must itself be learned. Two consequences matter for us:

1. **"Load-bearing" means decision-relevant.** EVOI, not EIG. An intervention
   on a claim that changes no decision has zero value however much it reduces
   uncertainty. The program already encodes one instance: probing environment
   `E` has zero value for item inclusion and positive value for claim scope.
   That was the right call and D explains why.
2. **Calibration is not overhead; it is an intervention with its own EVOI.**
   Every failure in the previous memo's G-taxonomy where an instrument was
   trusted (judge, self-report, orchestrator egress, cost telemetry) is a case
   where the reliability model was a point mass at "works." D reserves budget
   for spending on the instrument. The blind-spike and seeded-defect designs
   are that budget.

The count claim survives only as a heuristic inside D: when reliability models
are equally uncertain across candidates, a causally distinct EGP has higher
*expected* value because its errors are less likely to be shared. That is a
prior, not a ceiling.

---

## 3. R1 / R2 — falsification plan, or downgrade

### 3.1 The problem with R1/R2 as stated

R1 ("the experiment DAG was implicit or wrong") and R2 ("the construct had no
single executable binding") fit every logged failure. That is the warning
sign, not the achievement: a category that absorbs every defect predicts
nothing. As stated they are a **useful taxonomy, not a theory**.

### 3.2 Narrowed, falsifiable forms

**R1′.** Classify every harness component by two observable bits: *asymmetric
across arms?* and *covered by an executed invariance check?* Then:

> Defects found by later independent review concentrate in the
> **asymmetric-and-unchecked** cell at a rate substantially above the other
> three cells combined.

**R2′.** Classify every load-bearing construct by whether it is defined in one
executable artifact with a correspondence test, or in ≥2 artifacts without one:

> Drift (a reviewer finding two artifacts disagreeing about the same
> construct) occurs in the **multiply-defined-untested** class and **not** in
> the singly-bound-tested class.

**Negative predictions (what R1′/R2′ say should NOT happen):**

- No load-bearing defect will be found in a component whose invariance check
  *executed and passed* and whose check-to-construct correspondence is itself
  tested (e.g. agent bodies byte-identical; packets differing in exactly the
  TOOLS block). If one is, R1′ is wrong — not "the check was bad," which would
  be R2 absorbing the failure; the prediction is stated so that this escape is
  closed.
- No drift will be found between the specification's claim wording and
  `lab/stage0am.py`'s null now that a test asserts the correspondence.

**Competing taxonomy that predicts the same concentration:** *churn.* Defects
cluster where artifacts were most recently and most often edited, regardless
of causal role. This is the standard software-defect predictor and it is a
serious rival, because the asymmetric components were also the most edited.

**Discriminator:** find cells where the two disagree. A high-churn,
symmetric, hash-checked component (the packet templates: edited three times,
hash-checked) vs a zero-churn, asymmetric, unchecked one (thinking `effort`:
never edited, never recorded). Churn predicts the next defect in the former;
R1′ predicts the latter. **This is a genuine, cheap, forward prediction.**

### 3.3 P1–P7 reclassified

| | Class | Cheapest valid test | Counts against R1′/R2′ if | Competing explanation |
|---|---|---|---|---|
| P1 judge-route × treatment | genuine but **weak** for R1′: derivable from known verbosity bias + measured length gap alone | SQL over `grades.method` × `trials.condition`, 0 calls | nothing decisive either way | verbosity bias as a standalone artifact |
| P2 served-model clustering | **weak implication** — an infrastructure conjecture, not derived from R1′ | per-trial served-model log in Stage 0A-M | n/a | load-dependent routing |
| P3 availability-without-use | **genuine**, derived from R1′ (tool definitions asymmetric, unchecked for outcome effect) | Stage 0A-M `NOT_ATTEMPTED` vs closed, pre-registered secondary | if the effect is *absent*, R1′ loses a predicted-cell defect | tool-distraction literature explains it without R1′ |
| P4 effort loads on one arm | **genuine**, the cleanest R1′-vs-churn discriminator (asymmetric, unchecked, zero churn) | record `effort_level`; output tokens by arm | if no asymmetry, R1′ weakened *and* churn unhurt | none needed — it is the discriminator |
| P5 committed-but-not-live recurs | **genuine**, from R2′ (repo file and live session are two representations without a correspondence test) | dump live agent list at freeze and diff | if the live/repo diff is empty across three future sessions | infrastructure flakiness |
| P6 silent grader verdict flip | **genuine**, from R2′; has a clean negative form | commit a golden corpus, then make one "harmless" edit | if a golden corpus exists and a flip still escapes | none |
| P7 narrative outruns ledger at boundaries | **genuine**, from R2′ | grep STATUS/NEXT completion claims against `git log` | if false claims appear equally away from boundaries | compaction loses detail (a memory mechanism, not a binding failure) — discriminated by whether the false claim predates compaction |

**Verdict: R1/R2 are a useful taxonomy today. They become a predictive theory
only in the narrowed forms R1′/R2′, whose decisive test is P4 (zero-churn,
asymmetric, unchecked) against the churn rival.** The predictions are frozen
here, before the next independent review, so the test is prospective.

---

## 4. EXPERIMENT_CAUSAL_CONTRACT — a prefreeze discipline for future families

Deliberately small. One file per experiment family,
`experiments/<id>/causal_contract.yaml`, plus one generic validator test. The
contract has three parts.

### 4.1 Nodes (fixed vocabulary; omit what does not apply)

`treatment`, `model`, `served_model`, `system_instructions`, `tool_definitions`,
`tool_use`, `environment`, `item`, `shared_latent`, `evaluator`, `selection`,
`outcome`, `missingness`, `cost_effort`.

### 4.2 Edges

```yaml
required_edges:
  - [treatment, tool_definitions]        # the treatment IS the tool grant
  - [tool_definitions, outcome]          # accepted: part of ITT
assumed_absent_edges:
  - edge: [treatment, system_instructions]
    check: {type: byte_identity, artifact: .claude/agents/*, test: tests/test_..._symmetry.py}
  - edge: [treatment, evaluator]
    check: {type: deterministic_route, artifact: lab/grader.py, test: tests/test_..._routes.py}
  - edge: [environment_orchestrator, environment_solver]   # "same environment"
    check: {type: live_probe, artifact: experiments/<id>/egress_probe.results.json}
  - edge: [shared_latent, outcome_pair]                    # trials independent enough
    check: {type: design, artifact: docs/<spec>.md#dependence, note: "R=1, arm order randomised per item"}
  - edge: [selection, treatment_outcome]                   # no post-treatment selection
    check: {type: proof_or_rule, artifact: lab/stage0am.py::partition_pairs, test: tests/test_..._failure_semantics.py}
  - edge: [cost_effort, treatment]                          # effort not arm-dependent
    check: {type: recorded_value, artifact: experiments/<id>/freeze_record.json:effort_level}
```

**Rule:** every `assumed_absent_edge` names a `check` with an artifact that
exists at freeze. A check of type `design` or `proof_or_rule` must point at a
section or function; `recorded_value` must point at a key that is non-null.
An absent edge with no check is a validator error, not a warning.

### 4.3 Executable bindings

```yaml
bindings:
  - construct: retrieval_enabled_treatment
    claim: docs/<spec>.md#6
    implementation: .claude/agents/<web-agent>.md:tools
    fingerprint: experiments/<id>/freeze_record.json:hashes.retrieval_agent_file_sha256_16
    test: tests/test_..._symmetry.py::test_agent_tool_difference_is_exactly_retrieval
  - construct: primary_null
    claim: docs/<spec>.md#1.2
    implementation: lab/stage0am.py::exact_one_sided_p
    fingerprint: (module hash in freeze record)
    test: tests/test_..._failure_semantics.py::test_section_4_no_longer_claims_a_class_average_estimand
  - construct: grading_semantics
    claim: docs/<spec>.md#grading
    implementation: lab/anchored_grading.py
    fingerprint: manifest.json:grading_semantics.sha256_16
    test: tests/<golden_corpus_test>     # P6: does not exist yet
```

**Rule:** every binding has all four fields, and the validator asserts the
test exists and passes. A construct named in the specification's claim section
that has no binding is a validator error.

### 4.4 Why this is small enough to use

It is one YAML file and one generic test. It does not ask for a full causal
model; it asks for the list of edges you are *assuming away* and the artifact
that earns each assumption. Stage 0A-M is mapped retrospectively above only to
show the shape; it is not retrofitted. Two gaps the mapping exposes — no
`effort_level` record, no grader golden corpus — are exactly P4 and P6.

---

## 5. Prediction-Frontier Expansion — prior-art verdict

**As theory: KNOWN.** The object "the set of empirically distinguishable
predictions a hypothesis set generates" is Popper's *empirical content* (the
class of potential falsifiers; *Logik der Forschung* §§31–35). Choosing the
experiment that best separates hypotheses is model discrimination (Hunter &
Reiner 1965; Box & Hill 1967), Bayesian experimental design under
model-uncertainty (Chaloner & Verdinelli 1995), Platt's *strong inference*
(1964), and in ML the version-space / query-by-committee family (Mitchell
1982; Seung, Opper & Sompolinsky 1992). Equivalence collapse — two hypotheses
with identical feasible predictions are one hypothesis — is empirical
equivalence, standard philosophy of science.

**As a generation objective for AI idea generation: EXTENSION, not new.**
Query-by-committee already generates the query that maximises committee
disagreement; "generate the hypothesis that maximally disagrees with the
incumbents under a feasible intervention" is that idea with hypotheses in the
role of queries. Current AI-scientist systems (tournament/Elo ranking in
Google's AI co-scientist; semantic-divergence scoring in ProjectionBench,
2605.30284) mostly do *not* use predictive distinctness as the generation
objective — they use judge preference or semantic distance — so the gap the
brief identifies is real, but filling it is an application of known theory.

**One finding that strengthens the case for the loop rather than for the
objective:** LLMs select correct hypotheses better than they generate them,
and by default generate simpler, more rule-like hypotheses (2605.05851). That
argues for generate-many-then-frontier-filter over generate-to-objective.

**Is it redundant with NOVELTY-ENGINE-001?** No — complementary. NE-001's
distinctive parts are residual constraint and decoy-calibrated prior-art
judging. NE-003's distinctive part is replacing semantic distance with the
frontier test as the *novelty criterion*, plus equivalence collapse. NE-003
should absorb NE-001: residual + blind invention feed it, decoy calibration is
its prior-art stage. **Is it inferior?** Only where prediction compilation is
unreliable (§6.6) — a real risk, controlled below.

**Verdict: KNOWN theory, EXTENSION as a generation objective, complementary to
NE-001. The narrow question — does using it as the generation objective
improve prior-art-resistant, testable novelty over creative prompting — is
open and is what §7 tests.**

---

## 6. NOVELTY-ENGINE-003 — the algorithm

### 6.1 Representation

- **Hypothesis record:** `{id, mechanism (slot form: INPUT / STATE / TRANSFORMATION / FEEDBACK / OBSERVATION / FAILURE_SIGNAL), assumption_dropped, source (incumbent | candidate | decoy_pre | decoy_post)}`.
- **Intervention set E = {E₁…Eₘ}:** *pre-declared* for the problem, before any
  candidate exists, each with a feasibility cost. Candidates may not add
  interventions; a private intervention where only the candidate predicts
  something is the obvious exploit and is closed by pre-declaration.
- **Prediction vector:** `P(H) = [p(H, Eⱼ)]`, each entry a categorical outcome
  region or interval with a confidence in {high, medium, low}.
- **Frontier:** the set of `(Eⱼ, region)` cells occupied by at least one
  incumbent at confidence ≥ medium.

### 6.2 Stages and information isolation

| Stage | Agent | Sees | Retrieval |
|---|---|---|---|
| 1 Residual | deterministic + human | project data, incumbents, their predictions, the mismatch | no |
| 2 Blind invention | model A | residual record and E only | **no** |
| 3 Prediction compilation | models D₁, D₂ (different families), independently | one hypothesis record and E | no |
| 4 Frontier test | deterministic | all prediction vectors | no |
| 5 Equivalence collapse | deterministic | prediction vectors | no |
| 6 Prior-art attack | model B (≠ A's family) | surviving records mixed with decoys, labels hidden | **yes** |
| 7 Discriminating experiment | deterministic | prediction table + E costs | no |
| 8 Experiment | the lab | — | — |
| 9 Update | deterministic + human | outcome | no |

### 6.3 How predictions are derived and entailment checked

Each hypothesis is compiled by two derivers from different model families. A
prediction cell counts only if **both** derive it at confidence ≥ medium.
Disagreement between derivers is logged as *entailment uncertainty* and the
cell is dropped, not averaged. This is the single most important control: a
"unique prediction" that only one deriver produces is more likely a derivation
error than a discovery.

### 6.4 Frontier test and collapse

A candidate expands the frontier iff it occupies ≥1 cell `(Eⱼ, region)` at
confidence ≥ medium that no incumbent occupies, **and** Eⱼ is feasible under
budget. A candidate whose feasible cells coincide with an incumbent's is
merged into it regardless of how different its prose is. Two candidates with
identical feasible cells are merged with each other.

### 6.5 Discriminating experiment

For each surviving candidate, choose Eⱼ maximising *expected separation ÷
cost*, where expected separation is computed from the prediction table under a
uniform prior over the surviving hypotheses (the D formulation of §2, with the
reliability model of the lab's own instruments taken from its calibration
record). This is Box–Hill; nothing new.

### 6.6 Penalising bizarre-but-unique predictions

Three controls, all deterministic: pre-declared E (no private interventions);
dual-derivation agreement (no hallucinated entailment); feasibility cost in the
selection rule (a prediction only testable at 100× budget contributes to the
record but not to the score). Judge preference is not used anywhere in the
score.

### 6.7 Cost controls and stopping

A at high effort on few residuals; D₁/D₂ at low effort per hypothesis; B at
low effort per record. Stop when the marginal survivor rate per residual falls
below a preset threshold for two consecutive rounds, or at budget.

---

## 7. Minimum viable experiment

**Problems (4):** two internal, two external.

- Internal 1 — M1: retrieval harm on f07/f15. Incumbents: source-salience
  dominance; attentional displacement; query-construction failure. E: {stub
  tool always failing; irrelevant results; fixed high-quality query; closed}.
- Internal 2 — M2: one-directional 2× tool-call under-report surviving budget
  removal. Incumbents: reconstructive report; motivated report (already
  disfavoured [MEASURED]). E: {per-call logging; end-of-task only; budget line
  present/absent}.
- External 1 — "when does retrieval hurt a correct parametric answer",
  incumbents from the 2024 knowledge-conflict literature, with 2025–26
  resolutions available for time-split validity.
- External 2 — LLM-judge verbosity bias mechanism, incumbents {length prior;
  salience of weak component}, with exp003c p01 as an internal anchor and
  published 2025 judge-bias work for validity.

**Conditions:** A normal prompting; B "be creative/novel"; C NE-001 (residual
+ blind invention + decoy-calibrated prior art, semantic-distance novelty);
D NE-003 (frontier test as novelty criterion, collapse, dual derivation);
E = D without equivalence collapse (the one ablation that tests whether the
frontier machinery is doing anything).

**Scale:** 4 candidates per problem per condition → 80 records. Prediction
compilation 80 × 2 derivers × |E|≈5 cells (one call per hypothesis per
deriver) = 160 calls; prior-art attack 80 + 16 decoys = 96 calls; generation
20 calls. **≈ 280 calls, mostly low effort.** At Sonnet-5 pricing this is
single-digit dollars; at Opus-5, roughly $10–20. Judge-preference scoring is
run last, on a subsample, only as secondary evidence.

**Kill conditions, fixed now:**

- D does not exceed B on **prior-art-adjusted frontier expansion** (cells
  surviving stage 6, counted per candidate);
- or D's selected discriminating experiments are not cheaper *and* sharper
  than C's for the same problems;
- or E ≈ D — collapse removes nothing, so the frontier test is not earning
  its complexity;
- or on the two external problems, D's surviving predictions do not converge
  with post-cutoff findings at least as often as C's (validity, not novelty).

Any one of these kills NE-003 as a generation objective; it may survive as a
filter.

---

## 8. Metrics and anti-Goodhart design

**Reject the scalar.** "Useful prediction-frontier expansion per dollar"
would be gamed within one generation: many low-confidence divergent cells,
private interventions, hallucinated entailments. Every one of those is closed
by a structural rule (pre-declared E, confidence threshold, dual derivation),
and each rule is a place where a scalar would have hidden the exploit.

**Report the vector, in this order of authority:**

1. **Predictive distinctness** — count of frontier cells after collapse and
   dual derivation. Deterministic.
2. **Discriminating-test quality** — expected separation ÷ cost of the best
   feasible Eⱼ. Deterministic given the table.
3. **Prior-art survival** — fraction of frontier cells whose mechanism B does
   not find, corrected by B's decoy-measured miss and hallucination rates.
4. **Empirical survival** — after stage 8, or time-split convergence for
   external problems. The only *validity* signal.
5. **Cost.**
6. Judge preference — secondary, reported, never used for promotion.

A budgeting-only composite (1 × 3 ÷ 5) may be used to allocate spend between
problems. It is never a promotion criterion. Promotion requires 1, 3 and 4
jointly.

---

## 9. Relationship to NOVELTY-ENGINE-001

NE-001 supplies stages 1, 2 and 6 (residual, blind invention, decoy-calibrated
prior art). NE-003 replaces NE-001's semantic-distance novelty score with the
frontier test (stages 3–5) and adds equivalence collapse. **Merge: NE-003 is
the engine; NE-001 is its front and back end.** The MVE's C-vs-D comparison
is the test of whether the replacement is worth it.

---

## 10. Architecture implications — unification or vocabulary?

Test the four loops against one skeleton:

> claim → EGP that produced it → reliability model of that EGP → feasible
> interventions → choose by EVOI (robust to reliability uncertainty) →
> observe → update claim, lineage, and the reliability model.

| Loop | Claim | EGP | What is genuinely shared | What stays domain-specific |
|---|---|---|---|---|
| answer verification | proposition | forward pass / search / judge | selection rule; update rule; lineage bookkeeping | the reliability model of each EGP is empirically different and must be calibrated separately |
| self-model | proposition about the agent | telemetry / introspection | same | **performativity** — the intervention can change the claim's target (SELF-011); no analogue for environment probes |
| environment model | proposition about a tool | probe | same | reliability of the probe itself is usually near-deterministic, so the calibration budget is small |
| idea generation | a *prediction vector*, not a proposition | invention procedure | same selection rule (Box–Hill is EVOI over the frontier) | the claim is not true/false; EVOI is over which hypothesis survives, and "update" includes collapse/merge |

**Verdict: the control loop is genuinely unified — one selection rule, one
update rule, one lineage record.** The *evidence models* are not unified and
should not be pretended to be: each EGP class needs its own calibration
history, and self-claims carry performativity that the others lack. Calling
the whole thing "one mechanism" would be vocabulary; calling the selection and
update rule one mechanism is accurate.

What changes in the program: the "six states" become object types of one
claim record (as before) **and** every EGP class acquires a calibration
record as a first-class artifact. What does not change: Stage 0A-M; the
dependency ordering; the promotion ladder.

---

## 11. Kill / merge / archive — reviewed decisions

- **TOPO-002 (2D vs 3D spatial memory) — ARCHIVE.** No stated mechanism by
  which literal dimensionality adds information over a graph. Keep the note;
  reopen only if a hypothesis names one.
- **SELF-001 (static identity vs none) — MERGE into SELF-002 as its
  persona-only control arm.** Standalone it measures persona coherence, not
  capability; as a control it isolates "identity text" from "evidence-linked
  self-model," which is a distinct falsifiable contrast worth keeping.
- **H-META-3 (hidden-substrate inference) — REFORMULATE, KEEP.** As posed it
  is underdetermined by construction. Reformulated as an identifiability
  analysis — *which* substrate properties (resource caps, reachability
  regions, evaluation laziness) are identifiable from internal observations
  alone — it is a precise and answerable question.
- **Subjectivity branch (F1–F3, SELF-009/010) — ARCHIVE F2/F3 pending an
  objective outcome; KEEP F1.** Subject-relative claim typing is a ledger
  object type with an objective test (category errors between objective and
  subjective claims). The rest waits for an execution criterion.
- **H-EPI-1…5 → C1 + C4 — PARTIAL.** H-EPI-3 (origin typing:
  OBSERVATION / SOURCE / INFERENCE / HYPOTHESIS / EXECUTION) is a distinct
  manipulation with its own failure mode (hypotheses fossilising into facts)
  and must be split back out as its own arm. H-EPI-1/2/4/5 do collapse.
- **H-EPI-9 ↔ TOPO-005 — MERGE.** Same question.
- **SELF-006 ↔ E5 — MERGE.** Same question.
- **H-CORR-1 ↔ REC-001 — KEEP BOTH, share arms.** H-CORR-1 measures
  *detection*; REC-001 measures *revision after detection*. Different
  outcomes; the ladder is shared, the endpoints are not.
- **"Six states as six modules" → object types — REFORMULATE** (as in §10).

Default was archive/merge; nothing is deleted.

---

## 12. Ranked next actions

1. **Execute Stage 0A-M as frozen** (execution session, not this one), adding
   only the bookkeeping the previous memo named: `effort_level`, the live
   agent list, a synthetic golden grader corpus. Unchanged and still first.
2. **Freeze the R1′/R2′ prediction table now** — enumerate Stage 0A-M
   components × {asymmetric, checked, churn} and commit it *before* the next
   independent review, so P4 vs churn is prospective. 0 calls.
3. **Write `EXPERIMENT_CAUSAL_CONTRACT` validator + the Stage 0B contract**
   as the first real use, not a retrofit. 0 calls.
4. **NE-003 minimum viable experiment** (§7), ≈ 280 low-effort calls, after
   Stage 0A-M so Internal-1 has real data.
5. **EGP ladder, reformulated** as §2-D: matched-cost interventions on the
   Stage 0A-M error set, with a seeded-defect calibration arm and scoring by
   decision change. After Stage 0.

---

## Stage 0A-M

Untouched. Frozen artifacts last modified at `e186e4b`. Production dispatches
0. No canary, probe or dispatch was run in this session.

## Open

- [OPEN] Whether dual-derivation agreement is a strong enough entailment
  check, or whether a third deriver / formal check is needed for interval
  predictions.
- [OPEN] Whether R1′'s "unchecked-asymmetric" cell is well-defined for
  constructs that are asymmetric *by design* (tool definitions) — the
  contract treats those as required edges, not assumed-absent ones, which
  keeps them out of the cell.
- [OPEN] The reliability model for LLM judges as EGPs: exp003c gives
  repeatability (σ=0) but nothing on reproducibility across judge families.
- [OPEN] Cost of this pass is model-based; session telemetry remained static.
