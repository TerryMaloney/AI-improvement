# Stage 0A-M preflight — to be completed immediately before the first dispatch

**Status: NOT COMPLETE. The battery is a CANDIDATE. No dispatch is authorised.**

| # | Check | State |
|---|---|---|
| 1 | Branch and commit SHA recorded | pending at execution time |
| 2 | Item manifest generated, counts read from it | **done** — `experiments/exp004_stage0am/manifest.json` |
| 3 | Class assignments frozen, one class per item | **done**, tested |
| 4 | Key fingerprints recorded | **done**, per item in the manifest |
| 5 | Key provenance stored separately from trials | **done** — `docs/EXP004_STAGE0A_M_KEY_PROVENANCE.md` |
| 6 | **Independent key verification for all primary items** | **INCOMPLETE — 18 of 50 verified** |
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

## Blocking item

**Check 6.** 32 of 50 primary keys carry `PENDING_INDEPENDENT_VERIFICATION` and are
marked `production_eligible: false` in the manifest. They were authored from
careful recollection with the intended source named, but not confirmed against it
in-session. Freezing a key that has not been checked is exactly the failure this
lab exists to prevent, so they are labelled rather than assumed.

The egress probe (check 12) is left pending rather than improvised, per the
standing rule that a non-production diagnostic call needs its own authorisation.
