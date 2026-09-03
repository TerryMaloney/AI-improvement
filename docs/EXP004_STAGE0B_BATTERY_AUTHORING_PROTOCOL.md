# Stage 0B battery-authoring protocol

**Status: DRAFT. Authoring has NOT started and is NOT authorized.**

> **AMENDED 2026-09-03 (pre-calibration reconciliation) — §0 supersedes six
> statements in the text below.** This protocol was written before anyone had
> executed the live search runtime. Six of its sentences described a runtime that
> does not exist. They are marked in place and superseded in **§0**, not edited
> away, because how they came to be believed is part of the record: every one of
> them was a reasonable inference from the design draft, and every one of them was
> falsified by looking.

This protocol exists so that when authoring does start, the rules are already
frozen. Stage 0A-M's failure was not that its battery was badly authored; it was
that the battery's difficulty and treatment-sensitivity were **assumed** and
never measured before 130 dispatches were spent on it.

Prerequisite: `docs/EXP004_STAGE0B_DESIGN_DRAFT.md` §10 items 1–3 must be done
first. Until then this document is a specification, not a procedure to run.

---

## 0. Stale pre-runtime assumptions, superseded on measurement (2026-09-03)

Nothing here is a correction of an authoring judgement. Every entry is a claim
about the **search runtime** made before the runtime was executed.

| # | as written | measured reality | where the correction lives |
|---|---|---|---|
| 1 | §4.2 "≥ 1 of the **top-5 results** containing a reject alias" | There are no result *texts* to rank. The runtime block is a query echo, a `Links:` array of **titles and URLs only**, and a **prose answer synthesised inside the search system**. "Top-5 results" names an object that does not cross the boundary. | §4 clause 2, rewritten to the realized representation |
| 2 | §4.1 "records the **raw result block**" (implying the searcher returns it) | The searcher model *retells* the block: it reformats into markdown, drops the header and the trailing imperative, and duplicates the source list. **Nothing byte-identical survives the model.** The recorded artifact is the runtime's own `tool_result`, read from `--output-format stream-json`. | §4.1, rewritten |
| 3 | whole-block reject matching (the natural reading of clause 2) | Containment fires on incidental text: on the real Lovelace block the reject alias `1852` matched inside the link title "Ada Lovelace (1815 - 1852)", a date range asserting nothing. A whole-block rule would have spent a production slot on a foregone null. | `divergent` requires the alias in the **synthesised summary**; `reject_in_links_only` records the weak signal |
| 4 | §3 "the realized `c_disp`" | `c_disp` said "retrieved content carries displacing information". **No retrieved page content crosses the boundary at all.** Renamed `q_exposure`, and split by arm into `q_C` and `q_D`. | §3.1; `lab/stage0b_calibration.py:PARAMETER_GLOSSARY` |
| 5 | §3 "Run the calibration bank only, **closed-book**" | Closed-book dispatches measure `p` and nothing else. They cannot measure `q_C` (needs a query-writer and a C search), `q_D` (needs the fixed search), or the grader's behaviour on **exposed** answers — the one grader parameter the power model calls design-breaking. | §3.1, the six-dispatch structure |
| 6 | §1 "calibration bank ≥ 3× production" and "50 primary + 20 control" | Neither number was derived anywhere in the repository. | §1.1 and §3.1 |

**A seventh assumption is *not* listed, because it survived measurement:** the
probe is genuinely pre-treatment — it dispatches no answerer and produces no
outcome, and the persisted artifact asserts both.

**And one that must not be repaired by wishing:** two dispatches of an identical
query return **different bytes** (the synthesised paragraph varies; the `Links:`
array did not). A per-item artifact SHA is *provenance* — this item saw this
block — and is never a reproducibility guarantee. Any authoring rule that would
require re-running a search and getting the same block back is unimplementable
and must not be written.

---

## 1. The three pools, and the wall between them

| pool | size | may enter production? | what it is for |
|---|---:|---|---|
| **calibration bank** | **36 screen-passing items in batch 1, cap 84** (§1.1) | **NEVER** | measuring `p`, `q_C`, `q_D`, the screen pass rate `s`, and the grader's defect rate on fresh **closed and exposed** answers |
| **production pool** | **n primary re-derived from calibration + `negative_control_n(n)` controls** — 50 + 30 at the current design point (§1.1) | yes, if it passes §4 | the experiment |
| **reserve** | ≥ 10 | only as documented replacements for items withdrawn *before* any dispatch | replacing items that fail the §4 screen |

