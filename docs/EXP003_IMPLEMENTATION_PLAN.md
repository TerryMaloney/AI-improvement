# exp003 implementation plan (revision 2)

Supersedes the build order in `docs/EXP003_DESIGN_MEMO.md` §18. The memo's
diagnosis, red team and prior-art boundary stand unchanged and are not repeated
here. This document records what was **decided** after operator review, what
that changes in the build, and the order things happen in.

**Frozen:** `runs/exp001pilot/`, `runs/exp002/`, `batteries/answers.v1.frozen.yaml`,
and both experiments' stored results. Nothing in this plan reads-modify-writes
them. `factual_v1` is retained unedited as a regression battery.

**Objective, stated once:**

> Establish a clean causal baseline for whether the proposed epistemic control
> mechanisms do anything beyond prompt length, format, stochasticity, retrieval
> quality, and judge artifacts.

Failing to establish that is a result, not a failure.

---

## 1. Decisions taken at operator review

| # | Decision | Effect on the build |
|---|---|---|
| D1 | **Keep `A_only` in Stage 1.** | A composite directive can contain opposing components. Without `A_only`, a null on the full directive cannot separate four outcomes: (i) no component works; (ii) one works and another cancels it; (iii) the combination works only through interaction; (iv) the whole thing was placebo/length/format/stochasticity. `A_only` splits (i)/(ii) from (iv) at Stage 1 rather than after a cancelled Stage 2. |
| D2 | **exp003c runs first, alone, zero solver trials.** | Judge calibration is a precondition, not a parallel task. |
| D3 | **Interpretation thresholds pre-specified before exp003c runs.** | Written into `experiments/exp003c_judge_calibration.yaml` and committed before any judge is dispatched. |
| D4 | **If calibration shows a material effect, the evaluation design changes before solver trials.** | Reporting the bias and proceeding unchanged is explicitly forbidden. Mitigations are pre-bound to thresholds (§3.4). |
| D5 | **Deterministic primary outcomes.** | A judge may not determine a primary outcome where an objective grader reasonably can. Judges are confined to secondary/open dimensions. |
| D6 | **Placebo matched on six axes**, not word count alone. | §4. |
| D7 | **Every trial group states the effect size it can detect** before it is spent. | §6. |
| D8 | **Formal preflight after implementation, before solver execution.** | §8. Ten named questions; any issue fixed before solver calls. |
| D9 | **Displacement cell gets four conditions** where feasible. | §5.3, with the retrieval-state honesty rule enforced. |
| D10 | **Prior-art boundary is binding on wording.** | §9. |

---

## 2. Build order

| Step | What | Solver trials | Judge calls | Gate to proceed |
|---|---|---|---|---|
| **0** | This plan, committed | 0 | 0 | — |
| **1** | **exp003c** — judge phrasing/length calibration | **0** | **72** | §3.4 calibration gate |
| 2 | Evaluation-design revision if calibration is AMBER/RED | 0 | 0 | revision committed |
| 3 | Instrument work (§7): telemetry, placebo generator, task labels, retrieval states | 0 | 0 | tests green |
| 4 | `diagnostic_v1` battery + per-item experimental specifications | 0 | 0 | committed before any condition runs |
| 5 | Knowledge probe + ceiling/floor screen; frozen retrieval scout | ~70 | 0 | exclusions reported |
| 6 | **Formal preflight red team** (§8) | 0 | 0 | all ten questions answered, issues fixed |
| 7 | **exp003a** — cells L, R, D, U, N, C | ~390 | ~170 | §14 memo gate |
| 8 | **exp003b** — component ablation | ~250 | ~80 | only if gate passes |

**This turn delivers steps 0 and 1 only.** Steps 2–8 do not begin until the
calibration gate is evaluated.

---

## 3. exp003c — judge phrasing and length calibration

### 3.1 What it is for

Not to prove anything about the framework. To decide **whether the judge's
sensitivity to length and format is large enough to contaminate the judged
dimensions of exp003a/b**, and if so, to force a design change before solver
calls are spent.

This is instrument calibration against a **KNOWN** prior-art phenomenon (§9). It
is an obligation the lab skipped in exp001 and exp002, not a discovery.

### 3.2 Design

**Absolute single-answer scoring, not pairwise.** exp003a/b grade one answer at a
time against a rubric, using `lab.grading.JUDGE_TEMPLATE`. exp003c calibrates
*that* protocol with *that* template. Pairwise comparison would measure a
different instrument and would import position bias we do not otherwise have.

