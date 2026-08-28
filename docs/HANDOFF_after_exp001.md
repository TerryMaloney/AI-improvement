# Handoff after exp001

exp001 is complete and frozen. 60/60 trials, 0 excluded, 0 ungraded.
Full result: `runs/exp001pilot/EXP001_FINAL_REPORT.md`.

**Nothing has been changed in response to the results.** The grading defect
found in §7 of the report is documented and left in place. The directives,
prompts, battery, and scoring criteria are exactly as they were when the run
started. That is deliberate: the next experiment should begin from a frozen
baseline, not from a baseline already tuned to make exp001 look better.

This document says what should be tested next and what in exp001 motivates it.
It does not start that work.

---

## The result the next experiment has to deal with

`search_only` (84%) beat `verified` (78%). The full epistemic layer lost to its
own control. Under the f08 sensitivity correction the gap holds: 91% vs 85%.

Everything below follows from taking that seriously rather than explaining it
away.

---

## Before any new experiment: three repairs

These are repairs to the instrument, not changes to the theory. They should
land **before** the next run, and the next run should re-baseline against them.

### R1 — Fix the `reject`-list defect across the whole answer key (BLOCKING)

f06's reject entries were fixed during the pilot; f08's were not audited at the
same time, and f08 then failed both search conditions for the substring
"Poland and" inside a sentence saying Poland did not leave the EU.

The fix already exists in `grade_trap_detected` — explicit premise rejection
outranks an incidental mention. What is missing is an audit of every `reject`
and `accept_trap_markers` list in `batteries/answers.yaml` for the same class of
error, plus a test that fails when a reject string can match inside a negation.

**Why blocking:** it silently inverted a result on a trap question, which is
precisely the question type the project exists to measure.

### R2 — Make cost measurement observed-only

`searches_used` undercounts real tool calls by ~2×, one-directionally, in 18 of
30 trials. Judged by self-report, 0 trials broke their budget; judged by
observed calls, 13 did.

Record `tool_calls_observed` as the primary cost metric in the store and the
report generator. Keep the self-report as a separate column — the *gap* between
them is itself a measurement of whether a model knows what it did, which is
worth tracking, not discarding.

### R3 — Give the judge a reliability floor, or stop using single judgements

Measured: 67% verdict agreement, mean |Δscore| 0.133, max 0.40 on 12 paired
judgements. That puts a **±8 accuracy point noise floor** on any judge-graded
comparison at n=15.

Two workable options, in preference order:
1. **Judge every judged trial 3× and take the median**, reporting spread. Costs
   3× judge spawns, which are cheap and tool-free.
2. **Tighten the rubrics** so the two defensible readings collapse. `f14`'s
   rubric genuinely does not say whether a stale number or correct freshness
   framing dominates, and both judges were reasonable.

Do not do (2) alone — rubric tightening after seeing results is where an
experiment quietly becomes unfalsifiable. (1) is the honest fix; (2) is a
follow-on that should be pre-registered.

---

## The next experiment: exp002

**Question it must answer:** *is there any condition under which routed,
budgeted verification beats naive search — and if not, does the layer have a
purpose?*

exp001 says the layer's search arm is worse than naive search on this battery.
There are three live explanations, and they are distinguishable.

### Explanation 1 — the budget is the problem

**Evidence from exp001.** `verified` gets a route-derived budget (2 searches on
most questions, 0 on deterministic); `search_only` gets a flat 3. Observed
tool calls: 30 vs 39. **The treatment condition searched less than its control
and scored lower.** The layer may simply have been starved.

**Test.** Add a `verified_flat_budget` condition: full directive, flat budget of
3. If it matches or beats `search_only`, the directive is fine and the budget
policy is the defect — which is a narrow, fixable finding.

**This is the cheapest and highest-information next step, and it should be
exp002's core.**

### Explanation 2 — the directive hurts on contested questions

**Evidence from exp001.** Category accuracy on contested/moving-target
questions: baseline 82%, directive 83%, search 55%, verified 67%. On f15 both
search arms converged on an excess-mortality figure (~8.5M) that contradicts
the WHO figure in ground truth, while both closed-book arms gave the correct
15–20M range. **Searching made that answer worse**, and the directive did not
prevent it.

The directive tells the model to prefer retrieved evidence over its own recall
("your own recall is a hypothesis, not an answer"). On a contested quantity
where the model's prior is better calibrated than the top search result, that
instruction is actively harmful.

**Test.** Split the battery by whether retrieval is expected to help
(current-fact vs contested-quantity) and pre-register opposite predictions for
the two halves. If the directive helps on one and hurts on the other, that is
a real and useful boundary condition — and it reframes the layer from "makes
answers better" to "decides when to trust retrieval", which is a different and
more defensible claim.

### Explanation 3 — retrieval was too degraded to test the layer fairly

**Evidence from exp001.** `WebFetch` was blocked for at least 13 domains
including WHO-adjacent, IAU, Census and Wikipedia. Solvers fell back to search
snippets throughout. The layer's independence rule ("two sources tracing to one
report are ONE source") cannot be exercised when only aggregator snippets are
reachable.

**Test.** Re-run a subset with the proxy allowlist widened, or with primary
sources supplied as fixtures. If `verified` improves materially and
`search_only` does not, the independence machinery was real but untestable.

---

## Recommended exp002 design

Minimum viable, ~4 conditions × 15 questions × 1 model = 60 trials, plus 3×
judging:

| Condition | Directive | Budget | Purpose |
|---|---|---|---|
| `baseline` | no | none | re-baseline after R1–R3 |
| `search_only` | no | flat 3 | the control that won exp001 |
| `verified` | yes | route-derived | exp001's treatment, unchanged |
| `verified_flat` | yes | flat 3 | **isolates budget from directive** |

Pre-register, before running:
- the prediction for each condition on each battery half;
- that a difference under 8 points will be reported as null;
- that the f08-class grading audit (R1) is complete.

**Do not add models, do not add batteries, do not add ARC or LiveBench.** H4
(model size) is untested and interesting, but running it before the
single-model result is trustworthy would multiply an uncalibrated instrument
across three models and produce nine numbers nobody can defend.

---

## Explicitly deferred

- **H4, cross-model.** Only after exp002 settles the budget/directive
  confound.
- **The abstract battery** (`abstract.yaml`, 6 normative/predictive/definitional
  questions). Never run. It tests the half of the layer with no factual answer
  key, and it needs the judge fixed (R3) first, since it is 100% judge-graded.
- **H2 / H3, the TTL work.** exp001 touched neither. The registry has exactly
  one measured turnover interval (OpenAI CRO, ~270 days against a 30-day
  threshold). Needs a dedicated entity battery, not a rerun of this one.
- **Any self-improvement or benchmark work.** The instrument has a 2× cost
  measurement error and a 33% judge disagreement rate. Nothing built on top of
  it would mean anything yet.

---

## The honest summary for whoever picks this up

exp001 worked as an experiment. It produced a clean negative result about the
thing it was built to promote, it caught three defects in its own instrument,
and it did not get talked out of any of them.

What it has not done is show that the epistemic layer is worth building. On the
one battery where it has been measured, against the one control that matters,
it lost. The next experiment's job is to find out whether that is because the
idea is wrong or because the budget policy was wrong — and those are
distinguishable with one extra condition.

Resist the urge to fix the directive first. The directive is not what exp001
found fault with.
