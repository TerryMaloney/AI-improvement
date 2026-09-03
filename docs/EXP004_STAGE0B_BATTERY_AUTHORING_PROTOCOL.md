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

### 0.1 Second red team, same day — two of the corrections above were themselves wrong

The reconciliation at `120620c` fixed six pre-runtime assumptions and introduced
two defects of its own. Both were load-bearing, and both are corrected here.

| # | as written at `120620c` | why it was wrong | where the correction lives |
|---|---|---|---|
| 7 | "one calibration item yields **two** closed/exposed grader pairs, (A,C) and (A,D) ... pooled, so 24 holdout items → 48 pairs" | **Exchangeability is not independence.** Both pairs are built from the SAME closed-arm verdict on the SAME closed-arm answer, so a single closed-arm defect produced two counted events — the same draw written down twice. A Clopper-Pearson bound at n=2m assumes 2m independent trials, so the interval was **narrower than the evidence supports**, and an instrument-defect bound that is too narrow **under-sizes production**. It also bounded the wrong estimand: `g_one` is a property of the A-vs-C pair, because A-vs-C is the primary. | §3.3, and `lab/stage0b_calibration.py:ac_pair_defect` |
| 8 | "`q_D` = 1.0 **by construction** on the production pool" | The screen tests **one execution** of the fixed query. This repository already recorded that the artifact is **not reproducible**, and `lab/stage0b_harness.py:run_arm` executes arm D's fixed query **freshly at answering time**. The screened block is never the injected block, so `q_D = 1` was true of an artifact the experiment never uses. | §3.1a, and the `r_D` parameter |

Two further items from the same review are corrected without being defects of
fact: the p-rule tested a claim the design never made (§3.5a), and
`Q_GAP_PREREGISTERED` claimed a preregistration Stage 0B does not have (§3.7).

### 0.2 Fourth pass — the pre-dispatch check refused to author anything, and it was right

The calibration-run attempt stopped before authoring an item, dispatching once or
spending a cent, because the committed ledger **could not carry the key its own
adjudication needs**.

| # | as committed | why it blocks execution | corrected in |
|---|---|---|---|
| 9 | `CalibrationRow` carries one pair, `accept_aliases` / `reject_aliases` | `reference_verdict` needs `expected` for a boolean item and `value`/`tolerance`/`reject_values` for a numeric one. Neither existed, so those routes raised `KeyError` — **after** the dispatches were paid for | §2.2, `lab/stage0b_keys.py:AnswerKey` |
| 10 | the same pair also decided whether the search summary carried the dose | the two jobs coincide only on `exact_entity`. On boolean, the accept alias `"no"` matches inside `"not"` and the reject alias `"yes"` never appears as a claim; on numeric, a bare numeral matches years, ranges and citations | §2.3, `lab/stage0b_keys.py:ScreenSpec` |
| 11 | no calibration driver existed | protocol §5 requires it committed **before** the first dispatch, and the contract had it `[OPEN]` | §8, `lab/stage0b_calibration_runner.py` |
| 12 | recipe clause 7 demanded key provenance without defining how to obtain it | a calibration result is meaningless if the supposedly correct answer is wrong, and both `p` and the grader defect rate are measured against these keys | §2.4 |
| 13 | route composition was unconstrained | `grading_v2` is three mechanisms and Stage 0A-M produced a defect in two of them; an aggregate `g_one` over an arbitrary mixture is a mean over three failure modes | §3.9 |

**The escape that was refused:** authoring an entity-only bank would have dodged
9 and 10 at a stroke. It was rejected because the only grader defect this project
has ever measured was on the **boolean** route — the `a09` polarity class that hid
a 50% false-negative rate — so an entity-only bank cannot detect a recurrence of
the one failure mode actually observed, while reporting a bound that looks
complete.

**A ninth assumption is *not* listed, because it survived measurement:** the
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

**The count is PROVISIONAL, and 30 is not a commitment.** The rule is a *function
of the primary n*, and the primary n does not exist yet — it is re-derived from the
calibration bank, and the design draft's n=50 is itself superseded (§13.4). The
same rule gives:

| primary n | control n | clean bound |
|---:|---:|---:|
| 50 (superseded draft figure) | **30** | 0.095 |
| 66 | 40 | 0.0739 |
| **72 (currently expected)** | **42** | 0.0688 |
| 90 (affordability cap) | 54 | 0.0550 |

