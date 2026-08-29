# Current Research Status

> Coordination document only. This file is not a preregistration and must not override experiment-specific frozen artifacts.

## Current phase

**Stage 0A-M has a committed objective-mechanism specification, but production item authoring remains blocked by one final inferential-consistency audit.**

Committed specification: `docs/EXP004_STAGE0A_M_SPECIFICATION.md` at `330392d`.

The design currently uses:
- date-anchored and definition-anchored primary classes;
- arithmetic/deterministic as a negative control outside the Holm family;
- n=25 per primary class, n=15 control;
- two arms, R=1;
- deterministic keys;
- exact one-sided conditional-binomial/McNemar-style analysis;
- Holm over K=2 primary classes;
- 130 planned solver dispatches after production freeze.

The stale knowledge-probe infrastructure assertion has been replaced by the stronger contamination-prevention invariant; the non-dispatch suite reported 1029 passed / 0 failed at `330392d`.

## Current load-bearing audit questions

### Null / claim alignment

The committed analysis proof establishes validity under the pointwise null `delta_i >= 0 for every item`, while the specification describes the target as a negative **class-average effect**. Before authoring, the lab must prove the exact test also controls Type-I for the broader class-average null, or narrow/change the claim/test.

### Treatment definition

The retrieval arm must be frozen as either:
- retrieval-enabled/optional use (intent-to-treat procedure effect), or
- mandatory actual retrieval.

The scientific wording must match the delivered treatment.

### Negative-control measurement

The current control bound is conditional on discordant items and returns 1.0 when D=0, making a clean arithmetic control uninformative. The control metric must be reconsidered before production.

### Stage 0B advancement

“Query logs show no systematic construction defect” is currently non-operational and cannot remain an outcome-dependent subjective advancement gate. It must be objectively prespecified or removed; the fixed-query confirmation arm is the planned direct test of query-generation failure.

### Invalidation language

Latent/unobservable quantities such as true class harm-purity must not become post-outcome invalidation gates. Power sensitivities, observable invalidation rules, and interpretive limitations must be separated.

## Hard stop

Until this audit closes:
- no production item authoring;
- no Stage 0A-M solver dispatches;
- no production manifest freeze;
- no treatment search-result inspection.

## Broader Stage-0 architecture

0A-M — objective anchored mechanism assay.
0A-N — separate naturalistic/free-text manifestation.
0B — fresh independent confirmation + fixed-query challenge.
0C — naturalistic prevalence/importance.
0D — held-out controller test.
0E — richer action space only if earned.

False-premise remains outside 0A-M and belongs in 0A-N/execution-grounded work. H-EPI-11 (explicit epistemic structure as a protective intervention) remains a separate future experiment.

See `docs/NEXT.md` for the exact authorized audit.
