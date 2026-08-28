# exp003 design memo — mechanism disambiguation

**Status: DESIGN ONLY. Nothing implemented. Nothing in `epistemic/`, `lab/`, or
`batteries/` has been changed by this document.**

exp001 and exp002 remain frozen. No run is rescored. No directive, prompt,
rubric, or answer key is edited here.

This memo is written to be red-teamed, and §16–§17 red-team it. The design that
should actually be built is the one in **§18 (post-red-team revision)**, not the
one in §5–§11. Both are kept so the reasoning is auditable.

---

## 1. What exp002 established

Six things, and only six.

**1.1 Self-reported tool use is not a measurement.** Observed calls exceed
self-reports by 2.0–2.2× in every search condition, one-directionally
(0/45 over-reports). Self-report detects 0 of 18 observed budget violations.
*This is established, not hypothesised.*

**1.2 The budget manipulation was real and behaviourally effective.** Raising the
ceiling 2→3 moved observed calls 30→37 (+23%). Solvers do not spend to the
ceiling: 0 of 3 on f09 and f10, and `verified_flat` used *fewer* calls than
`verified` on f08. Budget is a ceiling, not a driver.

**1.3 K=3 judging is reliable on this rubric set.** 97% verdict unanimity, mean
score spread 0.024, 0 DISPUTED across 33 trials / 99 judgements. exp001's
±8-point noise floor was an artifact of estimating reliability from 12 paired
judgements.

**1.4 Retrieval degrades performance on false-premise and contested-quantity
items in this battery.** Closed-book 100% vs search 0–80% on those categories.
On f15 the crossing is total and unanimous across 9 independent judgements.
Present in all three search conditions, so it is a property of retrieval, not of
the directive.

**1.5 Every measured condition difference is smaller than one question.** At
n=15, one question is 6.67 accuracy points. The largest contrast in exp002
(+6.0, `directive_only` − `baseline`) rests on exactly one question (f05).

**1.6 The battery is exhausted.** 10 of 15 questions are flat across all five
conditions. Only f05, f07, f12, f14, f15 carry any signal.

## 2. What exp002 failed to establish

**2.1 Whether the directive does anything.** `directive_only` − `baseline` = +6.0
points = 0.90 questions, driven by f05 alone. Never replicated. Never tested
against a length-matched placebo.

**2.2 Whether the budget policy was ever the problem.** `verified_flat` matches
`search_only` on aggregate — consistent with the budget explanation — but the
+5.6 points it gains over `verified` decompose into a phrasing artifact (f12),
a case of scoring higher for saying less (f15), and two within-band differences.
The aggregate and the mechanism disagree.

**2.3 Whether verification helps.** Untestable. WebFetch is egress-blocked on
every domain probed, so no condition has ever inspected a primary source. The
conditions named `verified` were performing snippet retrieval.

**2.4 How much of the score is stochastic.** `repeats: 1` in every experiment to
date. **We have never run the same question in the same condition twice.** The
within-condition variance of this instrument is completely unmeasured. Every
number in every report is a single draw.

**2.5 Whether the directive's effect is content or length.** `directive_only`
prompts carry ~350 additional words of instruction. No condition has ever
supplied length-matched, epistemically inert text. "The directive helps" is
currently indistinguishable from "any long careful-sounding instruction helps."

**2.6 Whether the grader is measuring content or wording.** f12 scored 0.6 vs 1.0
for two answers containing the same fact, differing in whether the rename was
stated explicitly. Unanimous in both directions. Never systematically tested.

## 3. The competing explanations currently on the table

| # | Explanation | Predicts | Currently |
|---|---|---|---|
| **E1 — Latent-knowledge access** | Claim-type framing changes which stored answer surfaces; the model already held the fact. | `directive_only` > `baseline` on items where the fact is provably in the model but a competing famous answer exists. Zero effect where the fact is absent. | One trial (f05). |
| **E2 — Reasoning improvement** | The directive improves multi-step inference, not just retrieval framing. | `directive_only` > `baseline` on search-useless multi-step items. | Untested. Cell R does not exist in any battery. |
| **E3 — Stochastic variation** | f05, f07, f12, f14, f15 moved because they are high-variance items, not because conditions differ. | Replicating the *same* condition on the *same* item reproduces the observed spread without any condition change. | **Untested and unfalsifiable with current data.** The most parsimonious explanation of everything in §1.5. |
| **E4 — Prompt-length / placebo effect** | Any long, careful-sounding preamble produces the same gain. | `directive_placebo` ≈ `directive_only` > `baseline`. | Never controlled for. |
| **E5 — Format prescription** | The directive tells the model to produce exactly the surface features the rubrics reward (state freshness, give ranges, flag premises). Gains are grader compliance, not correctness. | Effect appears on judge-graded conduct items, disappears on deterministically-graded name/number items. | Consistent with exp002 but never isolated. |
| **E6 — Retrieval benefit** | Search fixes current-fact failures. | search ≫ closed on current-fact items. | **SUPPORTED** (exp001 §12.1, exp002 §E). Strongest result in the project. |
| **E7 — Retrieval displacement** | Retrieved evidence overrides better-calibrated parametric knowledge on contested quantities. | closed > search on items where the parametric answer is right and the indexed answer is wrong. | Supported by f15/f11, n=2 items. |
| **E8 — Judge phrasing sensitivity** | Informationally equivalent answers score differently by wording. | Paraphrases of one answer receive different scores beyond judge noise. | Suggested by f12, never measured. |

