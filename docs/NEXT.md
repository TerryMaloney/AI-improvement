# Next action — Stage 0A-M execution

**Stage 0A-M is freeze-ready. The next session performs execution-time preflight only, then runs the experiment. No design decisions remain, and none may be made after outcomes become visible.**

Read first, in this order:
1. `docs/EXP004_STAGE0A_M_SPECIFICATION.md` — the frozen design. §1.2 is the exact claim wording; §6.3 the treatment scope; §7 the failure semantics.
2. `docs/EXP004_STAGE0A_M_PREFLIGHT.md` — what is done and what remains.
3. `experiments/exp004_stage0am/manifest.json` — counts, fingerprints, grading semantics.
4. `experiments/exp004_stage0am/schedule.json` — the frozen dispatch order.
5. `docs/EXP004_STAGE0A_M_REPORT_SKELETON.md` — the report you will fill in.

## Execution-time preflight — the complete remaining list

| # | Check | How |
|---|---|---|
| 1 | Freeze commit SHA | `git rev-parse HEAD`; record in the run manifest |
| 10 | Model/version snapshot | record the solver model id per trial, plus any served-model fallback |
| 11 | Environment fingerprint | re-run the frozen egress probe once, screen-class; compare against `E` |
| 13 | Telemetry dry run | **synthetic stem only** |
| 15 | Fresh-context-per-trial | **synthetic canary only**: two synthetic trials, confirm the second cannot recall the first |
| 17 | Run directory | create at dispatch time; must not exist before |

**Checks 13 and 15 must never use a production stem.** Spending treatment exposure on infrastructure validation is exactly what the zero-exposure invariant protects against.

## Then run it

130 dispatches: 65 items × 2 arms × 1 replicate, in the order in `schedule.json`, arms adjacent per item, fresh context per trial. Grade with `lab/anchored_grading.py`; analyse with `lab.stage0am.analyse`; partition failures with `lab.stage0am.partition_pairs` before analysing.

## The traps this package already closed — do not reopen them

- **Do not condition anything on retrieval success.** A refused fetch with an answer is retained and graded (§7 case A). Only a dispatch that produced no gradeable answer voids its pair (case B). `partition_pairs` implements this; do not hand-filter.
- **Do not claim a class-average effect.** The licensed claim is §1.2's wording, verbatim. The class average is descriptive.
- **Do not drop an item because a source is unreachable.** `E` is search-capable, fetch-blocked; that scopes the conclusion, not the item set.
- **Do not re-key, re-word or reclassify an item after seeing an outcome.**
- **Do not pool across environments.** If check 11 disagrees with `E`, re-scope before dispatch or halt and report a split-environment run.
- **Scope every retrieval claim to `E`**, including in the null-result language of §15.

## Not authorization

The reflexive / error-correction research maps added 2026-08-30 are future context. They do not alter the Stage 0A-M battery, action space, hypothesis, inference, treatment, sample size, or report claim.