Each judge dispatch sees **one** answer, blind: no condition, no variant label,
no sibling variants, no indication that a comparison exists. "Winner" is computed
afterwards from scores; no judge is ever asked to pick one.

**6 stimulus items × 4 variants × 3 independent judges = 72 dispatches.**

| Item | Content correctness | Variant axis | Families covered |
|---|---|---|---|
| c01 | **correct** | 2×2: {concise, verbose} × {prose, directive-style} | A, C, E |
| c02 | **correct** (contested quantity) | 2×2: {concise, verbose} × {prose, directive-style} | A, C, E |
| c03 | **incorrect** (wrong value) | 2×2: {concise, verbose} × {prose, directive-style} | B, C, E |
| c04 | **incorrect** (accepts false premise) | 2×2: {concise, verbose} × {prose, directive-style} | B, C, E |
| c05 | **correct** | 4 terminology/notation-equivalent wordings | D |
| c06 | **correct** (uncertainty item) | 4 hedge-vocabulary-equivalent wordings | D |

Content is held **strictly** constant within an item. The verbose variant is the
concise variant plus text that introduces no new fact, number, hedge, source, or
epistemic move — elaboration and restatement only. The directive-style variant
reorganises the same sentences into labelled sections and bullets without adding
information. Both invariants are enforced by test (§3.5), not by inspection.

**Why the within-item contrast is immune to answer-key error.** All four variants
of an item carry identical content, so any error in that item's rubric or ground
truth applies equally to all four and cancels in the within-item difference. The
calibration does not depend on my having written correct rubrics — only on my
having written *consistent* ones. This is what makes exp003c trustworthy even
though its stimuli are authored rather than sampled.

### 3.3 Recorded per judgement

| Field | Source |
|---|---|
| `score`, `verdict`, `criteria`, `reasoning` | judge output |
| `answer_len_chars`, `answer_len_words` | computed from the stimulus |
| `formatting_features` | computed: bullet count, header count, line count, section labels |
| `variant`, `item`, `content_correct`, `axis` | stimulus metadata (never shown to the judge) |
| `judge_model` | `sonnet`, recorded per dispatch |
| `judge_saw_reasoning` | **`false` for every dispatch.** Our protocol never shows the judge a reasoning trace. The with/without-reasoning contrast is exp004's verifier question, not this one. Recorded as a constant so the scope is explicit rather than assumed. |
| `judge_tokens`, `judge_latency_ms` | harness dispatch telemetry |
| `replicate` | 1–3 |

Derived: within-variant spread (judge self-consistency), within-item variant
range, `winner` per item.

### 3.4 Pre-specified interpretation — written before any dispatch

Let, with content held constant and averaged over items:

- **Δ_length** = mean(score | verbose) − mean(score | concise)
- **Δ_format** = mean(score | directive-style) − mean(score | prose)
- **Range_term** = within-item (max − min) of variant means, on c05/c06
- **σ_judge** = mean within-variant spread across the 3 replicates

Thresholds, and the mitigation each one **binds** us to:

| Band | Criterion | Consequence — mandatory, not discretionary |
|---|---|---|
| **GREEN** | \|Δ\| < 0.05 on every axis, and Range_term < 0.10 | Judged dimensions usable as designed. Length still recorded and reported as a standing diagnostic. |
| **AMBER** | 0.05 ≤ \|Δ\| < 0.15 on any axis, or 0.10 ≤ Range_term < 0.20 | **Design change required before solver trials.** (a) Every judged contrast is reported with a length covariate; (b) any judged contrast smaller than **2×\|Δ\|** is declared *not established* by rule; (c) cell U's primary outcome converts from a continuous quality score to a forced categorical `response_mode` code with anchor examples. |
| **RED** | \|Δ\| ≥ 0.15 on any axis, or Range_term ≥ 0.20 | **Absolute continuous scoring is disqualified for exp003.** All judged dimensions convert to forced categorical codes with anchors; exp003c is re-run on the categorical protocol before any solver trial; if the categorical protocol is also RED, judged dimensions are dropped from exp003 entirely and only deterministic cells run. |

Two additional pre-specified checks:

- **Verbosity-rescues-errors.** If Δ_length computed on the *incorrect*-content
  items (c03, c04) is ≥ 0.15 while on the *correct*-content items it is < 0.05,
  that is treated as RED regardless of the pooled Δ_length. A judge that awards
  partial credit for elaborating a wrong answer is the specific failure that
  would most damage exp003a's judged cells.