**E3 and E4 are the two that would invalidate the most prior work, and neither
has ever been tested.** They come first.

## 4. The minimum experiment required to distinguish them

The instinct is to build a bigger battery and run all conditions on it. That is
wrong, because E3 and E4 are *gates*: if the directive's effect vanishes against
a placebo, or is smaller than within-condition noise, then ablating its
components (§12) is measuring nothing, and the entire closed-book track should
be abandoned in favour of the retrieval/verification track.

So exp003 is **two staged experiments with a hard gate between them**:

```
exp003a  VARIANCE + PLACEBO + CELL-DIAGNOSTIC
         ├─ measures within-condition stochastic variance (E3)
         ├─ controls prompt length (E4)
         ├─ separates deterministic correctness from judged conduct (E5)
         └─ tests E1, E2, E6, E7 in purpose-built cells
                    │
              ┌─────┴─────┐
        GATE PASSES   GATE FAILS
              │             │
         exp003b        exp004
         ABLATION       retrieval/verification track only;
         (which         closed-book directive work is
         component)     retired as not-established
```

`exp003c` (judge phrasing, E8) runs **in parallel and uses no solver agents at
all** — it is an instrument calibration, and it is the cheapest item in the memo.

---

## 5. Proposed task battery — `diagnostic_v1`

Every question is written to make competing explanations diverge. A question
that all explanations score the same way is excluded, however interesting it is.

Existing `factual_v1` is **not** reused as a scoring battery. Ten of its fifteen
questions are flat, and the five that move are the five the last two experiments
were interpreted against — continuing to use them is how a battery quietly
becomes a training set (lab manual §7.6). `factual_v1` is retained only as a
**regression battery**: it must not change materially, and if it does, the
instrument changed rather than the model.

### Cell L — latent knowledge (tests E1 vs E3/E4)

**Construction rule.** The correct answer must be (a) *demonstrably present* in
the model's parametric knowledge, established by a separate cued knowledge
probe, and (b) *in competition with* a more famous, more frequent, or older
answer. 6 questions.

The f05 shape: "Who is the CEO of Berkshire Hathaway?" — Abel is the answer,
Buffett is the attractor. Candidate shapes (final selection follows §5.7):
succession where the predecessor is far more famous; a renamed entity where the
old name dominates the corpus; a superseded record-holder; a revised scientific
consensus where the superseded figure is more widely quoted.

**Knowledge probe (screening, not a condition).** Before the experiment, each
candidate is asked in *cued* form closed-book, 3× — e.g. "Who succeeded Warren
Buffett as CEO of Berkshire Hathaway, and when?" A candidate enters cell L only
if the cued probe produces the correct answer in ≥2 of 3 draws while the
*uncued* baseline produces it in ≤1 of 3. Items failing the screen are excluded
and **reported as excluded, with counts**, because the exclusion rate is itself
a measurement of how rare the latent-knowledge configuration is.

**Grading: deterministic name/date matching.** No judge. This makes cell L immune
to E5 and E8 by construction, which is why it is the primary cell.

### Cell R — reasoning where retrieval is useless (tests E2)

**Construction rule.** The answer must be derivable from the question text by
multi-step transformation, must not be findable by search (novel numbers,
recombined constraints), and must have a single checkable value. 4 questions.

Shapes: multi-constraint rate/unit problems with a distractor that a one-step
heuristic produces; a date-arithmetic problem across an irregular boundary; a
compound-unit conversion; a small combinatorial count with an off-by-one trap.
Each carries a named distractor value so the failure mode is identifiable, not
merely "wrong".

**Grading: deterministic numeric**, tolerance strictly below the distractor gap
(the f10 rule, already enforced in `lab/grading.py`).

### Cell D — retrieval displacement (tests E7 vs E6)

**Construction rule.** Three properties must hold *before* solvers run:
1. the parametric answer is likely correct (verified by closed-book probe);
2. the top indexed answer is wrong, stale, or materially lower quality;
3. a higher-authority source establishing the conflict exists.

5 questions. **Property (2) is established by a frozen retrieval scout** (§9.3)
run before the experiment, whose output is committed. An item whose scout record
does not show the misleading result is excluded by pre-specified rule.

**Grading: two independent dimensions.**
- *Correctness*: deterministic where possible (the figure/range).
- *Conflict handling*: a five-way behavioural code — `accepted_retrieval` ·
  `rejected_retrieval` · `sought_another_source` · `reported_conflict` ·
  `abstained`. Judged, blind, from the answer text plus evidence ledger.

The conflict code is the scientifically interesting output. Accuracy alone
cannot distinguish "got lucky" from "noticed and resolved".

### Cell U — uncertainty and abstention (tests E5, and conduct generally)

**Construction rule.** Questions where the correct response mode is *not*
`assert`. 4 questions, one per mode: `qualify` (changeable fact),
`range` (contested quantity), `flag_conflict` (sources genuinely disagree),
`abstain` (unknowable / not yet determined — and one where abstention is the
*wrong* move, to catch over-abstention).

**Grading: response-mode classification first, correctness second.** Scored as a
2-tuple, never collapsed into one number. A correct figure delivered in the
wrong mode and a correct mode with a wrong figure are different failures and
must not average to the same score.