### 1.1 Both size rules are now derived. `lab/stage0b_calibration.py`; tests `tests/test_stage0b_calibration.py`.

**The negative control: 30, not 15 and not 20.** Both prior numbers are in the
repository and neither was computed from what the control has to establish.

- **15** was Stage 0A-M's *realized* `arithmetic_control` class size (15/15, D=0,
  bound 0.181), carried into `lab/stage0b_power.py` unchanged. It is a
  description of a past run, not a requirement.
- **20** was design draft §8: reuse those 15 and add 5 fresh ones so an exposure
  effect would be *visible*. The reuse argument is sound; the count was never
  checked.

**What the control must establish**, per the frozen code's own docstring
(`lab/stage0am.py:harm_rate_upper_bound`): an exact upper bound on the **generic
exposure tax** — how often mere exposure flips a correct closed-book answer on
items where the exposure cannot be relevant. In Stage 0B it is the **only** handle
on that tax, because the divergence screen admits only divergent items to
production, leaving no dosed-vs-undosed contrast inside the primary class.

**The derivation.** The primary cannot reject at all below D=5 discordant pairs
(one-sided exact floor at α=0.05), which at n=50 is a realized harm rate of
**0.10**. A clean control must exclude a generic tax that large, so its 95%
Clopper-Pearson upper bound at zero harms must be strictly below 0.10:

| n | clean 95% upper bound | clears 0.10? |
|---:|---:|---|
| 15 | 0.181 | no |
| 20 | 0.139 | no |
| 25 | 0.113 | no |
| **29** | **0.098** | **yes — the exact minimum** |
| 30 | 0.095 | yes |

**Chosen: n = 30** — the derived minimum 29, taken up one so the composition stays
**15 reused `arithmetic_control` items + 15 fresh**, which is design draft §8's
rule with a count behind it. The rule is a *function of the primary n*, not a
constant: if power re-derivation raises n primary, the control is recomputed as
`negative_control_n(n_primary)`.

**Declared brittleness, with its reporting rule fixed now.** A single harm in the
control lifts the bound to 0.149, above the threshold. That is **not** bought off
with more items. If the control shows any harm, the primary result is reported
with the generic exposure tax **explicitly not excluded** — stated in the same
sentence as the primary p-value.

**The calibration bank: derived from the decisions it resolves, not from a
multiplier.** See §3.1. The old "≥ 3×" rule is retired; it had no derivation
anywhere in the repository and was wrong in both directions at once.

**The wall.** A calibration item may never become a production item, under any
circumstance, including "it turned out to be a good item". The wall is what makes
the difficulty screen a pre-treatment operation instead of outcome selection: no
item whose closed-book outcome has been observed can reach the primary sample.

**Recorded, not asserted.** Every pool assignment is committed with the item, so
the wall is auditable from the repository rather than from a claim in a document.

---

## 2. Item recipe

An item is a candidate iff all of the following hold. Each is checkable by a
third party from the item text and key alone.

1. **Anchored stem.** The stem names an explicit anchor — a date, an edition, a
   definitional scope — such that the requested answer differs from the
   present-day or default-scope answer.
2. **A single displacing answer.** Exactly one principal wrong answer is implied
   by the mechanism (the current officeholder, the current value, the
   alternative-definition quantity). It is enumerated in the key as `rejects`.
3. **Separation invariant.** For numeric items, every reject lies strictly
   outside the accept band. Enforced by test, as in Stage 0A-M.
4. **Uncontested premise.** The stem admits no defensible reading under which the
   correct answer is "none", "undefined" or "it depends".
   *This clause exists because of `a08`*: asked how many planets the IAU
   recognised on 1 January 2006, Opus 5 opened with *"Strictly speaking, none —
   because on that date the IAU had no formal definition"*, which is a defensible
   reading the key did not admit. An item whose premise the model contests is not
   measuring displacement; it is measuring disagreement about the question.
5. **Answer-first compatible.** The correct answer must be statable in one
   leading sentence under 240 characters. *This clause exists because of `b18`*,
   whose answer sat ~360 characters into a single sentence.
6. **Route declared at authoring time**, from `{exact_entity, numeric, boolean}`.
   No runtime route escalation and no judge.
7. **Key provenance** per `docs/ANSWER_KEY_CORRECTION_PROCESS.md`, recorded
   before any dispatch. No re-keying after exposure.

### 2.1 Boolean items carry an extra constraint

Stage 0A-M's boolean route was asymmetric: `expected=False` items were robust,
`expected=True` items were exposed to any later negation token. Six of seven
items expected `False`, which hid a 50% false-negative rate on the exposed half.

