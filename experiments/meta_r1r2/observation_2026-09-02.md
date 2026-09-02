# R1′/R2′ prospective scoring — observation 1

The prospective component table (`prospective_component_table.yaml`, fingerprint
`068c842e4c8836c5`) was frozen at `37ac525` on 2026-09-02, **before** the
execution session that produced this observation. The table is not edited; this
file records the score.

## Observation

The first load-bearing defect found after the freeze is:
**`stage0am-solver-closed` declares `tools: TodoWrite`, which is unrecognized at
runtime, so the agent resolves to zero tools and the harness refuses to spawn
it.** The closed arm of Stage 0A-M could not be dispatched.

## Which cell

`live_agent_registry` — repository agent definition vs the live runtime.

| | prediction |
|---|---|
| R1′ predicted risk | **HIGH** (treatment-relevant, no executed invariance check binding declared → realized) |
| churn predicted risk | **low** (churn 0 — this component has no artifact and was never edited) |

This is one of the three pre-declared `r1_high_churn_low` discriminating cells.

## Verdict: SUPPORTS R1′ over the churn rival — n = 1

Honest qualifications:

- The 2026-09-01 registry failure (agents committed but not loaded by an older
  session) was used to *construct* R1′ and is excluded. This is a **different
  mechanism** in the same component: the agent is registered, but its declared
  tool list does not survive runtime resolution. The component was named in
  advance; the mechanism was not.
- n = 1. One defect does not establish a rate. The table's other two
  discriminating cells (`configured_effort`, `served_model_per_trial`) remain
  unscored, and no defect has yet appeared in the churn-high cells.
- The defect is also an R2′ instance: the tool surface is one construct with two
  representations (frontmatter file, live runtime) and **no correspondence
  test**. Every existing check reads the file. That is exactly the R2′ drift
  class, and it is why 1,397 green tests did not catch it.

## Consequence for the contract discipline

The `EXPERIMENT_CAUSAL_CONTRACT` schema already permits a `live_probe` check
type. Had the Stage 0A-M contract been a *gate* rather than a retrospective
fixture, the `[OPEN]` artifact on the `model → treatment` edge would have
blocked freeze for precisely this reason. Stage 0B's contract carries the same
edge as `[OPEN]`; it must be closed with a live probe, not a file test.
