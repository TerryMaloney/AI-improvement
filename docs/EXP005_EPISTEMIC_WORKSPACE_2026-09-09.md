# EXP005-EPI — Persistent Epistemic Workspace

**Status: IMPLEMENTED CONSTRUCT PROTOTYPE. No LLM outcome exists. No real-world accuracy claim is licensed.**

## 1. Research question

Can a frozen general-purpose model be made more accurate over long time horizons by placing it inside an external epistemic system that keeps **evidence**, **beliefs**, **derivations**, and **objectives/permissions** separate?

The target is not a larger prompt and not ordinary retrieval augmentation. The target is a model-agnostic truth-maintenance layer that can:

1. preserve what evidence actually said;
2. revise beliefs when evidence changes;
3. identify contradictions without forcing false certainty;
4. propagate a corrected premise through dependent beliefs;
5. distinguish independent corroboration from copied consensus;
6. proactively re-check weak, stale, load-bearing beliefs;
7. preserve a revision/provenance trail; and
8. prevent evidence from rewriting objective or permission state.

The intended falsifiable claim is eventually:

> Under delayed misinformation and contradictory evidence, an epistemic workspace reduces persistent false beliefs and downstream error propagation relative to compute- and metadata-matched RAG without increasing erroneous corrections.

That claim is **not yet supported**. This commit only establishes executable constructs.

---

## 2. Why ordinary RAG is not the whole problem

A RAG system primarily answers:

> Which stored information should be placed in context for this query?

The longitudinal epistemology problem is:

> What do I currently believe, why, which conclusions depend on it, what should change if new evidence conflicts with it, and which uncertainty is important enough to investigate proactively?

A document can be retrieved correctly while the system still fails because:

- five search results are copies of one underlying source;
- a later document is newer but weaker;
- a fact changed over time rather than an old source becoming false;
- a correction invalidates downstream conclusions but those conclusions are never revisited;
- two credible sources genuinely leave the issue unresolved;
- the system cannot reconstruct why it believes a claim;
- retrieval text is treated as instruction rather than evidence; or
- a self-improving agent changes its evaluator/objective while optimizing itself.

EXP005-EPI therefore treats retrieval as an evidence-acquisition mechanism, not the epistemology itself.

---

## 3. State separation

### 3.1 Evidence state — append-only

Implemented by `lab.exp005_epi.Evidence` and persisted by
`lab.exp005_epi_store.EpistemicStore`.

Evidence records:

- immutable `evidence_id`;
- proposition;
- asserted boolean value in v1;
- source;
- lineage;
- reliability;
- observation time;
- explicit supersession links;
- metadata.

Evidence is never overwritten. A correction creates new evidence and may mark an older evidence record as superseded for current inference while retaining the old record in the audit log.

### 3.2 Belief state — derived and reversible

`Belief` carries:

- `SUPPORTED`, `REJECTED`, `DISPUTED`, or `UNKNOWN`;
- a derived probability-like score;
- active evidence IDs;
- counts of independent supporting/rejecting lineages;
- dependency provenance.

The number is an **internal aggregation score under the declared v1 model**, not a calibrated real-world probability.

### 3.3 Derivation state — explicit dependencies

`DerivedRule` records which propositions a conclusion depends on.

V1 uses deterministic boolean conjunctions because they give exact ground truth.
When a premise changes, `EpistemicWorkspace.recompute()` updates descendants and records the revision.

Acyclicity is enforced. Silent dependency cycles are rejected.

### 3.4 Objective / permission state — outside epistemic revision

`ObjectivePolicy` is frozen.

Evidence metadata can contain arbitrary strings, including attempted objective or permission changes, but no ingestion path interprets those strings as policy.

The SQLite store refuses to reopen an existing workspace under a different objective.

This is the first alignment boundary: the system may revise what it believes; it may not infer from evidence that it has permission to change what it is for.

### 3.5 Procedure state — future, gated

Future source-weighting, retrieval, verification, or belief-update procedures may be learned, but no procedure is self-installed because it appears to improve its own exposed score.

Promotion must be:

candidate -> sandbox -> held-out external evaluation -> regression/safety tests -> promotion.

---

## 4. Source lineage

`EpistemicWorkspace._lineage_representatives()` counts copied evidence once per declared lineage.

This is intentionally simple. It does **not** solve source-independence inference. In v1, lineage metadata is supplied by the benchmark.

That creates a major future test:

> Can a system infer source lineage accurately enough from real evidence to retain the benefit?

A weak baseline that ignores lineage is insufficient. Therefore EXP005-EPI also implements `MatchedRAG`, which receives the same reliability, lineage and supersession metadata as the workspace.

Any future capability claim must beat that stronger control, not merely `NaiveRAG`.

---

## 5. Belief revision

For each proposition, active evidence is:

1. filtered for explicit supersession;
2. reduced to one representative per lineage;
3. weighted by the declared source-reliability score;
4. aggregated on a log-odds scale.

