# Stage 0B battery-authoring protocol

**Status: DRAFT. Authoring has NOT started and is NOT authorized.**
This protocol exists so that when authoring does start, the rules are already
frozen. Stage 0A-M's failure was not that its battery was badly authored; it was
that the battery's difficulty and treatment-sensitivity were **assumed** and
never measured before 130 dispatches were spent on it.

Prerequisite: `docs/EXP004_STAGE0B_DESIGN_DRAFT.md` §10 items 1–3 must be done
first. Until then this document is a specification, not a procedure to run.

---

## 1. The three pools, and the wall between them

| pool | size | may enter production? | what it is for |
|---|---:|---|---|
| **calibration bank** | ≥ 3× production | **NEVER** | establishing the closed-book accuracy band, validating the recipe, exercising the grader's span parser |
| **production pool** | 50 primary + 20 control | yes, if it passes §4 | the experiment |
| **reserve** | ≥ 10 | only as documented replacements for items withdrawn *before* any dispatch | replacing items that fail the §4 screen |

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

## 3. Calibration, and the accuracy band

Run the **calibration bank only**, closed-book, R=1, fresh context per trial,
graded by the candidate grader at its current fingerprint.

- **Target band: 0.90 ≤ closed-book accuracy ≤ 1.00.** Derived, not assumed:
  `runs/exp004_stage0b_design/power_simulation.json` shows 80% power needs n=54
  at p=0.95 and n=65 at p=0.80, and is **unreachable at n ≤ 120** for p ≤ 0.65,
  because repairs cancel harms in a one-sided paired test. Harder items do not
  add information; they add cancellation.
- If the realized band is below 0.90, the recipe is too hard and is revised —
  **the recipe, never the production pool**.
- Calibration also produces the numbers the power model currently assumes: the
  realized `p`, and — via §4 — the realized `c_disp`. Power is **re-derived from
  measured values** before any production dispatch.

Calibration is also the grader's first exposure to answers that are not Stage
0A-M's. The candidate grader must not be frozen before this: it has so far been
validated against 130 answers from a battery it was designed after.

---

## 4. The frozen selection rule

Written and committed **before the screen runs**. An item enters production iff:

1. it satisfies every clause of §2;
2. its **retrieval-divergence probe** returns ≥ 1 of the top-5 results containing
   a reject alias or a reject value;
3. it passes the grader's span parser on ≥ 3 synthetic paraphrases of the correct
   answer, at least one of which carries trailing successor context;
4. no production solver has ever seen it.

### 4.1 What the divergence probe is, and why it is pre-treatment

The probe executes the item's **fixed query** (per the design draft §5) through
the searcher and records the raw result block. **No solver is dispatched. No
answer is generated. No outcome exists.** It measures a property of the world and
the search index, not of the model.

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
