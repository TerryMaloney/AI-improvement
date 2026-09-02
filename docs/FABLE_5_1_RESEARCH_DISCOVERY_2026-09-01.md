# Research Discovery Memo — 2026-09-01

Status: research synthesis and proposal. Not a preregistration. Alters no frozen
Stage 0A-M artifact. Every claim below is tagged [PROVEN] / [MEASURED] /
[SUPPORTED] / [HYPOTHESIS] / [OPEN]; anything untagged is opinion.

Reconstructed from: RESEARCH_MAP, STATUS, NEXT, DECISION_LOG, the four program
maps, the reflexive map and addendum, the Stage 0A-M specification, remediation,
freeze record, egress-probe files, `lab/stage0am.py`, `lab/anchored_grading.py`,
exp002 and exp003c reports, exp001/002 SQLite schemas, and the discarded-diagnostic
record. exp003a has a 388-trial manifest and **zero** answers: it never ran
[MEASURED]. Literature checks are listed in §4 with what each one killed.

---

## 0. Core synthesis — the smallest theory that explains what we learned

> **We repeatedly reasoned carefully about the model's epistemics while leaving
> the causal structure of our own experiment implicit.** Nearly every mistake was
> a missing or wrong edge in the never-drawn DAG of the experiment itself, or a
> construct that lived in prose in several places with no single executable
> binding.

Two root causes account for all twenty-odd failures in §1:

- **R1 — the experiment's causal graph was never made explicit.** A component
  assumed to be off the outcome path was on it (instrument, instruction, tool
  scaffold, screening rule); a shared latent feeding "independent" observations
  was invisible (run, judge, grader route, model family); a conditioning step
  opened a collider (selecting on baseline difficulty, on retrieval success, on
  the max over conditions).
- **R2 — the construct had no single source of truth.** The claim lived in §1
  prose, the null in `stage0am.py`, the key in YAML, the grader in a module the
  fingerprint did not cover. Drift between representations is then not an
  accident; it is the default.

The unifying architectural consequence (§2) is that error correction — for the
model, the retrieval layer, the evaluator, the environment, the self-model, the
critics, the objective, and the human — reduces to one primitive and one
operation: a **typed claim with an explicit evidence-generating process (EGP)
attached**, and **perturbation of the EGP to see whether the claim moves.** The
program's "six states" are object types of claims, not six modules.

---

## 1. Explaining our failures — generative modes, not a list

### 1.1 The taxonomy

| Mode | Root | Instances in this project |
|---|---|---|
| **G1 Boundary misplacement** — a component assumed outside the treatment or the instrument was inside it | R1 | asymmetric `solver-web`/`solver-closed` system prompts (instructions rode with the tool grant); structured output fields cueing the step under study; judge route depending on the answer, hence on treatment; "has web" as one state when search and fetch differ; arm labels in agent `description`; TodoWrite present in one arm's early draft |
| **G2 Hidden shared cause mistaken for independence** | R1 | 255 judgements counted as observations when 75 trials were unique; exp002 re-grading exp001 and calling it evidence; within-item×arm ICC ≥0.02 breaking Type-I at R=10; cross-item run-orientation correlation; "three critics" from correlated model families; derivative sources counted as independent |
| **G3 Proxy substituted for construct** | R2 | ±1,500 km² tolerance repairing a stem that did not fix the answer; pointwise null proven while prose claimed the mean; oracle gap G = min(A⁺,A⁻) defined by a selection; solver self-report used as tool telemetry (2× undercount, one-directional [MEASURED]); "harm" read off a judge score |
| **G4 Environment assumed, not measured** | R1 | orchestrator egress assumed equal to solver egress; agents assumed registered when the session predated them; `get_session` cost telemetry frozen across calls; WebFetch assumed domain-selective when it was wholesale-blocked |
| **G5 Selection on post-treatment variables** | R1 | CEILING screen removing every reversal-capable item (0/12) because closed-correct is the precondition for harm; §7 voiding items on retrieval failure, which only the treated arm can exhibit; reversal-prevalence tempting as an inclusion criterion |
| **G6 Specification drift across artifacts** | R2 | §4 "class-average estimand" vs §1 pointwise; §6.3 ITT vs §7 void-on-egress-refusal; packet hashes changed after a "final" audit; record body-hash computed by a different method than its test; "authoring has not begun" in a spec whose battery existed |
| **G7 Narrative outrunning the ledger** — completion reported from the plan, not from a persisted artifact | R2 | 27 dispatches reported as 80 complete; "R=20 complete" for f11/f14/f12; discarded diagnostic with no run directory |

