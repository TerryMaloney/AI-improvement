# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M has cleared the post-verification battery audit at `da5f9b2`, with one diagnostic measurement still missing and two cross-section specification inconsistencies identified by independent review before final freeze.**

Reported state at `da5f9b2`:
- 25 date-anchored primary items;
- 25 definition-anchored primary items;
- 15 arithmetic negative controls;
- 65 total items / 130 eventual production dispatches;
- 50/50 primary keys source-verified;
- 65/65 production-eligible;
- 1293 tests passed;
- 0 production dispatches;
- final audited battery fingerprint `1ec90754f1de2696`.

Fingerprint lineage:
`a53d4d59856fc1db` authoring -> `afc208e1e8d1bd00` source verification -> `1ec90754f1de2696` post-verification audit.

## Post-verification repairs completed

- b11 Lake Michigan area item was replaced rather than tolerance-patched because the named NOAA source itself gave mutually inconsistent metric/imperial conversions. Replacement preserves the lake-definition mechanism with an exact 4-vs-5 count.
- b03 Everest tolerance was tightened from ±0.5 m to ±0.2 m after a generalized accept/reject separation audit exposed insufficient margin from the displacing value.
- A regression rule now requires numeric acceptance regions to remain separated from principal reject values.
- b09 definition-vs-date classification was made explicit in specification §3; b25 and b18 were re-audited cleanly.
- Fingerprints are now reproducibly generated from committed YAML by `lab/stage0am_fingerprint.py`.
- Retrieval packet now names both WebSearch and WebFetch, matching the solver-web grant.

## Retrieval environment measurement

Frozen probe design was committed before observation (`46ebdd9`).

Orchestrator arm:
- WebFetch refused 5/5 targets including `example.com` — page fetch is unavailable wholesale in that environment;
- WebSearch succeeded and returned substantive extracted page text.

Solver-web subagent arm:
- **INCONCLUSIVE / NO DATA** because the session rate limit terminated the screen-class subagent before it issued a tool call.
- This must not be inferred from architectural expectation.
- It may be rerun once, unchanged, as a screen-class diagnostic; it consumes zero production budget and must use no production item.

The experiment remains ITT over the retrieval procedure actually delivered. Reachability is treatment/environment provenance, never a post-outcome item filter.

## Two concrete pre-freeze specification inconsistencies found by independent review

### 1. Tool failure vs trial failure semantics

Specification §6.3 says a trial where retrieval is attempted and fails stays in the retrieval-enabled arm under ITT/no reachability conditioning. Specification §7 still defines tool-call error/timeout/egress refusal as a technical failure that voids the item across both arms.

Those rules conflict if, for example, WebFetch is refused but the solver still returns a gradeable final answer.

Required resolution before freeze:
- distinguish **internal retrieval-tool failure with a completed solver answer** from **trial/dispatch failure that produces no gradeable response**;
- the former should be logged as a treatment outcome and remain in ITT unless a stronger preregistered justification says otherwise;
- the latter may require paired voiding under the frozen missingness rule;
- do not condition inclusion on which domains/tools succeeded.

### 2. Primary estimand wording

Specification §4 still says `Estimand: the class-average effect`, while §1 explicitly demotes the class-average effect to descriptive-only and freezes the inferential claim as rejection of the pointwise null / existence of at least one authored item with lower correctness probability under retrieval-enabled.

Required resolution before freeze:
- make §4 consistent with §1;
- do not restore class-average inference without a valid proof/test;
- power parameterizations may remain descriptive design calculations but must not be mislabeled as the licensed inferential estimand.

## Current interpretation

No new statistical redesign is presently indicated. The battery changes themselves look coherent, but final freeze should not occur until the two contradictions above are resolved and the solver-side egress screen is either measured or explicitly frozen as missing with no unsupported transfer claim.

## Still prohibited

Until final freeze/execution authorization:
- no Stage 0A-M production solver/model dispatches;
- no production-item search/retrieval scout;
- no outcome-based item replacement/reclassification;
- no runtime re-keying;
- no Stage 0A-N or Stage 0B execution.

Program-level reflexive/error-correction research added on 2026-08-30 remains research context only and does not alter Stage 0A-M.

See `docs/NEXT.md` for the exact last pre-freeze action.