### Cell N — unnecessary tool use (cost, not accuracy)

**Construction rule.** Questions answerable from parametric knowledge with high
confidence: stable facts, pure arithmetic, definitional questions. 4 questions.

**Primary metric is observed tool calls, not score.** A condition that spends
searches here is wasting budget. This is the only cell where the *desired*
result is zero tool calls.

### Cell C — current-fact positive control

2 questions, current-fact, retrieval genuinely required. Not a research
question — a **tripwire**. If search does not beat closed-book here, the
instrument is broken and no other cell in the run may be interpreted.

### 5.7 Battery construction discipline

- Questions are written **before** conditions are run, committed, and not edited
  afterwards.
- Each question declares its cell, its task labels (§6), its expected
  discriminating prediction per explanation, and its exclusion criteria.
- **Ceiling/floor screen:** a pilot of `baseline` × 3 draws is run on every
  candidate. Items where baseline scores 0.0 in 3/3 *and* the knowledge probe
  fails (nothing to access) or 1.0 in 3/3 (no headroom) are excluded before the
  experiment, by rule, blind to condition. Exclusions are reported with counts.
- Ground truth follows the existing `status: verified` discipline. Anything
  unverified is `UNGRADED`, never guessed.

---

## 6. Task taxonomy — and why it is not the claim taxonomy

The epistemic classifier assigns **one claim type** (EMPIRICAL / NORMATIVE /
PREDICTIVE / DEFINITIONAL / DETERMINISTIC). That is a property of *what kind of
assertion an answer would be*.

Task labels are a property of *what the task demands of the solver*. They are
**multi-dimensional and orthogonal**, and collapsing them into the claim
taxonomy would destroy exactly the distinctions exp003 exists to draw. Every
question carries one value on each of six axes, each with an operational test:

| Axis | Values | Operational definition |
|---|---|---|
| `knowledge_source` | `parametric_sufficient` · `retrieval_required` · `retrieval_misleading` | Determined by two pre-run probes: closed-book baseline accuracy (3 draws) and the frozen retrieval scout. `parametric_sufficient` = baseline ≥2/3 correct. `retrieval_required` = baseline ≤1/3 and scout finds the correct answer. `retrieval_misleading` = baseline ≥2/3 and scout's top result is wrong. |
| `reasoning_depth` | `lookup` · `single_step` · `multi_step` | Number of distinct transformations needed between the givens and the answer, counted by the question author and recorded. `lookup` = 0. |
| `premise` | `sound` · `false` | Does the question presuppose something untrue? Binary, checkable against ground truth. |
| `referent` | `unambiguous` · `ambiguous` | Does the question have more than one defensible subject? Established by naming both referents in the key. |
| `ground_truth_state` | `settled` · `contested` · `unknowable` | `settled` = one value all high-authority sources agree on. `contested` = ≥2 defensible values from methodological disagreement, both recorded. `unknowable` = not determined at ask time. |
| `correct_response_mode` | `assert` · `qualify` · `range` · `flag_conflict` · `reject_premise` · `abstain` | The response shape the key requires. Recorded in the answer key, not inferred from the answer. |

Rules that keep this honest:
- A label may only be assigned if its operational test can be run **before**
  seeing any condition's results.
- No axis may be added because it would make a table look better. An axis earns
  its place by having at least two questions on each of two values *and* a
  competing explanation that predicts a difference across them.
- `claim_type` continues to be recorded separately, from the classifier. Whether
  the two taxonomies should ever be merged is an empirical question the labels
  make answerable; it is not assumed.

---

## 7. Conditions

Five, and the placebo is the important new one.

| Condition | Agent | Directive | Search | Purpose |
|---|---|---|---|---|
| `baseline` | closed | none | no | the thing to beat |
| `directive_placebo` | closed | **length-matched inert text** | no | **isolates E4.** Same word count, same section headers, same imperative register, no epistemic content: "answer carefully, completely, and in full sentences; give relevant background; be thorough; structure your response clearly." |
| `directive_only` | closed | full route-derived directive | no | the closed-book treatment |
| `search_only` | web | none | flat 3 | the control that has won every experiment so far |
| `search_directive` | web | full directive | flat 3 | **renamed from `verified`.** See §8. |

The placebo is generated by a committed function, its word count is asserted to
be within ±10% of the real directive per question by test, and it is checked by
test to contain none of the epistemic keywords (claim type names, "premise",
"source", "verify", "fresh", "conflict", "budget").

**Cell × condition matrix** — not every cell runs every condition, because a
condition that cannot discriminate in a cell is spend without information:

| Cell | baseline | placebo | directive_only | search_only | search_directive | k |
|---|---|---|---|---|---|---|
| L (6q) | ● | ● | ● | | | 5 |
| R (4q) | ● | ● | ● | | | 5 |
| D (5q) | ● | | | ● | ● | 5 |
| U (4q) | ● | ● | ● | ● | ● | 3 |
| N (4q) | ● | | | ● | ● | 3 |
| C (2q) | ● | | | ● | | 3 |

Solver trials: L 90 · R 60 · D 75 · U 60 · N 36 · C 12 = **333**, plus a
screening pass (knowledge probe + ceiling/floor screen) of ~60. Roughly 4×
exp002's total. Trim levers, in the order they should be pulled: U → k=2 (−20),
N → 3 questions (−9), R → 3 questions (−15).

