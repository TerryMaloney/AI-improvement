# Stage 0A-M preflight — to be completed immediately before the first dispatch

**Status: ALL STATIC CHECKS COMPLETE, INCLUDING AGENT SYMMETRY. Runtime canaries are BLOCKED
in the current session (agent registry frozen at session start) and require a fresh session.
No dispatch is authorised by this document.**

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
| 12 | Egress probe run, reachable states recorded | **done — both arms measured**, `egress_probe.results.json` |
| 13 | Telemetry active, verified on a dry run | pending at execution time |
| 14 | Item-order seed and per-item arm-order seed recorded | **done** — 20260830 / 8302026 |
| 15 | Fresh-context-per-trial verified | pending at execution time |
| 16 | `dispatch_class` enforcement | **done** — schedule declares `solver_experiment` |
| 17 | Run directory created at dispatch time | **must not exist yet**, tested |
| 18 | Report skeleton committed | **done** |
| 19 | Statistical analysis artifact committed and green | **done** — `lab/stage0am.py` |
| 20 | Stop and failure rules committed | **done** — §7 rewritten with the A/B taxonomy, executable in `lab/stage0am.py`, tested |
| 21 | Dispatch budget computed from the manifest | **done** — 130 |

## No blocking item remains

All 50 primary keys are source-verified and all 65 items are
`production_eligible: true`. What remains is execution-time only.

## Remaining execution-time checks

Checks 1, 10, 11, 13, 15 and 17 can only be performed at dispatch: commit SHA,
model snapshot, environment fingerprint, telemetry dry run, fresh-context
verification, and run-directory creation.

**Check 12 is now done.** The frozen probe was run in both arms — the
orchestrator and a screen-class `solver-web` subagent — and they agree on all
seven targets. See §"Measured retrieval environment" below.

## Measured retrieval environment — `E`

`[MEASURED]` Both probe arms, 2026-08-30, frozen design committed at `46ebdd9`
**before** any result was observed:

| tool | targets | result |
|---|---|---|
| `WebFetch` | example.com, noaa.gov, bls.gov, en.wikipedia.org, ecb.europa.eu | **5/5 REFUSED_BY_PROXY**, including the benign control |
| `WebSearch` | two neutral queries | **2/2 OK**, returning substantive extracted page text |

`E` = **search-capable, fetch-blocked.** The block is not per-domain: a trivially
benign control domain is refused identically, so the earlier per-domain framing
is superseded. The solver can read *about* a page through the search layer but
cannot open one to check a number at source, and cannot resolve a conflict
between two sources by opening either.

`[MEASURED]` The solver-web arm matched the orchestrator arm on every target, so
the key-verification environment and the solver's retrieval environment share one
egress path. Under the probe's pre-registered rule this licenses the transfer —
by measurement, not by architectural expectation.

**What this means for the claim.** Stage 0A-M studies *retrieval-enabled under a
search-capable, fetch-blocked environment*. That is materially **weaker** than
unrestricted browsing, and every claim is scoped to it (specification §6.3). It
does **not** constrain eligibility: no item is dropped, reweighted or
reclassified because a source is unreachable, and a solver whose fetch is refused
but which answers anyway is retained and graded (§7 case A).

`[PREREG]` The report's ALTERNATIVE EXPLANATIONS section carries `E` verbatim.

## Remaining at execution time — the complete list

| # | Check | How to satisfy it without exposing a production stem |
|---|---|---|
| 1 | Freeze commit SHA | `git rev-parse HEAD` at freeze; record in the run manifest |
| 10 | Target model/version snapshot | record the solver model id and any served-model fallback per trial |
| 11 | Execution environment fingerprint | re-run the frozen egress probe once, screen-class; compare to `E` |
| 13 | Telemetry dry run | use a synthetic non-production stem; never a battery item |
| 15 | Fresh-context-per-trial verification | synthetic canary: dispatch two synthetic trials, confirm the second cannot recall the first |
| 17 | Run directory creation | created at dispatch time; must not exist before |

`[PREREG]` **Checks 13 and 15 use synthetic probes only.** Exposing a production
stem to complete a dry run would spend treatment exposure on infrastructure
validation, which is exactly the thing the zero-exposure invariant protects.

`[PREREG]` **Split-environment rule.** If check 11 at execution time returns an
environment differing from `E`, the run does not silently proceed: it is either
re-scoped before dispatch or halted and reported as a split-environment run
(specification §7). Results from two environments are never pooled.

## 2026-09-01 — agent-symmetry validation, static part

| check | state |
|---|---|
| dedicated agent bodies byte-identical | **done** — `2e1fb5851b784b90` |
| descriptions identical, no arm label | **done** (repaired this turn) |
| tool difference exactly {WebSearch, WebFetch} | **done** |
| packets differ only in TOOLS block (3 lines) | **done** |
| no user-scope shadow of the dedicated agents | **done** — user scope holds only the shared solvers |
| no hooks | **done** |
| full suite | **green** |
| freeze record with recomputable hashes | **done** — `experiments/exp004_stage0am/freeze_record.json`, tested |
| closed canary · retrieval canary · fresh-context canary · egress probe via dedicated agent | **BLOCKED** — need a session started after `0fb8a7f` |

`[MEASURED]` The Agent tool in this session reports `stage0am-solver-closed` and
`stage0am-solver-web` as not found, before and after a context-reload request.
Claude Code registers `.claude/agents` at session start; this session predates
the agents. No safe substitute exists in-session: the generic agents can read
the answer key, and the shared solvers carry the asymmetric prompts.