> **Boolean items must be balanced within ±1 between `expected=True` and
> `expected=False`**, so that a polarity-asymmetric grading defect is visible in
> the class rather than concealed by the class's composition.

---

## 3. Calibration — what it measures, and what size makes it measurable

~~Run the **calibration bank only**, closed-book, R=1, fresh context per trial,
graded by the candidate grader at its current fingerprint.~~
**SUPERSEDED 2026-09-03 (§0 row 5).** Closed-book dispatches measure `p` and
nothing else. R=1 and fresh context per trial survive unchanged.

- **Target band: 0.90 ≤ closed-book accuracy ≤ 1.00.** Unchanged, and still
  derived rather than assumed: `runs/exp004_stage0b_design/power_simulation.json`
  shows 80% power needs n=54 at p=0.95 and n=65 at p=0.80, and is **unreachable at
  n ≤ 120** for p ≤ 0.65, because repairs cancel harms in a one-sided paired test.
  Harder items do not add information; they add cancellation.
- If the realized band is below 0.90, the recipe is too hard and is revised —
  **the recipe, never the production pool**.

Calibration is also the grader's first exposure to answers that are not Stage
0A-M's. The candidate grader must not be frozen before this: it has so far been
validated against 130 answers from a battery it was designed after.

### 3.1 The four decisions the bank exists to resolve, and the size each forces

`lab/stage0b_calibration.py`; `python -m lab.stage0b_calibration` →
`runs/exp004_stage0b_design/calibration_plan.json`.

| decision | statistic | what measuring it requires |
|---|---|---|
| does the recipe meet the target band? | `p`, and its 95% one-sided **lower** bound | 1 closed-book answerer per item |
| how large must production be? | `q_C` **on the C arm**, and the grader-defect bound | 1 query-writer + 1 C search per item |
| can the grader be frozen? | `g_one`, `g_both` on **fresh, including exposed** answers | 2 exposed answerers per item |
| is the C-vs-D claim authorized? | `q_C`, `q_D`, `p` | 1 fixed-query search per item |
| how many items must be authored per usable item? | `s`, the screen pass rate | the fixed-query search, on **every authored item** |

**`q_C` replaces `c_disp`, and the fixed-query rate cannot substitute for it.**
`c_disp` named "retrieved content carrying displacing information"; no retrieved
page content crosses the boundary. The parameter is defined on the representation
that does:

> **`q_C`** = P(the C-arm injected block's **runtime-synthesised summary** contains
> at least one predeclared reject alias, **given the item passed the fixed-query
> divergence screen**).
> **`q_D`** = the same for the frozen fixed query — and on the production pool it
> is **1.0 by construction**, because the screen admits on exactly that condition.
> It is never estimated.

The primary A-vs-C power calculation reads `q_C`. Arm D executes a different
query and produces a different block; substituting D's rate for C's is the
hypothesis assumed rather than measured.

**`delta` is NOT measured in calibration.** It is the quantity the experiment
exists to estimate, and estimating it on calibration items would size the run on
a first look at its own effect. It stays the preregistered minimum interesting
effect, 0.30.

### 3.2 The minimum dispatch structure, screened first

Every calibration estimand is **conditional on screen-passing**, because every
production item is. An item the screen rejects is not a cheaper calibration item;
it is a different population, and it contributes to `s` and to nothing else. So
the screen runs first and the other five dispatches only on passers.

| stage | dispatch | buys | measured cost |
|---|---|---|---:|
| 1 — every authored item | D fixed-query search | the screen, and `s` | $0.0640 |
| 2 — passers only | closed-book answerer | `p`; grader behaviour on fresh **closed** answers | $0.0164 |
| 2 | query-writer | the C query — without it `q_C` does not exist | $0.0136 |
| 2 | C model-query search | **`q_C`, from the correct arm** | $0.0640 |
| 2 | C exposed answerer | one closed/exposed grader pair, (A,C) | $0.0276 |
| 2 | D exposed answerer | the second pair, (A,D) — the cheapest pair in the design | $0.0276 |

**Deliberately absent.** No exposed answerer is bought to estimate exposure
divergence: divergence is measured on the **block**, before any answerer exists.
The two exposed answerers are bought by the *grader* objective and by nothing
else, which is why there are exactly two. No repeat dispatch of a query, because
the artifact is not reproducible and no sizing decision reads runtime variance.

### 3.3 The finding that sizes the bank, and it is not comfortable

