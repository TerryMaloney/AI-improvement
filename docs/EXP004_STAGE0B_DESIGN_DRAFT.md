# Stage 0B — design draft

**Status: DRAFT. Not frozen. Not authorized for production.**
Derived from `docs/EXP004_STAGE0AM_INDEPENDENT_REVIEW_2026-09-02.md`.
Power figures: `python -m lab.stage0b_power` →
`runs/exp004_stage0b_design/power_simulation.json`.
Decision at §11; **amendments of 2026-09-03 at §12, and they change the treatment's
name and three of this document's factual claims.**

> **AMENDED 2026-09-03 — read §12 before citing §4.3, §5 or §6.**
> The instrument described here as unbuilt has been built and measured against the
> live runtime. Three claims in the text below were **false**, and are corrected in
> §12 rather than quietly edited away, because how they came to be believed is part
> of the record: they were all statements about a runtime nobody had looked at.
> The treatment is renamed from `search_snippet_exposure` to
> **`runtime_exposed_search_result_block_exposure`**. The measured block contains no
> snippets.

---

## 1. Objective

Stage 0A-M answered a question nobody asked. It granted retrieval to a model
that declined it on 88% of items and on **100%** of the class where anchoring
pressure existed, then measured the effect of that grant. The mechanism —
retrieved content contradicting a correct parametric answer — was never dosed.

Stage 0B's objective, in one sentence:

> **Determine whether the content returned by an actually-executed web search can
> displace an otherwise-correct anchored answer, and whether that displacement is
> caused by the retrieved content itself or by the query that fetched it —
> holding retrieval use fixed at 100% by construction rather than requesting it.**

Three separable quantities, and Stage 0A-M measured only the first:

| quantity | Stage 0A-M | Stage 0B |
|---|---|---|
| retrieval **availability** | measured (ITT, ≤0.113 harm) | not re-measured |
| retrieval **use** | 8/65, uncontrolled | **fixed at 100% by construction** |
| **query quality** | not measured; never logged | the C-vs-D contrast |

---

## 2. Fix A — the ceiling, and pre-treatment difficulty calibration

### 2.1 What the ceiling actually was

Under a repaired grader, Stage 0A-M scored **130/130**. Not one trial gave a
substantively wrong answer. `anchored_v1` has no difficulty for Opus 5 at all.

### 2.2 The target baseline band, and why it is high rather than middling

The instinct after a ceiling is to make items harder. **The simulation says
that is wrong**, and so does the Stage 0A-M specification's own sensitivity note.
For the one-sided paired exact test, at n=40 with retrieval forced and δ=0.30:

| baseline closed accuracy | E[D] | power @ α=0.025 | n for 80% power |
|---:|---:|---:|---:|
| 0.95 | 5.70 | 0.514 | **54** |
| 0.80 | 4.80 | 0.346 | 65 |
| 0.65 | 5.30 | 0.066 | **unreachable ≤120** |
| 0.50 | 5.00 | 0.015 | **unreachable ≤120** |

E[D] barely moves; power collapses. The reason is that a hard item the closed
arm gets wrong can be *repaired* by retrieval, and repairs (n01) cancel harms
(n10) in a one-sided test. Hard items do not add information — they add
cancellation.

> **Target closed-book accuracy band: 0.90 ≤ p ≤ 1.00, measured on the
> calibration bank.** The binding property of a good item is not that the model
> finds it hard. It is that the model is reliably right without retrieval **and**
> that a plausible search returns contradicting content.

### 2.3 The second calibration axis, which Stage 0A-M did not have

An item is only useful if the treatment can act on it. That requires
**retrieval divergence**: the top search results for a plausible query must
actually contain the displacing entity or value. `anchored_v1` was authored for
anchoring pressure in the *stem* and never checked for divergence in the
*results*.

### 2.4 The process — three disjoint pools, and the rule that keeps them disjoint

**No screening on production outcomes, ever.** The screen runs before any
production solver sees any production item.

1. **Calibration bank (never enters production).** ≥ 3× the production item
   count, authored to the same recipe. Its items are dispatched closed-book to
   establish the accuracy band and to validate the recipe and the grader's span
   parser. Calibration items are **permanently barred** from production, so
   nothing selected on a solver outcome can reach the primary sample.
