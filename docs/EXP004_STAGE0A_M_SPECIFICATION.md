# Stage 0A-M — objective mechanism assay of retrieval-induced displacement

**Status: SPECIFICATION. Not frozen. No production items authored. No dispatches.**

Freezing requires the §13 preflight to pass at a named commit with a production
item manifest that does not yet exist.

---

## 1. The claim, and its boundary

**Stage 0A-M may establish exactly one thing:**

> On preregistered, treatment-blind classes of **explicitly anchored** questions,
> retrieval reduces the probability of an objectively correct answer relative to
> closed-book, on an authored stress sample.

Prohibited inferences, to be reproduced verbatim in the report regardless of
outcome:

- **not** naturalistic prevalence — the sample is deliberately enriched;
- **not** general retrieval harm — only anchored questions are tested;
- **not** controller or router value of any kind;
- **not** within-class sign heterogeneity — the statistic is blind to it by
  construction, and a test asserts this (`test_blind_to_within_class_sign_heterogeneity`);
- **not** existing-router performance or learned-router discoverability;
- **not** false-premise behaviour — that class is excluded (§3);
- **not** ordinary free-form temporal reasoning — see §2 on the construct.

---

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
reported as an **exact Clopper-Pearson upper bound on the share of discordant
items that are baseline-favouring** — a statement with content. If the control
class shows harm comparable to the primary classes, the correct reading is a
generic tool-use tax (wrapper differences, latency, budget language, broken
retrieval) rather than anchored displacement.

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

## 6. The retrieval treatment

CLOSED and RETRIEVAL wrappers are byte-identical except the retrieval
intervention, verified by diff at preflight.

**The FD-1 contradiction is resolved permanently for this experiment: the closed
arm's packet contains no `SEARCH BUDGET` line and no reference to tools it does
not have.** Prior experiments carried a phantom budget instruction in a
no-tool arm; that text does not appear here.

Logged per trial, with observed telemetry authoritative over model self-report:
actual query text, query count, returned evidence/snippets, tool success, tool
failures, timing, model snapshot, token counts, answer length, environment state.

---

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

A class advances to Stage 0B iff its Holm-adjusted p <= 0.05, its discordant
count is at least 8, and query logs show no systematic construction defect.
Confirmation is powered for a **smaller** effect than discovery observed, because
discovery selects the largest.

---

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

---

## 14. What would invalidate this specification

Honest failure modes, listed so they are not discovered late: class purity below
~70% (power collapses); anchoring proving to suppress the effect (a null would be
uninterpretable); the negative control showing harm comparable to the primary
classes (indicts a generic tool-use tax); void rate above 10%.
