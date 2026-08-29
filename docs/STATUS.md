# Current Research Status

> Coordination document only. This file is not a preregistration and must not override experiment-specific frozen artifacts.

## Current phase

**Stage 0 — validate the laboratory before the next production experiment.**

The immediate objective is to finish the statistical foundation for the next Stage-0 retrieval-heterogeneity experiment before spending production solver calls.

## Established / measured so far

- exp003c found judge sensitivity at a rubric boundary: verbosity changed one deliberately boundary-sensitive item by half a verdict step; the aggregate measured length contrast was -0.125.
- Fixed-input judge replicates were deterministic in that instrument (reported sigma_judge = 0 across 96 judgments). This does **not** establish absence of systematic judge bias across different inputs.
- Frozen exp001/exp002 data do not provide true solver replication; shared exp002 arms were re-grades of earlier solver outputs.
- Self-reported search counts materially understated observed tool calls in the audited frozen data. Observed telemetry is authoritative going forward.
- Retrieval state predicates are not a single ladder. Search can occur without source access or verification.
- Current environment probing found search available while source fetch was blocked; unreachable states must be reported as NOT MEASURED.
- The original oracle-gap null/test showed configuration-dependent Type-I failure and is not suitable as the confirmatory Stage-0 procedure.
- A candidate negative-direction statistic (A_minus) has shown substantially better calibration in the subsequent statistical investigation, but its final preregistration is not yet frozen.
- The old CEILING screening rule is inappropriate for the new reversal-sensitive question because it can remove exactly the high-baseline items that carry negative-direction signal.
- Treatment-side scout selection is not allowed for the new Stage-0 battery.
- Deterministic and judged outcomes should not be silently pooled when the judge measurement process can induce arm-dependent offsets.

## Current blockers before formal preregistration

1. Complete the planned replicate-independence diagnostic.
2. Resolve or explicitly bound the remaining LFC upper-quantile claim.
3. Finish R/n power comparison under the candidate valid test.
4. Freeze the redesigned qualification rule (no ceiling; no treatment-side selection).
5. Freeze deterministic-primary grading architecture.
6. Produce an end-to-end preflight checklist and dispatch budget.
7. Only then write/freeze the production preregistration and battery.

## Explicitly not authorized by this status

- No production solver dispatches.
- No production battery freeze.
- No Stage-1 controller build.
- No recursive procedure search.
- No claims that retrieval control works or does not work.

## Broader direction

See `docs/RESEARCH_MAP.md`.

The long-term program is not only benchmark experimentation. Once the lab is trustworthy, it must include an **execution lane** where discovered procedures are tested on useful tasks with external success criteria, initially favoring coding/build/test workflows.
