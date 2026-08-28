# exp002 — Was `verified`'s deficit the directive, or the budget?

**Status: COMPLETE. Primary question NOT resolved as posed. Experiment STOPS here per the
pre-specified decision rule — no further conditions were added.**

| | |
|---|---|
| Design | Follow-up to exp001, **not** an independent replication |
| New data | 15 trials, one new condition (`verified_flat`), haiku, 2026-08-28 |
| Reused data | exp001's 60 raw answers, re-graded under key v2 — **not re-run** |
| Battery | `factual` (f01–f15), unchanged |
| Answer key | v2 (correction C1 only, pre-specified in `docs/ANSWER_KEY_CORRECTION_PROCESS.md`) |
| Judging | K=3 independent blind judgements per judge-graded trial, sonnet |
| Trials answered | 75 / 75 |
| Trials graded | 75 / 75 (0 UNGRADED, 0 NO_ANSWER, 0 DISPUTED) |
| Audit flags | 0 SANDBOX, 0 LEAK-SUSPECT; 18 BUDGET(observed), 27 COUNT-GAP (both expected, see §A.5) |

exp001 remains frozen at `runs/exp001pilot/` with its v1 grades. Its database still lacks the
R2 schema columns, which is mechanical proof it was not rewritten.

---

# A. OBSERVATIONS

Things measured. No interpretation.

## A.1 Headline scores

Score = mean of per-trial scores (0.0–1.0), n = 15 questions per condition.

| Condition | exp001 (frozen, key v1, 1 judge) | exp002 (key v2, K=3) | Δ |
|---|---|---|---|
| `baseline` | 60.3% | **64.0%** | +3.7 |
| `directive_only` | 70.3% | **70.0%** | −0.3 |
| `search_only` | 84.3% | **86.0%** | +1.7 |
| `verified` | 78.3% | **80.7%** | +2.4 |
| `verified_flat` | — | **86.3%** | new |

Verdict counts under v2 (PASS / PARTIAL / FAIL): baseline 9/1/5, directive_only 10/1/4,
search_only 12/2/1, verified 11/2/2, verified_flat 12/2/1.

## A.2 The three pre-specified comparisons

One question = 6.67 accuracy points. The judge-noise floor below is derived from measured
K=3 spread (§A.4), scaled by each condition's judge-graded share.

| Comparison | Δ | Δ in questions | Judge-noise floor | Questions that differ |
|---|---|---|---|---|
| `directive_only` − `baseline` | +6.0 | +0.90 | ±1.0 | f05 +1.00, f12 −0.10 |
| `verified` − `search_only` | **−5.3** | −0.80 | ±1.1 | f07 −0.40, f12 −0.40 |
| **`verified_flat` − `search_only`** (primary) | **+0.3** | +0.05 | ±1.1 | f07 −0.30, f14 −0.05, f15 +0.40 |
| `verified_flat` − `verified` | +5.6 | +0.85 | ±1.1 | f07 +0.10, f12 +0.40, f14 −0.05, f15 +0.40 |

Every one of these differences rests on **four questions or fewer**, and every one is smaller
than the 6.67 points a single question is worth.

## A.3 Per-question score matrix (key v2, K=3)

| q | category | baseline | directive_only | search_only | verified | verified_flat |
|---|---|---|---|---|---|---|
| f01 | volatile_entity | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| f02 | volatile_entity | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| f03 | scheduled_entity | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| f04 | scheduled_hybrid | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f05 | stable_entity | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f06 | false_premise | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f07 | false_premise | 1.00 | 1.00 | 0.40 | 0.00 | 0.10 |
| f08 | false_premise | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f09 | deterministic | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f10 | deterministic | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f11 | empirical_numbers | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f12 | stale_and_renamed | 0.10 | 0.00 | 1.00 | 0.60 | 1.00 |
| f13 | ambiguous_referent | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| f14 | moving_target | 0.50 | 0.50 | 0.50 | 0.50 | 0.45 |
| f15 | contested_quantity | 1.00 | 1.00 | 0.00 | 0.00 | 0.40 |

Ten of fifteen questions are flat across all five conditions. All measured variance lives in
**f05, f07, f12, f14, f15**.

## A.4 Judge reliability (R3)

99 judgements, one item per grader agent (the run-experiment protocol forbids batching items
into one grader), sonnet, blind, K=3 per trial.