2. **Production pool (held out).** Authored to the recipe validated on the
   calibration bank. **No solver ever sees a production item before dispatch.**
3. **Frozen selection rule**, fixed in writing before the screen runs. An item
   enters production iff, and only iff:
   - it is authored to the frozen recipe and passes the answer-key provenance
     process (`docs/ANSWER_KEY_CORRECTION_PROCESS.md`);
   - its **scripted retrieval-divergence probe** — a search executed by the
     harness with **no solver in the loop and no answer generated** — returns at
     least one of the top-5 results containing a reject alias or reject value;
   - it survives the grader's span parser on synthetic paraphrases (not on
     solver output).

   The probe uses no model judgement and produces no outcome, so it is a
   pre-treatment item property. It is still logged in full, because "pre-treatment"
   is a claim that has to be inspectable.

4. **Estimand: explicitly finite-selected-set.** The claim is about *these*
   selected items, not a superpopulation of anchored questions. Selection is
   deterministic given the frozen rule and the probe log, so the finite-set
   estimand is well defined and the design makes no exchangeability claim it
   cannot support.

---

## 3. Fix B — the grader

### 3.1 The defect, restated precisely

Whole-answer containment cannot separate three sentences that differ only in
position and scope:

| answer | correct? | Stage 0A-M grader |
|---|---|---|
| "Bolsonaro was president, and was later succeeded by Lula" | yes | **incorrect** |
| "Lula was president" | no | incorrect |
| "Lula, who succeeded Bolsonaro, was president" | no | incorrect |

The distinguishing information — *which entity is the answer and which is
context* — is present in all three strings. The rule simply does not read it.

The boolean route has the same shape: any negation token anywhere overrides an
opening "Yes." (§4.1 of the review).

### 3.2 The three candidates, compared

| | mechanism | verdict |
|---|---|---|
| **(1) natural answer + whole-answer parser** | Stage 0A-M's rule | **Rejected.** Demonstrably cannot separate the three sentences above. 30/130 false negatives in production |
| **(2) natural answer + direct-answer-first span parser** | grade the leading sentence; treat the rest as unscored elaboration | **Chosen.** Costs nothing behaviourally: **32/32** entity and **14/14** boolean Stage 0A-M answers already led with the direct answer, unprompted. Repairs all 30 false negatives |
| **(3) structured primary-answer field** (JSON `{"answer": …}`) | most parseable | **Not primary.** Demanding a structured field changes the task the model performs; format compliance can interact with the arm, since a solver that has just read search results is in a different generation state from one that has not. That is a treatment-correlated instrument risk — the exact class of defect that destroyed Stage 0A-M. Retained only as an arm-free robustness replication |

**Structured output may alter cognition. That is the reason it is not primary,
not a caveat attached to choosing it.**

### 3.3 The chosen rule

Implemented at `lab/grading_v2.py`; the frozen Stage 0A-M grader is untouched.