- **Judge noise floor.** If σ_judge ≥ the mean within-item variant range, the
  judge cannot resolve the effect it is being asked about; K rises from 1 to 3
  for all judged trials in exp003a and the K=1-with-audit-sample rule in the
  memo §15 is withdrawn.

**Direction is reported and interpreted, not just magnitude.** If verbose scores
higher, the directive — which lengthens answers — received a free boost in
exp001/exp002, and those directive contrasts were inflated. If concise scores
higher, they were deflated. Either way the sign tells us which way the two
frozen experiments were biased, and that statement goes in the report.

### 3.5 Content-invariance enforcement

`tests/test_judge_calibration_stimuli.py` asserts, for every 2×2 item:

1. every number appearing in the verbose variant also appears in the concise
   variant, and vice versa (no new quantities);
2. no hedge term (`lab.grading._HEDGE_RE`) appears in one variant of a
   length pair and not the other;
3. no premise-flagging term (`_PREMISE_RE`) differs across a length pair;
4. the verbose variant is ≥ 1.6× the concise variant in words (the manipulation
   is actually present);
5. the directive-style variant contains ≥ 2 structural markers (bullets or
   labelled sections) and the prose variant contains none;
6. for c05/c06, all four variants share the same hedge-presence and
   number-set signature.

A stimulus set that fails any of these is a broken instrument, and the test
fails the build rather than the run producing a number nobody can trust.

---

## 4. Placebo specification (strengthened, per D6)

The placebo must be matched to the real directive on six axes and must not be
recognisably silly, because a placebo the model can identify as filler is not a
placebo.

| Axis | Match rule | Enforcement |
|---|---|---|
| Word count | within ±10% of the routed directive for that question | test |
| Instruction count | same number of imperative bullets | test (bullet count) |
| Structural complexity | same section headers, same nesting depth | test |
| Formatting | same markers (dashes, capitals, colons) | test |
| Expected response effort | asks for comparable elaboration — background, completeness, structure | review |
| Perceived seriousness | same register: direct, technical, non-jocular | review |

And it must contain **none** of the epistemic mechanism: no claim-type names, no
`premise`, `source`, `verify`, `fresh`, `stale`, `conflict`, `budget`,
`independent`, `evidence`, `abstain`, `calibrat*`. Enforced by keyword test.

The placebo is generated per question by a committed function so that its length
tracks the routed directive's length question by question, rather than being one
fixed block that matches on average and mismatches everywhere.

**Key comparison, in order:** `baseline` → `directive_placebo` → `A_only` →
`directive_only`. The question is whether the epistemic mechanism contributes
beyond generic careful instruction — which is the `A_only` − `placebo` and
`directive_only` − `placebo` contrasts, not the contrasts against `baseline`.

---

## 5. Cells, and what each item must declare

Six diagnostic areas retained. **Every item carries a written experimental
specification, committed before execution**, with these fields:

```yaml
intended_mechanism:      # what this item is here to detect
competing_explanations:  # which of E1-E8 could also produce movement here
predictions:             # per condition, the expected observable
discriminator:           # the observation that separates the explanations
grading:                 # method, and why it is deterministic if it is
exclusion_criteria:      # what pre-run probe result removes this item
```

An item without a discriminator that separates at least two explanations does
not enter the battery, however interesting it is. Battery size is not a goal.

### 5.1 Cell L — latent knowledge (primary, deterministic)
6 items · `baseline`, `directive_placebo`, `A_only`, `directive_only` · k=5 · **120 trials**.
Grading: deterministic name/date matching. No judge touches the primary outcome.

### 5.2 Cell R — reasoning where search is useless (primary, deterministic)
4 items · `baseline`, `directive_placebo`, `directive_only` · k=5 · **60 trials**.
Grading: deterministic numeric, tolerance strictly below the named distractor gap.

### 5.3 Cell D — retrieval displacement (four conditions, per D9)
5 items · k=5 · **175 dispatches** (trial ≠ dispatch here):

| Condition | Dispatches per trial | Retrieval state reached |
|---|---|---|
| `closed_book` | 1 | none |
| `search_only` | 1 | RETRIEVAL |
| `search_selfcheck` | 2 (answer, then self-review of own answer) | RETRIEVAL |
| `search_independent` | 3 (generator ▸ claim-blind evidence gatherer ▸ separate verifier) | RETRIEVAL + CLAIM_EVIDENCE_MATCH |

