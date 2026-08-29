# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Next authorized research action

Write and red-team the **Stage 0A mechanism-discovery specification**. No solver dispatches yet.

The specification must define:

1. The exact scientific claim:
   - a preregistered treatment-blind class has a negative mean retrieval effect on an authored stress sample.
   - explicitly not a general controller or naturalistic prevalence claim.

2. Four treatment-blind classes:
   - one class per item;
   - membership frozen before outcomes;
   - surface classes used for stratification;
   - hypothesized mechanism dimensions recorded only as covariates.

3. Fixed-n discovery design:
   - candidate starting point: 20 items/class;
   - two arms;
   - R=1;
   - deterministic subset primary;
   - exact one-sided conditional-binomial/McNemar-style test per class;
   - Holm across classes.

4. Authoring safeguards:
   - no treatment-arm outcomes during item construction;
   - no class rebalancing after outcome visibility;
   - answer definitions explicit enough to avoid f15-style key ambiguity;
   - clean closed arm;
   - identical wrappers except the retrieval intervention.

5. Query-generation confound:
   - log generated queries verbatim in Stage 0A;
   - predefine Stage 0B fixed-query arm now;
   - if discovery survives but confirmation harm disappears under fixed query, classify as query-construction failure rather than retrieval harm.

6. Confirmation architecture:
   - fresh independently authored items;
   - winner class/hypothesis frozen before confirmation items exist;
   - power confirmation for a smaller effect than discovery because of winner's curse;
   - candidate 25 fresh items;
   - three arms: closed, ordinary search, fixed-query search.

7. Stress-sample language:
   - discovery/confirmation may establish predictable harm under condition X;
   - they do not estimate naturalistic frequency or general-router value.

8. Final preflight:
   - egress state;
   - telemetry;
   - grading/key fingerprint;
   - report skeleton;
   - stale frozen-test assertion handled transparently.

## Hard stop

Do not dispatch Stage 0A until:
- the discovery specification has been independently red-teamed;
- item texts/keys are frozen;
- class assignments are frozen;
- n/classes/arms/grading/statistics are frozen;
- query logging is active;
- a distinct preregistration/freeze commit exists.

## Future stages after a positive Stage 0A

0B — fresh independent confirmation + fixed-query alternative.
0C — naturalistic prevalence/importance.
0D — held-out mixed-task controller test.
0E — richer action space, only if earned.

## Manual setup reminder

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, the response must begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.

## Required Claude handoff

```text
COMMIT:
TESTS:
DISPATCHES:

RESULT:

CHANGED:

OPEN:

DO NOT:
```
