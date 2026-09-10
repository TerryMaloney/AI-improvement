# EXP005-EPI red-team — 2026-09-09

Status: **POST-HOC MECHANISM AUDIT.**

This document does not alter the frozen A/B confirmation results. It narrows what
those results license after stronger controls were run on outcomes that were
already visible.

## 1. What remains measured

The original prospective claims remain true under their exact synthetic setup:

- Generator A: frozen debt beat random and uncertainty under the precommitted
  thresholds.
- Generator B: frozen debt again beat random and uncertainty under the
  precommitted thresholds.
- The verifier was oracle-correct and reported reliability 0.995.
- Source reliability, source lineage, proposition identity, dependency structure
  and objective-impact weights were supplied by the benchmark.

An independent local reimplementation reproduced the committed A/B policy means,
including the exact Generator-B values. This is a useful provenance check.

This does **not** establish that the full debt formula is the mechanism, that the
workspace beats a strong matched RAG, or that the result survives real evidence.

## 2. The first mechanism story does not survive intact

The frozen debt score is

`uncertainty × fragility × staleness × load × decision_impact`.

The prospective B test did not require debt to beat the dependency baseline.
On B:

- debt mean gain = 0.1323503
- dependency mean gain = 0.1303998
- paired debt - dependency = +0.0019504
- exploratory normal-approximation 95% interval = [-0.0023184, +0.0062193]

So Generator B provides no useful evidence that the full debt formula beats the
much simpler dependency controller.

That does not invalidate the frozen PASS. It invalidates a stronger story we
might have been tempted to tell about why it passed.

## 3. A simpler post-hoc controller beats debt on both visible sets

After the A/B results were visible, we tested:

`uncertainty × (own objective impact + sum of descendant objective impacts)`.

This is deliberately simple. It removes lineage fragility and staleness and
replaces raw descendant count with the actual downstream utility used by the
synthetic objective.

Mean gain:

| already-visible set | frozen debt | uncertainty × total downstream utility |
|---|---:|---:|
| Generator A | 0.1439061 | 0.1489314 |
| Generator B | 0.1323503 | 0.1536266 |

Paired post-hoc difference of the simpler controller minus debt:

- A: +0.0050253, exploratory 95% interval [+0.0013117, +0.0087389]
- B: +0.0212763, exploratory 95% interval [+0.0178420, +0.0247105]

This is **not confirmation** because the comparator was invented after seeing
A/B. It is a strong falsifier of the claim that the current multiplicative debt
formula is necessary or close to optimal.

## 4. Staleness and lineage fragility have not earned their place

Post-hoc ablations do not show benefit from the two most epistemically
interesting extra factors.

Generator B:

- debt = 0.1323503
- debt without staleness = 0.1331704
- uncertainty × load = 0.1295236
- uncertainty × fragility × load = 0.1252642

Generator A likewise does not show a clear benefit from the fragility term.

This does **not** prove lineage or staleness are useless. The generators may be
poor tests for them. It means we do not get to cite the current positive result
as evidence that those factors help.

## 5. Objective-weight coupling matters

The frozen controller receives `world.impacts`, and the primary loss uses the
same `world.impacts`.

That can be legitimate: a rational agent should know which decisions matter.
But it means the result is partly a utility-aware scheduling result, not a
generic epistemic-intelligence result.

When the same already-visible worlds are rescored with unweighted truth error:

Generator A:
- debt = 0.1354
- uncertainty × load = 0.1455

Generator B:
- debt = 0.13857
- dependency = 0.16803
- load-only = 0.16871
- uncertainty × load = 0.16166

So the full debt score is not robustly superior once the evaluator no longer
shares its impact weights.

## 6. The near-perfect verifier is load-bearing

The original confirmation used a truth oracle whose answer is always correct and
is ingested at reliability 0.995.

Post-hoc Generator-B stress with a fallible binary verifier:

| actual/report reliability | debt mean gain | debt harm rate |
|---|---:|---:|
| 0.995 / 0.995 original idealization | 0.13235 | 0.2% |
| 0.90 / 0.90 | 0.09786 | 4.8% |
| 0.80 / 0.80 | 0.07086 | 8.0% |
| 0.70 / 0.70 | 0.04280 | 14.8% |
| 0.90 actual / 0.995 reported | 0.10805 | 6.4% |