G1, G4, G5 are three ways of getting the experiment DAG wrong; G2 is a missing
common cause in the same DAG; G3 and G6 are the construct having no executable
binding; G7 is the special case where the artifact that should bind the claim was
never written. Seven modes, two roots.

### 1.2 What the taxonomy predicts that we have not yet hit

These are the deliverable of this section. Each is falsifiable and most are cheap.

- **P1 [HYPOTHESIS, zero dispatches] Judge-route × treatment interaction in
  frozen data.** Retrieval-arm answers were shorter (267 vs 413 chars
  [MEASURED]); Claude-family judges penalised verbosity on the one interior
  item in exp003c [MEASURED, n=1]. So on exp001/002 items graded by both routes,
  the judge-graded retrieval effect should be *more favourable* to retrieval
  than the deterministic-graded effect on the same items. G1: the instrument
  sits on the treatment path via length. Test: SQL over `grades.method` ×
  `trials.condition` in the existing databases. If confirmed, every judged
  retrieval contrast in exp001/002 carries a known-direction instrument bias.
- **P2 [HYPOTHESIS] Served-model fallback clusters in time and therefore in
  arm.** The harness records `last_served_model`; fallbacks under load are
  temporal. Adjacent-arm pairing cancels this *within* item only if both arms
  hit the same served model. Prediction: if any fallback occurs in Stage 0A-M,
  it will be concentrated in a contiguous block of the schedule, and because arm
  order is randomised per item it will not systematically favour one arm — but
  it *will* inflate discordance in that block. G4. Test: per-trial served-model
  log (already required) → block-wise discordance rate.
