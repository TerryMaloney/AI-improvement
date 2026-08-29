# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Next authorized research action

Write and independently red-team the **Stage 0A-M objective mechanism-assay specification**. No solver dispatches yet.

The grading investigation found that the cleanest primary measurement is not structured output and not LLM judging. It is to make the target unambiguous in the **question stem**, preserve ordinary answer format, and grade against frozen deterministic keys.

### Current candidate primary classes

1. **Date-anchored / time-indexed**
   - e.g. “As of YYYY-MM-DD, what was X?”
   - exact historical/current target frozen in the key.

2. **Definition-anchored / definition-fixed quantity**
   - scope, definition, date, unit, and convention explicitly fixed in the stem;
   - retrieval may surface an incompatible but superficially relevant quantity.

3. **Arithmetic / deterministic**
   - exact objective key;
   - retained as a low-ambiguity comparator even though its harm mechanism is more speculative.

False-premise is **not** part of the objective primary. It remains for Stage 0A-N naturalistic manifestation and later execution-grounded work because an explicit premise-status/decision field would itself cue premise inspection.

## Required specification work

Before any dispatch:

1. Precisely define each retained class so another researcher can classify items without retrieval outcomes.
2. Enforce one class per item.
3. Verify all primary keys are objective and frozen before dispatch.
4. Recompute power for 15/20/25 items per class under K=3 Holm correction.
5. Define item authoring rules that cannot use search-arm results or prior search outputs.
6. Freeze ordinary response format; do not add epistemic/status fields to the primary.
7. Log generated queries, returned evidence, tool state, timing, model snapshot, and telemetry.
8. Predefine Stage 0B's third fixed/high-quality-query arm now.
9. Specify technical-failure handling and fail-closed thresholds.
10. Prewrite the report skeleton and stress-sample claim limitations.
11. Define Stage 0A-N separately as exploratory naturalistic free-text work; do not pool its judged outcomes with Stage 0A-M.
12. Red-team whether question anchoring itself changes the intended construct. The anchor is necessary to define the target, but it may make tasks unusually explicit; this is an external-validity limitation that must be stated.

## Separate future hypothesis exposed

Do not merge into exp004:

**Does requiring explicit epistemic structure (premise status, time scope, definition scope, source status) itself reduce retrieval-induced errors?**

This belongs to the epistemic-system research branch as a genuine intervention experiment, not as grading calibration.

## Stale infrastructure test

The proposed replacement appears infrastructure-only:
- if the knowledge-probe artifact exists, assert `dispatch_class == "screen"`;
- assert its trials do not appear in solver-experiment manifests.

Frozen graded evidence must remain untouched. The next operator may recommend/implement this only if it is clearly isolated from experiment artifacts and tests document the invariant.

## Hard stop

Do not:
- run Stage 0A-M solver calls;
- author items with retrieval outcomes visible;
- introduce task-directing structured output into the objective primary;
- use runtime judge escalation;
- mix Stage 0A-N judged results into Stage 0A-M confirmatory inference;
- claim naturalistic prevalence or controller value.

## Final gate for next turn

Return one:
A. STAGE 0A-M READY TO FREEZE
B. READY AFTER SPECIFIC NON-DISPATCH REMEDIATIONS
C. ANCHORED CLASSES NOT OPERATIONAL ENOUGH
D. POWER/COST NOT JUSTIFIED
E. OBJECTIVE ASSAY STILL CHANGES THE CONSTRUCT TOO MUCH

If A, provide the exact proposed frozen specification and exact files to create/update, but do not dispatch unless separately authorized.

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
