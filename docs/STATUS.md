# Current Research Status

> Coordination document only. This file is not a preregistration and must not override experiment-specific frozen artifacts.

## Current phase

**Stage 0 is now split into successive mechanism-discovery, confirmation, naturalistic-validation, and controller phases.**

The previous prevalence-pilot architecture is retired.

## Current Stage-0 decomposition

### Stage 0A-M — Objective mechanism assay
Question: on preregistered, treatment-blind anchored task classes, can retrieval reduce objectively correct answers relative to closed-book?

Current candidate primary classes:
- date-anchored / time-indexed;
- definition-anchored / definition-fixed quantity;
- arithmetic / deterministic.

Primary measurement:
- ordinary answer format;
- frozen deterministic keys;
- no LLM judge;
- no task-directing output schema.

Interpretation is deliberately narrow: this is an authored stress-sample mechanism assay, not naturalistic prevalence, controller value, or within-class sign heterogeneity.

### Stage 0A-N — Naturalistic manifestation
Free-form answers on separate fresh items, with blinded pairwise judging only as a separate exploratory/naturalistic instrument.

False-premise is removed from the objective Stage 0A-M primary because forcing an explicit premise-status/decision field would itself cue premise inspection and alter the hypothesized mechanism.

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

### Stage 0E — Richer action space
Only after binary conditional retrieval earns value.

## Established / measured so far

- The pooled R=1 discordant-pair design is an ATE test, not a sign-heterogeneity/controller test; it is retired as the primary controller route.
- The class-stratified R=1 design is mathematically valid for detecting negative class-level mean effects under heterogeneous items when class membership is frozen before outcomes.
- The stratified test is blind to within-class sign heterogeneity; this is appropriate for a controller that only sees class labels, but disqualifies it as a general-headroom test.
- Hand-authored classes can establish a stress-sample mechanism and a trivial class rule; they do **not** establish that a general router can discover/generalize the signal.
- A discovery→fresh-confirmation design is cleaner and cheaper than prevalence-pilot→production.
- The strongest current alternative explanation for apparent retrieval harm is **query-generation failure**; confirmation should explicitly test this with a fixed-query arm.
- Naturalistic prevalence remains completely unmeasured.
- 27 earlier screen-class diagnostic calls are discarded/non-reusable due to incomplete persisted provenance.
- Frozen grading data showed that harm-plausible free-text classes were anti-correlated with deterministic gradability.
- Forcing explicit premise-status or forced-choice fields is itself a cognitive intervention and cannot be treated as a neutral grading device.
- Anchoring the target in the **question stem** can remove ambiguity without adding a new output-side reasoning scaffold.
- Date-anchored and definition-anchored formulations therefore provide the current cleanest objective mechanism assay.
- The old contested-quantity class is not retained as such; it is reformulated into a definition-fixed class with an objective target.
- False-premise remains scientifically important but moves to naturalistic/execution-grounded work rather than the objective Stage 0A-M primary.
- Explicit epistemic structure as a protective intervention is now a separate future hypothesis and must not be smuggled into exp004 as measurement calibration.

## Current candidate Stage 0A-M burden

Illustrative candidate:
- 3 classes × 20 items × 2 arms = 60 items / 120 solver dispatches.

This is not yet frozen. A final specification/red-team must verify that the anchored classes are operational, treatment-blind, and sufficiently powerable before production.

## Current blockers before Stage 0A-M

1. Formalize exact date-anchored, definition-anchored, and arithmetic class definitions.
2. Verify one-class-per-item assignment and objective key construction.
3. Recompute fixed-n power for 15/20/25 items per retained class under the new 3-class multiplicity structure.
4. Define treatment-blind authoring rules that do not use prior search results.
5. Freeze the ordinary closed/search arm wrappers and exact query logging.
6. Predefine the Stage 0B fixed-query challenge.
7. Define a separate Stage 0A-N naturalistic pairwise-judging protocol, but do not mix it into the objective primary.
8. Re-probe egress / tool environment.
9. Replace the stale knowledge-probe infrastructure assertion only if separately authorized; frozen evidence must remain untouched.
10. Freeze Stage 0A-M in a distinct preregistration commit before any production dispatch.

## Retired recommendations

Do not revive without a new derivation:
- oracle-gap primary test;
- repeated-trial A_minus fixed-LFC design;
- n=18/R=10/critical=0.1444;
- prevalence pilot as the next stage;
- pooled R=1 McNemar as a controller test;
- observed reversal prevalence as an inclusion criterion;
- treatment-side scouting;
- runtime judge escalation;
- treating structured output fields as neutral measurement;
- contested-quantity as an ambiguity-defined confirmatory class.

## Explicitly not authorized

- No Stage 0A-M production dispatches until its specification is frozen.
- No false-premise structured-output primary in exp004.
- No controller claim from a class-level discovery result.
- No naturalistic prevalence claim from an enriched stress battery.
- No Stage-1/recursive procedure work yet.

## Broader direction

See `docs/RESEARCH_MAP.md`, `docs/EXPERIMENTAL_PROGRAM_2026-08-29.md`, and `docs/EPISTEMIC_SYSTEMS_PRIOR_ART_MAP_2026-08-29.md`.
