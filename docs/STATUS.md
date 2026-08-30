# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M is FREEZE-READY. All pre-treatment work is complete; what remains is execution-time only.**

State:
- 25 date-anchored / 25 definition-anchored / 15 arithmetic controls = 65 items, 130 production dispatches;
- 50/50 primary keys source-verified; 65/65 production-eligible;
- 1324 tests pass;
- **production dispatches 0; treatment exposure NONE**;
- battery fingerprint `1ec90754f1de2696` (unchanged by this turn — no stem or key changed);
- grader fingerprint `10adaf1dac94ea70`, now recorded separately in the manifest.

Fingerprint lineage: `a53d4d59856fc1db` authoring → `afc208e1e8d1bd00` source verification → `1ec90754f1de2696` post-verification audit.

## Retrieval environment — now MEASURED on the solver's own path

The frozen probe (design committed at `46ebdd9` **before** any observation) was re-run in the missing arm and completed.

| tool | result, BOTH arms | |
|---|---|---|
| `WebFetch` | 5/5 `REFUSED_BY_PROXY`, including `example.com` | block is total, not per-domain |
| `WebSearch` | 2/2 `OK`, substantive extracted page text | search is the only external channel |

The solver-web subagent matched the orchestrator on **all seven targets**, so the two share one egress path and the transfer is licensed by measurement, not by architectural expectation.

**`E` = search-capable, fetch-blocked.** Stage 0A-M therefore studies *retrieval-enabled under a search-capable, fetch-blocked environment* — materially **weaker** than unrestricted browsing, and every claim is scoped to that (specification §6.3). The probe was never a gate: `E` came back degraded and the experiment proceeds, scoped rather than cancelled.

## Both independently-reported inconsistencies are resolved

**1. Failure semantics (§6.3 vs §7).** Resolved in favour of §6, on grounds rather than by tie-break: voiding on retrieval-tool failure is post-treatment selection on a variable only the treatment arm can exhibit, since the closed arm has no tools and can never register one. §7 now separates **case A — retrieval-tool outcome** (retained, graded, logged, never excludes) from **case B — dispatch-level failure** (no gradeable answer exists; pair voided, since a half-missing pair cannot enter a paired test at all). The discriminating question is *did the dispatch yield a gradeable final answer?* — not which tool failed. The 10% ceiling now scopes to case B only, and the void rate is reported broken down by which arm failed. The taxonomy is executable (`lab/stage0am.py`) and pinned by 21 tests.

**2. Primary estimand (§4 vs §1).** §4's `Estimand: the class-average effect` is gone. The inferential target is violation of the **pointwise** null; the class-average difference is a descriptive summary carrying no inferential claim; H0_mean is not tested. The power table is relabelled a design sensitivity — a class-level generative parameter used for sizing does not become a quantity the test licenses a claim about.

## A third defect, found by this audit, in the dangerous direction

Probing the repaired b11 surfaced a systemic grading fault. On the numeric route, a reject overrode a correct answer, so every one of these graded **incorrect**:

- `"193 member states, excluding the 2 permanent observers"` (b15)
- `"13 individual golds, out of 23 total"` (b08)
- `"381 m to the architectural top; 443 m with the antenna"` (b17)
- `"8 planets; there were 9 before 2006"` (b05)
- `"20 of the 27 EU member states"` (b09)

Each answers correctly and names the contrast to show the distinction was understood — the behaviour the anchored-stem design exists to elicit. **A solver that has just retrieved a source is likelier to state both figures**, so the false negatives concentrate in the retrieval-enabled arm and manufacture n10: a **false harm signal, pointing the way the hypothesis predicts.**

Fixed before any outcome was observed. Rejects no longer override a correct numeric answer — which costs nothing, because the separation invariant already puts every reject outside its accept band, so a bare displacing answer still fails on the accept test alone. Reject-precedence is retained on the entity route, where naming the displacing entity genuinely is a non-answer.

Also fixed: spelled-out integers 0–20 are now extracted alongside digits (six items have keys in that range), for the same arm-correlation reason.

## Still prohibited

Until execution authorization:
- no Stage 0A-M production solver/model dispatches;
- no production-item search/retrieval scout;
- no outcome-based item replacement/reclassification;
- no runtime re-keying;
- no Stage 0A-N or Stage 0B execution.

The reflexive/error-correction research added 2026-08-30 remains research context only and did not alter Stage 0A-M.

See `docs/NEXT.md` for the execution-time checklist.
