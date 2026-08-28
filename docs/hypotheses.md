# Hypothesis ledger

The lab's memory. Every hypothesis we're actually testing, what would settle it,
and what each experiment changed.

**The rule that makes this useful:** after every experiment, record what it
*changed*. A result that updates nothing here is either a badly chosen
hypothesis or an unread result. Both are worth catching.

**Status values:** `open` (no data yet) · `testing` (experiment running) ·
`supported` / `not supported` / `mixed` (has data) · `retired` (superseded or
no longer interesting, with a reason).

---

## H1 — The epistemic layer beats the model alone at comparable cost

> A model given claim-type routing, freshness warnings, and a budgeted
> verification directive produces more correct answers than the same model
> answering alone, and the extra cost is justified by the gain.

- **Status:** `WEAKENED` by exp001 (2026-08-28)
- **Result:** `verified` beat `baseline` (78% vs 60%) but NOT at comparable cost
  (0 -> 30 observed tool calls), and did NOT beat its own `search_only` control
  (78% vs 84%; 85% vs 91% under the f08 sensitivity correction). The "at
  comparable cost" clause fails outright. The layer's central promise — that
  routed, budgeted verification beats naive verification — is not supported.
- **Settled by:** `exp001`
- **Falsified if:** the `verified` condition's accuracy is within noise of
  `baseline`, or its accuracy gain costs more searches per additional correct
  answer than the gain is worth.
- **Partial evidence from `exp001pilot`:** the two halves of the treatment were
  measured separately and both help, so the full treatment is very unlikely to
  be null. But "does the combination beat either half at a cost worth paying"
  is exactly what has not been measured.
- **Why it's the priority:** the packet calls this "the single biggest open
  question", untested across the whole design session. Everything downstream —
  whether to build Phase 4 at all — is conditional on it.

### H1a — The directive alone helps, without any retrieval

> Telling a model what *kind* of claim it faces improves its conduct even when
> it cannot verify anything.

- **Status:** `NOT ESTABLISHED` after the completed exp001 (2026-08-28).
  Downgraded from the earlier partial run's "weakly supported".
- **Completed-run result:** **60% → 70%** on haiku at **zero tool cost**
  (n=15, single run, no repeats). Direction consistent with the partial run's
  +13, but the gap sits close to the **±8-point judge-noise floor** measured in
  H-judge, so it is suggestive rather than demonstrated. Not refuted either.
- **The single most informative trial:** `f05`, "Who is the CEO of Berkshire
  Hathaway?" — same model, same closed book, no tools either way.
  `baseline` answered **Warren Buffett**. `directive_only` answered **Greg
  Abel**, correctly, and explained the succession. The directive did not add
  information; the model already had it. What it changed was whether the model
  reached for the famous answer or for the current one. That is the mechanism
  this project claims exists, observed once.
- **Why "weakly":** n=15, one model, one run, no repeats. Several per-question
  differences are judge noise rather than effect (see H-judge below). The
  direction is consistent and the cost is genuinely zero, which is what makes
  it worth pursuing rather than believing.
- **Settled properly by:** `exp001` at full scale, across models
- **Why it's split out:** the packet's proposed "baseline vs. verified" design
  confounds the directive with web access. If H1a holds, the layer has a nearly
  free win available. If it doesn't, the layer's whole value is in how it
  *spends* searches — a more expensive and more fragile claim.

### H1b — Search alone accounts for most of the gain

> Most of `verified`'s advantage over `baseline` is web access, not the
> procedure.

- **Status:** `SUPPORTED` — and it is now the strongest finding in the project
- **Completed-run result:** `exp001`, 2026-08-28, full 15/15 — `search_only`
  reached **84%**, ABOVE the full treatment's 78%. Every one of the five
  closed-book failures was a current-fact question and search fixed all of
  them: volatile entity 0% -> 100%, scheduled entity 0% -> 100%.
- **Where it wins, precisely:** every question the closed conditions got
  *wrong* was a current-fact question. `volatile_entity` 0% → 100%,
  `scheduled_entity` 0% → 100%. No amount of procedure recovers a fact the
  model does not have; only retrieval does.
- **Read this cautiously:** 6 of 15 questions, and the 6 that ran were
  entity-lookup questions, which are search's best case. The remaining 9
  include the ambiguity, contested-quantity and freshness-conduct questions
  where search may add nothing. The 100% is almost certainly an overestimate.
- **Settled properly by:** completing `search_only` and `verified` in `exp001`

---

## H2 — The 30-day VOLATILE TTL threshold is approximately right

