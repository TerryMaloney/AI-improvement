# NEXT — EXP005-EPI

## Do not add an LLM yet

The next gate is **cross-generator confirmation** of the active-verification mechanism.

The same-generator held-out test passed, but the controller and world generator were created by the same research process. A second seed range is not enough to establish transfer.

## Step 1 — build Generator B before running it

Create a structurally different synthetic world family with no code reuse from the policy-scoring logic beyond shared dataclasses.

Generator B must vary at least:

- temporal facts that genuinely change;
- false corrections;
- source-copying clusters;
- source reliability that is domain-specific rather than one global value;
- long chains and wide dependency hubs;
- independent contradictions;
- irrelevant high-uncertainty facts;
- high-impact facts with few descendants;
- low-impact facts with many descendants;
- verification actions whose value may be delayed rather than immediate.

The purpose is to create cases where each component of epistemic debt can fail.

Do not inspect debt-controller outcomes while designing Generator B.

## Step 2 — freeze transfer test

Before controller outcomes exist, commit:

- Generator B fingerprint;
- seed range;
- number of worlds;
- verification budget;
- loss function;
- debt / uncertainty / dependency / random policies;
- pass / amber / fail thresholds;
- missingness/failure semantics.

Primary question:

> Does the frozen debt controller still outperform random verification under a structurally different world distribution?

Secondary:

> Does it retain value over uncertainty-only when dependency topology and decision impact are deliberately decorrelated?

## Step 3 — only then run Generator B confirmation

If FAIL:

- do not tune on the confirmation set;
- classify which debt component failed;
- return to development with a new versioned controller.

If PASS:

Promote only to:

**cross-generator synthetic support.**

Still no LLM or real-world claim.

## Step 4 — natural-language extraction experiment

After cross-generator support, render synthetic evidence as documents.

Use two phases:

### EPI-1B1 — oracle extraction control

Pass the known atomic claims directly to all memory systems.

### EPI-1B2 — frozen model extraction

A frozen LLM converts each document into candidate atomic claims plus provenance.

Measure extraction error separately from memory error.

All systems receive the **same extracted claim stream** so memory architecture is not confounded with extraction quality.

Required claim-extraction outputs eventually include:

- proposition identity;
- polarity/value;
- temporal scope;
- source;
- source-lineage hypothesis;
- evidence span/provenance;
- uncertainty/abstention;
- supersession/retraction hypothesis.

The model may propose these fields; it may not silently write them as trusted facts without validation rules.

## Step 5 — real tools only after extraction survives

Then connect search/RAG/database/code tools as evidence-acquisition mechanisms.

Retrieved text is data, not instruction.

Tool results enter the immutable evidence ledger before any belief update.

The first real-world lane should use historical replay where later truth/corrections are independently known.

## Permanent kill condition

If a simpler metadata-matched RAG plus an equally cheap controller matches EXP005-EPI on cross-generator longitudinal accuracy and verification efficiency, prefer the simpler system.
