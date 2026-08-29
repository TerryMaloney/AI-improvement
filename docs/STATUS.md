# Current Research Status

> Coordination document only. This file is not a preregistration and must not override experiment-specific frozen artifacts.

## Current phase

**Stage 0 — redesigning the next retrieval-heterogeneity experiment after the R=10/A_minus design failed a dependence robustness check.**

The immediate objective is now to determine whether reversal prevalence is high enough in treatment-blind candidate task classes to make an exact R=1 discordant-pair design feasible.

## Established / measured so far

- exp003c found judge sensitivity at a rubric boundary: verbosity changed one deliberately boundary-sensitive item by half a verdict step; the aggregate measured length contrast was -0.125.
- Fixed-input judge replicates were deterministic in that instrument (reported sigma_judge = 0 across 96 judgments). This does **not** establish absence of systematic judge bias across different inputs.
- Frozen exp001/exp002 data do not provide true solver replication; shared exp002 arms were re-grades of earlier solver outputs.
- Self-reported search counts materially understated observed tool calls in the audited frozen data. Observed telemetry is authoritative going forward.
- Retrieval state predicates are not a single ladder. Search can occur without source access or verification.
- Current environment probing found search available while source fetch was blocked; unreachable states must be reported as NOT MEASURED.
- The original oracle-gap null/test is retired after configuration-dependent Type-I failure.
- The subsequent A_minus fixed-LFC design with repeated within-arm trials is also retired as the primary Stage-0 route: within-arm ICC as small as 0.02 materially inflated Type-I, and no affordable diagnostic could certify ICC below the required threshold.
- Across-arm shared latent effects and across-item burst correlation were conservative in the tested simulations; within-item×arm replicate correlation was the dangerous direction.
- A new candidate Stage-0 procedure uses R=1 per arm and an exact one-sided discordant-pair / McNemar-style test. It is immune to within-arm replicate ICC by construction.
- The new candidate procedure was well calibrated across the tested tied, heterogeneous, and burst-correlation configurations.
- Power under the new design depends strongly on the number/prevalence of true baseline-favouring reversal items.
- The frozen 15-item battery provides only weak evidence of ~13% apparent reversal prevalence and zero established reversals; this is insufficient to set production battery size.
- The old CEILING screen remains prohibited for reversal-sensitive experiments.
- Treatment-side scout selection remains prohibited.
- Deterministic outcomes remain primary; judged outcomes must be analyzed separately.

## Current blockers before formal preregistration

1. Design and pre-register a **reversal-prevalence pilot** using treatment-blind candidate task classes.
2. Decide whether pilot items are wholly discarded or wholly carried forward; never filter them based on observed treatment direction.
3. Quantify feasible production sample size as a function of the observed pilot prevalence without post-hoc threshold shopping.
4. Persist or explicitly discard the 27 prior screen-class independence-check dispatches; they currently exist only in transcript/scratchpad and are not auditable in the repository.
5. Re-probe egress before any production freeze.
6. Freeze clean closed-book/search arms, grading routes, reporting skeleton, and telemetry.
7. Only then write/freeze the production Stage-0 preregistration and battery.

## Retired recommendations

Do not revive these without a new derivation:
- A_minus fixed-LFC with n=18, R=10;
- exact critical value 0.1444 for that design;
- completing the old 80-dispatch independence diagnostic;
- selecting n based on fixed reversal count;
- targeting observed reversal prevalence as an inclusion criterion.

## Explicitly not authorized by this status

- No production Stage-0 solver dispatches.
- No production battery freeze.
- No treatment-arm-based item selection.
- No Stage-1 controller build.
- No recursive procedure search.
- No claims that retrieval control works or does not work.

## Broader direction

See `docs/RESEARCH_MAP.md` and `docs/EXPERIMENTAL_PROGRAM_2026-08-29.md`.

The long-term program includes intervention science, epistemic state, execution grounding, persistent self-models, external cognitive tools, memory topology, generalization, and later automated/recursive procedure search. None of those branches alter the current Stage-0 gate.
