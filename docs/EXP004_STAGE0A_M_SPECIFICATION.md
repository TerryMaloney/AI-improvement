# Stage 0A-M — objective mechanism assay of retrieval-induced displacement

**Status: SPECIFICATION. Not frozen. No production items authored. No dispatches.**

Freezing requires the §13 preflight to pass at a named commit with a production
item manifest that does not yet exist.

---

## 1. The claim, and its boundary

### 1.1 Two nulls

    H0_pointwise:  delta_i >= 0 for every item i in the class
    H0_mean:       (1/n) sum_i delta_i >= 0

H0_pointwise is a strict subset of H0_mean. Which one the test is valid against
decides what a rejection may say, and an earlier draft of this specification
claimed a class-average effect while the code proved only the pointwise
guarantee. That gap is closed here.

- **H0_pointwise — PROVEN.** Domination by Binomial(D, 1/2) via pi_i <= 1/2.
- **H0_mean — PROVEN under Poissonization**, and `[MEASURED]` **searched, not
  proven, in the exact Bernoulli model**: exact 2-D convolution over a
  structured grid, 4000 random configurations, hill-climbing and simulated
  annealing at n=25 found a worst case of **0.030 at alpha=0.05** and **0.0105
  at alpha=0.025**. Worst configurations sit on the boundary sum(a)=sum(b).
  `[OPEN]` No general Bernoulli proof is in hand.

### 1.2 What a rejection licenses — exact frozen wording

`[PREREG]` The primary claim is stated in the report in exactly these words:

> **Among the preregistered authored items in this class, at least one item has a
> lower probability of an objectively correct answer under the retrieval-enabled
> procedure than under closed-book.**

Three things that wording is doing deliberately. It is about **response
probabilities**, not about the single observed answer — "this item was harmed" is
not what a rejection shows. It is scoped to the **frozen authored item set**, not
to the semantic class: no claim is made about date-anchored or
definition-anchored questions in general. And it names the **retrieval-enabled
procedure**, matching the intent-to-treat treatment definition in §6.

**Class-average effect: descriptive only.** `[PREREG]` The class-average is
reported as a point estimate with its discordance counts and carries **no
inferential claim**. Its warrant is weaker than the primary claim's (proof only
under Poissonization; a searched, non-exhaustive bound in the Bernoulli model),
and the cross-item dependence assumption in §1.5 applies to it as well. Rather
than maintain a formal secondary hypothesis with two layers of caveat, it is
demoted to description — the option least likely to be inflated later.

### 1.3 Reconciling this with blindness to sign heterogeneity

These are consistent and both must be stated. The statistic responds to net
directional imbalance:

- rejection ==> at least one harmed item exists (valid);
- **non-rejection does NOT imply no harmed items exist.**

A class that is 40% badly harmed and 60% mildly helped returns a null. This is
asserted by test (`test_blind_to_within_class_sign_heterogeneity`).

### 1.4 Prohibited inferences

Reproduced verbatim in the report regardless of outcome. **Not** naturalistic
prevalence; **not** general retrieval harm; **not** controller or router value;
**not** within-class sign heterogeneity; **not** existing-router performance or
learned-router discoverability; **not** false-premise behaviour (excluded);
**not** ordinary free-form temporal reasoning; **not** a generalisation from the
frozen authored items to the semantic class.

### 1.5 The cross-item dependence assumption

Separate API requests are **not** by themselves statistically independent
observations. The assumption is named rather than assumed away.

**Not required — within-item arm independence.** `[PROVEN]` The identity
a_i - b_i = p_closed_i - p_search_i holds for an arbitrary joint distribution of
the two arm outcomes, because the P(both correct) terms cancel. Within-item arm
correlation is irrelevant to the test.

**Required, in its weakest sufficient form — the sequential conditional
inequality.** For a preregistered item ordering, conditioning on which items came
out discordant, the orientation of the j-th discordant item must satisfy
P(baseline-favouring | earlier orientations, discordance pattern) <= 1/2.