V1 resolves:

- probability >= 0.80 -> `SUPPORTED`;
- probability <= 0.20 -> `REJECTED`;
- conflicting unresolved evidence -> `DISPUTED`;
- otherwise -> `UNKNOWN`.

These thresholds and the reliability model are **engineering hypotheses**, not validated epistemology.

They must later be ablated against simpler rules and calibrated using outcomes.

A correct architecture may survive while this exact weighting rule fails.

---

## 6. Truth maintenance

Every belief transition creates a `Revision` carrying:

- old status;
- new status;
- old/new score;
- evidence provenance or premise IDs;
- timestamp;
- reason.

`provenance(proposition)` recursively reconstructs why a derived belief currently has its state.

This is the intended answer to the delayed-false-premise problem:

> correcting premise X is not complete until every load-bearing descendant has been reconsidered.

---

## 7. Epistemic debt and active verification

`epistemic_debt()` is a first executable controller heuristic:

`uncertainty × source fragility × staleness × downstream load × decision impact`

It is not claimed optimal.

Its purpose is to make a stronger hypothesis testable:

> Proactively verifying high-debt beliefs reduces future error more efficiently than query-triggered retrieval or periodic random re-checking.

`verification_queue()` ranks current beliefs by this score.

A first unit test establishes only the construct: two equally uncertain beliefs are ranked differently when one supports more downstream conclusions.

Future experiment EPI-2 must compare this controller against:

- no proactive verification;
- random verification;
- uncertainty-only;
- age-only;
- dependency-only;
- oracle expected-value selection.

---

## 8. Persistence

`lab/exp005_epi_store.py` provides SQLite persistence with WAL enabled.

Tables:

- `metadata`;
- `evidence`;
- `rules`;
- `snapshots`.

There is deliberately no evidence UPDATE/DELETE interface.

A round-trip test reconstructs the workspace from immutable evidence + rules and requires the same workspace fingerprint.

This is an external memory system, not model-weight learning.

---

## 9. Comparators

### RecentContext

Only the most recent K pieces of evidence remain available.

This represents bounded conversational memory, not a competitive RAG system.

### NaiveRAG

Stores all evidence but:

- counts every document as independent;
- has no source-lineage control;
- has no revision history;
- has no epistemic-debt controller;
- has no objective boundary.

It is useful for specific failure demonstrations, not for the main scientific claim.

### MatchedRAG

Receives the **same**:

- evidence stream;
- reliability values;
- lineage metadata;
- supersession metadata;
- deterministic derivation rules.

It recomputes beliefs on demand but has no persistent belief/revision state, epistemic-debt queue, or objective boundary.

This is the important control.

If MatchedRAG matches the workspace on ordinary final-answer accuracy, the workspace has not earned an accuracy claim from those tasks.

---

## 10. Construct benchmark

`python -m lab.exp005_epi_benchmark`

Current deterministic scenarios:

1. **Delayed false premise** — X is believed incorrectly, Y/Z depend on X, and a stronger correction arrives much later.
2. **Copied consensus** — five visible sources share one lineage; one stronger independent source contradicts them.
3. **False-correction resistance** — weaker newer evidence contradicts strong old evidence.
4. **Genuine temporal change** — new authoritative evidence explicitly supersedes an old fact.
5. **Unresolved conflict** — equally strong independent evidence supports both sides.

Current construct result, generated locally and recorded in `runs/exp005_epi_construct/benchmark.json`:

| System | Correct epistemic states |
|---|---:|
| EpistemicWorkspace | 8 / 8 |
| MatchedRAG | 8 / 8 |
| NaiveRAG | 7 / 8 |
| RecentContext | 3 / 8 |

**License:** construct validation only.

The important result is not 8/8. The important result is that the stronger MatchedRAG control also scores 8/8, preventing a weak claim.

The workspace-specific value must therefore be demonstrated on *longitudinal* metrics that on-demand QA alone does not measure.

---

## 11. Primary future metrics

### Current-state truth accuracy
Fraction of current resolvable beliefs matching world state.

### Epistemic-state accuracy
Whether the system reaches the stance licensed by the available evidence, including `UNKNOWN` / `DISPUTED`.

### Correction latency
Events between corrective evidence becoming available and the belief changing.

### Propagation completeness
Fraction of downstream beliefs that are reconsidered/repaired after a load-bearing premise changes.

### Collateral damage
Unrelated correct beliefs changed by a revision event.

### False-update resistance
Rate at which weak/new misleading evidence incorrectly overturns a stronger belief.

### Stale-belief recurrence
Probability a corrected belief or dependent conclusion returns later without new supporting evidence.

### Provenance fidelity
Whether current conclusions can be reconstructed from the evidence/dependency log.

### Source-lineage sensitivity
Response to N apparent sources as a function of the number of genuinely independent lineages.

### Verification efficiency
Error prevented per verification/tool/model cost.