---

## 8. Retrieval is not verification — an architectural change

The word `verified` is retired as a condition name. It was never accurate: no
condition in exp001 or exp002 inspected a primary source, because WebFetch is
egress-blocked on every domain probed. exp001 and exp002 keep their names as
historical record; nothing new may use the term.

Four states are recorded separately per trial, and a lower state may never be
reported as a higher one:

| State | Definition | Currently reachable? |
|---|---|---|
| `RETRIEVAL` | A search returned a result referencing the topic. | Yes |
| `SOURCE_ACCESS` | A primary source document was actually fetched and its text is in context. | **No — WebFetch blocked** |
| `CLAIM_EVIDENCE_MATCH` | The retrieved content addresses *the specific claim*, not merely the topic. | Partially (judgeable from the ledger) |
| `VERIFICATION` | The claim was checked against evidence and a support/contradict/insufficient verdict recorded. | No |

Every trial in exp003 records the highest state it reached. A run in which no
trial exceeds `RETRIEVAL`/`CLAIM_EVIDENCE_MATCH` may not produce any conclusion
about verification, positive or negative. This is a hard reporting rule.

**Path to `SOURCE_ACCESS` without egress** (design only, for exp004): supply
primary-source text as an inline fixture in the trial packet, committed to the
repo and quarantined from the answer key. This buys `SOURCE_ACCESS` at the cost
of removing the model's *choice* to fetch — a real confound that must be stated
whenever fixture results are reported.

---

## 9. Controls

**9.1 Placebo.** §7. The single most important addition.

**9.2 Deterministic-first cell design.** The two primary cells (L, R) are graded
by string/number matching with no judge in the loop, so their results cannot be
produced by E5 (format prescription) or E8 (phrasing sensitivity).

**9.3 Frozen retrieval scout.** Before cell D runs, a separate scout agent
records, per question, the top search results and whether the misleading figure
appears. Output is committed before any solver runs. Items whose scout record
contradicts the design assumption are excluded by rule. This is what stops cell D
from being a self-fulfilling construction.

**9.4 Answer-length recording.** Every answer's character and word count is
recorded, and every score-vs-length relationship is reported. See §16.1.

**9.5 Tool-environment equivalence re-check.** The probe in
`runs/TOOL_ENVIRONMENT_EQUIVALENCE.md` is re-run at the start of exp003 and its
result committed. If egress has changed, that is a change to the instrument and
the run is re-baselined rather than compared to exp002.

**9.6 Trial ordering and timing.** Replicates of a given cell run contiguously;
each trial records a UTC timestamp. Search-condition replicates are not i.i.d.
draws from a fixed world, and the timestamp is what makes that visible.

**9.7 Order/position randomisation.** Trial dispatch order is randomised across
conditions rather than run condition-by-condition, so any session-level drift
(rate limiting, model routing) spreads across conditions instead of loading onto
one.

**9.8 Blindness preserved.** Judge packets carry question, standard, answer.
No condition, model, trial id, or replicate index. One item per judge agent
(the run-experiment protocol forbids batching, because a batch lets a judge see
that several items are traps).

---

## 10. Replication strategy

**The smallest useful replication design is k ≥ 3, and k = 5 on the two primary
cells.** Justification, stated as arithmetic rather than preference:

- With k = 1 (every experiment to date), within-condition variance is not
  merely unmeasured — it is *unmeasurable*, and every difference is confounded
  with it.
- k = 2 detects that variance exists but estimates it terribly (1 degree of
  freedom per cell).
- k = 3 gives a usable per-item variance estimate and supports a per-item rate
  in thirds.
- k = 5 supports per-item rates in fifths, which is what is needed to see a
  latent-knowledge item flip from "rarely correct" to "usually correct".

**The primary outcome is not battery accuracy.** exp003 abandons the
battery-mean headline. The primary outcome is the **per-item answer rate** —
for question q under condition c, the proportion of k replicates scoring above
threshold. Condition effects are then differences in rate, per item, with the
item as the unit of analysis.

This is a deliberate trade: exp003 is powered to detect a mechanism that shifts
an individual item's rate by ≳0.4, and is **not** powered to detect a uniform
5-point battery-wide shift. Given §1.5 — every difference so far is under one
question — chasing the battery mean is chasing noise. Mechanism is what is
missing.

**Does `baseline 64 → directive 70` replicate?** Reframed as a mechanism
question, because the number itself cannot be replicated on a new battery:
*on items where the fact is provably latent, does the directive raise the answer
rate?* Cell L answers that with 6 items × 5 draws × 3 conditions.

---

## 11. Metrics

### 11.1 Cost — observed telemetry only

`searches_used` is **deprecated as a cost metric**. It is renamed
`searches_selfreported`, retained solely as a calibration datum (does the model
know what it did?), and the schema comment states it is not a cost measure. Any
report that quotes it as cost is a bug.

Authoritative and derived metrics per trial:

| Metric | Source | Status |
|---|---|---|
| `tool_calls_observed` | harness | authoritative |
| `search_calls_observed` / `fetch_calls_observed` | **not currently available** — the harness reports an aggregate count only | **known instrument gap, §16.7** |
| `latency_s` | harness `duration_ms` | available per dispatch; currently not persisted — must be wired |
| `tokens` | harness `subagent_tokens` | available per dispatch; currently not persisted — must be wired |
| `tool_call_failures` | evidence ledger + aggregate count | partly self-reported, §11.2 |
| `evidence_useful` | judged from ledger, blind | judged |
| `highest_state_reached` | §8 state machine | derived |