At n_primary=50 the derived minimum is 29, taken up one so the composition stays
**15 reused `arithmetic_control` items + 15 fresh** — design draft §8's rule with a
count behind it. **No control item is authored until production n is fixed.** The
figure quoted throughout these documents is the one at n_primary=50 because 50 is
the draft's recommendation, not because 30 has been committed to.

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

### 2.2 The answer key is typed, and every route can rebuild its own

`lab/stage0b_keys.py:AnswerKey`. What makes a **solver answer** correct.

| route | key | validated |
|---|---|---|
| `exact_entity` | `accept`, `rejects` | both non-empty; no accept alias may contain a reject alias or vice versa, since no positional rule could then separate them |
| `boolean` | `expected: bool` | present. `route="boolean"` with no `expected` is refused — it is the exact combination that made a boolean item unadjudicatable |
| `numeric` | `value`, `tolerance`, `reject_values` | all present; every reject strictly outside the accept band (clause 3); an undetermined tolerance is an authoring failure, not a value to guess |

Cross-route fields are refused in both directions. `key_for_route()` on a
persisted row reconstructs exactly the dict `reference_verdict` consumes, so a row
is self-sufficient — which is the property whose absence stopped the last run.

### 2.3 The exposure-screen specification is a DIFFERENT object

`lab/stage0b_keys.py:ScreenSpec`. What makes the runtime's **synthesised summary**
count as carrying the dose. It is matched against prose written by a different
process for a different purpose, so it is not the answer key and it is not stored
in the same field.

| route | mechanism |
|---|---|
| `exact_entity` | `displacing_aliases` / `affirming_aliases`. Entity names do identify the proposition when the entity *is* the answer |
| `boolean` | `displacing_propositions` / `affirming_propositions` — phrases carrying subject **and** predicate. Bare polarity is refused outright |
| `numeric` | `subject_terms` plus value surface forms. A numeral counts only when it sits within `proximity_chars` of a subject term, outside every excluded context |

**Invariant S1**, committed before any item is authored:

> A screen phrase must be capable of occurring **only** where the summary asserts
> the proposition or value it stands for. (i) No bare polarity token. (ii) No
> phrase that is a substring of a phrase on the opposite side, either direction.
> (iii) A boolean phrase must carry a subject and a predicate. (iv) A numeral
> counts only through the structured numeric mechanism, never as a bare substring.
> (v) A match preceded within 24 characters by a negator is a **denial** and does
> not count.

S1(v) is why `"Finland was not a member of NATO"` does not read as the displacing
claim. Without it the boolean screen fires on correct denials — which is C1(b)'s
lesson (`"Poland and"` matching inside a correct denial) arriving on a new route.

**C1 scope, stated rather than broadened.** Correction C1 governs the
`accept_trap_markers` and `reject` fields of the exp001 key, matched against a
**model answer**. C1(a) (bare topic word) and C1(b) (bare entity fragment)
transfer unchanged. **C1(c)'s flat prohibition on bare numerals does not
transfer**: it governs strings matched against an answer, where a numeral cannot
discriminate, whereas the Stage 0B numeric screen matches a **search summary**
through subject-proximity and context exclusion, which *can* show a numeral is
asserted of the requested quantity. Declaring C1(c) universal would broaden a rule
past the evidence that motivated it and would make the numeric route unscreenable
rather than rigorous. S1 is the Stage 0B rule instead, and `tests/test_stage0b_keys.py`
enforces it.

### 2.4 Key verification, before any item is frozen

A calibration result is meaningless if the supposedly correct answer is wrong —
and both `p` **and** the grader defect rate are measured against these keys.

**The source rule.** One **authoritative primary** source settles an item on its
own: the body that defines or publishes the fact. Where none is available, **two
independent reputable** sources must corroborate — independent meaning not
republications of one another. There is no blanket two-source rule; demanding a
second source where a definitive primary one exists buys nothing and invites
padding the evidence list.

**Recorded per source**, and validated mechanically: `identifier`, `title`,
`establishes` (which proposition or value it settles), `accessed`, `tier`,
`verifier`.

