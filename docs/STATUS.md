# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M now has a fully source-verified 65-item candidate battery, but final freeze/execution remains blocked on a fresh post-repair audit and retrieval-environment fingerprint.**

Latest battery verification commit: `a262b89`.

Reported non-dispatch suite: **1281 passed, 0 failed**.

Solver/model production dispatches: **0**.

## Candidate battery

- 25 date-anchored / time-indexed primary items;
- 25 definition-anchored / definition-fixed quantity primary items;
- 15 arithmetic / deterministic negative-control items;
- 65 total items;
- 2 arms per item, R=1;
- 130 planned production dispatches only after final freeze/execution authorization.

Current battery fingerprint: `afc208e1e8d1bd00`.

All 50 primary keys are now source-verified and all 65 items are marked production-eligible. No production item has been exposed to the target solver or retrieval treatment.

## Verification changes requiring fresh audit

Source verification legitimately changed the candidate battery:
- b09 retired/replaced: unstable IMF nominal-GDP item -> euro-area membership-scope item;
- b25 retired/replaced: unstable IMF nominal-GDP item -> contiguous-Pacific-state-count item;
- b11 Lake Michigan key corrected from 58,030 to NOAA 57,573 km²;
- b18 principal reject refined to 8,851.8 km;
- pass-1 provenance records were repaired with UTC timestamps and verifier-pass metadata.

Because those changes moved the battery fingerprint, the authoring/verifying agent did not self-certify the same-turn repaired battery.

## Fresh audit issue already identified

**b11 remains potentially non-objective under its current stem.** The stem asks for Lake Michigan's surface area without fixing a source/convention, while verification found several defensible published values. The current ±1,500 km² tolerance absorbs source disagreement, but Stage 0A-M's definition-anchored rule prefers ambiguity to be eliminated in the stem rather than tolerated after the fact. Final audit must either source-anchor/reformulate b11 or explicitly prove that the acceptance-region formulation still satisfies the frozen class definition.

## Retrieval-environment issue

During key verification, direct fetches to at least `en.wikipedia.org` and `www.bls.gov` were refused by the network egress proxy while web search worked.

This does not invalidate the authored battery, but the production treatment must be fingerprinted as the **actual retrieval-enabled procedure available in the execution environment**, not an abstract idealized retrieval system.

Before execution the preflight must record, using the same production tool path where possible:
- search reachability;
- fetch/source-access reachability;
- fixed representative domains;
- tool identities/policies;
- model/runtime snapshot;
- environment state.

A positive result must be scoped to that reachable retrieval surface. Do not silently repair or change the retrieval environment after seeing production outcomes.

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

Until the post-repair audit and execution preflight pass:
- no Stage 0A-M production solver/model dispatches;
- no treatment search-result inspection on production items;
- no search-arm dry run on production items;
- no outcome-based item replacement/reclassification;
- no runtime re-keying;
- no Stage 0A-N or Stage 0B execution.

## Next step

Perform a bounded post-verification battery audit focused on the repaired/replaced items, b11 objectivity, artifact/fingerprint consistency, and the actual retrieval-tool reachability surface. If clean after any pre-treatment corrections, produce the final freeze/execution candidate and stop before production dispatch unless explicitly authorized.

See `docs/NEXT.md` for the exact authorized action.