> The flat 30-day default in `EntityRecord` is close enough to observed
> turnover intervals to be worth keeping.

- **Status:** `open` — and currently **unfalsifiable with the data we have**
- **Settled by:** an experiment that doesn't exist yet; needs observed
  turnover intervals for a larger entity sample
- **What exists:** `EntityRecord.observed_intervals_days` accumulates real gaps
  whenever `record_verification()` sees a changed value.
  `threshold_is_calibrated` returns False below three observations, and the
  staleness message says "threshold is uncalibrated — an estimate, not a
  measurement" out loud rather than letting a guessed number pass as a measured
  one.
- **Honest state:** the packet says this was "chosen by eyeballing two
  examples". That's still true. The machinery to fix it exists; the data
  doesn't.

---

## H3 — Entity-hazard TTL bucketing generalises beyond the seed entities

> VOLATILE / SCHEDULED / STABLE is the right carve-up, and holds on entities
> nobody had in mind when it was designed.

- **Status:** `open`
- **Settled by:** a battery of 20+ untested entities across the three buckets
- **Falsified if:** a substantial fraction of new entities don't fit any bucket,
  or the bucket assignment doesn't predict staleness better than a flat TTL
- **Known weak spot, already identified:** the "scheduled-hybrid" case (NATO SG,
  4-year renewable). A pure SCHEDULED reading gets renewal wrong, which is why
  `f04` asks about the term specifically. Watch this one.
- **Note:** this is `a04` in the abstract battery, so the lab also asks models
  to forecast it — the answer to record here is a calibrated one, not a verdict.

---

## H4 — The layer's benefit is larger for smaller models

> A weaker model gains more from being told how to handle a claim than a
> stronger one, because the stronger one already does some of it unprompted.

- **Status:** `open` — pilot ran haiku only
- **Settled by:** `exp001` (haiku vs. sonnet), extended by adding opus
- **Note from the pilot:** haiku's baseline was 60%, and its failures were
  concentrated in exactly the places the layer targets (stale entities,
  premise acceptance). That leaves room for the directive to help. A stronger
  model with a higher baseline has less room, which is the shape H4 predicts —
  but a prediction is not a measurement.
- **Falsified if:** the directive's effect is flat across model sizes, or
  inverted
- **Why it matters practically:** if it holds, the cheap play is a small model
  plus the layer rather than a large model alone — which is the actual
  deployment question behind "optimized and efficient".

---

## H5 — The classifier's safe-default asymmetry is cheap in practice

> Defaulting to EMPIRICAL when unsure (costing an extra search) rather than
> DETERMINISTIC (costing a skipped verification) doesn't waste much.

- **Status:** `WEAK EVIDENCE, ONE TRIAL` after exp001
- **exp001 observation:** the classifier misrouted f10 (a pure word problem) as
  EMPIRICAL with a 2-search budget. In `verified` the model overruled it —
  "the classification suggests it's an empirical claim, but this is actually a
  straightforward mathematical problem" — and spent 0 observed tool calls, so
  the misroute cost nothing. One trial, one obvious misroute. Also note 14/15
  questions routed EMPIRICAL, so the classifier barely discriminates on this
  battery.
- **Settled by:** measuring how many `verified`-condition searches were spent on
  questions the model would have answered correctly with no search at all
- **Falsified if:** a large share of searches change nothing about the answer
- **Connects to:** `a06` in the abstract battery — "what counts as *wasted*
  verification cost" is genuinely definitional, and the answer changes the
  accounting here. Settle the definition before quoting a number.

---

## H-judge — The judge is a reliable instrument

> Blind judge grading is consistent enough that a several-point difference
> between conditions is signal, not grader noise.

- **Status:** `NOT SUPPORTED` — now on measurement, not anecdote
- **Evidence:** exp001 re-judged 12 (question, standard, response) triples a
  second time, blind and independently. **Verdict agreement 8/12 = 67%**, mean
  absolute score difference **0.133**, max **0.40**, with 3/12 differing by
  >= 0.20. Verdicts flipped on f08-baseline, f11-baseline, f12-baseline and
  f14-directive_only. A thirteenth accidental replication returned the same
  verdict 0.10 apart.
- **The number that matters:** any judge-graded condition difference under
  roughly **8 accuracy points** at n=15 is inside grading noise.
- **What it changes:** any per-question difference of this size in a
  judge-graded row is uninterpretable on n=1. Deterministically-graded rows
  (`contains_any`, `numeric`, `trap_detected`) are not affected. The
  `directive_only` headline gain survives because it rests mostly on
  deterministic rows — but it is now a claim about those rows, not about the
  battery as a whole.