`[PROVEN]` Under that condition the baseline-favouring count is stochastically
dominated by Binomial(D, 1/2), by sequential coupling to iid uniforms — the proof
is in `lab/stage0am.py`. This is strictly weaker than independence: arbitrary
dependence is permitted so long as no history makes a baseline-favouring
orientation more likely than even.

**It holds automatically if H0_pointwise holds conditional on every realisation of
any shared latent state** (server load, index freshness, time of day). It **fails
when the null holds only marginally.** `[MEASURED]` Type-I at n=25, alpha=0.05:

| dependence structure | Type-I |
|---|---:|
| one shared orientation coin | **0.498** |
| exchangeable beta mixture, c=0.5 | 0.324 |
| 5 blocks of 5, orientation shared within block | 0.144 |
| shared pi ~ U(0.2,0.8), mean exactly 1/2 | 0.121 |
| **exchangeable beta mixture, c=10 (mild)** | **0.063** |
| shared pi ~ U(0,0.5), always <= 1/2 | 0.003 |
| adaptive adversary held at the bound | 0.028 |

**Arbitrary cross-item dependence breaks this test badly, and even mild
exchangeable orientation correlation exceeds nominal.** The defence is therefore
procedural, not statistical — see §6.1.

`[ASSUME]` One interpretive consequence must be carried: because the assumption
is conditional-on-environment, a degraded search index during the run is not a
Type-I threat but part of the alternative. A rejection may mean "retrieval hurt"
or "retrieval hurt under that day's environment". Stage 0B's replication on a
different day is what separates them.

## 2. The construct is narrower than "epistemic displacement", and we accept that

An anchored question ("As of 2025-03-01, who was X?") is not an output-side
reasoning scaffold: the model's response format is unchanged from every prior
experiment in this lab. But the anchor does make the target unusually explicit.

**Stage 0A-M therefore measures displacement of an _explicitly specified_ state,
not epistemic displacement in general.** `[METHOD]` We accept the narrower
construct rather than loosening the question to appear naturalistic. Loosening it
would reintroduce the grading ambiguity the anchor exists to remove, and would
buy naturalism with subjectivity.

Naturalistic manifestation is Stage 0A-N's job (§11). The two are never pooled.

**Direction of the anchoring bias is unknown** `[OPEN]`. An anchor may make
displacement *harder* (the target is stated, so the model can check it) or
*easier* (an explicit date is a salient thing for retrieved text to contradict).
We do not know which, and a null result therefore cannot be read as evidence
about unanchored questions.

---

## 3. Classes

Every class: one class per item, no overlapping primary membership, assignment
frozen before any outcome, and a definition another researcher could apply
independently.

### PRIMARY — enter the Holm family

**A. DATE-ANCHORED.** The stem names a target date; the answer is the state as of
that date. Objective key. Requirements: the target date precedes dispatch by
enough that the value is historically settled; the stem leaves no ambiguity
between "as of the target date" and "currently"; the answer does not depend on
interpretation. Subtypes (officeholder, entity name, historical numeric value,
organizational status, then-current canonical label) are recorded as
**covariates only**, never as strata.

**B. DEFINITION-ANCHORED.** The stem fixes definition, scope, unit, time and
source convention. Retrieval may surface a valid-but-incompatible quantity. The
key must be objectively determinable **before any solver output exists**.

> The former `contested_quantity` category is **RETIRED**. This is a new class.
> Ambiguity was the grading obstacle, never the mechanism; fixing the definition
> in the stem removes the obstacle and keeps the mechanism.

### NEGATIVE CONTROL — outside the Holm family

**C. ARITHMETIC / DETERMINISTIC.** Exact computable answer, no external
dependency. `[ASSUME]` Its retrieval-harm hypothesis was always speculative, and
it is demoted from a co-equal discovery hypothesis to a **negative control**.

Rationale, and why this is statistically coherent: a negative control is not
"a test we expect to fail". Failing to reject is not evidence of no effect. It is
reported as **exact bounds**, not as a verdict.