- **P3 [HYPOTHESIS, free secondary analysis] Tool availability changes answers
  without tool use.** Stage 0A-M logs `NOT_ATTEMPTED`. Prediction: on items
  where the retrieval arm declined to search, closed-vs-retrieval discordance is
  still above the R=1 noise floor, in the harm direction. Prior art already
  shows accuracy falls as tools are added to the prompt (BFCL; "Tool-Overuse
  Illusion", 2604.19749), so this is expected — but it changes what the ITT
  claim *means*: the effect decomposes into an availability effect (tool
  scaffolding in the system prompt) and a use effect. G1: the tool definitions
  are inside the treatment. This must be pre-registered as secondary before
  outcomes exist; see §9 DO NEXT.
- **P4 [HYPOTHESIS] Thinking effort is an unrecorded environment state that
  loads on one arm.** Fable 5.1 thinking is always on and effort is inherited
  by subagents; the retrieval arm processes more input and thinks more.
  Prediction: retrieval-arm trials show higher output-token counts, and any
  per-turn budget truncation produces case-B voids concentrated in the
  retrieval arm. G4. `effort_level` is not in `freeze_record.json` today; it
  should be recorded (bookkeeping, not a design change).
- **P5 [HYPOTHESIS] "Committed but not live" recurs.** Agents, skills, hooks,
  MCP servers and CLAUDE.md are session-start state. The agent-registry
  failure on 2026-09-01 [MEASURED] is one instance. Prediction: at least one
  further mismatch between repository configuration and the session's loaded
  configuration will be discovered before the program ends, unless the freeze
  record captures the *live* agent list rather than the repo's file list. G4.
- **P6 [HYPOTHESIS] A "harmless" grader edit will flip a verdict silently.**
  The grader is fingerprinted but has no behavioural golden corpus. Prediction:
  the next grader change that passes all current tests changes ≥1 verdict on a
  realistic answer string. G3/G6. Fix: a committed corpus of synthetic answer
  strings with expected verdicts, run by the suite. (Non-production; does not
  touch the frozen grader.)
- **P7 [HYPOTHESIS, zero dispatches] Narrative-over-ledger recurs at session
  boundaries.** Both G7 instances happened where a summary replaced an
  artifact. Prediction: auditing this repository's own session handoffs
  (STATUS/NEXT claims vs. commits) will find at least one more claim of
  completed work with no corresponding artifact. Test: grep completion claims
  in STATUS history against `git log` for the named artifacts.

---

## 2. The strongest unifying theory

### 2.1 What must be explained

Model error, retrieval error, evaluator error, environment error, self-model
error, correlated-critic error, objective error, human-oversight error.

### 2.2 The compression

Every one of these is a **claim whose evidence-generating process (EGP) is
different**:

| Error class | The claim | Its EGP |
|---|---|---|
| model | "the answer is X" | the forward pass |
| retrieval | "source S says X" | search/fetch under environment E |
| evaluator | "answer A is correct" | judge/grader/test oracle |
| environment | "tool T can do O here" | the harness at time t |
| self-model | "I tend to fail on family F" | introspection, or telemetry |
| correlated critics | "A is wrong" ×3 | three EGPs sharing an ancestor |
| objective | "X is the goal" | the reward/instruction channel |
| human oversight | "this design is sound" | a person reading prose |

Correction is therefore not "more inference inside the EGP" (more thinking,
self-review, longer context) but **intervention on the EGP**: re-ask with the
tool removed, re-ask a different model family, re-fetch from an independent
origin, execute instead of judge, draw the DAG instead of reading the prose.

### 2.3 Competing architectures, compared

| Architecture | What it is under the compression | Insufficient alone because |
|---|---|---|
| A. controller/router | the policy that consumes ledger state | it has nothing to read without typed claims and EGP lineage |
| B. claim/evidence ledger | the claim store with EGP lineage | passive; it records but never perturbs |
| C. predictive self-model | claims whose object is the agent | same store, one object type; not a module |
| D. multi-agent critics | EGP diversity | valuable exactly to the extent the EGPs are causally distinct, which must be measured, not assumed (CAPA, Goel et al. ICML 2025) |
| E. feedback network | the loop | says nothing about *which* EGP to perturb |
| F. active hypothesis manager | perturbation targeted at hypotheses | targets the wrong object: the discriminating move is usually to perturb the *process*, not to add a hypothesis |
| **G. typed claims + EGP lineage + EGP-perturbation controller** | B + F re-aimed at processes, with A as output | — |

**Minimum viable hybrid: G.** Components, each with the required properties:

1. **Typed claim record** — function: bind proposition to object type (world /
   self / env / objective / evaluator) and EGP lineage. Failure addressed: G3,
   G6 (no binding). Observable state: the record. Prediction: systems with
   typed claims detect the "retrieved but unreachable" vs "false" confusion
   that prose-context agents miss (H-META-2). Ablation: same evidence, prose
   only (= C1). Why simpler is insufficient: prose cannot be queried for lineage.
2. **EGP lineage** — function: record which process produced a claim and what
   it shares with other claims' processes. Failure: G2. Observable: ancestry
   graph. Prediction: support computed over lineage-distinct EGPs predicts
   correctness better than raw count. Ablation: count-based support.
3. **Perturbation controller** — function: spend a fixed budget perturbing the
   EGP of the load-bearing claim with the highest expected effect. Failure: G1,
   G4, G5 (unmeasured assumptions). Observable: perturbation log. Prediction:
   §2.4. Ablation: same budget spent deepening inference within the same EGP.

### 2.4 The theory's central testable prediction

> **The error-correction ceiling of a system is set by the number of causally
> distinct EGPs it can reach, not by the compute it can spend within one.**

At matched cost, on the set of Stage 0A-M errors once they exist, compare:
{2× thinking effort; self-review; same-model resample; different-family
re-answer; tool-removed re-answer; independent-origin re-fetch}. The theory
predicts the first three catch strictly fewer of the retrieval-induced errors
than the last three, and that the advantage scales with CAPA distance between
the EGPs. This is REC-003 ("what signal escapes the shared basin") made precise
and cheap: ~65 items × 6 arms at low effort, after Stage 0A-M.

**Nearest prior art:** ensembling/diversity; self-consistency vs cross-model;
Goel et al. 2025. **Classification: EXTENSION** — the matched-cost EGP ladder
with the ceiling claim is a sharper statement, not a new phenomenon.

---

## 3. Mechanism discovery on what we have actually observed

Format: OBSERVATION → candidate → competitor → discriminating experiment.

**M1. f07 (false premise) and f15 (contested quantity): 1.00 closed → 0.00–0.40
with search [MEASURED, exp002].**
- Candidate: *source-salience dominance* — retrieved text overrides a correct
  parametric premise check because it is more salient than the model's own
  doubt.
- Competitor: *attentional displacement* — the act of searching consumes the
  step in which the premise would have been inspected; content is irrelevant.
- Discriminator: retrieval arm whose results are forced irrelevant (neutral
  decoy query, or results filtered to unrelated pages). Salience predicts harm
  vanishes; displacement predicts harm persists. Add a fixed-query
  relevant-results arm to separate query-construction failure (already the
  planned Stage 0B alternative). ~15 items × 3 arms = 45 calls. P3
  (availability-without-use) is the zero-cost first cut: if harm appears with
  NOT_ATTEMPTED, displacement by scaffolding is already sufficient.

**M2. Solver self-report undercounts tool calls 2×, one-directionally
[MEASURED, exp002 A.5].**
- Candidate: *reconstructive report* — no introspective access to the count;
  the model reconstructs from salient (successful) calls.
- Competitor: *motivated report* — the budget instruction pressures reports to
  ≤ budget.
- ~~**Already discriminated:** `verified_flat` removed the budget line and the
  undercount persisted at 2.06× [MEASURED]. Motivated report is disfavoured.~~
  **CORRECTION 2026-09-02:** false premise. `verified_flat` packets carry
  `SEARCH BUDGET: 3 searches`; the manipulation raised the ceiling 2→3 and
  reworded it. Every search condition had a visible budget cue, and the
  self-reported count never exceeded it. The data do **not** disfavour a
  ceiling-anchored account. See `docs/results/CAUSAL_INTROSPECTION_M2.md`.
  This sentence was an unverified recollection that passed into two memos —
  a G7 instance inside the memo that named G7.
  Next discriminator: report-after-each-call vs report-at-end; reconstruction
  predicts the per-call log is accurate and the end-of-task total is not.
  This is the cheapest causal-introspection result the program owns and should
  be written up as such.

**M3. exp003c p01: verbose restatement of the weak component → PARTIAL
becomes FAIL [MEASURED, n=1, σ_judge=0].**
- Candidate: *evaluator lexical salience* — repeating the inadequate element
  makes its inadequacy salient.
- Competitor: *length prior* — verbose is penalised regardless of content.
- Discriminator: verbose variant that repeats the *strong* component instead.
  Salience predicts no drop; length prior predicts a drop. 12 judge calls.

**M4. Closed answers longer than search answers (413 vs 267) [MEASURED].**
- Candidate: *uncertainty-induced elaboration* — no evidence → hedging prose.
- Competitor: *copy brevity* — retrieval yields a quotable number and the
  model stops.
- Discriminator: closed-arm length on arithmetic controls (high certainty) vs
  anchored items. Elaboration predicts length tracks uncertainty; copy brevity
  predicts closed length is flat and only the search arm shortens. Free from
  Stage 0A-M telemetry.

**M5. CEILING screen destroyed reversal items (0/12) [MEASURED].**
Not a cognitive mechanism — a collider. Closed-correct is the precondition for
harm, so screening on baseline difficulty screens on the precondition. Already
fixed by treatment-blind authoring; recorded here because it is the cleanest
in-project instance of G5 and should be the worked example in any future
design checklist.

**M6. Judge σ = 0 across 96 calls [MEASURED, exp003c].** A deterministic judge
is not a reliable judge; it is a *repeatable* one. Gauge-R&R language:
repeatability ≈ perfect, reproducibility across judge families unknown [OPEN].
"Hidden Measurement Error in LLM Pipelines" (2604.11581) and ReasonBENCH
(2512.07795) already frame this; the program should adopt their vocabulary
rather than reinvent it.

---

## 4. Prior-art / novelty audit of the current maps

| Idea in our maps | Nearest work | Class |
|---|---|---|
| Epistemic ledger (claims + provenance + valid time) | TMS/ATMS, AGM, Graphiti/Zep, claim-verification graphs | KNOWN |
| Environment-state representation (H-EPI-12) | agent tool-state tracking; nothing separates it from world claims as a first-class type | EXTENSION |
| Evidence-lineage independence (H-EPI-7/13, H-META-1) | provenance, citation laundering, poisoned-RAG cascades | COMBINATION |
| Model-break / assumption-violation detection (H-ANOM) | OOD detection, model misspecification | EXTENSION |
| Performative self-model disclosure (SELF-011) | performative prediction (Perdomo 2020); SMARTCAL feeds a model its own calibration (2412.12151) | EXTENSION — the *disclosure-conditioned* design is not found, but calibration-feedback prompting is |
| Causal introspection under hidden manipulation (H-INTROSPECT-1) | Lindsey 2026 concept injection (2601.01828); "Self-explanations fail semantic invariance" (2603.01254); "A positive case for faithfulness" (2602.02639) | EXTENSION — procedure-choice attribution under hidden routing is a new setting, not a new question |
| Critic diversity vs count (H-CORR-1) | Goel et al. 2025 CAPA; "Judging with Many Minds" (2505.19477) | KNOWN |
| Controlled Goodhart proxy (H-GOODHART) | "Spontaneous reward hacking in iterative self-refinement" (2407.04549); "Reward hacking as equilibrium under finite evaluation" (2603.28063) | KNOWN |
| Champion/candidate recursive procedure search | EvolveMem; "Recursive self-improvement… autonomous research loops" (2607.07663) | KNOWN |
| Human↔AI reciprocal correction | human–AI complementarity literature | EXTENSION |
| Stage 0A-M itself: objective anchored-stem assay with pointwise-null paired inference over a measured tool surface | knowledge-conflict literature (2606.20245, 2508.15253, 2509.06472) has the phenomenon | COMBINATION — the methodological framing (ITT over measured E, pointwise null, arm symmetry by construction) is the contribution, not the phenomenon |
| 3D spatial memory (TOPO-002) | none needed | ILL-POSED — no mechanism by which literal dimensionality adds information over a graph |
| Self-node inside world topology (TOPO-006) | — | ILL-POSED as stated; it is a ledger object type, not a topology question |
| Hidden-substrate inference (H-META-3) | identifiability theory | ILL-POSED as stated — underdetermined by construction; reformulate as an identifiability analysis of specific substrate properties |
| Static identity vs none (SELF-001) | ID-RAG | KNOWN, and persona rather than capability — kill |

Two ideas I tried to call novel and could not:

- *Time-split retro-prediction as a novelty engine metric* → **KNOWN.**
  HindSight (2603.15164) scores generated ideas against future publications;
  MOOSE-Chem (ICLR 2025) rediscovers post-cutoff hypotheses.
- *Gauge R&R for evaluation harnesses* → **EXTENSION.** 2604.11581 and
  2512.07795 already decompose evaluation variance; what is missing is applying
  it *pre-freeze* to a harness rather than post-hoc to a benchmark.

---

## 5. New directions — generated by method, not brainstorm

### A. Contradiction mining

- **ITT vs mechanism.** §6 wants the intent-to-treat effect of *enabling*
  retrieval; §1.2 wants to license "retrieval displaced the anchored answer."
  Under P3 these come apart: an availability effect with no use is an ITT harm
  that is not displacement *by retrieved content*. Experiment: the
  three-arm decomposition {closed; tools defined but stubbed to always fail;
  tools live}. The stub arm is instruction-identical and content-free.
- **Symmetry vs treatment.** The remediation makes agent bodies identical, but
  tool definitions are unavoidably asymmetric and are themselves instructions.
  Contradiction: "only retrieval differs" cannot be true at the system-prompt
  level. Resolution is to *measure* the scaffold effect (stub arm), not to
  assert it away.
- **Fresh context vs prompt cache.** Fresh context per trial and shared cached
  prefix are both true; the cache is a shared latent the design does not name.
  Experiment: P2's block-wise discordance check.

### B. Inversion

- Retrieval "hurts" ↔ *closed-book is lucky*: on anchored items the closed
  model may be correct by defaulting to the most-trained state, which happens
  to be the anchored one. Inversion predicts harm concentrates on items whose
  anchored state is the training-frequent state. Test: split Stage 0A-M items
  by whether the anchored value is the pre-2024 default; harm should be
  higher there under inversion, flat under genuine displacement.
- Judge "biased against verbosity" ↔ verbosity *reveals* weakness (M3). The
  strong-component repetition arm separates them.
- Self-report "unreliable" ↔ the harness *over-counts* (retries, parallel
  calls). Test: reconcile observed call log against API request IDs.

### C. Missing state

The variable that would most simplify our observations is **per-trial
retrieval-content relevance** — whether what came back bore on the anchored
constraint. Without it, M1's two mechanisms are indistinguishable in the
primary data. It is cheap to log (the search results are in the transcript)
and should be extracted post hoc by a deterministic rule (does any result
mention the anchor date/definition?), never by a judge.

### D. Cross-domain imports, translated to mechanisms

- **Metrology → blind spikes.** Insert known-answer items with known-wrong
  distractors into judge/critic queues at a fixed rate to measure the
  instrument continuously. Executable: a `spike` dispatch class whose results
  never enter analysis. Distinct from calibration-before-run (exp003c) because
  it measures drift *during* the run.
- **Software engineering → fault seeding for reviewers.** Inject k defects of
  known G-class into a copy of a frozen artifact; have heterogeneous reviewers
  review blind; the detection matrix gives ground-truth critic correlation.
  This is §7's experiment.
- **Fault-tolerant computing → N-version with *forced* design diversity.**
  Independence is engineered by giving versions different specifications of
  the same function. Translation: critics that receive the *claim in different
  representations* (prose / DAG / table) rather than the same prose — testable
  as a diversity lever in §7.
- **Epidemiology → the study DAG.** Draw the experiment's own DAG with
  treatment, instrument, environment and shared-latent nodes, and require an
  executed invariance check per assumed-absent edge before freeze. This is §5E.
- **Immune systems → negative selection.** Train the anomaly detector on
  *self* (the dominant pattern) and flag anything non-self, rather than
  modelling the anomaly. Translation for H-ANOM: an assumption ledger checked
  by generated *violating* cases, not by uncertainty within the model.

### E. Adversarial route to the same objective

Assume the ledger/self-model/critic architecture is misguided. The alternative:
**no persistent state at all; every claim is re-derived from scratch by a
process chosen to be causally distinct from the one that produced it, and the
only memory is the log of which EGP pairs disagreed.** Correction becomes a
property of the *sampling policy over EGPs*, not of stored beliefs. Compared
with ours: it cannot fossilise hallucinations (no store), cannot launder
provenance (no aggregation), and is trivially auditable; it is expensive and
cannot exploit dependency structure. The honest comparison is C1-style: same
budget, ledger vs EGP-resampling, on tasks where stale-claim persistence is the
failure. If EGP-resampling matches the ledger, the ledger is not earning its
complexity. This is a real risk to the program and should be a control arm in
C1, not a footnote.

---

## 6. NOVELTY-ENGINE-001 — a procedure, and why ordinary generation fails

### 6.1 Why ordinary LLM novelty generation fails (with which failure we have evidence for)

- interpolation of familiar concepts and *semantic* recombination read as
  novelty — [SUPPORTED] by "LLMs can realize combinatorial creativity"
  (2412.14141) and by every "potentially novel" item in §4 that died on search;
- ignorance of prior art masquerading as invention — [MEASURED] in this memo:
  two of my own candidates were known;
- the novelty judge cannot tell rediscovery from invention — [SUPPORTED] by
  "On the limits of LLM-as-judge for scientific novelty" (2606.12071) and the
  axiomatic novelty-metric benchmark (2604.15145);
- creativity and verification in one pass, so plausibility bias kills the
  low-probability region before it is explored;
- novelty judged on prose surface rather than on *what the idea predicts*.

### 6.2 The procedure: Residual-Constrained Invention with Rediscovery Calibration

What is different from the map's existing thinking: invention is forced to
explain a *specific unexplained observation*; the novelty judge is *calibrated
with decoys* rather than trusted; ideas are structured records that must carry
a discriminating prediction; and stages are information-isolated.

**Stage 0 — Residual extraction (deterministic where possible; no LLM
invention).** From the project's own data, list observations no current
candidate mechanism predicts (e.g. f07's judge-score trajectory; the
one-directional self-report undercount surviving budget removal). Each residual
is a record: {observation, every existing candidate mechanism, what each
predicts, the mismatch}.

**Stage 1 — Blind invention (model A; no retrieval; sees residual records
only).** For each residual, generate mechanisms as structured records — INPUT /
STATE / TRANSFORMATION / FEEDBACK / MEMORY / OBJECTIVE / OBSERVATION / FAILURE
SIGNAL — and *require* a discriminating prediction against the nearest existing
mechanism in the record. Diversity is forced by an assumption-relaxation
lattice: each candidate must name the standard assumption it drops. Prose is
not accepted.

**Stage 2 — Decoy injection (deterministic).** Mix candidates with (a)
structured paraphrases of *pre-cutoff* known mechanisms and (b) structured
paraphrases of *post-cutoff* published mechanisms unseen by A. Labels are held
out.

**Stage 3 — Prior-art attack (model B, different family, retrieval on, blind
to labels).** For every record: nearest work, overlap score, and whether the
cited work contains the *mechanism* (not the vocabulary).

**Stage 4 — Calibrated scoring.** B is scored on decoys first: pre-cutoff
decoys must come back KNOWN; post-cutoff decoys must come back NOVEL-relative-
to-pre-cutoff. That yields B's miss rate and its hallucinated-novelty rate.
Candidate novelty = B's overlap score corrected by that calibration. Usefulness
= presence and cost of the discriminating prediction (deterministic check),
with judge preference secondary only. Hallucinated novelty is flagged when B
rates a candidate novel whose mechanism sits in a pre-cutoff decoy's
neighbourhood.

**Stage 5 — Repair (model C).** Survivors only, into experiment tables.

**Retrieval** occurs only in Stage 3. **Anchoring** is controlled by A never
seeing literature and B never seeing labels. **Diversity** is maintained by the
lattice and by rejecting candidates whose predictions coincide. **Stopping:**
marginal survivors per residual below a set rate, or budget. **Cost:** A at
high effort on few residuals; B at low effort per record; C only on survivors.

**Honest classification:** COMBINATION. Residual-driven invention is
abductive method; decoy calibration is metrology's blind spike; time-split
convergence is HindSight/MOOSE-Chem. The assembly — decoy-calibrated novelty
judging of *structured* ideas that must carry a discriminating prediction — I
could not find; it is not a new principle.

### 6.3 NOVELTY-ENGINE-002 — does it actually improve anything?

- **Problems:** 30 — 10 residuals from this project, 20 external drawn from a
  time-split corpus so that post-cutoff answers exist.
- **Conditions:** A frontier model prompted normally; B prompted for
  creativity; C the procedure; D1 no decoys; D2 prose instead of structured
  records; D3 retrieval before invention; D4 same family for A and B.
- **Blind metrics, in priority order:** (1) decoy-calibrated novelty; (2)
  number of discriminating predictions absent from all competing ideas
  (deterministic count); (3) time-split convergence — fraction of ideas whose
  mechanism appears in a post-cutoff paper (a *validity* check, not novelty);
  (4) nearest-paper embedding distance; (5) judge preference, secondary.
- **Evaluator Goodhart, addressed:** decoy sets are held out and refreshed per
  run; B's family ≠ A's family; structured records remove prose-surface
  novelty; convergence penalises bizarre-but-useless ideas because they
  converge with nothing; metric (2) is deterministic.
- **What would kill the procedure:** C fails to beat B on (1) and (2) jointly,
  or D1 (no decoys) matches C — which would mean the calibration is doing
  nothing and the gains are from structure alone.

---

## 7. Recursive improvement of the generator, with controls

Loop: P₀ → ideas → external evaluation → failure analysis → mutation P₁ →
compare P₁ vs P₀ on *held-out* problems → retain only demonstrated gains.

Dangers and the control for each:

| Danger | Control |
|---|---|
| optimising to the novelty evaluator | decoy refresh every generation; evaluator family rotated; metric (2) deterministic |
| bizarre but useless | joint criterion: novelty **and** time-split convergence must both improve |
| evaluator–generator collusion | measure CAPA between generator family and judge family on the decoy set; reject any generation where it rises |
| benchmark overfitting | problems are time-split; the held-out set is post-dated to the generation |
| semantic novelty without mechanistic novelty | ideas are structured records; overlap is computed on mechanism slots |
| recursive complexity growth | description-length penalty on P; a mutation must beat P₀ *and* a simpler ablation of itself |
| human oversight erosion | fixed-rate human spot-audit of survivors, sampled blind |

This is the same EGP-perturbation logic as §2: the generator is a process, and
its improvement is only trusted when measured by a causally distinct process.

---

## 8. Our development process as data

### 8.1 Schema

`review_event_id, model, model_family, artifact, artifact_commit, defect_proposed,
G_class (G1–G7), eventually_validated, severity, bias_direction (toward /
against hypothesis / neutral), previously_detected_by, external_verifier
(proof / source / test / execution / none), cost_usd, tokens, minutes,
repair_accepted, new_defect_introduced_by_repair`.

This memo's own findings are the first rows: numeric-reject precedence
(toward-hypothesis, external verifier = test), agent asymmetry (toward, none),
b03 tolerance (neutral, test), NOAA self-inconsistency (neutral, source).

### 8.2 The experiment

Seeded-defect heterogeneous review. Take five frozen artifacts; inject four
defects each, one per G-class, chosen so that a deterministic check exists for
each; reviewers = {same model repeated, same family, cross family, human,
deterministic suite}, blind, one artifact per call. Outputs: the detection
matrix; CAPA over reviewers on the *known* defects (this removes the usual
problem that critic correlation is measured on disputed items); the
repair-introduces-defect rate. Prediction under §2: cross-family detection
overlap is below same-family overlap but well above zero, and the deterministic
suite catches G3/G6 that no model reviewer catches. ~100 low-effort calls;
after Stage 0.

---

## 9. Ranked portfolio

Scoring is qualitative: importance / P(current view wrong) / info gain /
difficulty / calls / contamination risk / depends on Stage 0 / novelty
confidence.

### DO NEXT (≤3)

1. **Execute Stage 0A-M as frozen**, with three zero-design-change additions
   to the freeze record before the first dispatch: `effort_level`; the *live*
   agent list from the session; and a committed golden verdict corpus for the
   grader (synthetic strings, expected verdicts). High / n.a. / high / trivial
   / 130 / none / — . Decision changed: none — it is the gate everything
   else waits on.
2. **Pre-register the Stage 0A-M secondary analyses now, before outcomes:**
   P3 availability-without-use; P4 thinking-token asymmetry by arm; M4 closed
   length vs certainty; P2 block-wise discordance; per-trial deterministic
   retrieval-relevance flag (§5C). High / 0.5 / high / low / 0 / none /
   yes. Decision changed: whether the ITT claim is scoped as displacement or
   as scaffold effect.
3. **Zero-dispatch re-analyses of frozen data:** P1 judge-route × treatment
   interaction on exp001/002; P7 narrative-vs-artifact audit across session
   boundaries; M2 write-up as the program's first causal-introspection result.
   Medium / 0.6 / medium / low / 0 / none / no. Decision changed: whether any
   exp001/002 judged contrast may be cited at all.

### DO AFTER STAGE 0 (≤5)

4. **EGP-perturbation ladder at matched cost** on the Stage 0A-M error set
   (§2.4). Tests the unifying theory directly. ~400 low-effort calls.
5. **Displacement-mechanism discriminator** (M1): stub-tool, irrelevant-results,
   fixed-query arms; folds into Stage 0B. ~150 calls.
6. **Seeded-defect heterogeneous review** (§8.2). ~100 calls. Feeds
   critic-independence and the process dataset.
7. **Harness-DAG with executed edge checks** as a standing preflight
   procedure; evaluated by whether it finds anything independent review
   missed on the *next* design (Stage 0B). 0 solver calls.
8. **NOVELTY-ENGINE-002 pilot** at 10 problems. ~300 calls.

### KEEP IN RESERVE

C1 equal-evidence ledger **with the EGP-resampling control arm (§5E)**; C7
environment-state ledger; SELF-011 disclosure; D1 coding execution baseline;
H-META-1 corrupted-origin worlds; blind-spike judge monitoring.

### KILL / MERGE

- **Kill:** TOPO-002 (3D); SELF-001 (persona, not capability); H-META-3 as
  posed; SELF-009/F-branch subjectivity until an objective outcome exists.
- **Merge:** TOPO-006 → ledger object type; H-EPI-1…5 → C1 + C4 (five
  hypotheses, one experiment); H-EPI-9 ↔ TOPO-005 (same question); TOPO-003/007
  learned topology → memory-benchmark reserve; SELF-006 ↔ E5 (duplicate);
  H-CORR-1 ↔ REC-001 (same ladder, different names).
- **Reformulate:** the "six states" from six components to five claim object
  types plus lineage (§2).

---

## 10. Architecture change

**Specific:** stop treating world / self / environment / objective / evaluator
/ lineage as six modules. They are **object types of one claim record** whose
distinguishing field is the EGP. Add one operation — EGP perturbation — as the
only sanctioned form of error correction, and require every proposed component
to state which EGP it perturbs. This deletes complexity rather than adding it.

---

## 11. Confidence

**High:** the G1–G7 taxonomy fits every logged failure; exp003a never ran;
M2's motivated-report competitor is disfavoured by exp002's own data; three of
my candidate novelties are known (HindSight, tool-overuse, measurement error).

**Medium:** the two-root compression (R1/R2); the EGP theory as a useful
organiser; P1, P3, P4, P6 as predictions; NOVELTY-ENGINE-001 as a combination
that is not in the literature in assembled form.

**Speculative:** the ceiling claim in §2.4 as stated; §5E's EGP-resampling
matching a ledger; that seeded-defect CAPA transfers to unseeded defects.

---

## 12. Open

- [OPEN] Whether the retrieval arm's effect under E = search-only generalises
  to any fetch-capable environment; Stage 0A-M cannot say.
- [OPEN] Subagent served model is inherited, not observed; a per-trial
  served-model log is required before P2 can be evaluated.
- [OPEN] Whether the session's now-registered dedicated agents match the
  committed files byte-for-byte at runtime (the live registry reports the
  description text; the body is not exposed).
- [OPEN] Cost telemetry: `get_session` usage did not update across four calls
  in one session; the per-turn cost model in `cost_ledger.md` is unverified.
- [OPEN] Whether any G-class instance exists in exp001/002 not yet catalogued;
  P7's audit would surface it.

---

## Cost of this memo

Model-based (telemetry stale): ≈ $3.5–4.5 of the ≈ $10 budget — dominated by
cache reads over a ~330K-token context and ~25K tokens of document ingestion;
ten web searches; one document written. No solver dispatches.
