# R1′/R2′ prospective scoring — observation 2, and a correction to observation 2's first scoring

**Correction, made 2026-09-03.** The independent review
(`docs/EXP004_STAGE0AM_INDEPENDENT_REVIEW_2026-09-02.md` §0) and the decision log
recorded the Stage 0A-M grader defect as **"R1′ supported again, n=2"**. Checked
against the frozen prospective table, that scoring is not licensed. It is
corrected here. **The empirical finding is untouched:** the grader mis-scored 30
of 130 production trials in two independent ways, and every check read the rule
while none read a realized answer. What changes is the *theory scoring*, not the
observation.

## What the frozen table actually says about the grader

`prospective_component_table.yaml` was frozen at `37ac525`, before the review.
Its `grader` row:

| field | frozen value |
|---|---|
| `treatment_asymmetric` | `no` |
| `invariance_check_exists` | `true` |
| `check_executed` | `true` |
| `churn_commits` | 2 (medium) |
| `r1_prime_predicted_risk` | **`low (checked)`** |
| `r2_prime_binding` | `bound (fingerprint) + golden corpus` |

R1′ as frozen reads: *defects concentrate in components that are
treatment-asymmetric (or of unknown symmetry) **AND** lack an executed invariance
check.* The grader is symmetric and checked. It is not an R1′-high cell; the
table assigned it **low** R1′ risk in advance.

The three pre-declared `r1_high_churn_low` discriminating cells are
`configured_effort`, `live_agent_registry` and `served_model_per_trial` — all
`invariance_check_exists: false`. The grader is not among them, and the
`SUPPORT_R1_PRIME` clause ("…or in any other **unchecked** component") does not
reach it either.

## Correct classification of this observation

Under the frozen `what_future_observations_mean` map:

- **not `SUPPORT_R1_PRIME`** — the grader was checked;
- **not `SUPPORT_CHURN`** — churn 2 is medium, and the grader is not in the
  `manifest / specification / analysis_null / packet_retrieval` high-churn list;
- **`HURT_BOTH`** — "next load-bearing defect found in a low-churn, checked,
  symmetric component (e.g. schedule, keys) — neither theory predicts it".

**Verdict: HURT_BOTH. A load-bearing defect landed in a cell that neither R1′ nor
the churn rival predicted.** This is a *disconfirming* observation for R1′ as
frozen, not a confirming one.

## The prospective ledger, corrected

| # | observation | cell | R1′ | churn |
|---|---|---|---|---|
| 1 | `stage0am-solver-closed` tool list did not survive runtime resolution (2026-09-02) | `live_agent_registry` — pre-declared R1′-HIGH, churn-low | **supports** | contradicts |
| 2 | frozen grader mis-scored 30/130 (2026-09-02, found by independent review) | `grader` — pre-declared R1′-LOW, checked, symmetric | **disconfirms** | contradicts |

**Prospective confirmations of R1′: 1, not 2.** The earlier "n=2" double-counted:
it treated an observation in an R1′-low cell as though it were an observation in
an R1′-high one, on the strength of a shared narrative ("every check read the
rule, none read a realized output") that R1′ does not actually assert.

## What is NOT done here

The old hypothesis is not rewritten so that it wins. R1′ stays exactly as frozen:
*asymmetric-or-unknown **AND** unchecked*. Widening "unchecked" after the fact to
mean "not checked against the right thing" would make R1′ unfalsifiable — it
would then cover every defect ever found, since a defect that was checked for
would not exist. That move is refused.

## The successor hypothesis the observation motivates

The grader defect is not noise, and it is not explained by either frozen theory.
It motivates a **new, separately falsifiable** claim, recorded here as a
candidate and **not** scored by this observation (which constructed it):

> **R3′ — realized-output correspondence.** A check binds a component only to the
> representation it actually reads. A component checked exclusively against
> author-derived cases stays unbound to *realized runtime output*, and defects
> concentrate there regardless of how many checks exist or how symmetric the
> component is.

Its evidential fit, and its cost: the grader had a fingerprint (binding the rule
to itself), a 51-case golden corpus (binding the rule to cases the rule's own
author derived), and a spec↔code test — three checks, none of which had ever seen
a sentence a model actually produced. R1′ cannot express that distinction,
because its `invariance_check_exists` field is a boolean about *existence*, not
about *what the check reads*.

R3′ is a **successor**, not a repair: it makes a prediction R1′ does not, namely
that `check_executed: true` components with author-derived-only corpora carry
defect risk comparable to unchecked ones. That is testable and could be wrong.

**R3′ is prospectively scored only from its own frozen table forward.** A
`r3_prime_binding` column — `author_derived_only` vs `realized_output_bound` —
must be added to a new frozen table before the next independent audit, and the
grader observation may not be counted for it. Until that table is frozen, R3′ has
**zero** prospective evidence.

## Consequence already carried into Stage 0B

`tests/fixtures/stage0b_runtime/` is a real, sanitized runtime transcript, and
the Stage 0B parser tests run against it rather than against invented examples.
That is R3′ acted on before it is confirmed — cheap, and it already paid: the
design's "the searcher returns the block verbatim" was false in three ways, and
no author-derived corpus would have shown it.