| Metric | exp001 (paired, K=2) | exp002 (K=3) |
|---|---|---|
| Verdict agreement | 67% | **97.0%** (32/33 unanimous) |
| Mean score spread | 0.133 | **0.024** |
| Max score spread | 0.40 | 0.50 |
| DISPUTED (no majority) | n/a | **0** |
| Trials with spread ≥ 0.20 | — | 1 |

The only high-spread trial is `f11-search_only` (0.5 / 1.0 / 1.0 → median 1.0). Two other
trials show 0.10 spread (`f07-search_only`, `f14-verified_flat`); the remaining 30 are unanimous
in verdict and near-identical in score.

Derived judge-noise floor: mean spread 0.024 × judge-graded share (6–7 of 15) = **±1.0 to ±1.1
accuracy points per condition**. This is an order of magnitude below the ±8 points exp001's
single-judge measurement implied.

## A.5 Tool use — observed versus self-reported (R2)

`tool_calls_observed` comes from the harness. `searches_used` is the solver's self-report.
The budget audit is computed against **observed**, established before `verified_flat` was run.

| Condition | Observed | Self-reported | Ratio | Budget violations (observed) | Budget violations (self-report) |
|---|---|---|---|---|---|
| `baseline` | 0 | 0 | — | 0 | 0 |
| `directive_only` | 0 | 0 | — | 0 | 0 |
| `search_only` | 39 | 18 | 2.17× | 6 | **0** |
| `verified` | 30 | 15 | 2.00× | 7 | **0** |
| `verified_flat` | **37** | 18 | 2.06× | 5 | **0** |

Self-report undercounts observed use by roughly 2× in every search condition, and the error is
**one-directional** — no trial ever over-reported. By self-report there are zero budget
violations in the entire experiment; by observation there are 18.

## A.6 Did the manipulation actually change behaviour?

`verified_flat` differs from `verified` in exactly two prompt lines per question, both
`SEARCH BUDGET` (verified by diff). Observed effect:

* Ceiling: `verified` 2 on most questions (0 on deterministic) → `verified_flat` 3 everywhere.
* Observed tool calls: **30 → 37 (+23%)**, closing most of the gap to `search_only`'s 39.
* Per-question observed/ceiling (`search_only` / `verified` / `verified_flat`):
  f01 1/3, 1/2, 1/3 · f03 2/3, 1/2, 3/3 · f07 5/3, 3/2, 5/3 · f08 3/3, 2/2, 1/3 ·
  **f09 0/3, 0/0, 0/3 · f10 0/3, 0/2, 0/3** · f14 4/3, 4/2, 4/3 · f15 3/3, 2/2, 4/3.
* On f09 and f10 `verified_flat` spent **0 of 3** available searches. Raising a ceiling does not
  induce spending.
* On f08 `verified_flat` spent **fewer** searches than `verified` (1 vs 2) and scored the same.

## A.7 Retrieval failures and the tool environment

* `runs/TOOL_ENVIRONMENT_EQUIVALENCE.md`: two byte-identical probes, all 5 target domains
  returned `EGRESS_BLOCKED`. **WebFetch is effectively unusable in this environment**, for every
  condition equally. Every search condition therefore has WebSearch snippets and nothing else.
* Structured retrieval failures were recorded for `verified_flat` on f07 (3), f11 (3), f12 (2),
  f14 (3), f15 (2). The `retrieval_failures` field was introduced by R2 and so is **empty for
  the exp001 conditions** — their failures exist only in answer prose. This is a real gap in the
  dataset and is not patched.