Grader **asymmetry** dominates everything else. At n=50, α=0.05, p=0.95,
q_C=0.50, δ=0.30, power stays ≥ 0.80 only while `g_one` ≤ **0.014**:

| `g_one` | power at n=50 | n for 80% |
|---:|---:|---:|
| 0.000 | 0.858 | 46 |
| 0.014 | 0.801 | 50 |
| 0.040 | 0.710 | 59 |
| 0.080 | 0.607 | 72 |
| 0.100 | 0.567 | 78 |

Bounding `g_one` below 0.014 with zero observed defects needs **213 clean pairs**
— four times the production run. **Calibration cannot certify that the grader is
good enough for n=50, at any affordable size.**

So the design does the only honest thing left: **it measures the bound it can
reach and sizes production AT that bound.** `q_C` enters sizing at its point
estimate (an unbiased measurement of the environment, whose error moves power
either way); `g_one` enters at its 95% **upper** bound (an instrument defect, and
the one lesson Stage 0A-M paid 130 dispatches for is that a grader defect is never
assumed small — design draft §7.1). The consequence is a production n **larger
than 50**, and that is a result, not an overrun.

**What makes the bound affordable:** one calibration item yields **two**
closed/exposed pairs, (A,C) and (A,D), not one. They are exchangeable for this
parameter because the answering packet, the block format and the answerer agent
are byte-identical between C and D — only the query differs. The licence is
**checkable**: the two pair-wise defect counts are reported separately, and a
large split between them falsifies the pooling and forces the bound onto C pairs
alone.

### 3.4 The sequential plan, frozen before the first dispatch

Legitimate only because all four conditions hold: calibration items can **never**
enter production; the stopping rules below are frozen **now**; stopping depends
only on the statistics enumerated in §3.1; and no production outcome exists.

| | authored | screen-passing | dev | holdout | dispatches | cost |
|---|---:|---:|---:|---:|---:|---:|
| **batch 1** | 48 | 36 | 12 | 24 | 228 | **$8.44** |
| batch 2, 3 (each, only if triggered) | 32 | 24 | 8 | 16 | 152 | $5.63 |
| **maximum** | 112 | **84** | — | — | 532 | **$19.69** |

**The development/holdout split is made on the AUTHORED list, before any
dispatch** — 16 development / 32 holdout in batch 1 — so that which items land in
the holdout does not depend on which items the screen passed. At the canary pass
rate that yields the 12 / 24 screen-passing split above; if it does not, the
realized split is recorded and the bound is computed on whatever the holdout
actually holds.

The cap is where the calibration bank costs about what the production run costs.
Spending more on calibration than on the experiment is not caution; it is a
different experiment.

### 3.5 PASS / CONTINUE / REVISE — fixed now, not after the data

Implemented as `lab.stage0b_calibration.decide`, fingerprinted with the
instrument, and pinned by `tests/test_stage0b_calibration.py`. **The evaluation
order is part of the rule**: a recipe that fails cannot be rescued by a grader
repair.

**PASS** — all three hold, and it authorizes the grader freeze and the power
re-derivation:
1. `p` 95% lower bound ≥ **0.90**;
2. **zero** grader defects on the holdout, with `g_one` 95% upper bound ≤ **0.08**
   (the loosest bound keeping the re-derived n inside the affordable cap of 90);
3. re-derived production n ≤ **90**.

**CONTINUE** — run the next batch when the shortfall is one more items could fix:
the `p` bound has not yet cleared 0.90 though the point estimate has; the grader
bound is loose only for want of pairs; the required n exceeds 90 *only* because of
the grader bound; or the grader changed after the holdout was scored, in which
case a **fresh holdout** is required.

**REVISE ITEM RECIPE** — the point estimate, not the interval, is the problem, and
more items cannot move it:
- `s` < **0.40** — authoring the screened items the run needs would cost more in
  screen dispatches than the whole production run;
- `p` < **0.90** on ≥ 30 items — too hard, and harder items add cancellation;
- `q_C` < **0.15** — required n > 156 even with a perfect grader; the C arm cannot
  be dosed.

**REVISE GRADER** — any defect on the **holdout**. The repair is stated as a
*general semantic rule*, implemented in `lab/grading_v2.py`, and re-run against
(i) the frozen Stage 0A-M 130-answer regression corpus with **zero** regressions,
(ii) the 28-case hand-derived semantic corpus, and (iii) the development subset.
The holdout that revealed the defect has now informed the repair and is **spent**;
validation requires a fresh one. See §3.6.

