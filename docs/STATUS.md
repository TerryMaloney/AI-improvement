# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M statistical/specification red-team is complete enough to begin production item authoring. Solver dispatch remains blocked until a distinct production freeze/preflight commit.**

Latest load-bearing audit commit: `3015ea6`.

## Stage 0A-M design now in force

Primary mechanism-assay classes:
- **date-anchored / time-indexed** — 25 items;
- **definition-anchored / definition-fixed quantity** — 25 items.

Negative control:
- **arithmetic / deterministic** — 15 items, outside the Holm family.

Planned production total after freeze:
- 65 authored items;
- 2 arms per item;
- R=1;
- 130 solver dispatches.

Primary analysis:
- exact one-sided conditional-binomial / McNemar-style test within each primary class;
- Holm correction across K=2 primary classes;
- deterministic objective grading only;
- retrieval treatment is **retrieval-enabled** (intent-to-treat procedure effect), never conditioned on observed tool use.

Primary licensed claim is deliberately finite and narrow:
> Among the preregistered authored items in this class, at least one item has a lower probability of an objectively correct answer under the retrieval-enabled procedure than under closed-book.

The class-average difference is descriptive only, with no formal inferential claim.

## Dependence boundary

The test does **not** assume arbitrary cross-item dependence is harmless.

Sufficient condition: for the preregistered item order, conditional on the discordance pattern and previous orientations, each discordant item's probability of being baseline-favouring is <= 1/2 under the pointwise null.

Frozen procedural protections:
- item order randomized from a recorded seed;
- primary classes interleaved, not dispatched in contiguous class bursts;
- arm order randomized independently within item;
- the two arms of an item paired closely in time;
- fresh context per trial;
- no answer/output from one trial enters another;
- model/runtime/timing metadata recorded;
- dependence diagnostics reported only, never used as post-hoc gates.

Arbitrary shared-orientation dependence was shown to break the ordinary binomial tail severely, so separate API calls must never be described as automatically independent.

## Negative control

Headline metric is the baseline-favouring discordance rate `n10 / n` among all arithmetic-control items with an exact Clopper-Pearson upper bound.

Generic tool-use tax interpretation is diagnostic only; it is not an automatic invalidation criterion.

## Stage 0B bridge

A primary class advances iff:
- Holm-adjusted p <= 0.05; and
- discordant count D >= 8.

Query quality is not a Stage 0A exclusion/advancement criterion. A fresh Stage 0B fixed-query arm is the planned direct test of query-generation failure.

## Now authorized

Production **authoring and prefreeze construction only**:
- author the 25 date-anchored items;
- author the 25 definition-anchored items;
- author the 15 arithmetic negative-control items;
- build objective frozen keys;
- store key-construction provenance separately from experimental retrieval evidence;
- independently verify keys/class membership;
- create the production manifest and frozen authoring/preflight artifacts;
- run only non-solver validation/tests;
- commit/push the candidate production freeze package.

## Still prohibited

Until a separate post-authoring audit authorizes execution:
- no Stage 0A-M solver/model dispatches;
- no treatment search-result inspection;
- no search-arm dry run on production items;
- no outcome-based item replacement/reclassification;
- no runtime re-keying;
- no Stage 0A-N or Stage 0B dispatches;
- no controller claims.

## Authoring interpretation

This is an intentionally authored stress assay. Public authoritative references may be used to construct and verify keys before freeze. Such references are **KEY-CONSTRUCTION EVIDENCE**, not experimental retrieval evidence. The item set is not a random sample from all date-anchored or definition-anchored questions, so no prevalence/generalization claim follows.

## Broader architecture

0A-M — objective anchored mechanism assay.
0A-N — separate naturalistic/free-text manifestation.
0B — fresh independent confirmation + fixed-query challenge.
0C — naturalistic prevalence/importance.
0D — held-out controller test.
0E — richer action space only if earned.

False-premise remains outside 0A-M. H-EPI-11 remains a separate future intervention experiment.

See `docs/NEXT.md` for the exact authoring authorization and stop conditions.