> **Key-construction evidence is not experimental evidence.** A query used to
> **verify a key** may never become that item's fixed experimental query. The
> fixed query is derived from the stem alone by the frozen rule, checkable by a
> third party. Letting a verification query that "worked well" become the
> treatment would optimise the dose using observations made while building the
> key — authoring the treatment against the search index. Key evidence, the fixed
> query, the model-written C query and the runtime blocks are logged and
> fingerprinted **separately**.

Key evidence is quarantined from every solver, exactly as the Stage 0A-M key was.

### 2.5 Ambiguous keys fail authoring mechanically

Nobody picks the most reasonable answer. An item hitting any of these is
**rejected and persisted with its reason**, so the rejection rate is auditable and
the same defective item is not re-authored:

`CONFLICTING_SOURCES` · `ANCHOR_AMBIGUOUS` · `DEFINITION_AMBIGUOUS` ·
`TOLERANCE_UNDETERMINED` · `PREMISE_NOT_RESOLVABLE` ·
`DISPLACING_ANSWER_NOT_UNIQUE` · `SEPARATION_VIOLATED` ·
`ANSWER_NOT_ANSWER_FIRST_COMPATIBLE`

It is never repaired by widening the accept band or adding an alias — both decide
the item's outcome at authoring time. This is clause 4's uncontested-premise
requirement applied **at authoring** rather than discovered from a solver
contesting it, which is the `a08` lesson.

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
> **`r_D`** = P(a **RE-EXECUTION** of the frozen fixed query, at answering time,
> returns a block whose synthesised summary contains a reject alias | screen-passing).
> **Measured, not assumed.**

The primary A-vs-C power calculation reads `q_C`. Arm D executes a different
query and produces a different block; substituting D's rate for C's is the
hypothesis assumed rather than measured.

### 3.1a `q_D = 1.0 by construction` was false, and the repository already held the refutation

The claim rested on the screen admitting an item **iff** its fixed-query block is
divergent. But the screen tests **one execution**, and two facts already recorded
here defeat the inference:

1. **The artifact is not reproducible.** Two dispatches of an identical query
   return a different synthesised paragraph (design draft §12.3, §0 above).
2. **Arm D re-runs its query.** `lab/stage0b_harness.py:run_arm` calls
   `fixed_query(item)` and then `run_search_stage`, a fresh dispatch, at answering
   time. **The screened block is never the injected block.**

So `q_D = 1` described an artifact the experiment never uses. Three designs were
weighed before any outcome exists:

| | | verdict |
|---|---|---|
| **A** | reuse the screened D artifact — persist it and inject it | **Rejected.** It makes `q_D = 1` literally true, at the price of giving arm D a **stale** block while arm C's is contemporaneous. That breaks the one structural guarantee the C/D contrast rests on: `execute_search(query)` takes one parameter, so C and D have nothing else to differ in. Trading that away buys a true sentence about a treatment nobody runs |
| **B** | re-execute D's fixed query at answering time, and **measure** the rate | **CHOSEN.** It is what the committed harness already does, it needs no implementation change, and it keeps C and D contemporaneous and symmetric |
| **C** | freeze both C and D blocks before answer dispatch | **Rejected as unnecessary.** It buys ordering symmetry the design does not lack, at the cost of a C search on every screen failure |

**Under B the screen is a filter on item PROPENSITY, not a guaranteed dose.** It
selects items whose fixed query *tends* to return a displacing claim; `r_D` says
how often that tendency shows up again on the day. A production D trial whose
re-executed block is non-divergent is **not a failure — it is the measurement**;
voiding it would condition the sample on a realized treatment property of one arm.

`r_D` costs one extra dispatch per screen-passing calibration item: a **second**
fixed-query execution, distinct from the screen. Without it the bank would report
a divergence rate for an artifact the experiment never injects.

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
| 2 | **D production search** (a SECOND fixed-query execution) | **`r_D`** — see §3.1a | $0.0640 |
| 2 | C exposed answerer | the **(A,C)** grader pair — the unit that carries the bound | $0.0276 |
| 2 | D exposed answerer | the **(A,D)** pair as a **diagnostic** (§3.3), and the only exercise arm D's answer form gets before production, which grades arm D too | $0.0276 |

