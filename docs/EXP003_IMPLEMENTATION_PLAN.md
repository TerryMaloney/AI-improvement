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
