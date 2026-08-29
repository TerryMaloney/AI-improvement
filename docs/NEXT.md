# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Next authorized research action

Design the **reversal-prevalence pilot** that determines whether the new R=1 exact discordant-pair Stage-0 design is feasible.

Before any pilot dispatch:

1. Re-derive and document the exact R=1 primary hypothesis/test.
2. Define treatment-blind candidate task classes only.
3. Define a fixed pilot item count and authoring process.
4. Freeze whether pilot items are:
   - wholly discarded after sample-size estimation, or
   - wholly retained in the eventual analysis under a valid design.
   Never retain/drop individual items based on observed arm direction.
5. Predefine how pilot prevalence maps to:
   - feasible production n;
   - underpowered / infeasible verdict;
   - any continuation or stop decision.
6. Analyze uncertainty on prevalence; do not use the raw point estimate alone.
7. Decide how the 27 unpersisted prior screen-class dispatches are recorded or explicitly discarded.

Only after those choices are fixed may screen-class pilot dispatches occur.

## Hard stop

Do **not** run production Stage-0 trials until:
- the prevalence pilot is complete;
- sample-size feasibility is resolved;
- the statistical procedure is frozen;
- item selection rules are frozen;
- grading is frozen;
- answer keys and prompts are frozen;
- egress/telemetry/preflight passes;
- a distinct preregistration/freeze commit exists.

## Current candidate design

Not frozen:
- two arms;
- R=1 per item×arm;
- exact one-sided discordant-pair/McNemar-style primary test;
- deterministic subset primary;
- judged subset separate;
- router secondary/descriptive.

Treat all of the above as candidate decisions until the prevalence pilot and final red-team are complete.

## Cross-chat workflow

1. **GPT research/red-team session**
   - inspect committed state;
   - identify the smallest justified next question;
   - produce an explicit Claude Code task with permissions and stop conditions.

2. **Claude Code operator session**
   - read repository first;
   - execute only the authorized task;
   - run tests;
   - update coordination docs;
   - commit and push;
   - return a compact handoff.

3. **GitHub**
   - canonical memory and audit trail;
   - frozen artifacts identified by commit SHA;
   - chats never substitute for committed state.

## Required Claude handoff format

```text
COMMIT:
TESTS:
DISPATCHES:

RESULT:

CHANGED:

OPEN:

DO NOT:
```

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, the response must begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