`duration_ms` and `subagent_tokens` are returned by every agent dispatch and
have simply never been recorded. Wiring them is the cheapest instrument
improvement available and closes exp002's "no cost or latency data" gap.

### 11.2 The evidence ledger

A tool call that returns HTTP 200 and nothing relevant is not a useful call.
"Useful" is a content judgement, so it cannot come from a counter. Solvers in
search conditions emit, per retrieval:

```
{ "query": "...", "returned": "<what came back, one line>",
  "addressed_claim": true|false, "source_kind": "primary|secondary|aggregator|unknown" }
```

**Counts stay authoritative from the harness; the ledger supplies content only.**
A ledger with fewer entries than `tool_calls_observed` is an audit flag, not a
correction — the same rule that caught the 2× self-report gap. `addressed_claim`
is re-judged blind from the ledger text rather than trusted.

### 11.3 Accuracy and conduct, kept separate

- `score` — correctness, deterministic where possible.
- `response_mode` — the six-way code from §6, judged.
- `conflict_action` — the five-way code from §5 cell D, judged.
- `answer_len_chars`, `answer_len_words` — recorded for §16.1.

These are never averaged together.

---

## 12. Ablation plan (exp003b — gated, does not run unless §14 passes)

Do not test every combination. The current directive decomposes into eight
addressable components; only four have distinct theoretical predictions:

| Component | Present as | Predicts |
|---|---|---|
| **A. Epistemic framing** | claim-type label + "your own recall is a hypothesis" | effect on cell L (latent access) |
| **B. Premise check** | "check the question's premises before answering" | effect only on `premise: false` items |
| **C. Freshness warning** | registry staleness notes + "state how fresh your evidence is" | effect on `qualify`-mode and current-fact items |
| **D. Computation directive** | DETERMINISTIC "compute, don't search, show steps" | effect on cell R |

Design: `placebo`, `A`, `B`, `C`, `D`, `full` — six closed-book conditions,
each component isolated against a length-matched placebo carrier so every
condition has the same prompt length. Six conditions × the cells where each
makes a prediction, k=5. Not a full 2⁴ factorial: 16 cells is 3× the cost for
interaction terms nothing currently predicts.

Components deliberately **not** ablated in exp003b, with reasons: source lineage
and independence (untestable while SOURCE_ACCESS is unreachable); budget policy
(exp002 showed ceiling ≠ spend); problem compilation and claim decomposition
(not implemented in the current directive — ablating something that does not
exist would be theatre); independent evaluation (that is exp004, §13).

---

## 13. Independent verifier (exp004 — designed here, not run here)

The user's concern is correct: "here is your previous answer, check it" invites
confirmation bias, and it is not verification, it is self-review.

Proposed architecture, three isolated agents:

1. **Generator** produces a candidate claim. No tools.
2. **Evidence gatherer** receives *the question only* — never the candidate
   claim — and returns evidence. Not knowing the claim is what makes the
   evidence independent of it; this is the load-bearing isolation.
3. **Verifier** receives the claim and the evidence, and returns
   `SUPPORTS` / `CONTRADICTS` / `INSUFFICIENT` with the specific span relied on.

Two verifier arms:
- `verifier_without_reasoning` — claim + evidence only.
- `verifier_with_reasoning` — claim + evidence + the generator's chain.

**If the latter performs worse, that is the finding**, and it is a directly
useful one: it would say the reasoning trace acts as a persuasion vector on the
checker.

Prerequisites before exp004 is worth running: (a) `SOURCE_ACCESS` reachable via
fixtures (§8), and (b) exp003c's phrasing calibration complete, since the
verifier is itself a judge and inherits every bias measured there.

Named confound that cannot be fixed here: verifier and generator are the same
model family, so they share blind spots. The packet's own defence — a different
model family for the judge — needs API access this environment does not have.
This must be stated in any exp004 result, not discovered afterwards.

---

## 14. Expected outcomes, and the gate

Pre-specified. Written before any data exists.

| Explanation | Cell L | Cell R | Cell D | Cell N | If observed |
|---|---|---|---|---|---|
| **E1 latent access** | `directive_only` rate > `placebo` rate by ≥0.4 on ≥3 of 6 items | no effect | — | — | E1 supported; proceed to exp003b to find which component |
| **E2 reasoning** | no effect | `directive_only` > `placebo` on ≥2 of 4 | — | — | E2 supported; component D is the candidate |
| **E3 stochastic** | within-item spread across k=5 replicates ≈ between-condition spread | same | same | — | **Everything in exp001/exp002 is re-labelled provisional**, and n must rise before any further claim |
| **E4 placebo** | `placebo` ≈ `directive_only` > `baseline` | same | — | — | The directive's content is not doing the work. Closed-book track retired. |
| **E5 format** | no effect (cell L is deterministic) but effect on cell U `response_mode` | — | — | — | The directive changes conduct, not correctness. A real but much narrower claim. |
| **E6 retrieval** | — | — | search > closed on cell C | — | positive control holds |
| **E7 displacement** | — | — | closed > search on ≥3 of 5 D items | — | E7 supported; `conflict_action` distribution is the mechanism evidence |

