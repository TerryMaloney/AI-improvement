# Next Action

> This is the short cross-chat handoff file. Update it at the end of every substantial research action.

## Current state

Stage 0A-M has a committed specification and tested synthetic analysis at commit `330392d`, but **production item authoring is not yet authorized**.

A focused final inferential audit is required before authoring because review of the committed specification/code exposed several claim/measurement mismatches that must be resolved without solver dispatches.

## Next authorized research action

Perform a **read-only Stage 0A-M inferential-consistency audit**. No solver dispatches and no production item authoring.

### 1. Null / claim alignment — load-bearing

`lab/stage0am.py` proves validity under the pointwise class null:

> retrieval does not hurt any item in this class (`delta_i >= 0` for every item).

The specification/report language currently describes a **class-average negative effect**.

These are not automatically the same hypothesis.

Required:
- derive exactly what null the exact conditional-binomial test controls;
- determine whether it also controls Type-I for the broader null `mean(delta_i) >= 0` under arbitrary item heterogeneity;
- either prove that broader validity, exactly enumerate/bound it for the planned n, or produce a counterexample;
- if broader validity is not established, change the scientific claim/estimand or change the test before authoring.

Do not rely on the phrase “the statistic is driven by the class mean” as a proof.

### 2. Retrieval treatment definition

Freeze whether the retrieval arm means:
- retrieval is merely available and the model may choose not to use it; or
- at least one retrieval/search action is required.

If use is optional, the estimand is an intent-to-treat effect of a retrieval-enabled procedure, not the causal effect of retrieval conditional on actual use.

The scientific claim must match the treatment actually delivered. Never exclude a trial because the model chose not to search unless that rule was part of the treatment before outcomes.

### 3. Negative-control metric

The current arithmetic control reports a Clopper–Pearson upper bound on the **baseline-favouring share among discordant items**.

When `D=0`, the implementation correctly returns `1.0`, but that makes a perfectly clean arithmetic control maximally uninformative.

Investigate whether the control should instead bound something such as:
- the baseline-favouring discordance rate among **all** control items (`n10 / n`);
- paired risk difference;
- or another exact quantity that remains informative when no discordances occur.

The negative control must have a prespecified interpretation and must not be promoted to a causal claim it cannot support.

### 4. Remove subjective Stage 0B advancement language

The current spec advances a class only if query logs show “no systematic construction defect.” That phrase is not operationalized and could create post-outcome researcher discretion.

Either:
- define a fully objective pre-outcome rule;
- or remove it from the advancement gate and let Stage 0B’s fixed-query arm test query-generation failure directly.

Query logs may remain diagnostic regardless.

### 5. Operationalize invalidation language

Review §14 phrases including:
- “class purity below ~70%”;
- “negative control showing harm comparable to the primary classes”;
- “anchoring proving to suppress the effect.”

For each, decide whether it is:
- observable under this design;
- a formal invalidation rule;
- a power sensitivity;
- or merely a limitation.

Do not leave an unobservable latent quantity such as true harm-purity as a post-outcome invalidation gate.

### 6. Null-result interpretation

Define exactly what a clean null licenses.

A null in Stage 0A-M must not become evidence that retrieval is harmless on unanchored/naturalistic tasks. But it should also not be called wholly “uninterpretable” if it validly says the anchored stress assay did not detect its preregistered effect.

Freeze the report language now.

### 7. Re-run synthetic adversarial tests

Add no production data.

Stress the finalized test against:
- mixed positive/negative item effects with nonnegative class mean;
- heterogeneous baseline difficulty;
- low/high discordance rates;
- negative-control `D=0` and small-D cases;
- optional-vs-mandatory retrieval semantics where representable.

If a counterexample invalidates the current claim, treat that as a successful audit result.

## Hard stop

Do not:
- author production items;
- freeze the production manifest;
- run solver calls;
- inspect treatment search results;
- preserve a claim merely because code/tests are currently green.

## Final gate

Return exactly one:

A. SPEC INTERNALLY CONSISTENT — AUTHORING MAY BEGIN
B. SPEC REQUIRES NON-DISPATCH PATCHES BEFORE AUTHORING
C. PRIMARY TEST DOES NOT SUPPORT THE CLAIM
D. NEGATIVE CONTROL MUST BE REDESIGNED
E. TREATMENT/ESTIMAND MUST BE REFORMULATED

If A or B, commit/push any specification, analysis, and synthetic-test corrections that are justified, run the full non-dispatch suite, and stop before item authoring.

If a future stage requires Terry to manually install, authorize, connect, or physically configure anything, begin with the mandatory manual-setup alert defined in `docs/EXTERNAL_COGNITIVE_TOOLS_AND_TOPOLOGY_2026-08-29.md`.