* f07, all three search conditions: none could reach 2021 US–Japan bilateral trade data.
  `verified` names the blocker explicitly ("The Census Bureau maintains this data but was
  inaccessible to me"). `verified_flat` spent all 3 searches and still abstained.

## A.8 Every non-PASS trial

| Trial | Score | What happened |
|---|---|---|
| f01/f02/f03 baseline, directive_only | 0.00 | Closed-book; no access to post-cutoff officeholders. Both flagged staleness. |
| f05 baseline | 0.00 | Named Buffett as Berkshire CEO. `directive_only` named **Abel** — the one closed-book question the directive changed. |
| f07 search_only | 0.40 | Wrote "deficit" for 2019, never stated the premise is false, no 2021 figure. |
| f07 verified | 0.00 | Framed it as "Japan had a trade surplus", accepting the question's framing. Unanimous FAIL. |
| f07 verified_flat | 0.10 | Called the phrasing "ambiguous" rather than false; no 2021 figure. |
| f12 baseline | 0.10 | "Elon Musk is the CEO of Twitter" — wrong even at its own cutoff. |
| f12 directive_only | 0.00 | Same error, and never mentioned the X rename. |
| f12 verified | 0.60 | Correct on the vacancy; wrote "Twitter/X" without explicitly stating the 2023 rename. |
| f14 all five | 0.45–0.50 | Freshness conduct passes everywhere; the count component fails everywhere. |
| f15 search_only | 0.00 | Gave 8.5M as the excess-mortality figure (truth: high teens of millions). |
| f15 verified | 0.00 | Same 8.5M figure, **attributed to The Lancet**; judges called the attribution fabricated. |
| f15 verified_flat | 0.40 | Gave no excess figure at all — under-specified rather than wrong. |

## A.9 Source conflicts recorded, not resolved

* **f14 (Saturn).** Ground truth holds two figures: 285 (arithmetic traceable: 146 + 128 + 11)
  and 293 (asserted by one source without derivation). All three search conditions returned 293.
  `verified` and `verified_flat` both narrated the 146→+128→+11 trail and then stated 293 —
  an internal inconsistency their own arithmetic contradicts. No condition surfaced the conflict.
* **f11 (1918 flu).** Four different framings across five conditions: baseline 50–100M,
  directive_only 50–100M+, search_only **15–17.4M** ("more recent scholarly research"),
  verified 50–100M, verified_flat 21–100M. Search moved the answer furthest from the
  commonly-cited figure. Judges split on search_only (0.5/1.0/1.0) — the run's only real
  disagreement.
* **f15 (COVID).** All three search conditions converged on ~8.5M excess deaths. The key holds
  high-teens-of-millions. The two closed-book conditions gave 15–20M and passed unanimously.

## A.10 What C1 changed, isolated

C1 changed only which grading route a trial takes. Deterministic route changes, v1 → v2:

| Trial | v1 route + score | v2 route + score | Δ |
|---|---|---|---|
| f07 `search_only` | `trap_detected` **1.00** (bare marker "deficit") | judge **0.40** | −0.60 |
| f08 `search_only` | `trap_detected` **0.00** (reject "Poland and") | judge **1.00** | +1.00 |
| f08 `verified` | `trap_detected` **0.00** (reject "Poland and") | judge **1.00** | +1.00 |

Isolated C1 effect: `search_only` +0.40 raw (+2.7 pts), `verified` +1.00 raw (+6.7 pts).
Observed total movement was +1.7 and +2.4 points respectively; the remainder is re-judging under
K=3, which moved f07-verified 0.15→0.00 and f08-baseline 0.55→1.00. **The C1 effect and the
re-judging effect changed at the same time and cannot be fully separated in this run.**

## A.11 Cost and latency

`duration_s` is null for every exp002 trial — the field exists but the orchestrator does not
populate it for agent-dispatched trials. **Token counts, dollar cost, and wall-clock latency are
unavailable in this harness.** Observed tool calls (§A.5) is the only cost proxy that exists.

## A.12 Infrastructure incidents

None during exp002. No rate limits, no failed dispatches, no lost trials, no re-runs.
(exp001's two rate-limited trials remain recorded in its own `incomplete_trials.json`.)

---

# B. INTERPRETATIONS

Reasoning about the observations. Weaker than §A.

**B.1 The primary comparison is a null.** `verified_flat` (86.3%) and `search_only` (86.0%) are
0.3 points apart — one twentieth of a single question. Whatever the epistemic directive is doing
when its budget matches the control's, it is not moving the aggregate score in either direction.

**B.2 The `verified_flat` − `verified` gap moves in the direction explanation (ii) predicts, but
not by the mechanism (ii) requires.** The +5.6 points decompose as:

* **f12 (+0.40) — a rubric-sensitivity artifact, not a retrieval difference.** Both conditions
  found the same fact (the CEO seat is vacant since Yaccarino's July 2025 resignation). `verified`
  wrote "Twitter/X"; `verified_flat` wrote "X (formerly Twitter)". All three judges scored the
  first 0.6 (rename not explicitly stated) and the second 1.0, unanimously in both cases. The
  extra search did not find anything the shorter budget missed.
* **f15 (+0.40) — `verified_flat` scored higher for saying less.** `verified` asserted a specific
  wrong figure with a fabricated attribution; `verified_flat` asserted no figure. Under a rubric
  that penalises confident wrongness, silence outscores error. This is not evidence the budget
  helped; if anything it is evidence that the extra search made the answer *less* specific.
* **f07 (+0.10) and f14 (−0.05)** are within-band noise on questions both conditions failed.

So the budget manipulation demonstrably changed behaviour (+23% observed tool calls, §A.6) and
demonstrably moved the aggregate — but tracing the movement question by question, **none of it
came from better retrieval.**

**B.3 Neither exp001 explanation survives intact.** Under key v2 the entire
`verified` − `search_only` deficit is two questions, f07 and f12, and both turn on *how the
answer was phrased* rather than *what was retrieved*. Explanation (i) ("the directive is harmful")
requires a mechanism by which the directive degrades answers; what f07 and f12 show is a
directive-condition answer phrased in a way the rubric scores lower while containing the same
substance. Explanation (ii) ("the budget starved it") is contradicted by B.2. The exp001
negative result appears, on this evidence, to have been **substantially a measurement effect** —
but that is an inference from n=2 questions and is stated as such.

**B.4 Search is not uniformly beneficial; it trades one failure mode for another.** On current-fact
retrieval, search conditions score 100% against closed-book's 20–40%. On the false-premise and
contested-quantity questions the ordering **reverses**: closed-book 100%, search 0–80%. On f15 the
crossing is total — both closed conditions PASS unanimously, all three search conditions score
≤0.40, because retrieval supplied a wrong number (8.5M) that displaced correct parametric
knowledge (15–20M). This is the most robust finding in the run: it is unanimous across 3
independent judges, consistent across all three search conditions, and orthogonal to the budget.

**B.5 The environment cannot support what the directive asks.** The directive instructs source
verification; WebFetch is egress-blocked, so no solver can open a primary source. Every search
condition is running on search-result snippets. Any test of "does structured verification help?"
in this environment is really testing "does structured *snippet reading* help?"

**B.6 K=3 changed what the instrument can see.** exp001's ±8-point noise floor was an artifact of
measuring reliability from 12 paired judgements. With 3 judgements per trial the floor drops to
~±1 point. That does not make small differences meaningful — it relocates the dominant uncertainty
from the judge to the **sample**: at n=15, one question is 6.67 points, and every comparison in
this experiment is smaller than that.

---

# C. HYPOTHESES

Candidates for future tests. Not established here.

* **H-budget (revised).** Budget ceiling affects observed tool spend (+23% confirmed) but not
  answer quality within the 2–3 range. A wider sweep (0, 1, 3, 6, 12) on a battery where retrieval
  is decisive would test whether there is *any* budget-to-quality gradient.
* **H-phrasing.** A large share of measured between-condition variance is rubric sensitivity to
  answer phrasing rather than difference in retrieved content (f12: 0.6 vs 1.0 for the same fact;
  f07: 0.0 vs 0.4 for the same abstention). Testable by scoring paraphrases of a single answer.
* **H-search-displacement.** Retrieval can *displace* correct parametric knowledge with a wrong
  retrieved figure on contested quantities (f15, f11). Testable: closed vs search on a battery of
  contested quantities where the correct answer is a well-known range.
* **H-arithmetic-blindness.** On f14 both directive conditions narrated 146 + 128 + 11 and then
  asserted 293, without noticing their own arithmetic gives 285. Suggests generated reasoning
  chains are not checked against generated conclusions.
* **H-selfreport-invalidity.** Self-reported tool use is invalid as a cost metric — 2× undercount,
  one-directional, 0/18 violations detected. Any published epistemic-layer result relying on
  self-reported cost is unsound. (Close to established; kept as hypothesis because n=45.)
* **H-directive-abel.** f05 is the single closed-book question the directive changed
  (Buffett → Abel). One example. Explicitly **not** a claim that the directive improves
  closed-book accuracy.

---

# D. JUSTIFIED CONCLUSIONS

Supported by this experiment's data as it stands.

**D.1 The primary question is NOT resolved.** *"Did `verified` underperform `search_only` because
the procedure is harmful, or because the budget starved it?"* — `verified_flat` matches
`search_only` on aggregate score, which is consistent with the budget explanation; but the
question-level mechanism (§B.2) shows the recovered points came from a phrasing artifact and from
one condition saying less, not from improved retrieval. **INCONCLUSIVE.** Per the pre-specified
decision rule, the experiment stops here rather than adding conditions.

**D.2 Every measured condition difference in this experiment is smaller than one question.**
At n=15 with a ±1-point judge floor, the binding uncertainty is sampling, not grading. No
comparison in §A.2 is interpretable as a real effect. This includes `directive_only` − `baseline`
(+6.0 points, driven by exactly one question, f05).

**D.3 Solver self-reported tool use is not a valid measurement.** 2.0–2.2× undercount in all three
search conditions, one-directional, and it detects 0 of 18 observed budget violations. Established
by direct comparison against harness counts.

**D.4 The budget manipulation was real and was enforced against observed behaviour.** Ceiling 2→3
produced 30→37 observed calls. Solvers do not spend to the ceiling (0 of 3 on f09 and f10;
`verified_flat` used fewer calls than `verified` on f08). Budget is a ceiling, not a driver.

**D.5 Search hurts on false-premise and contested-quantity questions in this battery.** Closed-book
100% vs search 0–80% on those categories, with f15 unanimous across 9 independent judgements. The
effect is present in `search_only`, `verified`, and `verified_flat` alike, so it is a property of
retrieval, not of the epistemic directive.

**D.6 The K=3 judge is reliable enough to measure with; exp001's noise floor was overstated.**
97% unanimity, mean spread 0.024, 0 DISPUTED. exp001's ±8-point floor was an artifact of a
12-judgement reliability sample.

**D.7 No claim of model improvement is made.** No condition in this experiment demonstrates that
the epistemic control system makes the model more correct. `verified_flat` ties its own
search-only control; `verified` trails it; `directive_only` beats `baseline` by one question.

**D.8 The instrument has a known, unrepaired gap.** WebFetch is egress-blocked, so the
source-verification half of the directive cannot execute. Results here bound what can be learned
about the directive **in this environment**, not about the directive in general.

---

# E. CAPABILITY / FAILURE MAP

Scores are means over the questions in each row, key v2, K=3, n per condition in the last column.

| Capability | baseline | directive_only | search_only | verified | verified_flat | n |
|---|---|---|---|---|---|---|
| **Factual retrieval (current facts)** | 20% | 40% | **100%** | **100%** | **100%** | 5 |
| **False-premise handling** | **100%** | **100%** | 80% | 67% | 70% | 3 |
| **Procedural reasoning (arithmetic)** | **100%** | **100%** | **100%** | **100%** | **100%** | 2 |
| **Uncertainty / conflict handling** | 72% | 70% | 70% | 62% | **77%** | 5 |
| **Epistemic verification (executed)** | n/a | n/a | \* | \* | \* | — |
| **Tool-use efficiency** (observed calls) | 0 | 0 | 39 | **30** | 37 | 15 |

\* Not measurable in this environment: WebFetch is egress-blocked, so no condition could open a
primary source. What is measured is snippet-level search, not verification.

**Reading the map.**

* **Retrieval is the one place search is decisive** — +60 to +80 points, unanimous, no dependence
  on the directive. Both closed-book conditions fail f01/f02/f03 outright and flag their own
  staleness while doing so.
* **False-premise handling inverts.** Closed-book is perfect; search degrades it. On f07 the
  search conditions went looking for a number and, in the process, accepted the question's false
  framing. The closed conditions, having nothing to look up, examined the premise instead.
* **Procedural reasoning is saturated** at 100% in every condition and contributes zero variance.
  This battery cannot distinguish conditions on reasoning. (f10 remains the case where a solver
  correctly overruled the classifier's EMPIRICAL misroute.)
* **Uncertainty handling is the weakest capability overall** — nothing above 77%, and f14 fails
  in *every* condition. Failure mode is not abstention but unflagged source conflict:
  narrating 146+128+11 and then asserting 293.
* **Tool-use efficiency**: `verified` is the cheapest search condition (30 calls) at 80.7%;
  `verified_flat` spends 37 for 86.3%; `search_only` spends 39 for 86.0%. On this battery the
  cost-per-point differences are within one question of each other and should not be used to rank
  the conditions.

---

# F. WHAT REMAINS UNKNOWN

Stated plainly, per the instruction to stop rather than extend.

1. **Whether the epistemic directive helps at all.** Every comparison is under one question wide.
2. **Whether the budget policy was ever the problem.** The aggregate says maybe; the mechanism
   says no. These disagree and this experiment cannot adjudicate between them.
3. **Whether structured verification helps**, because verification cannot execute here —
   WebFetch is blocked.
4. **How much of exp001's negative result was C1 versus single-judge noise.** Both changed
   together in this run (§A.10).
5. **Whether any of this generalises** beyond haiku, 15 questions, one battery, and one session.
6. **Cost.** No token, dollar, or latency measurement exists in this harness.

The battery's ceiling is the binding constraint: 10 of 15 questions are flat across all five
conditions, so at most 5 questions carry any signal at all. Any future experiment intended to
detect an effect of this size needs a larger battery of *discriminating* questions before it
needs another condition.