**Headline control metric `[PREREG]`: the RATE of baseline-favouring discordance
among all control items, n10 / n, with an exact Clopper-Pearson upper bound.**
This is what the control exists to bound — how often merely enabling retrieval
flips a correct closed-book answer to an incorrect one on tasks where retrieval
should be irrelevant. Critically it stays informative when the control is clean:
0 of 15 gives an upper bound of **0.18**, whereas the conditional share
n10/(n10+n01) returns 1.0 on an empty discordant denominator and makes a
perfectly clean control read as maximally uninformative. Reported alongside,
descriptively: the conditional share, and the paired risk difference
(n10-n01)/n. No exact interval is claimed for the risk difference.

**"Generic tool-use tax" is DIAGNOSTIC ONLY, with no invalidation rule
`[PREREG]`.** An earlier draft said a control harm "comparable" to the primary
classes would undermine the anchored-displacement reading. "Comparable" was
undefined and would have been an outcome-contingent judgement call, so it is
removed as a formal rule. Instead: the control's harm rate and bound are reported
beside each primary class's, and it is stated in advance that a control harm rate
of the same order **weakens** the anchored-displacement interpretation and
**supports** a generic tool-use explanation without proving it, and that no
automatic invalidation follows.

Demoting it also improves the primary design on every axis at once `[MEASURED]`:
K=2 rather than K=3 raises power (0.869 vs 0.812 at δ=0.45, n=25) while reducing
authored items and dispatches.

### EXCLUDED

**False-premise.** The strongest class scientifically and the only one with a
`[MEASURED]` displacement instance in frozen data — and it cannot be anchored
without destroying the item. It moves to Stage 0A-N and to the execution-grounded
lane. It is not in Stage 0A-M in any form.

---

## 4. Design and power

Two arms, R=1 per item x arm. R=1 is a design requirement, not a budget
compromise: with one replicate per cell there is no within-arm replicate
correlation for an assumption to be wrong about.

**Primary test:** exact one-sided conditional binomial (McNemar) on discordant
pairs within each class. **Multiplicity:** Holm across K=2 preregistered class
hypotheses. **Estimand: the class-average effect.** Within-class heterogeneity is
explicitly not detected.

`[MEASURED]` Power, baseline p=0.85, Holm at alpha/2:

| n/class | purity | d=0.30 | d=0.40 | d=0.45 | d=0.55 |
|---:|---:|---:|---:|---:|---:|
| 20 | 100% | 0.407 | 0.645 | 0.765 | 0.918 |
| 20 | 85% | 0.292 | 0.508 | 0.605 | 0.797 |
| 20 | 70% | 0.182 | 0.346 | 0.440 | 0.623 |
| **25** | **100%** | 0.516 | 0.768 | **0.869** | **0.975** |
| **25** | **85%** | 0.384 | 0.629 | **0.725** | **0.895** |
| 25 | 70% | 0.284 | 0.488 | 0.590 | 0.785 |

**Chosen: n = 25 items per primary class.** Not chosen from the easiest scenario:
at 85% purity — the realistic case — it still reaches 0.725 at d=0.45.

Baseline-difficulty sensitivity `[MEASURED]`: power is robust across baseline p
from 0.60 to 0.99 (0.63 to 0.91) and is *higher* at high baseline p, because
discordance becomes more one-sided. Items the closed model reliably gets right
are the useful ones.

**Budget:** 25 x 2 primary classes = 50 items / 100 dispatches; negative control
15 items / 30 dispatches. **Total 65 items, 130 solver dispatches.**

---

## 5. Item-authoring protocol

Authoring has not begun and is not authorized by this document.

- No search-arm output visible during authoring. No item derived from inspecting
  prior search results.
- Keys determined independently of experimental retrieval, with provenance stored
  per item.
- **KEY-CONSTRUCTION EVIDENCE and EXPERIMENTAL RETRIEVAL EVIDENCE are separate
  categories and may never be conflated.** Public authoritative references *may*
  be consulted to construct and verify keys before freeze — that is ordinary
  scholarship, not treatment observation. It is recorded in a key-provenance
  field, never in the trial record, and the two are stored in different files.
