# Stage 0A-M — independent post-result review

**Reviewer:** a separate session, taking over after Stage 0A-M completed.
**Date:** 2026-09-02. **Reviewed commit:** `f15d6ff`. **Freeze commit:** `a1f4efb`.
**Reproduce:** `python -m lab.stage0am_review` →
`runs/exp004_stage0am/independent_review.json`; assertions in
`tests/test_stage0am_independent_review.py`.

Nothing in this review alters the Stage 0A-M raw outcomes, graded ledger, frozen
grader, or official primary result. Every number below was recomputed from the
persisted artifacts, using statistics re-implemented in `lab/stage0am_review.py`
rather than borrowed from `lab/stage0am.py`, so a shared bug could not make the
reconstruction agree by construction. (The two implementations are then asserted
to agree on a grid of inputs, which is a different claim from agreeing on this
run's numbers.)

---

## 0. Verdict table

| QUESTION | ANSWER | CONFIDENCE | EVIDENCE |
|---|---|---|---|
| Was execution valid? | **Yes, without qualification** | OBSERVED | 130 raw files ≡ 130 ledger rows ≡ 130 graded rows; 65 complete pairs, 0 incomplete; all 130 under the single freeze commit `a1f4efb`; 0 dispatch failures, 0 voids, 0 ungradeable rows, 0 permission denials, 0 harness errors; `claude-opus-5` present in all 130; schedule compliance errors 0 across all 65 positions; dispatch order exactly 1…130 |
| Are the freeze hashes real? | **Yes** | OBSERVED | All 130 per-file SHAs recomputed and matched; ledger `3a86ea6664e1a9c8` and combined `65bdf4fd8d523d5c` reproduced; battery fingerprint `1ec90754f1de2696` regenerated from the battery + key files; grader `10adaf1dac94ea70`; schedule `321c3a2397958c30` |
| Were raw outcomes frozen before grading? | **Yes** | OBSERVED + INFERRED | `graded.jsonl` differs from `trials.jsonl` in exactly one added field and nothing else. The grader (`anchored_grading.py`) and the analysis (`stage0am.py`) were both last modified at `9c57635`, an ancestor of `4f4ba3f`, the first commit that persisted any outcome. Caveat below (§1.1) |
| Was the official primary reconstruction correct? | **Yes, exactly** | OBSERVED | Re-running the frozen grader on the frozen answers reproduces all 130 grades with 0 mismatches. `date_anchored` n00=14 n01=1 n10=1 n11=9 D=2, p = **3/4** in exact rationals; `definition_anchored` n11=25 D=0 p=1; `arithmetic_control` n11=15 D=0. Holm K=2: no rejection. Every field of `analysis.json` agrees |
| Was the null scientifically informative? | **No — and more sharply than the report says** | OBSERVED | At D=2 the smallest attainable exact p is **1/4**. Rejection requires D ≥ 5 at α=0.05 and D ≥ 6 at the Holm first step. **No orientation of the observed discordances could have rejected**, before a single grade was read |
| Was the definition class ceilinged? | **Yes (25/25 both arms) — but "ceiling ⇒ no information" is wrong** | OBSERVED + INFERRED | See §3. Under the design's own power model a closed-arm ceiling is the *most* favourable condition, not the least. This class produced the run's tightest harm bound |
| Was the arithmetic control ceilinged? | **Yes, by design, and it behaved** | OBSERVED | 15/15 both arms, D=0, harm-rate upper 95% 0.181. A negative control at ceiling is a control that worked |
| Was the date grading artifact real? | **Yes, and larger than reported** | OBSERVED | **32/32** exact_entity trials contained the accepted entity. In **28/28** graded-incorrect cases the accepted entity appeared **strictly before** any reject alias. Zero entity trials failed on knowledge |
| Is there a *second*, unreported grading artifact? | **Yes — the boolean route** | OBSERVED | 14/14 boolean answers opened with the correct polarity token. `a09` was graded incorrect in **both** arms because `"no"` matches inside `"no longer a member state"` 409 characters later. Not named anywhere in the Stage 0A-M report |
| Were the discordances genuine retrieval displacement? | **No — and this is now provable, not inferred** | OBSERVED | In all four trials of the two discordant pairs the solver named the accepted entity. Both retrieval-arm trials issued **zero** searches (`num_turns=1`, `webSearchRequests=0`). A trial that did not retrieve cannot have been displaced by retrieved content |
| Was retrieval exercised often enough? | **No. Not remotely** | OBSERVED | 8 of 65 treated trials retrieved. **All 8 were `definition_anchored`.** `date_anchored` — the only class with any outcome variance — had **0/25**. WebFetch: 0/65, never attempted |
| What did Stage 0A-M measure? | **Retrieval AVAILABILITY, not consumption** | OBSERVED | 57/65 treated trials declined. The only bound on consumed retrieval rests on 8 trials: harm ≤ **0.312** (95% CP) |
| P2 — served-model fallback clusters | **No fallback. Not supported** | OBSERVED | `claude-opus-5` in all 130; `claude-haiku-4-5` appears in all 130 as harness work (median 15 output tokens), never as the solver |
| P3 — availability changes answers without use | **Not supported, at zero power** | OBSERVED | 57 availability-without-use trials → 2 discordant pairs, both proven artifacts. The test could not have rejected |
| P4 — realized effort loads on the retrieval arm | **Not supported as an ITT claim; strongly supported conditional on use** | OBSERVED | Arm medians 184 vs 180 output tokens, 6.88 s vs 6.95 s. But the 8 trials that *searched*: median 506 tokens and 16.63 s vs 161 tokens and 6.69 s for the 57 that did not. The ITT null is a dilution artifact of 12% uptake |
| R1′ status | **CORRECTED 2026-09-03: not a second confirmation. This observation DISCONFIRMS R1′ as frozen (`HURT_BOTH`). Prospective confirmations remain n=1** | OBSERVED (cell), INFERRED (reading) | The empirical finding stands: the grader mis-scored 30 of 130 production trials while every check read the rule and none read a realized answer. But the frozen prospective table classifies `grader` as symmetric, `check_executed: true`, `r1_prime_predicted_risk: low (checked)` — R1′ predicted this cell was *safe*. The pre-declared R1′-high cells are the unchecked ones (`configured_effort`, `live_agent_registry`, `served_model_per_trial`). Under the table's own `what_future_observations_mean`, a defect in a low-churn, checked, symmetric component is `HURT_BOTH`: neither theory predicted it. Correction and the successor hypothesis it motivates (R3′, realized-output correspondence): `experiments/meta_r1r2/observation_2026-09-03_grader.md` |
| Should the frozen result be changed? | **No** | — | The grader is defective, but it was frozen before outcomes and the run is scored under it. The repair belongs to Stage 0B and must be frozen before Stage 0B outcomes |

---

## 1. Execution validity — separated from measurement limitation

**EXECUTION VALIDITY: clean.** Every integrity check passed. Specifically:
`arm → agent` mapping is 1:1 and correct in all 130; the closed arm issued zero
search and zero fetch requests and never exceeded one turn, so there is no
contamination; `dispatched_at` is non-decreasing across the full 17-minute run;
the two arms of each item are adjacent in dispatch order exactly as scheduled.

**MEASUREMENT / POWER: destroyed.** Three independent, compounding failures,
none of which is an execution defect. They are the subject of §2–§5.

One imbalance is worth recording without over-reading it: arm-first order came
out 37 retrieval-first / 28 closed-first overall, and 16/9 within
`date_anchored`. The order was drawn pre-outcome from a recorded seed
(`arm_order_seed: 8302026`), and each trial ran in a fresh context — the
fresh-context canary confirmed a planted token was unrecoverable across trials —
so there is no path by which order can transmit information between arms. It is
recorded as a chance imbalance, not a defect.

### 1.1 One provenance caveat, stated rather than buried

`lab/stage0am_report.py`, the driver that freezes, grades and analyses, was
first committed at `4f4ba3f` — the same commit that first persisted raw
outcomes, when **33 of 130** trial rows already existed on disk. It has never
been modified since.

This does **not** compromise the freeze, because the two outcome-sensitive
components — the grading rule and the test statistic — were both frozen at
`9c57635`, well before any outcome, and are byte-identical between the freeze
commit and `HEAD` (verified: `anchored_grading.py`, `anchored_v1.yaml`,
`answers.anchored_v1.yaml`, `schedule.json` and `stage0am.py` all unchanged
after `a1f4efb`). The driver contains no grading logic of its own and asserts
the grader fingerprint before use. But it is a real, if narrow, window in which
a discretionary choice could have been made with 33 answers visible, and a
review that did not say so would be worth less.

**Recommendation for Stage 0B:** the freeze/grade/analyse driver is itself a
load-bearing construct and must be committed and fingerprinted *before* the
first dispatch, not during the run.

---

## 2. Independent reconstruction of the primary result

Recomputed from `graded.jsonl`, with an independently written exact conditional
binomial in exact rationals and an independently written Holm step-down.

| class | n | n00 | n01 | n10 | n11 | D | exact p | Holm | min attainable p at this D |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| `date_anchored` | 25 | 14 | 1 | 1 | 9 | 2 | **3/4 = 0.750** | not rejected | **0.250** |
| `definition_anchored` | 25 | 0 | 0 | 0 | 25 | 0 | **1.000** | not rejected | **1.000** |
| `arithmetic_control` (outside the family) | 15 | 0 | 0 | 0 | 15 | 0 | 1.000 | not tested | 1.000 |

Holm across K=2: the smaller p must clear 0.025, the larger 0.05. Neither does.
**Reconstruction agrees with `analysis.json` on every field**, including the
Clopper–Pearson harm bounds to 1e-9. There is no material disagreement on the
primary result, so Stage 0B design proceeds.

**The sharpest statement of the power failure.** The last column is not in the
existing report and it is the one that matters. The exact test's p-value is a
function of the discordant pairs alone. At D=2, even if *both* discordances had
pointed the harm way, p = 1/4. Rejection needs D ≥ 5 at α=0.05 and D ≥ 6 at the
Holm first step.

> Stage 0A-M was incapable of rejecting its primary hypothesis at the moment the
> 130th dispatch returned, whatever the answers said.

---

## 3. Ceiling audit — where I disagree with the existing report

Realized accuracy, both arms, every class:

| class | route | closed | retrieval | discordant |
|---|---|---:|---:|---:|
| `date_anchored` | exact_entity (16 items) | **2/16** | **2/16** | 2 |
| `date_anchored` | boolean (7 items) | 6/7 | 6/7 | 0 |
| `date_anchored` | numeric (2 items) | 2/2 | 2/2 | 0 |
| `definition_anchored` | numeric (25 items) | **25/25** | **25/25** | 0 |
| `arithmetic_control` | numeric (15 items) | **15/15** | **15/15** | 0 |

### 3.1 The report's stated mechanism for the ceiling is wrong

The Stage 0A-M report says of `definition_anchored` and the arithmetic control:

> *"Zero discordance is possible at a ceiling, so those classes contributed no
> information whatsoever."*

The first clause is true; the inference is not. **Under the design's own power
model a closed-arm ceiling is the most favourable condition, not the least.**
The specification says so explicitly (§4): *"power is robust across baseline p
from 0.60 to 0.99 … and is **higher** at high baseline p … Items the closed
model reliably gets right are the useful ones."* At p_closed = 1.00 every item is
at risk, so under a real per-item effect δ the discordant count would be
Binomial(25, δ) with every discordance oriented as harm — the best-powered
configuration the design admits.

What produced D=0 in `definition_anchored` was not the ceiling. It was that the
**retrieval arm was also 25/25** — the treatment produced no flips. That is a
measurement of δ, not an absence of measurement. It is weak, but it is the
strongest thing in the run:

| bound (Clopper–Pearson, one-sided 95%) | value |
|---|---:|
| P(retrieval flips a correct closed answer) — `definition_anchored`, all 25 items | ≤ **0.113** |
| same — `arithmetic_control`, all 15 items | ≤ **0.181** |
| same — `date_anchored`, all 25 items | ≤ 0.176 |
| same — `date_anchored`, conditional on the closed answer being correct (n=10) | ≤ 0.394 |
| **same — restricted to the 8 trials that actually retrieved** | ≤ **0.312** |

The distinction the report should have drawn is not ceiling-versus-variance. It
is **availability versus consumption**: the 0.113 bound is a bound on the effect
of *enabling* retrieval on a model that mostly declines it, and only the 0.312
bound — on 8 trials — is about retrieved content at all.

### 3.2 Did the design assume a baseline region Opus 5 does not occupy?

Partly, and in an unexpected direction. The power table assumes p ≈ 0.85. Opus 5
realized 1.00, 1.00 and 0.40 in the three classes — bimodal, not centred. But
p = 1.00 is *inside* the range the spec calls robust and on the favourable side
of it. The genuinely out-of-model value is the 0.40, and §4 shows it is not a
baseline value at all: it is an instrument reading.

---

## 4. The date-class grading artifact — deterministic analysis

Position analysis over all 32 `exact_entity` trials, on the same normalised text
the frozen grader uses. Every accept and reject alias was located by
word-boundary match and its first position recorded.

| finding | count |
|---|---:|
| entity trials | 32 |
| **contained the accepted entity** | **32** |
| contained no accepted entity | **0** |
| graded correct | 4 |
| **contained the accepted entity and were graded incorrect** | **28** |
| of those, a reject alias also present | 28 |
| **of those, accepted entity appears STRICTLY BEFORE the reject** | **28 / 28** |
| of those, accepted entity within the first 40 normalised characters | 15 |

A successor/temporal cue (`succeeded`, `until`, `took office`, `later`,
`retired its previous name`, …) sits within ±120 characters of the reject
mention in **26 of 28**; the two that my cue list missed are both `a19`, whose
reject hit is `"Redskins"` introduced as *"had retired its previous name"* — a
predecessor, not a successor.

### Classification of the 28

Deterministic evidence first, then a clearly-labelled semantic read.

- **DETERMINISTIC:** accept present 28/28; accept strictly first 28/28; a
  contextual cue adjacent to the reject 26/28.
- **POST-HOC SEMANTIC REVIEW** (labelled; not used for any count that feeds a
  statistic): **A — correct requested answer plus a historical or comparative
  mention: 28. B — genuinely contradictory or ambiguous: 0. C — other: 0.**

Representative, in full:

> *"As of 1 June 2020, the President of Brazil was **Jair Bolsonaro**. He took
> office on 1 January 2019 and served until 31 December 2022, when he was
> succeeded by **Luiz Inácio Lula da Silva**."* → graded **incorrect**

> *"**Roger Federer.** As of 1 January 2020, Federer led all male players with 20
> Grand Slam singles titles… **Rafael Nadal** was second with 19… and **Novak
> Djokovic** third with 16."* → graded **incorrect**

The second is worse than the first: the rejects are the *runners-up in a ranking
the question asked for*. Naming them is not context, it is the answer being
complete.

### 4.1 The second artifact, on the boolean route

Not identified in the Stage 0A-M report.

`grade_boolean` computes `neg = any(negation phrase present anywhere)` and, for
`expected=True`, requires `pos and not neg`. Item `a09` ("As of 1 January 2020,
was the UK a member state of the EU?", expected `True`) was answered **"Yes."**
as the first word in **both** arms and graded **incorrect in both**, because the
token `no` matches inside *"…it was **no** longer a member state…"* at character
409.

All 14 boolean trials open with the correct polarity token. The rule is also
**asymmetric**: for `expected=False`, `neg and not expected` short-circuits to
correct, so a "No." answer is robust; only `expected=True` items are exposed. Six
of the seven boolean items expect `False`, which is why one item's failure looks
like noise instead of a 50% false-negative rate on the exposed subclass.

### 4.2 The consequence — the finding that decides Stage 0B

Total incorrect grades in the run: **30 of 130**. Of those, 28 are the entity
artifact and 2 are the boolean artifact. **30 of 30.**

Re-scored under a first-mention / first-polarity-token rule
(`POST-HOC COUNTERFACTUAL, diagnostic only, no inferential standing`):

| class | closed | retrieval | n00 | n01 | n10 | n11 | D |
|---|---:|---:|---:|---:|---:|---:|---:|
| `date_anchored` | 25/25 | 25/25 | 0 | 0 | 0 | 25 | **0** |
| `definition_anchored` | 25/25 | 25/25 | 0 | 0 | 0 | 25 | **0** |
| `arithmetic_control` | 15/15 | 15/15 | 0 | 0 | 0 | 15 | **0** |

**130 / 130.** Not one trial in the entire experiment gave a substantively wrong
answer.

This is stronger than the report's *"date-anchored difficulty was largely an
instrument artifact"*. It was **entirely** an instrument artifact. The
`anchored_v1` battery contains **zero items that Opus 5 answers incorrectly**.
The battery is not a stress sample that turned out mild; it is at complete
ceiling, and its only apparent difficulty was the grader.

The frozen grades are unchanged. This counterfactual is a diagnosis of the
instrument, not a re-analysis of the experiment, and it is the reason §9 retires
the battery rather than salvaging it.

---

## 5. The discordant pairs

Both, in full. Neither is evidence of anything about retrieval.

| item | arm | search calls | turns | accept hit | reject hit | frozen grade |
|---|---|---:|---:|---|---|---:|
| `a13` | closed | **0** | 1 | Bolsonaro @0 | **Lula** | 0 |
| `a13` | retrieval | **0** | 1 | Bolsonaro @0 | — | 1 |
| `a23` | closed | **0** | 1 | Sturgeon @0 | — | 1 |
| `a23` | retrieval | **0** | 1 | Sturgeon @0 | **Yousaf** | 0 |

`a13` closed: *"…the President of Brazil was **Jair Bolsonaro**. He took office
on 1 January 2019 and served until 31 December 2022, when he was succeeded by
Luiz Inácio Lula da Silva."*
`a13` retrieval: *"**Jair Bolsonaro.** He served as President of Brazil from 1
January 2019 to 31 December 2022, so on 1 June 2020 he was the sitting
president…"*

Same knowledge, same correct entity, different amount of trailing context.

**Classification: GRADING / ELABORATION ARTIFACT — both pairs.** Not
"ambiguous". The Stage 0A-M report reached the same conclusion by reading the
answers; this review can close it mechanically: **the retrieval-arm trial in each
pair performed zero searches**. A trial that never retrieved cannot have been
displaced by retrieved content. The single `n10` and the single `n01` are
elaboration style interacting with reject-precedence, and nothing else.

The official p-value is unchanged.

---

## 6. Retrieval-uptake audit

Measured from the raw harness records, per trial, for all 65 treated trials.

| | |
|---|---:|
| treated trials | 65 |
| **NOT_ATTEMPTED** | **57** |
| **WebSearch attempted** | **8** |
| **WebFetch attempted** | **0** |
| total search requests | 12 (8 trials × 1–2) |
| tool failures among attempts | 0 |
| permission denials | 0 |

**The claimed ~8/65 is confirmed** — but not by the field one would reach for
first, and the discrepancy is worth recording:

- `usage.server_tool_use.web_search_requests` is **0 in all 130 trials**. It is
  not a usable retrieval indicator on this harness path.
- `modelUsage["claude-haiku-4-5"].webSearchRequests` is > 0 in exactly 8, and
  `modelUsage["claude-opus-5"].webSearchRequests` is **0 in all 130** — the
  search is billed to the harness's search model, not to the solver.
- `num_turns > 1` holds in exactly the same 8 trials, and `num_turns > 1 ⟺
  webSearchRequests > 0` with no exceptions. A third turn is a tool round-trip,
  which is independent corroboration.

Their answers corroborate it in substance: `b04` cites *"RTE's Bilan électrique
2022"*, `b21` says *"remains unchanged as of September 2026"*, `b19` says
*"currently has 24 official languages"* — present-tense, source-attributed
framing absent from the declining trials.

### 6.1 Where the retrieval landed — the finding the report does not make

| class | attempted / treated |
|---|---:|
| `definition_anchored` | **8 / 25** |
| **`date_anchored`** | **0 / 25** |
| `arithmetic_control` | 0 / 15 |

**All eight retrieval attempts fell in the one class that was at 100% accuracy
in both arms. The class with the only outcome variance in the entire experiment
received zero doses of the treatment mechanism.**

Among the 8 that retrieved: 8/8 correct, closed partners 8/8 correct, 0
discordant. Bound on harm given actual consumption: ≤ 0.312 on n=8.

### 6.2 What Stage 0A-M primarily measured

> **Retrieval AVAILABILITY.** It is a clean intent-to-treat estimate of the
> effect of *granting* `WebSearch` and `WebFetch` to a model that then declines
> to use them 88% of the time — and, in the class designed to create anchoring
> pressure, 100% of the time.
>
> It is **not** a measurement of the consumption of retrieved information. The
> entire evidential basis for that question is 8 trials in a class at ceiling,
> and 0 trials in the class that could have shown displacement.

`E` was search-capable and fetch-blocked, so even the availability treatment was
search-snippets-only. WebFetch was never attempted, so the environment's block
was never exercised in production; it constrained the treatment definition, not
the observed behaviour.

### 6.3 A defective field in the official analysis artifact

`analysis.json` reports `retrieval_failure_rate: {attempted_retrieval: 0,
declined_retrieval: 65}`. This is **not a measurement**. `analyse_run` constructs
every `TrialOutcome` with `retrieval_outcomes=()`, so `retrieval_failure_rate`
classifies all 65 treated trials as `NOT_ATTEMPTED` by construction; it would
return the same numbers if all 65 had retrieved. The true value is 8.

The primary result does not depend on it (grades alone determine the tables), so
nothing is invalidated. But the field must not be cited, and Stage 0B must bind
its retrieval-outcome vocabulary to something actually recorded per trial —
which, on this harness, means `num_turns` and `modelUsage[*].webSearchRequests`,
not `usage.server_tool_use`.

---

## 7. Effort, as a mediator

| group | n | median output tok | median wall | cost |
|---|---:|---:|---:|---:|
| closed | 65 | 184 | 6.88 s | $1.06 |
| retrieval (all) | 65 | 180 | 6.95 s | $1.45 |
| — of which **searched** | 8 | **506** | **16.63 s** | $0.60 |
| — of which **declined** | 57 | 161 | 6.69 s | $0.85 |

P4 is scored "not supported" as an ITT claim, correctly. But the ITT null is a
dilution artifact: conditional on actually retrieving, output tripled and wall
time went up 2.5×. **The effort effect of retrieval is large and was hidden by
88% non-uptake** — the same dilution that hid whatever displacement effect may
exist.

---

## 8. What Stage 0A-M taught, and what it did not

**Taught (OBSERVED).**
1. The execution machinery works end to end: 130/130, 0 voids, single freeze
   commit, perfect schedule compliance, verified realized tool surfaces.
2. Opus 5, closed-book, answers 65/65 anchored and definition-anchored items
   correctly. The `anchored_v1` battery has no difficulty for this model.
3. Opus 5 declines available retrieval on 88% of these items, and on **100%** of
   the date-anchored ones. Availability is a weak intervention on a confident
   model.
4. When it does retrieve, cost and latency roughly triple.
5. A deterministic, fingerprinted, golden-corpus-tested grader mis-scored **30 of
   130** production trials, in two independent ways, and every pre-production
   check passed.

**Did not teach (and must not be claimed).**
1. Nothing about whether retrieved content displaces a correct anchored answer.
   The evidence is 8 trials, all in a ceiling class, none date-anchored.
2. Nothing about query construction. No query was ever logged; the harness does
   not record query text, and the raw records contain no tool transcript.
3. Nothing about unrestricted web retrieval. WebFetch was blocked and never
   attempted.
4. Nothing about safety. A null at a sensitivity that could not have rejected is
   not evidence of absence, and the run's own harm bounds (≤0.113 availability,
   ≤0.312 consumption) are far too wide to reassure anyone.

---

## 9. Recommendations, in dependency order

1. **Repair the grader before Stage 0B, and freeze the repair before any Stage 0B
   outcome.** Both routes, not just the entity route. Candidate implemented at
   `lab/grading_v2.py` with a hand-derived semantic corpus at
   `tests/golden/stage0b_grader_semantic_corpus.yaml`.
2. **Retire `anchored_v1` for confirmation.** It is at complete ceiling and it is
   production-exposed. See the Stage 0B design draft §8.
3. **Stop measuring availability.** At 12% uptake — 0% where it mattered — an
   optional-retrieval arm is unpowered at every n the simulation reaches.
4. **Log the query, the retrieved content, and its relevance per trial.** None of
   the three is recoverable from Stage 0A-M's artifacts.
5. **Commit and fingerprint the freeze/grade/analyse driver before the first
   dispatch** (§1.1).
6. **Bind retrieval-outcome fields to something actually recorded** (§6.3).

Design work following from these: `docs/EXP004_STAGE0B_DESIGN_DRAFT.md`.