**Honesty rule, binding:** WebFetch is egress-blocked, so **no condition reaches
`SOURCE_ACCESS` and none reaches `VERIFICATION`**. `search_selfcheck` and
`search_independent` are **snippet-level checking**, and must be named that way
in every result. No negative conclusion about full source verification may be
drawn from this cell. If the pre-run egress probe (§7) shows WebFetch has
unblocked, that is a change of instrument and the cell is re-planned, not
silently upgraded.

Primary outcome: correctness, deterministic where the item permits.
Secondary (judged, categorical): `conflict_action` ∈ {`accepted_retrieval`,
`rejected_retrieval`, `sought_another_source`, `reported_conflict`, `abstained`}.

### 5.4 Cell U — uncertainty / abstention
4 items · 5 conditions · k=3 · **60 trials**. Judged, and therefore
**secondary**: this cell cannot carry a primary conclusion. Its outcome form
depends on the exp003c band (§3.4).

### 5.5 Cell N — unnecessary tool use
4 items · `baseline`, `search_only`, `search_directive` · k=3 · **36 trials**.
Primary metric is observed tool calls. Deterministic by construction — it is a
counter, not a judgement.

### 5.6 Cell C — current-fact tripwire
2 items · `baseline`, `search_only` · k=3 · **12 trials**. If search does not
beat closed-book here, the instrument is broken and nothing else in the run may
be interpreted.

**Totals:** ~390 solver trials / ~463 dispatches, plus ~70 screening. Trim levers
in order: cell D `search_selfcheck` dropped (−50 dispatches), U → k=2 (−20),
R → 3 items (−15). `A_only` and k≥3 are **not** trim levers (D1, §6).

---

## 6. Power — stated per trial group, before spending

| Group | n | What it can detect | What it cannot |
|---|---|---|---|
| Cell L, per item, k=5 × 4 conditions | 6 items | a per-item rate shift of **≥0.4** (e.g. 1/5 → 3/5) at the item level; a consistent direction across ≥3 of 6 items | a uniform 0.1 rate shift; any battery-mean claim |
| Cell R, per item, k=5 × 3 conditions | 4 items | same, ≥0.4 per item | interaction between components |
| Cell D, per item, k=5 × 4 conditions | 5 items | closed-vs-search reversal of ≥0.4 per item; a shift in `conflict_action` distribution of ≥40 points | small differences among the three search variants |
| Cell U, k=3 | 4 items | only a categorical mode change on ≥2 of 4 items | any continuous quality difference under 0.2 |
| Cell N, k=3 | 4 items | a difference of ≥1 observed tool call per item | sub-call differences |
| Cell C, k=3 | 2 items | tripwire only — is search ≫ closed, yes/no | nothing else |

**Restated plainly:** exp003 is powered to detect a mechanism that changes an
individual item's outcome rate by roughly 0.4 or more. It is **not** powered to
detect a uniform few-point battery-wide shift, and the battery mean is not a
primary outcome. If the effect we care about is smaller than that, this design
cannot see it and the design must change before solver calls are spent — that
decision point is here, in this section, not after the results.

---

## 7. Instrument work (step 3, before solver trials)

1. **Telemetry.** Persist per dispatch: `tool_calls_observed` (authoritative
   aggregate), `latency_ms`, `tokens`, `timestamp_utc`, `dispatch_role`
   (solver / judge / scout / verifier). Judge tokens and latency persisted too.
2. **Deprecate self-report.** `searches_used` → `searches_selfreported`,
   retained as a calibration datum only. Any report path that uses it as cost is
   a test failure.
3. **Per-tool split marked NOT MEASURED.** The harness returns an aggregate
   count; the split is not obtainable at this scale. Recorded as unavailable
   with the reason, never estimated.
4. **Evidence ledger.** Per retrieval: query, what returned, whether it addressed
   the specific claim, source kind. Counts stay authoritative from the harness; a
   ledger shorter than the observed count is an audit flag, not a correction.
5. **Retrieval-state machine.** `RETRIEVAL` / `SOURCE_ACCESS` /
   `CLAIM_EVIDENCE_MATCH` / `VERIFICATION` recorded per trial; a lower state may
   never be reported as a higher one.
6. **Task-label axes** (memo §6), six orthogonal dimensions, each with a pre-run
   operational test, kept separate from `claim_type`.
7. **Placebo generator** (§4) plus its tests.
8. **Egress re-probe** committed before cell D is planned.

---

## 8. Formal preflight (step 6 — after implementation, before any solver call)