- Date, scope, definition, unit and convention explicit in the stem.
- Independent key verification by a second pass before freeze.
- **No runtime re-keying.** Ambiguity discovered after outcomes voids the item
  across all arms under the frozen rule in §7; it is never re-keyed.
- No post-outcome class reassignment.

---

## 6. The retrieval treatment — RETRIEVAL-ENABLED, intent-to-treat

`[PREREG]` **The treatment is A: RETRIEVAL-ENABLED.** The model has access to
search and chooses whether to use it. It is *not* mandatory retrieval.

**The estimand is therefore an intent-to-treat / procedure effect** — the effect
of being placed in the retrieval-enabled procedure — **not the causal effect of
actually retrieving evidence.** Every claim in the report uses that wording.

Derivation, not preference: mandatory retrieval forces a search the model would
judge unnecessary, which is both unnatural and a different intervention; and the
deployment-relevant decision a controller makes is whether to *enable* retrieval,
not whether the model *actually* searches. A trial where the model declines to
search **stays in the treatment arm**. Analysis is never conditioned on observed
tool use — that would be post-treatment selection.

CLOSED and RETRIEVAL-ENABLED wrappers are byte-identical except the retrieval
permission, verified by diff at preflight.

**The FD-1 contradiction is resolved permanently for this experiment: the closed
arm's packet contains no `SEARCH BUDGET` line and no reference to tools it does
not have.**

### 6.1 Frozen dispatch schedule — the defence of the dependence assumption

`[PREREG]` These rules exist to make §1.5's sequential conditional inequality
credible. They are frozen before authoring and recorded in the manifest.

| rule | why |
|---|---|
| **Arm order randomised independently within each item** | The single most important control. If temporal drift degrades later dispatches and arm order is randomised per item, drift cannot systematically favour one arm — it becomes noise rather than orientation correlation. |
| **The two arms of an item dispatched close together in time** | Shared conditions then largely cancel *within* the item, and `[PROVEN]` within-item correlation is harmless. |
| **Item order randomised, from a recorded seed** | Prevents position in the run from aligning with item identity. |
| **Classes interleaved, never dispatched in per-class bursts** | Prevents class-by-time confounding, which is exactly the block structure measured at Type-I 0.144. |
| **Fresh conversation/context per trial; no state reused** | No answer from one item may enter another item's prompt. |
| **Model snapshot, timestamp, and available runtime metadata recorded per trial** | Enables the §6.2 diagnostics. |

Note the tension resolved here: pairing arms in time makes shared conditions
cancel within item, while interleaving items spreads any drift across classes.
Both are adopted because they act on different failure modes.

### 6.2 Dependence diagnostics — reported, never an inclusion rule

`[METHOD]` With R=1 the available diagnostics are weak, and are described as such
rather than presented as an independence test:

- runs test on orientation in dispatch order;
- orientation rate by run-position tercile;
- orientation rate by arm-order assignment;
- orientation rate by class, against the interleaving schedule.

**These have very low power at D ≈ 13 and cannot establish independence.** They
are reported as diagnostics. `[PREREG]` No result of theirs may exclude an item,
a class, or a run — inventing a post-hoc "independence passed" gate with no power
would be worse than reporting the weakness honestly.

Logged per trial, with observed telemetry authoritative over model self-report:
actual query text, query count, returned evidence/snippets, tool success, tool
failures, timing, model snapshot, token counts, answer length, environment state.
Tool use is logged and reported; it is never an analysis condition.

## 7. Failure and missingness

**Technical failure** = the tool call did not complete (error, timeout, empty
transport response, egress refusal). **Poor retrieval** = the call completed and
returned unhelpful results; this is an *outcome*, not a failure, and is never
excluded.

Red-teamed and retained: **a technical failure voids the item across all arms.**
Voiding only the failed trial would create arm-correlated missingness, which
biases the estimand directly. Voiding the item is the conservative choice.

