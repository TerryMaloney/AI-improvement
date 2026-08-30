# Stage 0A-M preflight — to be completed immediately before the first dispatch

**Status: NOT COMPLETE. The battery is a CANDIDATE. No dispatch is authorised.**

| # | Check | State |
|---|---|---|
| 1 | Branch and commit SHA recorded | pending at execution time |
| 2 | Item manifest generated, counts read from it | **done** — `experiments/exp004_stage0am/manifest.json` |
| 3 | Class assignments frozen, one class per item | **done**, tested |
| 4 | Key fingerprints recorded | **done**, per item in the manifest |
| 5 | Key provenance stored separately from trials | **done** — `docs/EXP004_STAGE0A_M_KEY_PROVENANCE.md` |
| 6 | **Independent key verification for all primary items** | **done — 50 of 50 source-verified** |
| 7 | Grading route declared per item, no runtime escalation | **done**, tested |
| 8 | Arm packet hashes and diff | **done** — `arm_packet_diff.json`, 3 differing lines |
| 9 | Closed arm free of phantom search-budget text | **done**, tested |
| 10 | Model and version pinned | pending at execution time |
| 11 | Retrieval environment recorded | pending at execution time |
| 12 | Egress probe run, reachable states recorded | **pending — requires separate authorisation** |
| 13 | Telemetry active, verified on a dry run | pending at execution time |
| 14 | Item-order seed and per-item arm-order seed recorded | **done** — 20260830 / 8302026 |
| 15 | Fresh-context-per-trial verified | pending at execution time |
| 16 | `dispatch_class` enforcement | **done** — schedule declares `solver_experiment` |
| 17 | Run directory created at dispatch time | **must not exist yet**, tested |
| 18 | Report skeleton committed | **done** |
| 19 | Statistical analysis artifact committed and green | **done** — `lab/stage0am.py` |
| 20 | Stop and failure rules committed | **done** — specification §7, §14 |
| 21 | Dispatch budget computed from the manifest | **done** — 130 |

## No blocking item remains

All 50 primary keys are source-verified and all 65 items are
`production_eligible: true`. What remains is execution-time only.

## Remaining execution-time checks

Checks 1, 10, 11, 13, 15 and 17 can only be performed at dispatch: commit SHA,
model snapshot, environment fingerprint, telemetry dry run, fresh-context
verification, and run-directory creation.

**Check 12, the egress probe, stays pending for the final execution review** —
per the standing rule that a non-production diagnostic call needs its own
authorisation.

## Environment finding from key verification — relevant to the retrieval arm

While verifying keys, direct page fetches to `en.wikipedia.org` and `www.bls.gov`
were **refused by the network egress proxy**, while web *search* worked normally.

This matters for the treatment, not just for authoring. If the solver's retrieval
arm can search but cannot fetch several major authoritative domains, then
"retrieval-enabled" in this environment means *degraded* retrieval, and any harm
observed could reflect the retrieval environment rather than retrieval as such.

`[OPEN]` The egress probe must therefore record, per domain, which of search and
fetch actually succeed, and the report's ALTERNATIVE EXPLANATIONS section must
carry the reachable-domain set. This does not block freezing the battery; it
constrains how a positive result may be read.
