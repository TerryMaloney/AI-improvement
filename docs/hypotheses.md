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

- **Status:** `open` — the `verified` condition has not run yet
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

- **Status:** `supported` (weakly — one model, n=15, single run)
- **First evidence:** `exp001pilot`, 2026-08-27 — **60% → 73%** on haiku, at
  **zero additional searches**. Trap accuracy 65% → 82%; premise-flagging rate
  25% → 50%.
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

- **Status:** `supported so far, and it matters` — the deflationary hypothesis
  is currently the strong one
- **First evidence:** `exp001pilot`, 2026-08-27 — `search_only` scored **100%
  on the 6 of 15 questions that completed** before a rate limit ended the
  condition, against 60% baseline, for 6 searches (2.5 searches per additional
  correct answer).
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

- **Status:** `open`
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

- **Status:** `not supported` — added because the pilot produced a direct
  counterexample
- **Evidence:** `exp001pilot`, question `f14` (Saturn's moons). The `baseline`
  and `directive_only` answers both gave the same stale number, 146, with the
  same as-of qualifier. Different judges scored them **PARTIAL (0.65)** and
  **PASS (0.90)** — a 25-point gap on materially identical content, one judge
  penalising the stale figure and the other crediting the freshness framing the
  rubric asked for.
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
| `exp001pilot` | 2026-08-27 | H1a, H1b, H-judge | `baseline` 60% · `directive_only` 73% (0 searches) · `search_only` 100% on 6/15 · `verified` not run | H1a → supported (weakly). H1b → supported and now the strong deflationary reading. H-judge added and immediately not supported. Three bugs found in the lab's own instrument (see below). |
| `exp001` | — | H1, H1a, H1b, H4 | not yet run | — |

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