Ten questions, answered in writing, committed, with fixes applied before spend:

1. What result could fool us?
2. What confound could produce a false positive?
3. What confound could produce a false negative?
4. Could response format be rewarded by the grader?
5. Could prompt length explain the effect?
6. Could stochasticity explain the effect?
7. Could retrieval quality explain the effect?
8. Could judge bias explain the effect?
9. Could the answer key be wrong?
10. Could the task itself fail to discriminate the hypotheses?

Questions 4, 5 and 8 are answered **with exp003c's measured numbers**, not with
reasoning. That is the point of running it first.

---

## 9. Prior-art boundary (binding on wording)

The following are **KNOWN** phenomena this lab is now measuring in its own
instrument. They may not be described as discoveries, findings, or
contributions, in any report, commit message, or summary:

- judge phrasing / length / format sensitivity;
- stochastic evaluation variance and the need for replicates;
- retrieval displacing correct parametric knowledge (context-memory conflict);
- model self-report being an unreliable cost metric.

Correct framing: *"a known effect, measured here at magnitude X in our
instrument, with consequence Y for our design."*

Any contribution must come from something narrower and specific — currently the
best candidates are the **`conflict_action` taxonomy under an explicit budget**
(KNOWN EXTENSION) and **entity-hazard TTL** (UNDEREXPLORED, untouched by any
experiment so far).

---

## 10. What this plan does not do

- No semantic entropy, frontier routing, ARC, SWE-bench, multimodal,
  cross-model, or self-improvement work. Deferred, unchanged.
- No modification of exp001, exp002, or their stored results.
- No solver trial until the exp003c gate is evaluated and any bound mitigation
  is implemented and committed.

---

# 11. AMENDMENT — exp003c result and the design changes it binds

**exp003c is complete: 96 judge dispatches, 0 solver trials. Band = AMBER.**
Full record: `runs/exp003c/EXP003C_REPORT.md`.

Measured: **Δ_length = −0.125** (verbose scores *lower*), driven entirely by one
of four partial-band items which moved PARTIAL→FAIL on identical content;
Δ_format = 0.000; terminology and hedge-vocabulary effects = 0.000;
**σ_judge = 0.0000 across all 96 judgements** — the judge is deterministic on
fixed input, so the movement is systematic, not noise.

Verbosity never rescued a wrong answer (24/24 at 0.00). The dangerous direction
is clean.

## 11.1 Changes now binding on exp003a/b (step 2 of §2, complete)

| # | Change | Where it applies |
|---|---|---|
| **C1** | **Length covariate on every judged contrast.** Answer length is reported beside every judged number, with a score-vs-length relationship per cell. | all judged tables |
| **C2** | **The 2× rule.** Any judged contrast smaller than **0.25** score units is declared NOT ESTABLISHED by rule. | all judged contrasts |
| **C3** | **Cell U converts to a forced categorical code.** Primary outcome is `response_mode` ∈ {assert, qualify, range, flag_conflict, reject_premise, abstain}, with anchor examples in the packet — not a continuous quality score. | §5.4 |
| **C4** | **K=3 for judged trials** (from the round-1 `judge_noise_floor` trigger). | all judged trials |

C1–C3 supersede the corresponding text in §5.4 and §6. They are not optional and
were bound to the AMBER band before the band was known.

## 11.2 An open operator decision, to be settled in exp003a's pre-registration

**C4 (K=3) fired on a degenerate `0.0 >= 0.0` comparison.** It is applied because
pre-registration is binding and more judging is the conservative direction. But
σ_judge = 0.0000 over 96 judgements means replicates added nothing measurable,
and K=3 triples judge cost for no evident information.

Relaxing C4 to K=1-with-audit-sample is defensible **only** as an explicit,
written decision in exp003a's pre-registration, made before exp003a runs. It may
not be relaxed silently, and it may not be relaxed after seeing exp003a results.
Flagged here so the choice is made deliberately rather than by drift.

## 11.3 Consequence for the deterministic-first principle (D5)

exp003c strengthens D5 rather than weakening it. The measured effect appears
**only at a rubric boundary in a judged continuous score**, and is exactly zero
everywhere the outcome is unambiguous. Cells L and R — the two primary cells —
are graded by name and number matching with no judge in the loop, so C1–C4 do
not touch them and the primary result cannot be a length artifact. That was the
design bet, and the calibration vindicates it.

## 11.4 Directional caveat on exp001 and exp002 — neither is rescored