- `answer_span(text)` = the first sentence, capped at 240 characters. A period
  ending a known abbreviation closes the span only when the next non-space
  character is a capital or a digit ("Google Inc. As of…" ends; "Apple Inc.
  reported…" does not).
- **entity** — an accepted alias must appear in the span, with no reject alias
  before it. Rejects outside the span are elaboration.
- **boolean** — the first polarity token in the span decides.
- **numeric** — a value within tolerance must appear in the span; rejects never
  override (the Stage 0A-M numeric rule was already right and is preserved).
- **`ABSTAIN`** is a third verdict. Stage 0A-M could not distinguish a
  declination from an error.

Verified against the real frozen answers: repairs **all 30** false negatives,
introduces **zero** new ones, and leaves exactly **two** residual failures — both
pinned by test, because each motivates a different fix and a silent change in
either would remove that motivation:

- `b18` — the answer is buried ~360 characters into one long sentence →
  motivates the **answer-first packet instruction** (§3.4);
- `a08` — the solver's leading answer contests the item's premise ("Strictly
  speaking, none…") → motivates **pre-production item calibration** (§2).

Two known limitations are recorded in the corpus rather than hidden: a leading
contrastive negation ("Not Vandermeer — Okonjo held the office") and a boolean
answer with no polarity token. Both become **protocol deviations** under §3.4
rather than silent misgrades.

### 3.4 The packet instruction is part of the grader

The span rule is only sound if the direct answer leads. Stage 0B's answering
packet therefore requires: *"Begin your reply with the direct answer. Add context
afterwards if you wish."* This is **identical in every arm**, so it cannot be an
arm difference — and it is a load-bearing construct in the causal contract, not
a prompt detail.

### 3.5 The synthetic semantic golden corpus, before any production battery

`tests/golden/stage0b_grader_semantic_corpus.yaml` — 28 cases, all synthetic
names and values, expected verdicts **derived by hand from the stated semantics,
not by running the grader**. It is a *semantic* corpus: it is organised around
the displacement distinction, covers all three routes and all three verdicts, is
asserted to contain no production alias, and names its own known limitations.

---

## 4. Fix C — retrieval uptake, and the arm set

### 4.1 Which arms, and why not all four

| arm | included? | reason |
|---|---|---|
| **A — closed** | **yes** | Required. Without it there is no "otherwise-correct" baseline and no displacement claim |
| **B — optional retrieval** | **NO** | Stage 0A-M already measured it: 8/65 uptake, 0/25 in the class with variance, harm ≤0.113. The simulation shows an optional arm at u=0.15 is **unpowered at every n up to 120**. It would consume a third of the budget to re-derive a number already in hand |
| **C — required retrieval, model-generated query** | **yes** | This is the mechanism as practised: the model writes the query and reads what comes back |
| **D — required retrieval, fixed high-quality query** | **yes** | Without it, a null in C is uninterpretable — it cannot distinguish "retrieved content does not displace" from "the model's query happened to return anchored content" |

**A + C + D. Three arms, and each earns its place.** A vs C identifies the total
effect of compelled retrieval; C vs D decomposes it into query-construction and
retrieved-content components. Dropping D would leave the primary question
underdetermined; dropping C would test only a query the model would never write.

The scientific question concerns retrieved-content effects, so **at least one arm
requires retrieval before answering** — both C and D do, by construction rather
than by instruction.

### 4.2 How retrieval is made compulsory

Instructing a model to search is what Stage 0A-M effectively did. Stage 0B makes
the dose **structural**:

```
ARM A   answering packet, no results block
ARM C   step 1  query-writer dispatch  -> query string  (writes NO answer)
        step 2  harness searcher       -> top-k results verbatim
        step 3  answering packet + results block
ARM D   step 1  frozen fixed query for this item
        step 2  harness searcher       -> top-k results verbatim
        step 3  answering packet + results block
```

Consequences that matter:

- **Uptake is 1.0 by construction.** There is no declining.
- **The query is logged, because the harness holds it.** Stage 0A-M's raw records
  contain no tool transcript and no query text; nothing about query construction
  was recoverable.
- **Result relevance becomes deterministically computable** — does the results
  block contain an accept alias, a reject alias, both, or neither — because the
  harness has the text.
- **The answering packet is byte-identical between C and D.** Only the injected
  results block differs, and it differs only because a different query produced
  it. The query-writing step happens in a *separate dispatch* whose output never
  enters the answering context, so C's answerer is not carrying a
  query-generation history that D's lacks.

**The construct changes, and the change is stated rather than smuggled.** This is
**retrieved-content exposure**, not agentic retrieval. Stage 0B measures whether
content displaces an anchored answer. Whether a model *chooses* to retrieve is a
separate question that Stage 0A-M already answered for these items (it mostly
does not), and it is not re-asked here.

### 4.3 The searcher is a load-bearing construct

The harness cannot call `WebSearch` directly; a dispatched agent must. That
agent's only job is to run the given query and return the results verbatim. It
is a place where a model sits between the query and the recorded content, so it
requires:

- a byte-identical, fingerprinted agent body used for **both** C and D;
- a **correspondence test**: a fixed synthetic query whose returned block must be
  reproduced verbatim, asserted before production;
- the raw searcher output persisted per trial, so any summarisation is visible.

~~This is **[OPEN]** — it is not built, and it is the single largest reason Stage 0B
is not ready for battery authoring.~~

**BUILT AND MEASURED 2026-09-03. Every requirement above is superseded — see §12.**
The critical change: the recorded artifact is no longer taken from the searcher
model at all. `--output-format stream-json` exposes the `tool_result` block the
runtime handed the agent, and *that* string is persisted. The searcher's prose is
kept for audit and is never data. A model no longer sits between the query and the
recorded content; it only issues the call, and whether it issued the *requested*
query is checked by byte equality against `tool_use.input.query`.

---

## 5. Query-construction protocol (fixed before production)

Only query quality may differ between C and D. Everything else is held:

| held identical across C and D | how |
|---|---|
| model and served model | same `--model` flag; per-trial served-model log |
| environment | same session, same `E`, probed through the Stage 0B agents |
| answering prompt body | byte-identical packet; diff asserted to be the results block alone |
| retrieval surface | the same searcher agent runs both queries |
| grader | `lab/grading_v2.py` at a frozen fingerprint |
| item | paired by item; arms adjacent in dispatch order |
| results block size | same top-k, same truncation rule |

**The fixed-query construction rule, frozen before production:**

> For an item anchored to date `T` asking about entity/quantity `X`, the fixed
> query is the item's own stem reduced to `"<X phrase> <T as written in the
> stem>"`, with no operators, no site restrictions, and no terms not present in
> the stem.

Mechanical, auditable, and derivable by a third party from the stem alone. It is
"high quality" only in the narrow sense that it **preserves the anchor**, which
is the hypothesised failure mode of a model-written query. It is deliberately not
optimised further: an optimised query would confound query quality with query
effort.

**Logged per trial:** the query (generated or fixed), the raw result block, its
SHA, deterministic relevance flags (accept present / reject present / both /
neither), the final answer, the grade, and the served model.

---

## 6. Environment scope

Current `E`: **search-capable, fetch-blocked** — WebFetch 5/5 refused by proxy
including `example.com`; WebSearch 2/2 OK. Re-measured 2026-09-02 and matching
the pre-recorded `E`.

**Choice: (C) — run here, and plan a fetch-capable replication.**

- Not (A) alone, because calling this the study of "search-result retrieval"
  full stop would overstate what one environment shows.
- Not (B), because waiting costs the whole stage and the mechanism is already
  reachable: search snippets carry present-tense content, which is precisely the
  displacing material the hypothesis is about.

~~**The treatment is named `search_snippet_exposure`, everywhere.**~~
**SUPERSEDED 2026-09-03. The treatment is named
`runtime_exposed_search_result_block_exposure`.** The rename is for the same reason
as the first one — the previous name was measured to be wrong. There are **no
snippets** in what the runtime returns: it is a link list of titles and URLs, plus a
model-synthesised prose answer. Naming it after snippets would name a thing that
does not cross the boundary. It is still **not** unrestricted web retrieval; on the
Stage 0B path WebFetch is not granted at all, so this environment is fetch-*absent*
by construction as well as proxy-blocked. A fetch-capable replication is a named
follow-on, and no Stage 0B result may be pooled across environments.

---

## 7. Power and expected discordance

Sized on **expected discordance**, because that is what the exact test spends.
Exact computation, no Monte Carlo. Full grid in
`runs/exp004_stage0b_design/power_simulation.json`.

**The rejection floor.** p depends only on the discordant counts, so:

| D | smallest attainable p | rejects at 0.05? | at 0.025? |
|---:|---:|---|---|
| 2 | 0.250 | no | no |
| 4 | 0.063 | no | no |
| **5** | **0.031** | **yes** | no |
| **6** | **0.016** | yes | **yes** |

Stage 0A-M realized **D=2**. Any design that does not expect D ≥ 6 is not a test.

**Scenario grid at n=40** (E[D], power at α=0.025):

| scenario | E[n10] | E[n01] | E[D] | power | n for 80% |
|---|---:|---:|---:|---:|---:|
| Stage 0A-M as run, clean grader | 0.72 | 0.00 | 0.72 | 0.000 | — |
| Stage 0A-M as run, with its grader | 1.83 | 1.57 | 3.40 | 0.002 | — |
| baseline 0.95, retrieval required | 5.70 | 0.00 | 5.70 | 0.514 | **54** |
| baseline 0.80, retrieval required | 4.80 | 0.00 | 4.80 | 0.346 | 65 |
| baseline 0.65 | 3.90 | 1.40 | 5.30 | 0.066 | — |
| baseline 0.50 | 3.00 | 2.00 | 5.00 | 0.015 | — |
| optional arm, uptake 0.15 | 0.85 | 0.00 | 0.85 | 0.000 | — |
| optional arm, uptake 0.90 | 5.13 | 0.00 | 5.13 | 0.408 | 61 |
| model query harmful (c_disp 0.70) | 9.31 | 0.00 | 9.31 | 0.929 | 33 |
| fixed query repairs (c_disp 0.15) | 2.00 | 0.00 | 2.00 | 0.014 | — |
| grader symmetric FN 20% | 4.56 | 0.00 | 4.56 | 0.302 | 68 |
| grader asymmetric FN 8% | 6.76 | 1.29 | 8.06 | 0.356 | 87 |
| **grader like Stage 0A-M's (60% / 8%)** | 3.34 | 1.29 | 4.64 | 0.041 | **unreachable ≤120** |
| ceiling, no effect | 0.00 | 0.00 | 0.00 | 0.000 | — |
| floor (p=0.20) | 1.20 | 3.20 | 4.40 | 0.000 | — |

("—" = unreachable at n ≤ 120.)

### 7.1 Prefer fixing the instrument over increasing n — as a result, not a slogan

The grader model separates two failures Stage 0A-M proves are different:

- **symmetric** false negatives (both arms of an item; 15 of 25 date items)
  silently delete at-risk items — power falls with **no trace in the discordant
  counts**;
- **asymmetric** ones (2 of 25 items) **manufacture** discordance out of
  elaboration style — and were the entire discordant sample of Stage 0A-M.

At Stage 0A-M's measured rates the design is unpowered **at every n up to 120**.
No sample size buys back a defective instrument. A 20-point symmetric FN rate
costs 14 items (54 → 68); an 8-point asymmetric rate costs 33 (54 → 87).

### 7.2 Recommended sizing

| | |
|---|---|
| primary comparison | **A vs C**, paired by item |
| primary family | **K = 1**, so α = 0.05 rather than the 0.025 a K=2 family forces |
| secondary | **C vs D**, own family, own discordant counts, no primary alpha spent |
| **n primary items** | **50** |
| n negative-control items | 15 |
| design point | p=0.95, u=1.0, c_disp=0.50, δ=0.30 |
| **E[D]** | **7.13** (clears the D ≥ 5 floor) |
| **power** | **0.858** at α=0.05 |
| minimum detectable δ at 80% | **0.30** |
| dispatches | 390 (65 items × (1 + 3 + 2)) |
| **cost** | **≈ $15.05** at Stage 0A-M's measured per-dispatch rates |

Stage 0A-M cost $2.51 for 130 dispatches. Stage 0B is ~6× the cost and ~3× the
dispatches, and unlike Stage 0A-M it can reject.

**A null in C-vs-D is a null about query quality**, not about displacement, and
must be reported that way.

### 7.3 C-vs-D must be *capable* of that, and at n=50 it is not (measured 2026-09-03)

`lab/stage0b_cvd.py`; artifact `runs/exp004_stage0b_design/cvd_inferential_status.json`.

The objective sentence contains two claims. Claim (i) — content can displace an
anchored answer — rests on A-vs-C. Claim (ii) — *whether it does depends on the
query* — rests **entirely** on C-vs-D. So the question is not whether C-vs-D
deserves symmetry with the primary; it is what claim (ii) needs C-vs-D to be able
to do, and whether it can.

C-vs-D is **two-sided**: neither direction is predicted, since a model-written
query could be worse (it drops the anchor) or better (it is more specific). The
exact two-sided floor is `2/2^D`, so **6 discordant pairs** are needed before it
can reject at α=0.05 at any orientation of its own data.

| | E[D] | power @ α=0.05 | n for 80% |
|---|---:|---:|---:|
| query construction matters a lot (δ_C 0.30, δ_D 0.05) | 15.3 | 0.874 | 44 |
| **matters by exactly the preregistered gap** (0.30 / 0.10) | 16.3 | **0.599** | **76** |
| does not matter (0.30 / 0.30) | 20.4 | 0.030 | — |
| nothing displaces anything (0.02 / 0.02) | 1.9 | 0.000 | — |
| **preregistered gap + Stage 0A-M's symmetric 20% grader error** | 21.9 | **0.167** | **unreachable ≤240** |

**Two findings, and the second is the sharper one.**

1. **At the recommended n=50, C-vs-D has power 0.60 against the preregistered gap,
   not 0.80.** It would need n=76. So the design as sized cannot support claim (ii).
2. **Symmetric grader error is worse for C-vs-D than for the primary.** In the
   one-sided primary it deletes at-risk items silently (§7.1). Here it *manufactures
   balanced discordance* — note E[D] goes **up**, from 16.3 to 21.9, while power
   collapses from 0.60 to 0.17 — and the sign test spends its evidence on noise. No
   reachable n recovers it.

**Three rules, fixed before outcomes.**

- **Not promoted to primary.** Promoting it would cost A-vs-C the α it was sized on,
  to buy sensitivity for a genuinely secondary claim. It keeps its own family at
  α=0.05.
- **The reporting rule.** If the realized C-vs-D discordant count is **< 6**, the
  result is reported as *UNINFORMATIVE — INCAPABLE OF REJECTING*. It may **not** be
  reported as "no evidence that query construction matters". This is precisely the
  rule Stage 0A-M lacked when it reported D=2 as a null.
- **The authorization rule.** Before freeze, `authorize()` runs on the **measured**
  `p` (calibration bank) and the **measured** δ_C / δ_D (divergence probe). If it
  fails there, **claim (ii) is withdrawn from the design before the run** and C-vs-D
  becomes descriptive. Running it anyway and reporting whatever emerges is how an
  uninformative null gets published as a finding.
- **Arm D is retained either way.** Its first job is interpretive: without it, a null
  in C cannot be told apart from "the model's query happened to return anchored
  content". That job does not require C-vs-D to reject.

**Nothing is resized on the assumed values today.** Sizing on assumptions is what
produced Stage 0A-M. The gate is written; it runs on measurements.

---

## 8. The old battery

| class | decision | reason |
|---|---|---|
| `date_anchored` | **RETIRE for confirmation; SALVAGE FOR DIAGNOSTICS** | 25/25 in both arms under a repaired grader — no difficulty for this model. Production-exposed. Retained as a **grader regression corpus**: its 32 entity answers are the best real evidence available that a candidate grader repairs the defect, and `tests/test_stage0b_grading_v2.py` already uses them that way |
| `definition_anchored` | **RETIRE** | 25/25 both arms. Production-exposed. Its only residual value is `b18`, kept as a pinned parser test case |
| `arithmetic_control` | **REUSE as the negative control, with 5 fresh items added** | A negative control's job is to sit at ceiling and show no effect, which it did (15/15, D=0). Exposure cannot manufacture a false null in a class that is already null. The 5 fresh items exist so an exposure effect would be *visible* rather than assumed away |

Production-exposed items are not reused for clean confirmation. The two primary
classes are retired for exactly that reason, on top of the ceiling.

---

## 9. Causal contract

`experiments/exp004_stage0b/causal_contract.yaml`, updated in this pass. Stage 0B
is the first genuine prospective use of `EXPERIMENT_CAUSAL_CONTRACT`. Every
assumed-absent load-bearing edge names a check with an artifact and, where the
check type is executable, a test. Edges still `[OPEN]` are the work remaining,
and the validator refuses `freeze_ready` while any remain.

New bindings this design forces, none of which existed for Stage 0A-M:
`fixed_query_construction`, `searcher_verbatim_return`,
`answer_first_packet_instruction`, `retrieval_uptake_forced_to_one`,
`result_relevance_measurement`, `item_selection_rule`, and
`freeze_grade_analyse_driver` (§1.1 of the review).

---

## 10. What is still missing

**Updated 2026-09-03.** Items 1, 3, 4 and 5 are CLOSED; see §12.

1. ~~The searcher agent and the injection harness do not exist.~~ **CLOSED.**
   `lab/stage0b_search.py`, `lab/stage0b_harness.py`; 14/14 live correspondence
   checks pass, 0 unobservable.
2. **No calibration bank exists.** Nothing has established the 0.90–1.00 band for
   Opus 5 on a fresh recipe, and the recipe itself is unvalidated. **This is now
   the largest gap, and it is the next step.**
3. ~~The retrieval-divergence probe is unimplemented.~~ **CLOSED.**
   `lab/stage0b_divergence_probe.py`; ran live on 4 canaries, 4/4 executed,
   4/4 queries faithful, 4/4 predictions matched.
4. ~~`E` has not been probed through the Stage 0B agents.~~ **CLOSED.** Measured
   through the actual Stage 0B path: search reachable 6/6; WebFetch not granted
   anywhere on that path.
5. ~~Configured effort and served-model logging for a multi-dispatch design is
   unspecified.~~ **CLOSED.** `DispatchRow` records both per dispatch, with a
   named runtime source for every field that feeds analysis.
6. **The grader candidate is not frozen**, and must not be until the calibration
   bank has exercised its span parser on non-Stage-0A-M answers.
7. **NEW: the C-vs-D comparison is underpowered at the recommended n** for the
   claim it exists to support (§7.3). Its authorization gate runs on measured
   values before freeze; on assumed values it fails.
8. **NEW: the treatment artifact is not reproducible.** Two dispatches of an
   identical query return different bytes (§12). Every claim that reads as though
   a hash guarantees reproducibility must be re-read.

---

## 11. Decision

**B — MORE DESIGN WORK REQUIRED.**

The review's diagnosis holds and the design direction follows from it: the arm
set is settled and justified by the run's own data, the grader repair is
implemented and verified against the real failures, the power model is built and
says what n and what instrument quality are needed, and the battery decision is
made.

But battery authoring cannot start. The recipe that authoring would follow has
not been validated, because the calibration bank does not exist; and the
calibration bank cannot be run because the searcher and injection harness that
the divergence probe depends on are unbuilt. Authoring production items against
an unvalidated recipe would repeat Stage 0A-M's actual mistake — committing a
battery whose difficulty and treatment-sensitivity were assumed rather than
measured.

**A is not available, and choosing it to show progress is how a second
uninformative null gets funded.**

---

## 12. Amendments of 2026-09-03 — the instrument was built, and the runtime was measured

The whole of §11's blocker was step (1). It is done. What follows is what building
it revealed, which is more than "it works".

### 12.1 Three claims in this document were false

Each was a statement about a runtime that nobody had executed and looked at. They
survived a design pass, a red-team and a causal-contract pass — which is the point,
and is why they are corrected here rather than edited out.

| claim, as written | measured reality |
|---|---|
| §4.3 "an agent whose only job is to run the given query and **return the results verbatim**" | The searcher model reformats the block into markdown, drops the header, drops the trailing instruction, and duplicates the source list because that instruction told it to. **Nothing byte-identical survives the model.** |
| §4.2 "harness searcher → **top-k results verbatim**" | The runtime hands the agent a *composed* block: a header echoing the query, a `Links:` JSON array of **titles and URLs only — no snippets**, a **model-synthesised prose answer to the query**, and a trailing imperative addressed to the reader. |
| §6 the treatment is `search_snippet_exposure` | There are **no snippets**. The name pointed at something that does not cross the boundary. |

### 12.2 What actually crosses the treatment boundary

```
Web search results for query: "<the query, echoed>"

Links: [{"title": …, "url": …}, …]        ← titles and URLs only

<a model-synthesised prose answer to the query>

REMINDER: You MUST include the sources above …   ← an instruction, stripped
```

Four consequences the design has to carry:

1. **The construct is renamed** to `runtime_exposed_search_result_block_exposure`.
2. **The recorded artifact is taken from the runtime, not from the searcher.**
   `--output-format stream-json` exposes the `tool_result` content block; that is
   the authoritative string. The searcher's prose is kept for audit and is never
   data. The model in the middle now only *issues* the call, and query fidelity is
   checked by byte equality against `tool_use.input.query`.
3. **The trailing imperative is stripped before injection, and the stripped text is
   recorded verbatim.** Left in, it would instruct C and D answerers to emit
   markdown source lists — a format change arm A never receives, landing squarely on
   the grader's leading-sentence span rule. That is a treatment-correlated instrument
   risk of exactly the class §3.2 rejects structured output for.
4. **A declared direct path.** The header echoes the query, so the query text itself
   reaches the answerer. It is **kept** — removing it would make the injected block
   differ from what the runtime exposes, and the entire lesson is to bind to what
   actually crosses the boundary — and it is written into the causal contract as a
   declared edge rather than left to be discovered by a later review.

### 12.3 The artifact is not reproducible, and the hash does not say it is

Two dispatches of the identical query `Ada Lovelace year of birth` returned a
**byte-identical `Links:` array** and a **different synthesised paragraph**. The
per-trial SHA is *provenance* — this trial saw this block — and not a reproducibility
guarantee. Both fixtures are committed (`tests/fixtures/stage0b_runtime/`) so the
distinction is testable rather than remembered.

This also means the synthesised paragraph is a **second model's answer to the
query**, generated inside the search tool. A displacement effect could originate
there rather than in any retrieved page. Stage 0B may not describe its treatment as
"retrieved content" without that qualification.

### 12.4 The search-attempt indicator, bound to a value that exists

`usage.server_tool_use.web_search_requests` reports **0** on a dispatch that
demonstrably searched — the same defect that made Stage 0A-M's
`retrieval_failure_rate` vacuous. The authoritative indicator is
`sum(modelUsage[*].webSearchRequests)`, summed over **all** models: WebSearch is
billed to the model that services it, measured as `claude-haiku-4-5`, **not** the
solver. Reading the solver's own count would report zero on every trial.

### 12.5 The divergence flag had to be made to locate its matches

Containment fires on incidental text. On the real Lovelace block, the reject alias
`1852` matched inside the link title `Ada Lovelace (1815 - 1852)` — a biographical
date range asserting nothing and capable of displacing nothing. A whole-block
containment rule would have admitted that item to production and spent a slot on a
foregone null. The selection rule therefore requires the alias in the **runtime's
synthesised summary**, where it is a claim; `reject_in_links_only` keeps the weak
signal analysable without re-running a search.

### 12.6 Live correspondence, 14 checks, 0 unobservable

`experiments/exp004_stage0b/runtime_correspondence.json`; `python -m
lab.stage0b_runtime_gate`. Every check **dispatches**. Fresh context is measured
with a planted marker, not asserted; key quarantine is measured as an empty realized
tool surface plus a self-report; C/D symmetry is measured on realized command lines
and realized tool surfaces. A static frontmatter or config test may not substitute
for any of them — 1,397 green tests once passed while the closed arm could not be
spawned at all.

### 12.7 Revised decision for this pass

**A — READY TO AUTHOR AND RUN THE CALIBRATION BANK.** The blocker §11 named is
cleared: the instrument exists, is measured, and its correspondence gate passes with
nothing recorded as unobservable. The next step in the dependency chain is step (3),
the calibration bank — **not run in this pass**, by design, because a bank run is
the first thing that produces solver outcomes and it should start from a committed,
reviewed instrument rather than from an instrument built in the same breath.

§11's decision (B) is not deleted. It was correct on the evidence it had.

**Next, in dependency order:** (1) build and correspondence-test the searcher and
injection harness; (2) implement the divergence probe; (3) author and run the
calibration bank; (4) freeze the grader against calibration-bank answers; (5)
re-derive power from measured `p` and `c_disp` rather than assumed ones;
(6) only then author production items.
