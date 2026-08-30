# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M candidate production battery is authored and prefreeze-tested, but execution remains blocked on independent source verification of 32 primary keys.**

Latest battery commit: `4c7725f`.

Reported non-dispatch suite: **1279 passed, 0 failed**.

Solver/model dispatches: **0**.

## Candidate battery

- 25 date-anchored / time-indexed primary items;
- 25 definition-anchored / definition-fixed quantity primary items;
- 15 arithmetic / deterministic negative-control items;
- 65 total items;
- 2 arms per item, R=1;
- 130 planned production dispatches only after final freeze/execution authorization.

Battery fingerprint: `a53d4d59856fc1db`.

The production schedule, arm-order randomization, fresh-context rule, quarantined answers, provenance records, packet templates, preflight checklist, and report skeleton have been authored. No production item has been exposed to the target solver or retrieval treatment.

## Current blocker — key verification only

Of the 50 primary keys:
- **18 are source-verified** in the authoring session;
- **32 remain `PENDING_INDEPENDENT_VERIFICATION` and `production_eligible: false`.**

The 15 arithmetic-control keys are deterministic and were recomputed in-session.

A remembered or model-supplied answer is not sufficient evidence. Every pending primary key must be checked directly against authoritative public source material before eligibility can be flipped.

This is a bounded pre-treatment remediation, not a redesign.

## What may change during verification

Before any production exposure, a pending item may be corrected or replaced if direct source inspection shows that:
- the remembered key is wrong;
- the requested date/definition/scope is not uniquely supported;
- the named source does not support the claimed answer;
- the accepted-answer normalization is incomplete or incorrect;
- the proposed displacing/alternative state is not actually distinct in the intended way.

Every such change must be documented as an authoring-stage correction and re-tested.

No item may be changed because of observed or predicted target-solver behavior.

## Stage 0A-M design still in force

Primary classes:
- date-anchored / time-indexed;
- definition-anchored / definition-fixed quantity.

Negative control:
- arithmetic / deterministic, outside the Holm family.

Treatment:
- **retrieval-enabled** intent-to-treat procedure versus closed-book;
- never condition analysis on observed tool use.

Primary inference:
- exact one-sided conditional-binomial / McNemar-style test within each primary class;
- Holm across K=2;
- finite authored-item existence claim only.

Frozen primary wording:
> Among the preregistered authored items in this class, at least one item has a lower probability of an objectively correct answer under the retrieval-enabled procedure than under closed-book.

The class-average effect is descriptive only.

## Dependence protections

- randomized item order from recorded seed;
- classes interleaved;
- independently randomized arm order within item;
- paired arms adjacent/close in time;
- fresh context per trial;
- no prior output enters later prompts;
- runtime/timing metadata recorded;
- dependence diagnostics reported only, never used as exclusion gates.

## Still prohibited

Until all 50 primary keys are independently verified and a final freeze/execution review passes:
- no Stage 0A-M solver/model dispatches;
- no treatment search-result inspection;
- no search-arm dry run on production items;
- no target-model answer used for key verification;
- no outcome-based item replacement/reclassification;
- no run directory creation;
- no Stage 0A-N or Stage 0B execution.

## Next step

Verify the 32 pending primary keys directly against the named or better authoritative sources, update provenance and production eligibility, rerun the full non-dispatch suite, then conduct one final freeze/execution review.

See `docs/NEXT.md` for the exact authorized remediation.
