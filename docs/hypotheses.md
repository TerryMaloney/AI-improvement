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

- **Status:** `open`
- **Settled by:** `exp001`
- **Falsified if:** the `verified` condition's accuracy is within noise of
  `baseline`, or its accuracy gain costs more searches per additional correct
  answer than the gain is worth.
- **Why it's the priority:** the packet calls this "the single biggest open
  question", untested across the whole design session. Everything downstream —
  whether to build Phase 4 at all — is conditional on it.

### H1a — The directive alone helps, without any retrieval

> Telling a model what *kind* of claim it faces improves its conduct even when
> it cannot verify anything.

- **Status:** `open`
- **Settled by:** `exp001`, the `directive_only` cell
- **Why it's split out:** the packet's proposed "baseline vs. verified" design
  confounds the directive with web access. If H1a holds, the layer has a nearly
  free win available. If it doesn't, the layer's whole value is in how it
  *spends* searches — a more expensive and more fragile claim.

### H1b — Search alone accounts for most of the gain

> Most of `verified`'s advantage over `baseline` is web access, not the
> procedure.

- **Status:** `open`
- **Settled by:** `exp001`, the `search_only` cell
- **Note:** this is the deflationary hypothesis, and it is deliberately in the
  ledger. If `search_only` ≈ `verified`, the honest finding is "let it search"
  and the layer is doing little.

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

- **Status:** `open`
- **Settled by:** `exp001` (haiku vs. sonnet), extended by adding opus
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

## Retired / superseded

*(nothing yet)*

---

## Experiment log

| Experiment | Date | Hypotheses | Result | What it changed |
|---|---|---|---|---|
| `exp001` | — | H1, H1a, H1b, H4 | not yet run | — |

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
