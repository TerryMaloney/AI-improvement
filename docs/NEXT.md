# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Current state

Post-verification audit commit: `da5f9b2`.

Reported state:
- 65 items = 25 date-anchored + 25 definition-anchored + 15 arithmetic control;
- 50/50 primary keys source-verified;
- 65/65 production-eligible;
- 1293 tests passed;
- 0 production dispatches;
- battery fingerprint `1ec90754f1de2696`;
- no production treatment exposure.

The battery audit repaired b11 and b03, confirmed b09/b25/b18, added reproducible fingerprint generation, and preregistered/measured an egress probe.

One screen-class egress arm remains unmeasured because the solver-web subagent hit a session rate limit before issuing any probe call. Orchestrator WebSearch worked; orchestrator WebFetch was refused on all 5 frozen targets including example.com.

Independent review found two cross-section spec inconsistencies that must be resolved before final freeze.

## Next authorized action — final pre-freeze repair + solver-side egress measurement

**No production Stage 0A-M dispatches.**

### 1. Re-run the already-frozen solver-web egress probe exactly once

Use:
- `experiments/exp004_stage0am/egress_probe.frozen.json`
- the existing `solver-web` agent;
- dispatch class `screen`;
- no production item/stem/key;
- the exact frozen target/query set;
- no additions, deletions, substitutions, or retries chosen from outcomes.

Record the solver-web results in `egress_probe.results.json`.

If the screen call again fails before any tool observation, record that honestly and continue the specification audit without inferring the solver surface from the orchestrator.

### 2. Resolve §6.3 vs §7 failure-semantics contradiction

Current conflict:
- §6.3 says a retrieval attempt that fails remains in the retrieval-enabled arm under ITT / no reachability conditioning;
- §7 says tool-call error, timeout, empty transport response, or egress refusal is a technical failure that voids the item across both arms.

Freeze an operational distinction before production outcomes.

Preferred conceptual separation to audit:

**Tool-level retrieval failure with a completed gradeable solver response**
- e.g. WebFetch REFUSED_BY_PROXY, search timeout, useless/failed retrieval attempt, but solver still returns an answer;
- treatment mechanism/outcome;
- remains in retrieval-enabled ITT arm;
- log tool failure and grade the final answer;
- never reachability-condition inclusion.

**Trial/dispatch-level technical failure**
- e.g. API/agent failure, timeout or transport failure prevents any gradeable final answer from being produced;
- paired missingness rule may void the item across arms;
- count/report separately.

Decide exact vocabulary and thresholds, patch spec/code/tests/report skeleton consistently, and test the boundary cases.

Do not use the egress-probe outcome to invent a favorable rule after the fact; the rule must be coherent under either reachable or blocked retrieval.

### 3. Resolve §4 primary-estimand wording

Current §4 says:
`Estimand: the class-average effect.`

But §1 freezes:
- formal validity against `H0_pointwise`;
- licensed rejection claim = among the finite frozen authored items, at least one has lower correctness probability under retrieval-enabled;
- class-average effect = descriptive only, no formal inference.

Make §4 consistent with §1.

Do not restore inferential class-average language unless a valid proof/test is supplied. Power simulations may continue to use class-level generative parameters as design sensitivities but must not be described as the licensed estimand.

### 4. Re-audit the repaired battery only for concrete regressions

Check:
- b11 replacement exact 4 vs 5 endpoint;
- b03 ±0.2 tolerance and generalized accept/reject separation invariant;
- b09 classification rule;
- b25 scope item;
- b18 reject refinement;
- key/provenance/manifest/fingerprint consistency;
- no answer leakage;
- schedule unchanged and valid;
- packet diff still restricted to retrieval tool permission;
- no production exposure.

Do not reopen unrelated statistical design questions absent a concrete contradiction/counterexample.

### 5. Final preflight inventory

Determine exactly what remains execution-time only after this turn, including as applicable:
- final freeze commit SHA/fingerprint;
- model snapshot/version;
- environment fingerprint;
- telemetry dry-run;
- fresh-context dry-run;
- run-directory initialization;
- any runtime-only credential/tool checks.

If these can be prepared without exposing a production item, do so. Do not create a production run or execute production trials.

### 6. Update canonical coordination docs

Update `docs/STATUS.md`, `docs/NEXT.md`, and `docs/DECISION_LOG.md` with the final state.

If all pre-treatment artifacts are internally consistent, create/commit/push a **final freeze-ready candidate** and stop before production execution.

## Gate

Return exactly one:

A. FINAL PREFREEZE AUDIT CLEAN — BATTERY/SPEC READY TO FREEZE; EXECUTION-TIME PREFLIGHT ONLY REMAINS

B. CLEAN AFTER NON-DISPATCH REPAIRS — BATTERY/SPEC READY TO FREEZE; EXECUTION-TIME PREFLIGHT ONLY REMAINS

C. SOLVER RETRIEVAL SURFACE STILL UNMEASURED, BUT BATTERY/SPEC CLEAN — FREEZE POSSIBLE WITH EXPLICIT MISSING ENVIRONMENT MEASUREMENT

D. SPECIFICATION STILL INTERNALLY INCONSISTENT

E. NEW LOAD-BEARING DESIGN FLAW FOUND

Regardless of gate:
- **PRODUCTION DISPATCHES: 0**
- report diagnostic/screen calls separately.

Return:

COMMIT:
TESTS:
PRODUCTION DISPATCHES: 0
DIAGNOSTIC/SCREEN CALLS:

RESULT:
SOLVER-WEB EGRESS:
FAILURE-SEMANTICS RESOLUTION:
PRIMARY-ESTIMAND RESOLUTION:
CHANGED-ITEM REAUDIT:
BATTERY FINGERPRINT:
FINGERPRINT LINEAGE:
PACKET/TOOL SURFACE:
KEY/MANIFEST CONSISTENCY:
TREATMENT-EXPOSURE AUDIT:
PREFLIGHT REMAINING:
CHANGED:
OPEN:
DO NOT:

If a future execution step requires Terry to manually install, authorize, connect, provide credentials, or physically configure anything, begin the response with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