**REVISE STAGE 0B DESIGN** — the estimand itself is out of reach: required n > 120
**even with a perfect grader**, or the cap of 84 screen-passing items is reached
with PASS still unmet.

### 3.6 The grader development / validation wall

The trap is named so it can be avoided: *"the grader failed, so we edit it until
these answers pass."* Three rules close it.

1. **Adjudicate before grading.** For every calibration answer the hand-derived
   verdict is recorded **first**, and the ledger row asserts
   `hand_verdict_recorded_first`. A grader defect is then a disagreement between
   two things written down in a fixed order, not a judgement made after seeing
   which way it went. A row graded without that flag, or without a recorded grader
   fingerprint, is a schema error.
2. **Repairs come from the development subset only.** A repair must be expressible
   as a general semantic rule about answer form, not as a fix for a particular
   answer. Rules derived from a holdout answer burn the holdout.
3. **The bound comes from the holdout only.** Development answers may find
   defects; they may never bound the rate, because the grader was changed in
   response to them.

No production item may be used for either purpose, ever.

---
## 4. The frozen selection rule

Written and committed **before the screen runs**. An item enters production iff:

1. it satisfies every clause of §2;
2. ~~its **retrieval-divergence probe** returns ≥ 1 of the top-5 results
   containing a reject alias or a reject value;~~
   **REWRITTEN 2026-09-03 to the realized representation (§0 rows 1 and 3).** Its
   **retrieval-divergence probe**, executing the item's frozen **fixed** query,
   returns a block whose **runtime-synthesised summary** contains at least one
   reject alias or reject value. A match that appears **only** in the `Links:`
   array is recorded as `reject_in_links_only` and **does not** admit the item:
   measured on the real Lovelace block, the reject alias `1852` matched inside the
   link title "Ada Lovelace (1815 - 1852)", a biographical date range that asserts
   nothing and could displace nothing. The summary is where the runtime makes a
   *claim*; a link title is not a claim. Implemented at
   `lab/stage0b_search.py:relevance_flags`, field `divergent`;
3. it passes the grader's span parser on ≥ 3 synthetic paraphrases of the correct
   answer, at least one of which carries trailing successor context;
4. no production solver has ever seen it.

### 4.1 What the divergence probe is, and why it is pre-treatment

The probe executes the item's **fixed query** (per the design draft §5) and
records **the runtime's own `tool_result` block**, read from
`--output-format stream-json`. ~~through the searcher and records the raw result
block~~ — **corrected 2026-09-03 (§0 row 2)**: the searcher model *retells* the
block rather than returning it, so its prose is kept for audit and is never data.
The searcher is reduced to the one thing the harness cannot do itself, issuing
the tool call, and whether it issued the *requested* query is checked by byte
equality against `tool_use.input.query`.

**No solver is dispatched. No answer is generated. No outcome exists.** It
measures a property of the world and the search index, not of the model.

**The block is not reproducible, and the probe does not pretend otherwise.** Two
dispatches of an identical query return a different synthesised paragraph. The
recorded SHA is per-item provenance — *this item was screened on this block* — and
is never re-checked by re-running the search.

That is what makes it pre-treatment. It is nonetheless logged in full — query,
raw block, block SHA, relevance flags — because "pre-treatment" is a claim that
must be inspectable rather than asserted.

### 4.2 What the rule may never do

- It may never read a solver outcome on a production item.
- It may never select on reversal prevalence — reversal is an outcome.
- It may never be revised after any production dispatch. If it proves wrong, the
  stage restarts with a new rule and a new pool.
- It may never be applied by a model's judgement. Every clause is mechanical.

### 4.3 Estimand

**Finite-selected-set.** The claim is about the selected items, not a
superpopulation of anchored questions. Selection is deterministic given the
frozen rule and the probe log, so the finite-set estimand is well defined, and
the design makes no exchangeability claim it cannot support.

---

## 5. Fingerprints required before the first production dispatch