**Deliberately absent.** No exposed answerer is bought to estimate exposure
divergence: divergence is measured on the **block**, before any answerer exists.
The two exposed answerers are bought by the *grader* objective and by nothing
else, which is why there are exactly two. No repeat dispatch of a query, because
the artifact is not reproducible and no sizing decision reads runtime variance.

### 3.3 The finding that sizes the bank, and the sampling unit that carries it

Grader **asymmetry** dominates everything else. At n=50, α=0.05, p=0.95,
q_C=0.50, δ=0.30, power stays ≥ 0.80 only while `g_one` ≤ **0.014**:

| `g_one` | power at n=50 | n for 80% |
|---:|---:|---:|
| 0.000 | 0.858 | 46 |
| 0.014 | 0.801 | 50 |
| 0.040 | 0.710 | 59 |
| 0.080 | 0.607 | 72 |
| 0.100 | 0.567 | 78 |

Bounding `g_one` below 0.014 with zero observed defects needs **213 clean items**
— four times the production run. **Calibration cannot certify that the grader is
good enough for n=50, at any affordable size.**

So the design measures the bound it can reach and **sizes production AT that
bound.** `q_C` enters sizing at its point estimate (an unbiased measurement of the
environment, whose error moves power either way); `g_one` enters at its 95%
**upper** bound (an instrument defect, and §7.1 is the reason it is never assumed
small). The consequence is a production n **larger than 50**, and that is a
result, not an overrun. `p` enters at its 95% **lower** bound, the conservative
direction (§3.5a).

#### The sampling unit is the ITEM. Corrected in the second red team.

`120620c` pooled the two closed/exposed pairs of an item and applied the bound at
**n = 2 × items**. That was invalid twice over:

1. **The two indicators share a component completely.** Both pairs are built from
   the same closed-arm verdict on the same closed-arm answer. A single closed-arm
   defect produced **two** counted `g_one` events — one draw written down twice.
   Clopper-Pearson at n=2m assumes 2m independent trials, so the interval came
   back **narrower than the evidence supports**. For an instrument-defect bound
   that error runs in the dangerous direction: too narrow a bound **under-sizes
   production**.
2. **It bounded the wrong estimand.** `g_one` is a property of the **A-vs-C** pair,
   because A-vs-C is the primary comparison. An (A,D) defect describes arm D's
   answer form, and folding it in rests on an assumption about *model behaviour*
   — that C and D answers take the same form — which no packet-level symmetry
   establishes, since the two blocks differ.

**The bound is computed on the (A,C) pair only, one observation per item.** That
is the same unit the power model's own generative assumption uses. What it costs:

| holdout items | invalid claim (2×items) | valid bound (items) | n_prod claimed | n_prod actual |
|---:|---:|---:|---:|---:|
| 24 | 0.0605 | **0.1173** | 66 | **84** |
| 36 | 0.0408 | **0.0798** | 60 | **72** |

**At the old 24-item holdout, a perfectly clean result bounds `g_one` at 0.117 —
above the PASS threshold of 0.08. Batch 1 could not have passed even with a
flawless holdout.** The holdout therefore rises to **36 items**, the smallest clean
holdout whose bound reaches the threshold at all.

**The (A,D) pair is retained as a diagnostic** — it says whether an exposed-answer
defect is query-specific, and it is the only exercise arm D's answer form gets
before a production run that grades arm D too. It enters **no bound**. An
**item-level union** bound (a defect in either pair, one unit per item) is reported
alongside as a conservative companion; it bounds a larger quantity, so it can only
raise the required n, and it is never substituted for the headline.

### 3.4 The sequential plan, frozen before the first dispatch

Legitimate only because all four conditions hold: calibration items can **never**
enter production; the stopping rules below are frozen **now**; stopping depends
only on the statistics enumerated in §3.1; and no production outcome exists.

| | authored | screen-passing | dev | holdout | dispatches | cost |
|---|---:|---:|---:|---:|---:|---:|
| **batch 1** | 96 | 72 | 16 | **56** | 528 | **$21.48** |
| one further batch (only if triggered) | 32 | 24 | 6 | 18 | 176 | $7.16 |
| **maximum** | 128 | **96** | — | — | 704 | **$28.64** |

