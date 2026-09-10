# EXP005-EPI Generator C — 2026-09-10

Status: **PROVISIONAL AMBER — exact committed runner still must reproduce the result.**

The frozen plan is `experiments/exp005_epi/generator_c_confirmation_plan.json` at
commit `9f678a545da5b8a785e10a93057c3a4bd8f9c9af`. Generator C, the candidate CRV
controller and its matched baselines were committed before any Generator-C
controller outcome was inspected.

## What Generator C changed

Generator C deliberately removes several gifts from A/B. Controller-visible
metadata can be wrong: source reliability is only an estimate, reported lineage
can split copies or merge independent evidence, temporal supersession can be
missed or falsely claimed, impact weights are noisy estimates, and verifier
reported accuracy can differ from hidden actual accuracy. Verification also has a
real acquisition cost and can be declined.

The controller does **not** receive hidden truth, evaluation impacts, actual
source accuracy, actual lineage, actual verifier accuracy or future verifier
outcomes.

It also contains blocked dependency paths: some propositions have many structural
descendants, but another already-resolved premise means changing the proposition
cannot currently change those conclusions. This is the case CRV is supposed to
handle better than a raw downstream-utility count.

## Frozen primary comparison

The candidate was:

`CRV-net = uncertainty × counterfactual affected reported utility × reported tool information quality - cost`

where counterfactual affected utility is measured by running the current belief
updater under opposite reports from the candidate tool and counting only beliefs
whose resolved state differs.

The strong simple baseline was:

`UDU-net = uncertainty × all structural downstream reported utility × reported tool information quality - cost`

Both choose the maximum positive action and otherwise choose no verification.

The important design choice is that tool economics are matched. The primary test
is therefore about the consequence signal, not about giving CRV a cost term that
the baseline lacks.

## Provisional outcome

The current artifact was produced by an independent local semantic
reimplementation because the analysis container could not resolve github.com for
a checkout. Before aggregation, the reimplementation was checked against the slow
committed semantics on frozen seeds: complete belief states and CRV consequence
fractions matched on five worlds, and complete outputs for all five policies
matched on three worlds. This is strong but not sufficient provenance for final
promotion, so the result remains provisional until the exact committed runner is
executed.

Across 1,000 frozen worlds:

| policy | weighted epistemic gain | cost | weighted net gain | net harm | early stop |
|---|---:|---:|---:|---:|---:|
| CRV-net | 0.04596 | 0.04382 | **+0.00213** | **45.5%** | 48.4% |
| UDU-net | **0.05112** | 0.07071 | -0.01959 | 64.7% | 3.5% |
| structural-net | 0.03370 | 0.11064 | -0.07695 | 93.1% | 0.0% |
| uncertainty-own-net | 0.00736 | 0.00701 | +0.00035 | 37.0% | 98.5% |
| legacy debt | 0.02592 | 0.04353 | -0.01760 | 64.5% | 0.0% |

Paired CRV-minus-UDU weighted net gain was **+0.02173**, approximate 95% interval
`[+0.01938, +0.02407]`. That clears the frozen primary practical threshold.

But CRV-minus-UDU weighted epistemic gain was **-0.00516**, and unweighted
epistemic gain was **-0.00567**. The latter narrowly misses the frozen -0.005
non-inferiority margin.

Most importantly, CRV's 45.5% net-harm rate catastrophically misses the frozen
10% absolute safety threshold. Its mean conditional net loss on harmed worlds was
about -0.0423; the 5th percentile was -0.0922 and the worst world was -0.2520.
This is not merely a rounding artifact around zero.

The frozen decision is therefore **AMBER**, not PASS.

## What the result actually says

The positive part is narrower than "CRV reasons better."

CRV acquired **less information** than UDU and achieved slightly *worse* final
truth accuracy, but spent much less on verification. Its mean net utility was
therefore better. The no-verification mechanism was genuinely exercised: CRV
stopped before the four-action maximum in 48.4% of worlds, versus 3.5% for UDU.

So the surviving signal is:

> Counterfactual consequence can be useful for refusing structurally impressive
> but economically poor verification actions.

That is a resource-allocation result, not yet an epistemic-superiority result.

## What failed

Three precommitted requirements failed:

1. CRV did not match UDU's weighted epistemic gain.
2. CRV narrowly failed the unweighted epistemic non-inferiority margin.
3. CRV's absolute per-world net-harm rate was far above the 10% safety target.

The third failure is the most important. A positive average hides a controller
that is wrong often enough, and by enough, that it would be irresponsible to
promote as a general acquisition policy.

## Mechanistic interpretation

Generator C attacks point estimates at two levels simultaneously:

- the current belief can be overconfident because source reliability, lineage and
  supersession metadata are wrong;
- the proposed verifier can be overconfident because reported tool accuracy is
  wrong.

CRV currently treats both point estimates as though they were the right numbers.
That makes its expected-value calculation brittle. The result therefore points to
a more specific next question than "make CRV smarter":

> Can the controller remain useful when the reliability of its beliefs and tools
> is itself uncertain?

This suggests **risk-sensitive / robust Value of Information**, not another
multiplicative heuristic.

A principled candidate should represent a range or posterior over tool quality
and, eventually, over source/lineage trust, then buy information only when the
action remains worthwhile under a conservative part of that uncertainty. A
simple lower-confidence-bound policy is the baseline to beat; a fancier Bayesian
or distributionally robust planner does not earn complexity unless it beats that.

## Do not over-credit persistence

Nothing here establishes that persistent storage is the causal mechanism. A
metadata-matched system that reconstructs the same structured belief state on
demand should produce the same decisions absent context or computation limits.
Persistence is therefore an engineering advantage until a later experiment gives
it a resource-constrained causal role.

## Next gate

Before designing Generator D or tuning a safer controller on C, first reproduce
this result with the **exact committed** Generator-C runner. If it does not match,
stop and debug provenance rather than interpreting the provisional numbers.

If it reproduces, C becomes development data. Any conservative thresholds,
reliability discounts, posterior models or sequential-verification ideas explored
on C are post-hoc and must be confirmed on a fresh Generator D.

The next design should test a risk-sensitive controller against at least:

- CRV-net v1 frozen here;
- UDU-net;
- uncertainty-own-net, because its tiny positive mean and lower harm rate make it
  an important simplicity/safety baseline;
- a fixed conservative-margin CRV baseline;
- only then any richer reliability-uncertainty model.

A useful innovation target is **sequential robust information acquisition**:
permit a cheap weak observation, then decide whether to stop, corroborate with an
independent channel, or escalate to a stronger expensive tool. The controller
must learn that sometimes the best next action is not another fact lookup but a
check on the reliability of the channel producing facts.

That idea is development direction only. It is not licensed by Generator C.