- **Next:** either grade judge-rows in duplicate and report disagreement, or
  tighten the rubrics so the two readings of "stale number with correct
  framing" cannot both be defensible. The second is cheaper and probably
  right — the rubric genuinely does not say which component dominates.

---

## Retired / superseded

*(nothing yet)*

---

## Experiment log

| Experiment | Date | Hypotheses | Result | What it changed |
|---|---|---|---|---|
| `exp001pilot` (partial) | 2026-08-27 | H1a, H1b, H-judge | 36/60 trials; `verified` never run | Superseded by the completed run below. Preserved, not discarded. |
| **`exp001` (complete)** | **2026-08-28** | H1, H1a, H1b, H-judge, H5 | **60/60 trials.** baseline 60% · directive_only 70% · search_only **84%** · verified **78%** | H1 -> WEAKENED: the layer lost to its own search-only control. H1b -> SUPPORTED, now the strongest result. H1a -> downgraded to NOT ESTABLISHED (inside noise). H-judge -> NOT SUPPORTED on measured 67% agreement. Sandbox bug verified fixed behaviourally; a fourth instrument defect found (f08 reject-list artifact). Full report: `runs/exp001pilot/EXP001_FINAL_REPORT.md`; next steps: `docs/HANDOFF_after_exp001.md`. |

---

## Bugs the lab found in itself

Kept because they are the same shape as the classifier bugs in the handoff
packet: each read as obviously correct and was wrong in practice.

1. **`tools: []` grants every tool, not none.** Both closed-book solvers and
   the judge were declared that way and were not sandboxed at all. The test
   that was supposed to catch it asked "are any forbidden tools listed?" — and
   an empty list lists nothing, so it passed vacuously. A check that cannot
   fail on the empty case is not a check. Fixed by declaring an explicit inert
   tool and requiring a non-empty list.
2. **A numeric tolerance that swallowed its own distractor.** `f10` used
   tolerance 0.5 against a distractor 0.5 away from the truth, so the trap
   answer (77.5 for 78) scored as correct. The grader now refuses that
   configuration instead of producing a wrong number from it.
3. **The trap grader failed correct answers for mentioning a year.** "Tesla
   never won ... he was nominated in 1912" failed because "1912" was on the
   reject list. Explicit rejection now outranks an incidental mention, and a
   both-present case escalates to a judge rather than auto-failing.

A fourth was a false alarm rather than a bug: the leak audit flagged every
*correct* answer, because it matched against the accept-strings a right answer
necessarily contains. Narrowed to distinctive ground-truth prose.

**Found in the completed exp001 (2026-08-28):**

4. **The reject-list defect was fixed for f06 and missed for f08.** Both
   search-enabled f08 answers explicitly said no EU member state left in 2024,
   and both were auto-failed for containing the substring "Poland and" inside
   a clause saying Poland did *not* leave. Same defect class as bug 3, fixed in
   one place and not audited elsewhere. **Not rescored** — exp001 was frozen —
   but reported with a sensitivity analysis (costs each search condition 6.7
   points; does not change the ordering).
5. **`searches_used` is not a measure of tool use.** Self-reports undercount
   observed tool calls by ~2x, one-directionally, in 18 of 30 search trials and
   never over-report. By self-report 0 trials broke their budget; by observed
   calls, 13 did.

---

## Open questions not yet formed into hypotheses

Parked here rather than lost. Promote one when it's sharp enough that a
specific result would settle it.

- **Held-out battery.** Iterating directive wording against `factual_v1` will
  eventually tune the directive to those 15 questions. A second battery, never
  used for iteration, is the standard defence. This is the most likely way the
  lab quietly stops measuring anything (lab manual §7.6).
- **Judge-generator correlation.** A Claude judge grading Claude solvers shares
  blind spots. The packet's defence — a different model family for the judge —
  needs API access we don't have. Is there a cheaper proxy?
- **Does the abstract battery move at all?** Normative/predictive/definitional
  conduct might be nearly invariant to the directive, in which case the layer's
  value is entirely on the empirical path and the other four claim types are
  documentation rather than mechanism.
- **Cost of being wrong about the claim type.** The classifier's demotion rail
  is asymmetric by design. What does a misroute actually cost in practice, per
  direction?
- **Prior art re-check.** Packet §8's "fragmented, open gap" framing rests on a
  time-bound search and the packet flags it as the claim most likely to have
  shifted. Re-run the multi-vocabulary search before relying on it.