**Resized again by the route-composition repair (§3.9).** The binding constraint
is no longer the aggregate bound — that needs 36 — but the **per-route floor**:
with the smallest route at weight 0.25, a 14-item floor forces a 56-item holdout.
That is a cost increase and also a tightening: the aggregate clean bound falls
from 0.0798 to **0.0521**, which *lowers* the re-derived production n from 72 to
**63**.

**A change that is reported rather than absorbed:** at the cap, calibration now
costs about **$28.64** against a production run of about **$24.3**, so the earlier
"calibration ≤ production" heuristic **no longer holds**. What broke it is a
validity requirement, not a budget preference. Only **one** further batch fits
under the cap, so a second CONTINUE reaches it — and reaching the cap without PASS
is a REVISE_STAGE0B_DESIGN result anyway.

**The development/holdout split is made on the AUTHORED list, before any
dispatch** — 16 development / 48 holdout in batch 1 — so that which items land in
the holdout does not depend on which items the screen passed. At the canary pass
rate that yields the 12 / 36 screen-passing split above; if it does not, the
realized split is recorded and the bound is computed on whatever the holdout
actually holds.

The cap is where the calibration bank costs about what the production run costs
(at n_primary 72 plus 42 controls, 684 dispatches and ~$24). Spending more on
calibration than on the experiment is not caution; it is a different experiment.

### 3.4a Route composition, because the grader is three mechanisms

`lab/grading_v2.py` is a span parser plus **three** route mechanisms — entity
ordering, boolean first-polarity, numeric tolerance — and Stage 0A-M produced a
measured defect in **two** of them: 30 entity false negatives, and the `a09`
boolean polarity class. An aggregate `g_one` over an unconstrained route mixture
is a mean over three different failure modes, and it transfers to production only
if the production mixture is the same mixture.

**Chosen: Option A — a precommitted mixture, held identical between the
grader-validation holdout and the production pool, plus a per-route floor.**

| | |
|---|---|
| production mixture | `exact_entity` 0.50, `boolean` 0.25, `numeric` 0.25 |
| holdout mixture | **identical**, which is what makes the aggregate bound transfer |
| per-route floor | **14** items = ⌈log(0.05)/log(0.80)⌉ — a 95% chance of surfacing at least one instance of a route-specific defect occurring at rate 0.20 |
| holdout forced | **56** = 14 / 0.25, allocated 28 / 14 / 14 |
| aggregate clean bound | **0.0521**, valid for the production-weighted rate |
| per-route bounds | 0.101 / 0.193 / 0.193 — **descriptive, not relied on** |
| boolean polarity | balanced within ±1 in every subset (§2.1) |

**Why the aggregate bound is legitimate here.** With the mixtures matched, the
holdout defect count is Binomial(N, `g_one_weighted`) and the exact bound bounds
the production-weighted rate. It would **not** transfer under a different mixture,
which is why the mixture is precommitted and checked at bank level rather than
left to whatever gets authored.

**What stops a broken route hiding behind the aggregate** is not the weighting: it
is that PASS requires **zero** defects on the holdout, and every route carries at
least 14 items. A route failing at rate 0.20 has a 95% chance of tripping
REVISE_GRADER.

**Option B — route-stratified bounding — was derived and costed, not waved away.**
A weighted bound of 0.08 with `n_r ∝ √w_r` needs 44/31/31 = **106 holdout items**
against Option A's 56. It buys per-route bounds the PASS rule does not consume,
since PASS already demands zero defects. Rejected on the record, with its price,
so the choice can be re-argued rather than assumed.

### 3.5 PASS / CONTINUE / REVISE — fixed now, not after the data

Implemented as `lab.stage0b_calibration.decide`, fingerprinted with the
instrument, and pinned by `tests/test_stage0b_calibration.py`. **The evaluation
order is part of the rule**: a recipe that fails cannot be rescued by a grader
repair.

**PASS** — all three hold, and it authorizes the grader freeze and the power
re-derivation:
1. closed-book **point estimate** inside the band **[0.90, 1.00]** (§3.5a — this
   is *not* a certification that p exceeds 0.90);
2. **zero** grader defects on the holdout, with `g_one` 95% upper bound ≤ **0.08**
   — **unit: item** (§3.3) — the loosest bound keeping the re-derived n inside the
   affordable cap of 90;
3. re-derived production n ≤ **90**.