### Objective-integrity violations
Any path by which evidence or learned procedure modifies objective/permission state without the external promotion mechanism.

---

## 12. Experimental ladder

### EPI-0 — construct validation — CURRENT

No LLM required.

Purpose:
- prove the objects are executable;
- prove revision propagates;
- prove evidence remains immutable;
- prove objective state is separated;
- establish strong controls.

No real-world capability claim.

### EPI-1A — synthetic longitudinal world, oracle extraction

Generate many randomized worlds with known truth and known atomic evidence.

The systems receive the **same pre-extracted atomic claims**.

This isolates memory/revision/control architecture from language extraction.

Compare:

- recent context;
- ordinary flat retrieval;
- metadata-matched RAG;
- epistemic workspace.

Primary outcomes must be longitudinal, not only final QA.

No LLM judge is needed for ground truth.

### EPI-1B — model claim extraction

Render the same synthetic evidence as natural-language documents.

A frozen model extracts candidate atomic claims.

Measure extraction accuracy separately.

Then pass the **same extracted claims** into competing memory architectures.

This isolates:

`language -> claim extraction`

from:

`claims -> epistemic state`.

### EPI-2 — active verification

Give systems a limited verification budget.

Hidden world state determines which verification would be useful.

Compare epistemic-debt routing against matched cost baselines.

This is the first direct test of the proposed "information-gain controller".

### EPI-3 — historical replay

Select real domains with timestamped evidence and later corrections.

At each simulated date, the system may use only evidence that existed by then.

Primary question:

> Did it maintain the best state supportable at that time?

Do not score only against today's final answer.

### EPI-4 — cross-model transfer

Freeze the epistemic layer and repeat with multiple LLM families.

A model-independent gain requires the same procedure to transfer without model-specific retuning on the confirmation sets.

### EPI-5 — procedure learning

Only after the earlier layers survive.

Allow a development agent to propose:

- retrieval policies;
- source-lineage heuristics;
- reliability calibration;
- verification policies;
- conflict-resolution procedures.

Promotion remains external and held-out.

---

## 13. Alignment / misalignment guardrails

1. **Evidence is data, never instruction.**
2. **Evidence cannot grant permissions.**
3. **A model statement is not evidence merely because the model emitted it.**
4. **Objective and permission state is not autonomously revisable.**
5. **Old evidence is retained after correction/retraction.**
6. **Unresolved conflicts may remain unresolved.**
7. **Procedure changes do not self-promote.**
8. **Evaluator state lives outside the optimization loop.**
9. **Source count is not treated as independence count.**
10. **A later timestamp is not automatically higher evidential weight.**
11. **Tool output is quarantined from system/control instructions.**
12. **Every model-generated transformation will need provenance linking back to the raw evidence it summarized.**

---

## 14. Current limitations

The prototype intentionally has major limitations:

- propositions are boolean;
- claim identity is supplied, not discovered;
- source reliability is supplied, not learned;
- source lineage is supplied, not inferred;
- derived rules are deterministic conjunctions;
- direct evidence and derived evidence cannot yet coexist on the same proposition;
- the log-odds aggregator assumes independence across declared lineages;
- no semantic/vector retrieval exists yet;
- no natural-language claim extraction exists yet;
- no real tool/web evidence is ingested;
- no model inference has been run;
- the benchmark is tiny and designed by the same researcher who designed the system.

Therefore the current result proves only:

> The software can represent and execute the intended epistemic operations on deterministic fixtures.

Nothing stronger.

---

## 15. Kill / revise criteria

Revise or kill the architecture if any of the following survives appropriate debugging/ablation:

1. MatchedRAG achieves the same longitudinal performance at equal cost with a substantially simpler state representation.
2. The advantage disappears once source reliability/lineage must be inferred rather than supplied.
3. Active verification cannot beat random/uncertainty-only baselines at matched cost.
4. Revision propagation increases collateral damage enough to erase correction gains.
5. Claim-extraction errors dominate the memory-layer effect.
6. Persisted stale beliefs re-enter answers despite the revision graph.
7. Cross-model gains require model-specific retuning.
8. Source-lineage inference creates larger errors than duplicate-source control prevents.
9. Procedure learning improves exposed metrics but worsens hidden truth-state metrics or objective-integrity tests.

---

## 16. Next implementation step

Do **not** add an LLM yet.

Build EPI-1A as a randomized, seeded world generator with:

- many propositions;
- dependency DAGs;
- controlled misinformation;
- delayed corrections;
- copied-source clusters;
- genuine temporal changes;
- unresolved conflicts;
- false corrections;
- limited observation windows;
- per-belief decision impact.

Freeze the world generator before comparing systems.

Then derive sample size and primary longitudinal metrics from the generated discordance/sensitivity, using the same proof-before-production discipline learned in Stage 0.

The next real scientific question is:

> Does persistent truth maintenance provide measurable value beyond a metadata-matched RAG that can simply recompute the answer on demand?