Verbose scored **lower**. The epistemic directive lengthens answers. If the p01
effect generalises, the directive conditions in exp001 and exp002 were
**deflated** by the grader rather than flattered by it, making those contrasts
conservative rather than inflated.

This rests on one item. It is a caveat on how to read two frozen experiments,
not a correction to them. Neither is rescored; both remain frozen.

## 11.5 Where the build now stands

| Step | State |
|---|---|
| 0 plan | done |
| 1 exp003c | **done — AMBER** |
| 2 evaluation-design revision | **done — C1–C4 above** |
| 3 instrument work (§7) | **done — §12** |
| 4 `diagnostic_v1` battery + per-item specs | **done — §13** |
| 5 screens + frozen retrieval scout | **done — §14** |
| 6 formal preflight (§8) | **built and failing closed — §14.4** |
| 7 exp003a | blocked on 6 |

**No solver trial has been run. None may run until steps 3–6 are complete.**
Questions 4, 5 and 8 of the §8 preflight can now be answered with measured
numbers rather than reasoning, which was the point of running exp003c first.

---

## 12. Step 3 — instrument work, as built

Built as an instrumentation task, not an experiment: **zero solver dispatches**,
no battery changes, no condition changes. The governing rule throughout was that
instrumentation may become more informative but must not quietly change what
exp003a is testing, so every behaviour touching the estimand, treatment, judge or
outcome went into `docs/EXP003A_FROZEN_DECISIONS.md` as a pre-registration
decision instead of being silently repaired.

### 12.1 What was delivered against §7

| §7 item | Delivered | Where |
|---|---|---|
| 1 Telemetry per dispatch | tokens, latency, timestamps, role, model — for judge dispatches too | `lab/telemetry.py`, `lab/store.py` |
| 2 Deprecate self-report | storage column renamed, cost tables switched to observed calls, self-report demoted to a reported diagnostic | `lab/store.py`, `lab/report.py`, FD-2 |
| 3 Per-tool split NOT MEASURED | recorded with its reason, never estimated | `lab.telemetry.NOT_MEASURED` |
| 4 Evidence ledger | per-retrieval query / returned / depth / claim-addressing / origin; short ledger is an audit flag, never a correction | `lab/states.py`, `lab/ingest.py` |
| 5 Retrieval-state machine | four independent predicates, depth-qualified labels, licensing rule | `lab/states.py` |
| 6 Task-label axes | six axes, vocabulary, operational tests, coherence rules, collinearity check | `lab/labels.py`, `lab/battery.py` |
| 7 Placebo generator + tests | per-question generation, four measured axes, two declared review axes | `lab/placebo.py`, `tests/test_placebo.py` |
| 8 Egress re-probe | run and committed before cell D planning | `runs/egress_probe/probe-2026-08-28.json`, FD-4 |

### 12.2 Four things the build found that the plan had not anticipated

Recorded because each changed a decision, and because "the instrument work went
smoothly" is exactly the report that hides them.

1. **Closed-book directive packets contradict themselves.** Every
   `directive_only` packet ever generated tells the solver it has no tools and
   then gives it a search budget. This is a defect in the *treatment* exp001 and
   exp002 measured, so it is frozen as-is rather than fixed — FD-1.

2. **`searches_used` is inside the prompt, not just the schema.** Four of its
   nine occurrences are in solver-facing text. The deprecation therefore lands on
   storage and reporting only; renaming the field the solver is asked to fill
   would be a treatment change wearing a refactor's clothes — FD-2.

3. **The four retrieval states are not one ladder.** Modelling them as rungs made
   the ordinary search-only case (claim matched in a snippet, no source opened)
   look like a sandbox breach. They are independent predicates — FD-4.

4. **The self-report gap is large on real data.** Rendering exp002 under the new
   cost code shows every search-enabled condition reporting roughly half the
   observed tool calls. That is the evidence for the deprecation rather than an
   argument for it — FD-8.

### 12.3 Two claims the build deliberately does not make

* **That the placebo is length-neutral.** The tests prove no pool variant
  contains a numeral or a size term. They cannot prove what the placebo does to
  *response* length, which needs solver trials. A pre-registered diagnostic with
  a pre-committed consequence is bound instead — FD-7.
* **That verification does or does not help.** WebFetch is blocked, so
  `SOURCE_ACCESS` and `VERIFICATION` are unreachable and no claim about them is
  licensed from any trial run here — FD-4.

### 12.4 Test baseline