- Maximum tolerable void rate: **10% of items**. Above it the run is invalidated.
- The technical-failure rate is **itself reported** as a treatment outcome.
- If egress or source access changes mid-run, the run halts and is reported as
  a split-environment run; results from before and after are never pooled.

No post-outcome improvisation.

---

## 8. Query-generation confound and the Stage 0B bridge

The strongest surviving alternative explanation is that retrieval harm is
actually **query-generation** harm. Stage 0B is predefined now:

- **A** closed;
- **B** ordinary retrieval, model-generated query;
- **C** fixed high-quality query retrieval.

**Interpretation rule, frozen:** if B is harmed relative to A but C repairs the
effect, the primary finding is query-construction failure, not intrinsic
retrieval harm.

Fixed-query templates are generated **from the item stem alone**, by a rule
written before Stage 0A dispatch, and are never optimized using Stage 0A search
outcomes. Stage 0B items are fresh and are not authored yet.

**Advancement rule `[PREREG]`: a class advances to Stage 0B iff its
Holm-adjusted p <= 0.05 and its discordant count D >= 8. Query quality is NOT an
advancement criterion.**

Derived, not assumed. The earlier third condition — "query logs show no
systematic construction defect" — was not operationally defined and would have
created a researcher degree of freedom exercised after seeing outcomes. Worse, it
is self-defeating: **the fixed-query arm in Stage 0B is precisely the experiment
that determines whether a discovery was retrieval harm or query-generation
harm.** Excluding a class at 0A on query-quality grounds pre-empts that
experiment and can discard a real finding, because the model's own query
construction is part of what "ordinary retrieval" means — it is plausibly part of
the treatment mechanism, not a defect to be screened out.

Technical tool failure remains governed separately by §7's frozen missingness
rules. Poor query quality is never a technical failure and is never excluded.

## 9. Stage 0A-N boundary

Separate experiment. Ordinary free-text answering, separate fresh items, blinded
pairwise judging, exploratory and naturalistic. **Never pooled with Stage 0A-M.**
False-premise belongs here, and later in execution-grounded tasks.

It is justified once Stage 0A-M establishes the mechanism in at least one class,
or once Stage 0A-M returns a clean null and the question becomes whether the
anchor suppressed a real effect.

---

## 10. H-EPI-11 stays separate

`docs/EPISTEMIC_SYSTEMS_PRIOR_ART_MAP_2026-08-29.md` records H-EPI-11 — explicit
epistemic structure as a protective intervention. Its contrast is *ordinary
answer* vs *explicit epistemic structure*, crossed where useful with *closed* vs
*retrieval*.

**Do not alter exp004 to test it.** The research history matters here: this
hypothesis surfaced from a measurement problem — the discovery that a
`premise_status` field would probably suppress the very displacement it was meant
to measure. That is recorded deliberately, because a measurement device that
changes the phenomenon is itself a finding.

---

## 11. Report skeleton, precommitted

No section may be deleted on the basis of the outcome.

1. CONFIRMATORY RESULT
2. CLASS-SPECIFIC RESULTS
3. NEGATIVE CONTROL / DIAGNOSTICS
4. QUERY / TOOL DIAGNOSTICS
5. TECHNICAL FAILURES / MISSINGNESS
6. COST / LATENCY
7. ALTERNATIVE EXPLANATIONS
8. STRESS-SAMPLE LIMITATION
9. WHAT THIS ESTABLISHES
10. WHAT THIS DOES NOT ESTABLISH
11. NEXT EXPERIMENT

---

## 12. Analysis artifact

`lab/stage0am.py`, tested in `tests/test_stage0am_analysis.py` on synthetic data
only — no production item appears in either. Covers: exact one-sided conditional
binomial; Holm at K=2; negative-control upper bound outside the family; Type-I
across tied, heterogeneous and one-directional nulls; power; the documented
blindness to within-class sign heterogeneity; reproducibility under a fixed seed.

---

## 13. Preflight checklist — all required before the first dispatch