| artifact | fingerprint |
|---|---|
| battery (stems + keys) | sorted-key SHA-256, first 16 hex, as in `lab/stage0am_fingerprint.py` |
| grader `lab/grading_v2.py` | file SHA-256:16, pinned by the semantic golden corpus |
| fixed-query table (item → query) | file SHA-256:16 |
| divergence probe log | file SHA-256:16 |
| dispatch schedule | file SHA-256:16 |
| answering packet, per arm | file SHA-256:16, plus an asserted diff |
| searcher agent body | file SHA-256:16, byte-identical across C and D |
| **freeze/grade/analyse driver** | file SHA-256:16 — **committed before the first dispatch**, not during the run (Stage 0A-M's driver was first committed with 33 outcomes already on disk) |
| **calibration decision rules** `lab/stage0b_calibration.py` | file SHA-256:16, in `instrument_fingerprints.json` — **committed before the first CALIBRATION dispatch**, for the same reason the grader is fingerprinted: a stopping rule that can be edited once the data arrives is not a stopping rule |
| calibration ledger (§7) | file SHA-256:16, written as the bank runs |

---

## 6. What this protocol is guarding against

Each rule traces to a measured Stage 0A-M failure, so none of them is a
precaution in the abstract:

| rule | the failure it prevents |
|---|---|
| calibration bank with a hard wall | a battery at complete ceiling (130/130 under a repaired grader) reaching production unmeasured |
| uncontested-premise clause | `a08` |
| answer-first-compatible clause | `b18` |
| boolean polarity balance | the hidden `a09` false-negative class |
| divergence probe | authoring for anchoring pressure in the stem while never checking the results carry displacing content |
| re-derive power from measured values | sizing on an assumed p=0.85 that turned out bimodal at 1.00/1.00/0.40 |
| driver committed before dispatch | the one real provenance window in Stage 0A-M |
| the calibration parameters named for what crosses the boundary (§3.1) | `c_disp` survived a design pass, a red-team and a causal-contract pass while naming content that does not exist on this path |
| the negative-control count derived from the bound it must beat (§1.1) | two different unjustified numbers, 15 and 20, sat in the repository at once, and neither excluded a generic exposure tax the size of the entire primary signal |
| decision rules frozen and fingerprinted before the bank runs (§3.5) | there is no Stage 0A-M failure for this one. It is the failure this pass exists to prevent: a later session inventing thresholds after seeing calibration outcomes |
| adjudicate before grading (§3.6) | the same |

---

## 7. The calibration ledger row

`lab/stage0b_calibration.py:CalibrationRow`; schema errors are raised by
`validate_row` and pinned by `tests/test_stage0b_calibration.py`.

**Every quantity that later feeds power has lineage to a recorded field.**
`REQUIRED_FOR_EACH_STATISTIC` maps each statistic to the fields it is computed
from, and a statistic with no entry there may not be computed at all — that is
the rule Stage 0A-M lacked when `analyse_run` built `retrieval_failure_rate` out
of empty tuples and reported a plausible number with no lineage.

| group | fields |
|---|---|
| identity and the wall | `item_id`, `pool` (always `calibration`), `subset` (`development` \| `grader_validation_holdout`), `batch`, `production_barred` (always `True`, asserted **per row**) |
| the item | `stem`, `route`, `accept_aliases`, `rejects`, `key_provenance`, `query_subject`, `anchor_as_written` |
| stage 1 — the screen | `fixed_query`, `d_raw_artifact_sha`, `d_injected_block`, `d_injected_block_sha`, `d_relevance`, **`d_divergent`**, `d_reject_in_links_only`, `d_query_faithful`, `screen_passed` |
| stage 2 — the C arm | `model_written_query`, `c_raw_artifact_sha`, `c_injected_block`, `c_injected_block_sha`, `c_relevance`, **`c_divergent`** (`q_C`'s numerator), `c_reject_in_links_only`, `c_query_faithful` |
| the three answers | `closed_answer`, `c_exposed_answer`, `d_exposed_answer` |
| adjudication, recorded **first** | `hand_verdict_closed/_c/_d`, `hand_verdict_recorded_first`, `hand_adjudicator` |
| the candidate grader | `grader_fingerprint`, `grader_verdict_closed/_c/_d` |
| derived, never entered by hand | `defect_closed`, `defect_c`, `defect_d` |
| provenance, keyed by stage | `served_models`, `configured_effort` (the realized command line), `realized_tool_surface`, `web_search_requests` — **`sum(modelUsage[*].webSearchRequests)`, never `usage.server_tool_use`** — `cost_usd`, `session_ids` |
| failure | `failure`, `failure_stage` |

`None` means **NOT OBSERVED**, exactly as in
`lab/stage0b_harness.py:DispatchRow`. It never means zero and it never means
`False`.

**Four schema errors that are refused rather than warned about:** a row whose
`pool` is not `calibration`; a row with `production_barred` false; a row graded
without `hand_verdict_recorded_first` or without a `grader_fingerprint`; and a row
with `screen_passed` true whose `d_divergent` is not true.