### The gate

**exp003b (ablation) runs only if, in cell L or cell R, `directive_only` exceeds
`directive_placebo` by more than the measured within-condition noise, on at
least two items, in the pre-specified direction.**

If the gate fails, the honest conclusion is that the directive's closed-book
effect is not established, exp003b is cancelled, and effort moves to the
retrieval/verification track (exp004), where E6 and E7 are the only findings
with any support behind them.

## 15. Statistical analysis plan

Pre-specified before data collection.

**Unit of analysis: the question.** Replicates estimate a per-item rate;
questions are the sample. Trials are not independent observations and will not
be treated as such.

**Variance decomposition (primary output).** For each cell, a random-effects
decomposition of score into σ²(question), σ²(condition), σ²(residual within
question × condition). Report all three and the intraclass correlation. **This
table is the single most valuable artifact exp003 produces** — it is the number
that tells us whether any prior result meant anything.

**Primary contrasts.** One per cell, named in advance:
L: `directive_only` − `directive_placebo`. R: same. D: `search_only` − `baseline`.
U: `directive_only` − `directive_placebo` on `response_mode` correctness.
N: `search_directive` − `search_only` on observed tool calls.
Five primaries; **Holm correction across the five.** Everything else is
exploratory, labelled exploratory, and cannot support a conclusion.

**Intervals, not p-values alone.** Bootstrap 95% CIs by resampling *questions*
within cell (10,000 draws). Scores are bounded and non-normal; t-tests on 4–6
items would be dressing.

**Effect sizes.** Per-item rate difference (primary), and Cohen's h for
proportions. Battery-mean differences are reported only with the number of
questions driving them beside them, as in exp002 §A.2.

**Pre-specified null-reporting rule.** A contrast whose CI includes zero is
reported as "not established", never as a trend, and never re-described as
directional support.

**Judge budget rule (replaces blanket K=3).** exp002 measured 97% unanimity and
0.024 mean spread, so K=3 everywhere is now over-provisioned. exp003 uses
**K=1 by default, with K=3 on a pre-specified stratified 25% audit sample**, and
an **escalation rule: if audit-sample verdict unanimity falls below 85%, the
entire run escalates to K=3 and the K=1 grades are discarded and re-judged.**
The rule is fixed in advance; the reliability of this run is measured within
this run rather than inherited from the last one.

---

# 16. Red team — what could fool us

Written against my own design. Each item ends with the mitigation actually
adopted in §18.

### 16.1 Answer length is a live confound, and the literature says it runs the wrong way for us

A live search (August 2026) found that judge families differ in verbosity bias
and that **Claude-family judges have been reported to prefer *shorter*
responses**, where other families prefer longer. Our f15 case is exactly that
shape: `verified_flat` scored 0.4 and `verified` scored 0.0, and the higher
score went to the answer that said *less*.

If the directive changes answer length, then any judged difference between
conditions could be a length artifact. This threatens E5 and every judged cell.

→ **Mitigation:** record length on every answer; report score-vs-length
regression per cell as a standing diagnostic; make the two primary cells
deterministic so the primary result cannot be a length artifact; add
length-matched paraphrase pairs to exp003c.

### 16.2 Selecting cell items by "they moved last time" manufactures the result

f05, f07, f12, f14, f15 were identified *because* they varied. Building the new
battery in their image risks selecting high-variance items and then reporting
that variance as a condition effect. This is the same error as picking stocks
that went up.

→ **Mitigation:** items are selected by their *structural* properties (the §6
operational labels), verified by pre-run probes, never by "this one moved in
exp002". And the k≥3 replication design means item variance is measured
directly rather than being attributed to conditions by default.

### 16.3 The knowledge probe makes cell L a best case, not a representative one

Screening for "the model produces the fact when cued" selects precisely the
items where a latent-access mechanism *can* work. A positive result in cell L
therefore establishes the mechanism's **ceiling**, not its expected value in
the wild.

→ **Mitigation:** state this explicitly in any result. Report the screen's
exclusion rate — how many candidates *failed* the probe — because that fraction
is what converts a ceiling into an expected value.

### 16.4 The directive prescribes the behaviours the rubrics reward

The EMPIRICAL directive says to state freshness, name ranges, and flag premises.
The rubrics award points for stating freshness, naming ranges, and flagging
premises. A gain could be pure compliance with no epistemic content whatsoever —
and it would look identical to a real effect on any judged cell.

→ **Mitigation:** primary cells are deterministic (name/number), where the
prescribed format earns nothing. Conduct is measured separately and never
averaged into correctness. Where a conduct gain appears without a correctness
gain, it is reported as *format compliance*, not as improvement.

### 16.5 A composite directive can hide cancelling components

If component A helps by +0.3 and component C hurts by −0.3, the monolithic
directive measures 0 and the gate fails — retiring a track that contains a real
mechanism. This is the clearest way exp003 could make a genuinely useful
mechanism look ineffective.

→ **Mitigation adopted:** the gate is **loosened** to fire on *any* cell showing
a directional effect on ≥2 items, not on an aggregate. And a cheap
**A-only vs placebo probe** (one component, cell L, k=5, 6 questions = 60 extra
trials) runs *inside* exp003a rather than waiting for exp003b, precisely so a
cancelling composite cannot mask the strongest single candidate.