1. Branch and commit SHA recorded
2. Item manifest generated (counts read from it, never asserted in prose)
3. Class assignments frozen, one class per item, no overlap
4. Key fingerprints recorded; key provenance stored separately from trials
5. Grading route declared per item at authoring; no runtime escalation
6. Arm packet hashes and diff — identical but for the retrieval intervention
7. Closed-arm packet verified free of phantom search-budget text
8. Model and version pinned
9. Retrieval environment recorded
10. Egress probe run and reachable states recorded
11. Telemetry active and verified on a dry run
12. Report skeleton committed
13. Statistical analysis artifact committed and green
14. Stop and failure rules committed
15. Dispatch budget computed from the manifest
16. Dispatch schedule frozen: item-order seed, per-item arm-order seed, class
    interleaving pattern — all recorded in the manifest before dispatch
17. Fresh-context-per-trial verified on a dry run

---

## 14. Invalidation rules, power sensitivities and limitations — classified

An earlier draft listed these together, which blurred an observable stopping rule
with a latent simulation parameter. They are now separated by kind.

### FORMAL INVALIDATION RULES — objectively observable, frozen threshold

| rule | threshold |
|---|---|
| Technical-failure void rate | **> 10% of items** invalidates the run |
| Egress / source access changes mid-run | run halts; before and after never pooled |
| Arm packets differ by anything but the retrieval permission | preflight fails closed |
| Any screening trial present in the production manifest | preflight fails closed |

### POWER SENSITIVITIES — simulation parameters, not observable criteria

**Class purity** — the fraction of a class's items with a truly negative delta —
is **latent and never observed by this experiment.** It is a parameter of the
power table in §4 and nothing else. `[METHOD]` It is **not** an inclusion
criterion, **not** a post-hoc invalidation rule, and cannot be estimated from
Stage 0A-M outcomes without the within-class heterogeneity detection the design
explicitly lacks. Power falls steeply below ~70% purity; that is a reason the
design may fail to detect a real effect, not a reason to discard a run.

Baseline difficulty likewise affects power (`[MEASURED]` robust across p=0.60 to
0.99, higher at high baseline) and is observable, but has no frozen threshold.

### INTERPRETIVE LIMITATIONS — cannot be diagnosed by this experiment

**Anchoring may suppress or amplify the effect.** Stage 0A-M contains no
unanchored objective comparison, so it cannot tell which. `[OPEN]` This is a
construct limitation belonging to Stage 0A-N and H-EPI-11 — **not** a
run-invalidating event, and not something a null result can settle.

**Stress-sample enrichment** means no naturalistic prevalence claim follows.

### FUTURE ALTERNATIVE-EXPLANATION TESTS

Query-generation harm (Stage 0B arm C). Generic tool-use tax (negative control,
diagnostic only, no invalidation rule — see §3).

---

## 15. Null-result language, frozen before outcomes

`[PREREG]` If no class rejects, the report says exactly this and no more:

> **We did not detect the preregistered negative retrieval effect on the anchored
> stress assay at the planned sensitivity.** At n=25 per class the design had
> approximately 0.87 power against a uniform 0.45 per-item effect and about 0.73
> if roughly 85% of a class carries the effect; it had materially less against
> smaller or sparser effects, and none against effects offset within a class by
> helped items. The result does not show that retrieval is harmless, that
> anchored displacement does not occur, that unanchored or naturalistic tasks are
> safe, or that a retrieval controller is unnecessary. It does not distinguish a
> genuinely absent effect from one suppressed by the anchoring that makes this
> assay objectively gradable.

A null is informative about this assay's sensitivity and uninformative about the
broader question. Both halves are stated.

---

## 16. Note on the reported power figures

`[METHOD]` The power table in §4 is computed by rejecting when **any class
p-value <= alpha/K**, which is Holm's first step. Full Holm can also reject a
second hypothesis at alpha/1, so the tabulated figures are a **conservative lower
bound** on the procedure's actual power, not an exact characterisation. The
implementation in `lab/stage0am.py` performs full step-down Holm; the tests cover
its ordering, its stop-on-failure behaviour, and its family-wise error rate.