### 3.5a The p-rule tested a claim the design never made

`120620c` required the **95% one-sided lower bound** on p to clear 0.90 — a
*certification* that p exceeds the band edge. Its operating characteristics make
it unusable as a gate:

| holdout n | closed-book errors admitted | P(pass \| p=0.90) | P(pass \| p=0.95) | P(pass \| p=1.00) |
|---:|---:|---:|---:|---:|
| 36 | **0** | 0.023 | **0.158** | 1.000 |
| 60 | 1 | 0.014 | 0.192 | 1.000 |
| 84 | 3 | 0.026 | 0.390 | 1.000 |

A recipe sitting **exactly on the design point of 0.95** would fail the gate about
five times in six at n=36, drive the bank to its cap, and there be declared a
design failure. And P(pass | p = 0.90) ≤ 0.05 **by construction** of the bound: a
recipe precisely at the band edge is rejected by design.

Design draft §2.2 sets a **band on the measured accuracy**, not a certification
that its edge is exceeded. The certification is withdrawn, and p now plays two
separate honest roles:

- the **band** is checked on the **point estimate**, as written;
- **sizing** uses the 95% **lower** bound — the conservative direction, since a
  lower p means fewer at-risk items and so a larger required n.

Errors in the bank therefore cost **production items** instead of triggering a
near-certain false stop, and the affordability cap remains the binding gate. This
is a change of statistical criterion to match the intended claim, not a relaxation
made because certification was expensive.

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
  be dosed;
- `r_D` < **0.30** — a screened item's fixed query rarely re-delivers a displacing
  claim, so the screen is selecting on runtime noise rather than item propensity,
  and arm D stops doing its interpretive job;
- more than **15%** of answers escalated for `PREMISE_CONTEST` or `NO_KEY_MATCH` —
  both are recipe defects (§2 clauses 4 and 7), not grader defects.

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

### 3.7 "Preregistered" is not the word for any of this

**Stage 0B has no frozen preregistration.** The design draft says "DRAFT. Not
frozen"; the causal contract validates as `draft`. Every threshold in this
protocol is a **PRE-CALIBRATION COMMITMENT** — fixed and fingerprinted before any
calibration outcome exists, which is what makes it binding, and which is a real
but weaker claim than preregistration. They become preregistration at design
freeze, which cannot happen until the bank has run.

`Q_GAP_PREREGISTERED` is renamed **`PRECALIBRATION_COMMITTED_Q_GAP`**. It was
created at `120620c`, *after* the runtime was characterised, by restating the 0.20
displacement-scale gap committed on 2026-09-02 onto the exposure scale. Calling it
"preregistered" backdated a commitment by a day and a runtime discovery. The
lineage is preserved in `lab/stage0b_calibration.py:PARAMETER_LINEAGE`, which
records the old quantity, the old scale, the conversion and the date.

### 3.8 Who produces the ground truth

`lab/stage0b_adjudication.py`; tests `tests/test_stage0b_adjudication.py`.

The grader's defect rate is worth exactly what the verdicts it is compared against
are worth. Two tiers, and a burden stated **before** dispatch:

- **Tier 1 — deterministic reference adjudication.** Decides from the key alone, by
  a rule that is **not** the rule under test: first-occurrence order over the
  **whole** answer, and a flat 240-character opening window with no sentence
  segmentation and no abbreviation handling. It does not import `grading_v2.py`,
  and a test asserts it.
- **Tier 2 — human adjudication by Terry**, on escalated cases only.

**The honest difficulty, stated rather than designed around:** any deterministic
reference shares assumptions with a deterministic grader. A rule reading
first-occurrence order reproduces the span rule's verdict on most inputs —
*including* on the cases where the span rule is known to be wrong. Using it as
ground truth there would certify the grader against its own blind spot. So tier 1
**refuses to decide** exactly those cases:

| escalation | why a rule must not decide it |
|---|---|
| `CONTRASTIVE_NEGATION` | the grader's own documented limitation ("Not Vandermeer — Okonjo held the office") |
| `PREMISE_CONTEST` | the `a08` class; no key adjudicates a contested premise |
| `NO_KEY_MATCH` | outside the key's alias coverage, or off-topic |
| `REJECT_LEADS_ACCEPT` | genuine wrong answer, or contrastive correction — a positional rule cannot tell |
| `NO_POLARITY` | a boolean with no polarity token |
| `MULTIPLE_NUMERIC_CANDIDATES` | which value is the answer is a reading question |

