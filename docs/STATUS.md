# Current Research Status

> Coordination document only. This file is not a preregistration and must not override experiment-specific frozen artifacts.

## Current phase

**Stage 0 is now split into successive mechanism-discovery, confirmation, naturalistic-validation, and controller phases.**

The previous prevalence-pilot architecture is retired.

## Current Stage-0 decomposition

### Stage 0A — Mechanism discovery
Question: does retrieval have a negative mean effect in at least one preregistered, treatment-blind task class?

Candidate design:
- 4 treatment-blind surface classes;
- fixed-n discovery sample;
- R=1 per arm;
- exact one-sided conditional-binomial/McNemar-style test within class;
- Holm correction across classes;
- deterministic grading primary;
- stress-sample interpretation only.

This is **mechanism discovery**, not general controller evidence.

### Stage 0B — Independent confirmation
Freeze one discovered class/hypothesis, then test it on entirely fresh items authored without outcome visibility.

Important follow-up arm:
- search with fixed/high-quality query construction

Purpose: distinguish retrieval harm from naive query-generation harm.

### Stage 0C — Naturalistic validation
Use an unenriched task source to estimate how often the confirmed condition appears and whether it matters outside the authored stress sample.

### Stage 0D — Controller test
On held-out mixed tasks, compare fixed policies with a router using only pre-treatment observables.

Only this stage can begin to support a general controller claim.

## Established / measured so far

- The pooled R=1 discordant-pair design is an ATE test, not a sign-heterogeneity/controller test; it is retired as the primary controller route.
- The class-stratified R=1 design is mathematically valid for detecting negative class-level mean effects under heterogeneous items when class membership is frozen before outcomes.
- The stratified test is blind to within-class sign heterogeneity; this is appropriate for a controller that only sees class labels, but disqualifies it as a general-headroom test.
- Hand-authored classes can establish a stress-sample mechanism and a trivial class rule; they do **not** establish that a general router can discover/generalize the signal.
- A discovery→fresh-confirmation design is cleaner and cheaper than prevalence-pilot→production.
- The strongest current alternative explanation for apparent retrieval harm is **query-generation failure**; confirmation should explicitly test this with a fixed-query arm.
- Surface classes should be used for preregistered stratification; hypothesized mechanism dimensions may be recorded as frozen covariates but are not yet operationally validated.
- Naturalistic prevalence remains completely unmeasured.
- 27 earlier screen-class diagnostic calls are discarded/non-reusable due to incomplete persisted provenance.

## Current candidate discovery burden

Illustrative candidate:
- 4 classes × 20 items × 2 arms = 160 solver dispatches.
- Approximate power from the red-team:
  - pure class harm delta≈0.55: 0.87
  - pure class harm delta≈0.40: 0.54
  - 67% reversal-pure at delta≈0.55: 0.43

These numbers are orientation only until the discovery specification is independently frozen.

## Current blockers before Stage 0A

1. Independently specify the four treatment-blind classes and one-class-per-item assignment rule.
2. Freeze item-authoring rules before outcomes.
3. Decide discovery n/class after a final power/cost check.
4. Freeze exact grading/key rules and clean arms.
5. Define query logging and confirmation fixed-query intervention now, before discovery outcomes.
6. Define the report skeleton and stress-sample claim language.
7. Re-probe egress / tool environment.
8. Resolve the pre-existing stale test assertion without altering frozen historical evidence.
9. Freeze Stage 0A in a distinct preregistration commit before any production dispatch.

## Retired recommendations

Do not revive without a new derivation:
- oracle-gap primary test;
- repeated-trial A_minus fixed-LFC design;
- n=18/R=10/critical=0.1444;
- prevalence pilot as the next stage;
- pooled R=1 McNemar as a controller test;
- observed reversal prevalence as an inclusion criterion;
- treatment-side scouting.

## Explicitly not authorized

- No Stage 0A production dispatches until its discovery specification is frozen.
- No confirmation-item authoring with discovery outcomes visible unless the authoring process prevents outcome leakage.
- No controller claim from a class-level discovery result.
- No naturalistic prevalence claim from an enriched stress battery.
- No Stage-1/recursive procedure work yet.

## Broader direction

See `docs/RESEARCH_MAP.md` and `docs/EXPERIMENTAL_PROGRAM_2026-08-29.md`.


## Latest Stage 0A specification red-team — grading blocker

[MEASURED] Three of the four proposed harm-plausible Stage 0A classes escalated 100% of their frozen examples to an LLM judge. Only deterministic/arithmetic graded cleanly.

This exposes a structural conflict:
- the classes most likely to show retrieval harm require nuanced epistemic judgment;
- the classes easiest to grade deterministically are the least harm-plausible.

Therefore Stage 0A is **not ready to freeze**. The blocker is now grading architecture, not statistics or taxonomy.

Contested-quantity/definition should not remain a primary class in its current form because its defining property is answer ambiguity, which conflicts with the requirement for an unambiguous frozen key.

Three remediation directions remain open:
1. pre-author deterministic acceptance criteria and validate coverage before dispatch;
2. admit judged items to the primary under a pre-registered bias audit / measurement model;
3. restrict to deterministic classes, accepting reduced scientific relevance.

Do not author Stage 0A items until one grading path is selected and independently scrutinized.