The pre-existing 130 tests remain green and unmodified. Step 3 adds coverage in
four new files (placebo six-axis matching, task labels, retrieval states,
telemetry and store), taking the suite to **385 green**. All three frozen result
databases were verified byte-identical after being opened and fully read through
the new code path.


---

## 13. Step 4 — the diagnostic_v1 battery, as built

Twenty-five items, six cells, matching §5's structure exactly: L 6, R 4, D 5,
U 4, N 4, C 2. **Zero solver dispatches.** Every item's specification was
committed before any, which is the only thing that makes its predictions
predictions.

Artefacts: `batteries/diagnostic_v1.yaml` (items and specifications),
`batteries/answers.diagnostic_v1.yaml` (quarantined ground truth),
`docs/DIAGNOSTIC_V1_SPECIFICATION.md` (the inspectable document, generated from
the battery so the two cannot disagree), `lab/spec.py` (the model and the tier
wall), `tests/test_diagnostic_battery.py`.

### 13.1 The tier wall

The operator's requirement was a hard separation between **measurement
validity → diagnostic result → primary experimental result**, so that a
diagnostic discovering the instrument is sensitive to some feature does not
become evidence for the hypothesis. It is implemented as a declared tier per
item plus `lab.spec.cite()`, which **raises** when an item is used above its
tier:

| Tier | May support | Items |
|---|---|---|
| `MEASUREMENT_VALIDITY` | instrument validity only | C01, C02 (and both are gates) |
| `DIAGNOSTIC` | instrument validity, ruling an explanation in or out | all of D, U, N |
| `PRIMARY` | all of the above, plus a mechanism effect | all of L, R |

Two structural consequences follow and are enforced at load time:

* **`PRIMARY` requires `outcome_type: deterministic`.** D5 said a judge may not
  determine a primary outcome; exp003c then measured a real judge length effect
  at rubric boundaries. So a judged item cannot reach the top tier by
  construction, not by discipline.
* **A judge-free item must declare `length_sensitivity: NONE`, and an item with
  a judge anywhere in it may not.** The two fields have to agree about whether
  a judge exists for length to act through.

`deterministic_with_judge_fallback` was added as its own outcome type rather
than rounding cell D into one of the other two: the trap grader decides most
cases by string match and escalates the rest, so a fraction of those trials are
judged and the length caveat applies to exactly that fraction.

### 13.2 What each item locks, before dispatch

All fifteen fields the operator required, plus the plan's three (§5) and the
tier: id, conditions, cell and family, six task labels, intended mechanism,
expected retrieval state **per condition**, gold criterion, response mode and
anchors, outcome type, known confounds, why it is in the battery, PASS /
PARTIAL / FAIL / NOT_ESTABLISHED rules, length sensitivity, placebo or matched
relationship, exclusion criteria, the consequence of each named failure,
competing explanations, per-condition predictions, and the discriminating
observation. Validation refuses an item missing any of them — a field left
blank now is one filled in after the results are in, and one filled in then is
not a prediction.

### 13.3 Four things the battery build found

1. **`expected_retrieval_state` is checked against the committed egress probe.**
   An item may not be specified to reach a state the environment cannot produce,
   so FD-4 binds at authoring time rather than at analysis time. No cell-D arm
   claims `SOURCE_ACCESS` or `VERIFICATION`; the two multi-dispatch arms are
   named snippet-level checking in the file itself.

2. **Three condition texts do not exist yet** — `A_only`, `search_selfcheck`,
   `search_independent`. Each is a treatment, so each is now an open
   pre-registration item due before dispatch rather than something assembled at
   runtime (FD-9).

3. **A reject string was removed for a defect the lab had already met.** D02's
   candidate appeared verbatim inside a correct *denial* — the same shape as the
   exp001 Tesla failure. The rule was not relaxed to admit it; the key was fixed
   (FD-10).

4. **Two of the step-4 tests were wrong, not the data.** A leak check flagged
   L04's accept string `nato` inside the word "discrimi**nato**r", and an
   import check flagged `trials.py`'s docstring for *describing* the rule it
   obeys. Both were re-operationalised — word boundaries, and an AST check on
   the import graph — and the reasoning is recorded in the tests themselves.

### 13.4 What is deliberately not claimed

* **That the battery is unbiased.** Its items were written by the same process
  that wrote the mechanism. The collinearity check ensures no task axis is a
  relabelling of `claim_type`, and every axis varies — but a battery written by
  someone who had never seen the epistemic layer would still be a stronger test,
  and that remains an open weakness rather than a solved one.