**Never**: the candidate grader producing its own ground truth; the orchestrating
model adjudicating an answer whose grader verdict it has already seen; any re-run
of any grader to resolve an escalation. The first two are **schema errors** —
`validate_row` refuses a row graded without a recorded adjudicator, and refuses one
naming `grading_v2`.

> **MANUAL PREREQUISITE, flagged before dispatch rather than discovered mid-bank.**
> A 48-item batch produces 144 answers; at the forecast escalation rate roughly
> **29** of them need human adjudication, and they must be adjudicated **before**
> the candidate grader is run on them. If that burden is unacceptable, the bank is
> not dispatched — the alternative is not to skip adjudication, because a defect
> rate measured against the grader's own rule is not a measurement.

The forecast rate is a forecast: it sizes no sample and enters no bound. The
realized escalation rate is itself a recipe-quality signal, which is why two of the
escalation classes are REVISE-RECIPE triggers in §3.5.

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
| **calibration runner** `lab/stage0b_calibration_runner.py` | file SHA-256:16 — **committed before the first CALIBRATION dispatch** (§8). The PRODUCTION freeze/grade/analyse driver is a different artifact and is still unbuilt |
| answer keys + screen specs `lab/stage0b_keys.py` | file SHA-256:16. Two objects, fingerprinted together because S1 binds them jointly |
| key-construction evidence, per item | recorded and fingerprinted **separately from** the fixed-query table, so a verification query can never become a treatment (§2.4) |

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
| the answer key and the screen spec kept apart (§2.2–2.3) | one alias pair served both jobs, so a boolean item could not be adjudicated from its own row and a numeric screen matched years and citations. Found by the pre-dispatch check, before an item existed |
| key verification defined before authoring (§2.4) | clause 7 demanded provenance and named no procedure; both `p` and the grader defect rate are measured against these keys |
| route composition precommitted (§3.4a) | the grader is three mechanisms with two measured defects; an aggregate bound over an arbitrary mixture is a mean over three failure modes |
| the calibration driver committed before dispatch (§8) | it did not exist, and the protocol had required it since the Stage 0A-M review |

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
| the item | `stem`, `route`, **`answer_key`** (typed, §2.2), **`screen_spec`** (typed, §2.3 — a *different* object), **`key_sources`** (§2.4), `key_provenance`, `query_subject`, `anchor_as_written` |
| stage 1 — the screen | `fixed_query`, `d_raw_artifact_sha`, `d_injected_block`, `d_injected_block_sha`, `d_relevance`, **`d_divergent`**, `d_reject_in_links_only`, `d_query_faithful`, `screen_passed` |
| stage 2 — the C arm | `model_written_query`, `c_raw_artifact_sha`, `c_injected_block`, `c_injected_block_sha`, `c_relevance`, **`c_divergent`** (`q_C`'s numerator), `c_reject_in_links_only`, `c_query_faithful` |
| stage 2 — arm D's **production** search (§3.1a) | `d_production_raw_artifact_sha`, `d_production_injected_block`, `d_production_injected_block_sha`, `d_production_relevance`, **`d_production_divergent`** (`r_D`'s numerator), `d_production_query_faithful`, `screen_block_differs_from_production_block`. **This is the block arm D's answerer receives.** The screen's block is kept above for provenance and is never injected |
| the three answers | `closed_answer`, `c_exposed_answer`, `d_exposed_answer` |
| adjudication, recorded **first** | `hand_verdict_closed/_c/_d`, `hand_verdict_recorded_first`, `hand_adjudicator`, `adjudication_route_closed/_c/_d` (the tier-1 rule that decided, or the escalation reason that sent it to a human), `escalated_to_human` |
| the candidate grader | `grader_fingerprint`, `grader_verdict_closed/_c/_d` |
| derived, never entered by hand | `defect_closed`, `defect_c`, `defect_d` |
| provenance, keyed by stage | `served_models`, `configured_effort` (the realized command line), `realized_tool_surface`, `web_search_requests` — **`sum(modelUsage[*].webSearchRequests)`, never `usage.server_tool_use`** — `cost_usd`, `session_ids` |
| failure | `failure`, `failure_stage` |