The controller still has positive average value in these post-hoc simulations,
but the original low-harm story does not survive ordinary verifier error.

A real search, database query, model critic or human report is not a truth oracle.
Future controllers need an explicit model of tool reliability and the option not
to purchase low-value verification.

## 7. Bigger oracle assumptions still untouched

The benchmark currently supplies:

1. exact atomic proposition identity;
2. exact source lineage;
3. calibrated source reliability;
4. exact temporal supersession relationships;
5. the dependency graph;
6. objective/decision impact;
7. a verification action that can reveal the hidden base truth.

These are useful isolation controls. They are also most of the hard real-world
epistemology problem.

The next tests must progressively remove these gifts rather than adding an LLM
on top and declaring victory.

## 8. Implementation risks found during review

These are not failures of the frozen synthetic claims, but they block a serious
real-world interpretation:

- direct evidence on a proposition that is also a rule output is currently
  excluded from direct belief aggregation; derivation wins by construction;
- derived beliefs jump to probability 0 or 1 when premises cross the discrete
  decision threshold, so uncertainty is not probabilistically propagated;
- one scalar `reliability` is required to be > 0.5 and is treated as calibrated;
- within one lineage, the highest-reliability active item is selected as the
  representative, which is a policy assumption rather than an inferred fact;
- any evidence record can supersede an existing evidence id; semantic/temporal
  legitimacy of supersession is not yet a typed invariant;
- revision-log count is a recomputation trace, not yet a clean measure of
  semantic belief revisions.

Do not hide these by adding more benchmarks.

## 9. What survived the red team

The defensible surviving hypothesis is narrower and more interesting:

> Explicit structured belief state can expose *where resolving uncertainty could
> change downstream conclusions*, and that signal may let a limited verification
> budget outperform blind or uncertainty-only retrieval.

The result is no longer specifically about the current `epistemic_debt` product.

## 10. New candidate: counterfactual revision value

A more principled next controller should ask a counterfactual question:

> If I learned that proposition P were true versus false, which currently
> decision-relevant beliefs could actually change?

A candidate score is:

`CRV(P) = uncertainty(P) × affected_utility(P) × tool_information_quality / cost`

where `affected_utility(P)` is computed by running the truth-maintenance engine
under two hypothetical verification outcomes and summing the objective weights
of beliefs whose resolved state differs.

This avoids counting descendants that are structurally downstream but currently
blocked by some other premise.

This is **not claimed as a novel Value-of-Information theory**. Value of
Information and active diagnosis are established fields, and Dong et al.,
ACL 2026, apply VoI directly to LLM-agent information acquisition. The possible
contribution here is narrower: an inspectable approximation to VoI over a
persistent revision graph, with provenance, temporal belief revision and
external verification costs.

The existing A/B outcomes may be used to develop CRV. They may never confirm it.

## 11. Next falsifiable gate

Before evaluating CRV:

1. freeze the CRV formula;
2. freeze strong baselines, especially:
   - uncertainty;
   - dependency/load;
   - uncertainty × load;
   - uncertainty × total downstream utility;
   - frozen old debt;
3. build Generator C with blocked dependency paths, heterogeneous verifier
   quality/cost, imperfect source-reliability estimates and imperfect lineage;
4. score both weighted decision loss and unweighted truth loss;
5. include a no-verification action;
6. freeze pass/amber/kill rules;
7. only then inspect outcomes.

Kill/simplify rule:

> If a simpler metadata-matched RAG plus the same controller matches the
> persistent workspace, or if CRV does not beat the simple
> uncertainty × downstream-utility baseline, prefer the simpler mechanism.

## 12. Claim ledger after this audit

**Measured:**
- the frozen debt policy beat its precommitted random/uncertainty comparators on
  A and B under oracle synthetic metadata and verification;
- the workspace and metadata-matched RAG tie on the simple construct final-QA
  benchmark.

**Post-hoc diagnostic:**
- simpler structural/utility policies explain at least as much of the A/B signal;
- current staleness/fragility factors have not earned causal credit;
- imperfect verification sharply raises harm.

**Not measured:**
- real-world source reliability;
- inferred lineage;
- natural-language claim extraction by an LLM;
- noisy web/database tool acquisition;
- real-world accuracy improvement;
- alignment under autonomous procedure modification.