* **That the screens will keep 25 items.** Cell L's L06 and cell D's D05 are
  deliberate near-ceiling items, included so the step-5 screen is exercised on
  real cases. If either is excluded, the §6 power statement is restated for the
  reduced item count *before* anything is read.

### 13.5 Test baseline

The 130-test baseline remains unmodified and green. The suite is now **670**.


---

## 14. Step 5 — final pre-experiment hardening

Zero solver dispatches. The step's objective was not to finish the setup but to
establish whether the experiment is *runnable* — every rule fixed in writing,
every screen actually run on criteria fixed beforehand, no specification claim
the runtime cannot produce, every named condition an actual text, and every
mechanism the design cannot separate written down in advance.

**Verdict: NOT RUNNABLE.** The preflight answers **NO** at 20/25. Full report in
`docs/EXP003A_READINESS.md`; blockers summarised in §14.5.

### 14.1 Two findings, obtained for zero solver dispatches

**Routing agreement is 60% (15/25).** The router picks which directive gets
injected, so a misroute means the arm delivers a different treatment from the one
the item's specification predicts about. The failures are systematic: word
problems never reach DETERMINISTIC (the classifier needs an explicit operator
between two numbers), and superlatives — "first successful", "Best Picture" —
route NORMATIVE at 0.90 confidence. All four cell-R items are affected, which
would leave cell R testing an irrelevant directive. Recorded as FD-12 with three
options and their measured costs; the decision is the operator's.

**Two of five cell-D items excluded by their own pre-registered criteria.** The
frozen scout showed D01's and D02's search spaces *correct* the premise rather
than restating it — D01's top result is titled "Why didn't Einstein get the Nobel
Prize for the theory of relativity?", and every first-page result for D02 is a
debunking. They test retrieval benefit, not displacement. Cell D runs on three
items and is REDUCED: consistency falls from 2-of-5 to 2-of-3.

### 14.2 The three conditions that were only labels are now treatments

`A_only` is built by the placebo machinery, reusing the placebo's carrier text
almost verbatim, so it is matched on word count within 10% and on bullet count,
section headers, paragraph blocks and em-dash count **exactly**, and differs from
`directive_placebo` on at most four lines. `search_selfcheck`'s reviewer sees the
question and the draft but not the snippets. `search_independent`'s gatherer
receives a **frozen neutral topic string** rather than the question — without
which "claim-blind" is empty on this battery, since every cell-D question
contains its own false premise.

Neither multi-dispatch arm is called verification: `is_verification()` computes
the answer from the formal definition and the probed environment, and returns
True for `search_independent` only under hypothetical open egress. Neither is
counted as one dispatch.

### 14.3 The mechanism question, answered before dispatch

Retrieval, external information and repeated attempts are excluded from the
primary cells **by construction** — closed-book arms, no retries, replicates
scored independently. Two mechanisms are **not** separated, and both are recorded
in FD-11 with a bounding plan rather than discovered later:

* **Additional computation.** "Show the steps" elicits more intermediate tokens,
  which improves arithmetic on its own. The placebo matches the prompt, not the
  response. Bounded now by a response-token covariate — explicitly a weak bound,
  since response length is a mediator. Measured properly only by adopting
  `elaboration_only`, which is written and frozen but deliberately not adopted:
  it costs 20 trials and changes cell R's estimand.
* **Self-correction versus a second pass.** Reported as "a second dispatch of any
  kind", never as self-correction.

### 14.4 The preflight

Twenty-five checks, fail-closed, one binary question: *can the experiment run
without changing any experimental rule after seeing solver results?* An unknown
check is a FAIL, an unrun screen is BLOCKED, and `runnable` is the conjunction of
all of them. A test asserts it currently answers NO — so clearing the blockers is
visible as that test starting to fail, rather than as nothing.

### 14.5 Blockers

| # | Check | Status | Needs |
|---|---|---|---|
| D1 | `routing_consistency` | FAIL | an operator decision between route overrides, rewording, or exclusion (FD-12) |
| D2 | `screens_complete` | BLOCKED | the knowledge probe dispatched, ~125 trials, thresholds already frozen |
| D3 | `power_recomputed` | BLOCKED | resolution of D1, then one operative power table |
| D4 | `experiment_identity` | FAIL | the exp003a config, written after D1 and D2 |
| D5 | `git_identity` | FAIL | a clean tree at dispatch time |

### 14.6 Test baseline

The 130-test baseline remains unmodified and green. The suite is now **756**.