`None` means **NOT OBSERVED**, exactly as in
`lab/stage0b_harness.py:DispatchRow`. It never means zero and it never means
`False`.

**`answer_key_typed()`, `screen_spec_typed()` and `key_for_route()`** rebuild both
objects from the row alone, so a persisted row is self-sufficient for adjudication
on every route. `FIELD_SEPARATION` records which statistic may read which, and
neither may stand in for the other.

**Bank-level invariants** no single row can carry, checked by `validate_bank`:
route composition against the precommitted mixture, the per-route holdout floor,
and boolean polarity balance.

**Schema errors that are refused rather than warned about:** an answer key that
cannot produce a reference-verdict key; a key or screen spec whose route disagrees
with the row; a screen spec violating S1; missing or non-independent key sources;
and, as before, a row whose
`pool` is not `calibration`; a row with `production_barred` false; a row graded
without `hand_verdict_recorded_first`; a row graded without a `grader_fingerprint`;
a row graded without a recorded `hand_adjudicator`; a row whose `hand_adjudicator`
names `grading_v2` (the candidate grader may never produce its own ground truth);
and a row with `screen_passed` true whose `d_divergent` is not true, or with a
production D block on an item that did not pass the screen.

---

## 8. The calibration runner

`lab/stage0b_calibration_runner.py`; tests
`tests/test_stage0b_calibration_runner.py`. Committed **before the first
dispatch**, which is what §5 requires and what did not exist.

**It exercises no scientific discretion.** It does not author an item, repair one,
choose a key, re-key after a screen, or retry a stochastic search to obtain a
better result. Where a committed rule does not cover a case it records a failure
and stops. An improvising driver is an unlogged experimenter.

### 8.1 Lifecycle

| stage | what it does |
|---|---|
| `--stage validate` | loads the authored bank and checks every row and every bank-level invariant. **Refuses to dispatch against an invalid bank** rather than repairing it |
| `--stage screen` | one fixed-query execution per authored item, no answerer. The raw artifact is persisted **before** any flag is derived from it |
| `--stage answer` | on screen passers only, six dispatches in a fixed order: closed A · query-writer · C search · **D production search** · C answer · D answer |
| `--stage adjudicate` / `export-queue` | deterministic reference adjudication, then the frozen human queue |
| `--stage import-verdicts` | validated import of Terry's C/I/A, with attribution |
| `--stage status` | ledger counts, screen pass state, queue fingerprint, and the grading-authorization verdict |
| `--dry-run` | swaps in the synthetic backend; makes **no paid call** |

### 8.2 The ordering it makes impossible to skip

```
authored bank → screen → answers → reference adjudication
              → human queue → HUMAN VERDICTS → candidate grading
```

`authorize_grading()` is the **only** door to the last step and refuses while any
escalated answer lacks an attributed human verdict. That is a lock, not a
convention: the grader cannot be run early by forgetting a step, and a partial
verdict import leaves it shut.

### 8.3 Resumability, because this is hundreds of paid dispatches

- **Append-only JSONL ledger**, flushed and `fsync`ed before the next expensive
  call. A torn final line does not lose the rest.
- **Deterministic, content-free dispatch ids** (`item|stage|slot`), so a resume
  can tell "already done" from "not started" without interpreting results.
- **A resume re-dispatches nothing** — demonstrated against the synthetic backend,
  not asserted: a second pass over a populated ledger makes zero backend calls.
- **No automatic retry anywhere.** Retrying is forbidden wherever it would
  condition the sample on a realized outcome, and the runner does not get to
  decide which case it is looking at.
- A dropped session, a killed container or an exhausted quota costs the dispatch
  in flight and nothing else.

### 8.4 The human queue

Exported with a fingerprint before Terry sees it. Each case carries the item, the
route, the arm, the stem, the key material that route needs, the exact model
answer, the escalation reason, and blank verdict and adjudicator fields.

It carries **no** candidate-grader output, no suggested verdict, no statement of
which way a case cuts for the hypothesis. `build_queue` **raises** if any
forbidden token appears anywhere in the serialised artifact — a queue that leaks
the grader is not blind, and that is enforced rather than intended.