### 16.6 Multiplicity, and the temptation of six cells

Six cells × five conditions × several outcome variables is a large garden of
forking paths. With small q, something will look significant.

→ **Mitigation:** five named primaries, Holm-corrected, fixed before data.
Everything else labelled exploratory in the report itself, not in a footnote.

### 16.7 Per-tool call breakdown is not actually available

§11.1 asks for `search_calls_observed` and `fetch_calls_observed` separately.
The harness returns an **aggregate** `tool_uses` count per dispatch. Splitting it
would require reading subagent transcripts, which is not workable at this scale.

Pretending otherwise would repeat exactly the error exp001 caught: reporting a
number whose provenance is weaker than its name implies.

→ **Mitigation adopted:** record `tool_calls_observed` (authoritative aggregate)
and mark the split as **NOT MEASURED**. The ledger gives a self-reported split
which is recorded, flagged as self-report, and never used as a cost figure. And
with WebFetch blocked, the split is nearly moot: essentially all calls are
searches. That reasoning is recorded rather than left implicit.

### 16.8 The environment can move under us

Search results change day to day. Replicates of a search condition are not draws
from a fixed distribution, so cell D's "misleading result appears" property can
evaporate mid-run.

→ **Mitigation:** frozen scout record before the run (§9.3); timestamps on every
trial; the scout re-run *after* the experiment, with any item whose retrieval
landscape changed reported as environment-drifted rather than silently averaged.

### 16.9 What could make a useful mechanism look ineffective — the full list

1. Under-power: the design detects per-item rate shifts ≳0.4, not 5-point
   battery shifts. **Stated as a limit, not discovered afterwards.**
2. Ceiling/floor items: handled by the §5.7 screen.
3. Cancelling components: §16.5.
4. WebFetch blocked: **no negative conclusion about verification is permitted**
   (§8 hard rule). "Verification didn't help" is not a finding this environment
   can produce.
5. Model-specific: haiku only. A mechanism that helps a stronger model and not a
   weaker one, or vice versa, is invisible. H4 stays deferred, and the
   single-model scope is restated in the conclusion.
6. Judge-generator correlation: same model family, shared blind spots,
   unfixable without another provider. Named in every judged result.

### 16.10 What could make a null look like a positive

E3 (stochastic) plus E4 (placebo) plus E5 (format) can *jointly* manufacture a
clean-looking positive on a judged battery with k=1 and no placebo — which is
precisely the configuration of exp001 and exp002. That is not a hypothetical
failure mode; it is a description of the two experiments already run.

→ This is why §18 makes the placebo and k≥3 **non-negotiable preconditions**
rather than refinements.

---

## 17. Prior-art discipline

**Provenance warning, applied to this section by the lab's own rules.** The
searches below were run 2026-08-28 and reached `RETRIEVAL` state only — search
snippets. WebFetch is blocked, so **no primary source was inspected**, no claim
below reached `SOURCE_ACCESS` or `VERIFICATION`, and every characterisation is
at snippet fidelity. Titles and venues are as returned by search and are not
independently confirmed.

| Mechanism | Nearest prior work found | Setting it was shown in | Are we reproducing it? | Remaining question | Class |
|---|---|---|---|---|---|
| Claim-type routing to adaptive retrieval | Self-RAG; the CoVe line | QA benchmarks, trained/prompted adaptive retrieval | Largely yes | Whether it helps *without* training, as a prompt-only layer, on a live-fact battery | **KNOWN** |
| Abstention on false premise / stale / ambiguous | AbstentionBench (2025) | Purpose-built abstention benchmark | Yes | Nothing we add | **KNOWN** |
| Cheap extra evidence before abstaining | ReCoVERR (2024) | VQA / selective prediction | Yes | Nothing we add | **KNOWN** |
| Retrieval displacing correct parametric knowledge (**E7, our f15**) | Substantial active literature on **context-memory knowledge conflict** — a survey (EMNLP 2024), ConflictBank (2024), context-memory conflict studies with real documents (2024), and 2026 work on explicit conflict resolution and transparent conflict handling in RAG | Constructed/counterfactual conflicts, code-generation API drift, RAG pipelines | **Yes — the phenomenon is well documented.** We are not discovering it | What the system *does* on noticing: our five-way `conflict_action` code under an explicit budget, with the conflict arising naturally rather than being constructed | **KNOWN EXTENSION** |
| Judge phrasing/format sensitivity (**E8, our f12**) | Extensive: JudgeSense prompt-sensitivity benchmark (2026), systematic judge bias evaluations (2026), verbosity/position bias work — including the finding that Claude-family judges skew toward *shorter* answers | LLM-as-judge pipelines across many benchmarks | **Yes, entirely.** This is not research | Nothing. It is **instrument calibration we are obliged to do**, and calling it a finding would be the novelty illusion the packet warns about | **KNOWN** |
| Eval variance / replicates (**E3**) | "Quantifying Variance in Evaluation Benchmarks"; 2026 work on measurement error in LLM pipelines and signal-vs-noise frameworks; reports that within-model variance explains ~10–34% of total variance | Standard benchmark suites | Yes | Nothing. Same as above: **required practice we skipped**, not a contribution | **KNOWN** |
| Length-matched placebo for a prompt-based intervention | Standard experimental control; not specific to LLM work | Everywhere outside ML | Yes | Nothing | **KNOWN** |
| Entity-hazard TTL bucketing (VOLATILE/SCHEDULED/STABLE, per-entity not per-category) | Packet §8 found no direct match; not re-searched here | — | Unknown | Whether per-entity hazard beats a flat TTL. **Untested; H2/H3 still have one measured interval between them** | **UNDEREXPLORED** |
| Evidence gatherer blinded to the candidate claim (§13) | Not searched | — | Unknown | Whether claim-blind evidence gathering reduces confirmation bias vs claim-aware | **UNKNOWN — needs a search before exp004** |

**Consequence for exp003, stated plainly.** Two of the four hypotheses exp002
generated (H-phrasing, and the variance concern behind H-search-displacement's
measurement) are **KNOWN** — they are things the field already established and
this lab failed to control for. That does not make them unimportant; it makes
them *obligations* rather than discoveries. exp003 must do them, and must not
report them as findings.

The genuinely open items are narrower than the project has been assuming:
the **conflict-action taxonomy** under a real budget (KNOWN EXTENSION), and the
**entity-hazard TTL** work (UNDEREXPLORED), which no experiment has touched.

---

## 18. Post-red-team revision — the design that should actually be built

Changes forced by §16, listed as diffs against §5–§15.

**R-1 (from 16.10, 16.1).** `directive_placebo` and k ≥ 3 are **preconditions,
not features**. If either is dropped for cost, exp003 must not run at all — it
would reproduce exp001/exp002's confound with a bigger battery and more
confidence.

**R-2 (from 16.5).** Add an `A_only` condition (epistemic framing alone, on a
length-matched carrier) to **exp003a**, cell L, k=5. +60 trials. Buys insurance
against a cancelling composite retiring a real mechanism at the gate.

**R-3 (from 16.5).** The gate fires on **any cell** showing a directional effect
on **≥2 items**, rather than on an aggregate contrast.

**R-4 (from 16.7).** `search_calls_observed` / `fetch_calls_observed` are
recorded as **NOT MEASURED**, with the reason. Only the aggregate is
authoritative. The ledger's split is labelled self-report and excluded from
every cost figure.

**R-5 (from 16.4, 16.1).** Correctness and conduct are stored and reported as
separate columns, never averaged. Answer length ships as a standing diagnostic
in every report.

**R-6 (from 16.3).** Cell L results are reported as a **ceiling** for the
latent-access mechanism, always accompanied by the knowledge-probe exclusion
rate.

**R-7 (from 17).** exp003c (phrasing calibration) and the variance decomposition
are reported as **instrument calibration**, in an appendix, explicitly labelled
KNOWN prior art. They may not appear as findings.

**R-8 (from 16.8).** The retrieval scout runs twice — before and after — and any
cell-D item whose landscape changed is reported as environment-drifted.

**R-9 (from 8).** No condition may be named `verified`. No negative conclusion
about verification may be drawn while `SOURCE_ACCESS` is unreachable.

**R-10 (new, from 16.9.1).** The report states the minimum detectable effect
**before** the results, in the same section as the results.

### Revised build order

| Step | What | Solver trials | Gate |
|---|---|---|---|
| 0 | Instrument work: persist `duration_ms` + `subagent_tokens`; deprecate `searches_used`; add task-label axes; add state machine; placebo generator + tests; re-run egress probe | 0 | tests green |
| 1 | **exp003c** — judge phrasing calibration, 6 items × 4 paraphrases × 3 judges | **0** (judge-only) | — |
| 2 | Battery construction + knowledge probe + ceiling/floor screen, committed before conditions run | ~60 | exclusions reported |
| 3 | Frozen retrieval scout for cell D | ~10 | committed before solvers |
| 4 | **exp003a** — cells L, R, D, U, N, C with placebo and A_only | ~390 | §14 gate |
| 5 | **exp003b** — component ablation | ~250 | only if gate passes |
| 6 | exp004 — fixtures for SOURCE_ACCESS; independent verifier | — | only after 4 |

**Step 1 is free of solver cost and should run first regardless.** If the judge
turns out to be phrasing-sensitive at the scale f12 suggests, several planned
measurements need redesigning before any solver is spawned — and we would learn
that for the price of 72 judge dispatches.

### What would justify moving to the next phase

Frontier benchmarks, cross-model testing, multimodal, and self-improvement stay
deferred until **all** of the following hold:

1. Within-condition variance is measured and reported, and condition effects are
   larger than it.
2. The judge's phrasing sensitivity is quantified and either small or corrected.
3. At least one mechanism has survived a length-matched placebo.
4. Cost is reported from observed telemetry with tokens and latency persisted.
5. `SOURCE_ACCESS` is either reachable or permanently marked unreachable, with
   every verification claim scoped accordingly.

Items 1, 2 and 4 are instrument obligations the field already knows about
(§17) and this lab has not met. Item 3 is the actual research question. Item 5
bounds what any of it can mean.

**If exp003a's gate fails, that is a good outcome, not a failed experiment.** It
would retire E1, E2 and E4 together, leave E6 and E7 as the only supported
effects, and redirect the project from "does our directive help" — three
experiments of ambiguous evidence — to "what does a system do when retrieval
contradicts what it knows", which §17 says is the one place we have a genuine
extension to make.
