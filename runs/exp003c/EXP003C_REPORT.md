# exp003c — judge phrasing / length / format calibration

**Result: AMBER. The bound mitigations are mandatory and are applied in §7.
Solver trials for exp003a remain blocked until the plan changes land.**

| | |
|---|---|
| Purpose | Decide whether judge length/format sensitivity is large enough to contaminate exp003a/b |
| Solver trials | **0** |
| Judge dispatches | **96** (72 round 1 + 24 round 2) |
| Judge | `grader-judge`, sonnet, one item per agent, blind |
| Protocol | production `lab.grading.JUDGE_TEMPLATE`, absolute single-answer scoring |
| Judge saw reasoning | `false` on all 96 |
| Judge tokens | 205,214 (round 1) + ~69,000 (round 2) |
| Mean judge latency | 2.45 s |

**This is a KNOWN prior-art phenomenon** (LLM-as-judge prompt-sensitivity and
verbosity-bias literature). It is an obligation exp001 and exp002 skipped, not a
discovery, and it is not described as one anywhere below.

---

## 1. What was held constant

Within every stimulus item, all variants assert **identical facts with identical
correctness**. Verified mechanically by `tests/test_judge_calibration_stimuli.py`:
identical number sets, identical hedge terms, identical premise terms, verbose
≥1.6× concise, format variants structurally distinct but length-matched to
within 30%.

**Why this makes the result robust to my own errors.** Because content is
constant within an item, any mistake in that item's rubric or ground truth
applies equally to all its variants and cancels in the within-item contrast. The
calibration does not depend on my having written *correct* rubrics — only
*consistent* ones.

## 2. Round 1 — 72 dispatches, six items, length × format × terminology × hedge vocabulary

Every pre-registered quantity came back **exactly zero**:

| Quantity | Value |
|---|---|
| Δ_length | **+0.0000** |
| Δ_format | **+0.0000** |
| Δ_length on correct-content items | +0.0000 |
| Δ_length on incorrect-content items | +0.0000 |
| Range_terminology (c05 notation, c06 hedge vocabulary) | **0.0000** |
| σ_judge (within-variant, 3 replicates) | **0.0000** |

48 scores of exactly 1.00, 24 of exactly 0.00. Not one score in between.

**Why that is a narrow finding, not a clean bill of health.** Every round-1
stimulus was unambiguously right or unambiguously wrong against a crisp rubric.
The judge never returned a PARTIAL and never used the interior of the scale.
Score sensitivity to wording is *undefined* when all scores are saturated: a
ceiling cannot move up, a floor cannot move down. Round 1 establishes that
wording does not **flip a verdict** when correctness is unambiguous, and says
nothing about the regime the original concern came from — exp002's f12 scored
0.6 versus 1.0, in the interior, on two answers carrying the same fact.

The pre-registration permits extending the budget for a principled reason. A
design that cannot express the measured quantity is one. Amendment 1 was written
and committed **before** any round-2 stimulus existed.

## 3. Round 2 — 24 dispatches, four items built to land in the PARTIAL band

Two-component rubrics; each answer satisfies one component fully and the other
only implicitly. Length varied, content constant.

| Item | concise | verbose | Δ | verdicts |
|---|---|---|---|---|
| **p01** Jupiter / composition | 0.50 | **0.00** | **−0.50** | PARTIAL ×3 → **FAIL ×3** |
| p02 Berlin Wall / reunification | 0.50 | 0.50 | 0.00 | PARTIAL ×3 → PARTIAL ×3 |
| p03 1918 flu / why estimates differ | 0.50 | 0.50 | 0.00 | PARTIAL ×3 → PARTIAL ×3 |
| p04 undescribed fungi / anchor | 0.50 | 0.50 | 0.00 | PARTIAL ×3 → PARTIAL ×3 |

**Δ_length = −0.1250** over four items. **σ_judge = 0.0000** — the judge returned
identical scores on all three replicates of every single variant, in both rounds.

### 3.1 The effect is not noise, and it is not uniform

σ_judge is exactly zero across all 96 judgements. The judge is effectively
deterministic on these stimuli. So the p01 movement is **not** sampling noise:
it is a systematic change in how the rubric boundary is applied, driven by
length alone.

It is also concentrated: 1 item of 4 moved, 3 did not. Pooling to a single
Δ_length of −0.125 is the pre-registered statistic and is what the band is
computed from, but the per-item table above is the more informative object.

### 3.2 The mechanism on p01, from the judges' own reasoning

Both variants name Jupiter and describe it only as a "gas giant", never naming
hydrogen and helium. The verbose variant additionally **restates the weak
component** at the end ("…it is the largest, and it is a gas giant").

- Concise judges: *"correctly names Jupiter but only says 'gas giant'… supplies
  only one of the two required components"* → PARTIAL.
- Verbose judges: *"never states its composition is mainly hydrogen and helium…
  this falls short of even a PARTIAL"* → FAIL.

Elaboration that repeats an inadequate component appears to make its inadequacy
more salient, tipping a boundary case downward. This is a hypothesis about
mechanism from n=1 item, offered as a lead, not a result.

### 3.3 Direction, and what it implies about exp001 and exp002

**Verbose scored LOWER.** That direction matters, and it is the direction the
published verbosity-bias work reports for Claude-family judges.

The epistemic directive *lengthens* answers. If this effect generalises, then
the directive conditions in exp001 and exp002 were **deflated** by the grader,
not flattered by it — the opposite of the worry that motivated this calibration.
That would mean those directive contrasts are, if anything, conservative.

**Neither experiment is rescored. Both remain frozen.** This is stated as a
directional caveat on how to read them, on the strength of one item, and nothing
more.

## 4. Band determination

Round 2 governs, because round 1 could not express the quantity.

```
|Δ_length| = 0.1250      →  0.05 ≤ 0.125 < 0.15  →  AMBER
```

Additional pre-specified checks:

- **verbosity_rescues_errors**: NOT triggered. Verbose never rescued a wrong
  answer; on the two round-1 incorrect items, all 24 judgements were 0.00.
  The dangerous direction is clean.
- **judge_noise_floor**: triggered in round 1 on a degenerate `0.0 >= 0.0`
  comparison. Applied anyway — pre-registration is binding and the consequence
  is conservative. See §7.4.

## 5. What this establishes

1. **Wording does not flip a verdict when correctness is unambiguous.** 72
   judgements, four manipulations (length, format, notation, hedge vocabulary),
   zero movement.
2. **Notation is not a trap.** "0.39 million" was converted and passed, three
   times, against a rubric stating a range in plain digits.
3. **Hedge vocabulary is interchangeable.** "range from", "uncertain", "vary",
   "approximation" scored identically.
4. **Verbosity does not rescue a wrong answer.** 24/24 at 0.00.
5. **Length does move boundary cases, downward, on some items.** Δ = −0.50 on
   p01, 0.00 on three others.
6. **The judge is deterministic on fixed input.** σ = 0.0000 over 96 judgements.

## 6. What this does NOT establish

- **Not that the judge is unbiased in general.** Six + four authored items, one
  model, one template. A wider or adversarial stimulus set could find more.
- **Not the size of the effect.** −0.125 pooled rests on one moving item. The
  honest statement is "at least one boundary case in four moved by half a
  verdict step", not "the judge has a 0.125 length bias".
- **Not that σ = 0 means the judge is right.** Perfect self-consistency is
  consistency, not accuracy. A judge that is reliably wrong scores σ = 0 too.
- **Nothing about pairwise comparison**, which this lab does not use.
- **Nothing about with-reasoning judging.** `judge_saw_reasoning` was `false` on
  all 96; that contrast belongs to exp004's independent verifier.

## 7. Mandatory consequences — applied, not discussed

The AMBER band binds three changes. They are implemented in
`docs/EXP003_IMPLEMENTATION_PLAN.md` before any solver trial runs.

**7.1 Length covariate.** Every judged contrast in exp003a/b is reported with
answer length alongside it, and with a score-vs-length relationship for that
cell. Non-negotiable, on every judged table.

**7.2 The 2× rule.** Any judged contrast smaller than **2 × 0.125 = 0.25** in
score units is declared **NOT ESTABLISHED** by rule, not by argument. This is a
high bar and it is meant to be: it is the price of using a continuous judged
score at all.

**7.3 Cell U converts to a forced categorical code.** The uncertainty/abstention
cell's primary outcome is no longer a continuous quality score. It becomes a
forced `response_mode` code — `assert` · `qualify` · `range` · `flag_conflict` ·
`reject_premise` · `abstain` — with anchor examples in the packet. A categorical
code with anchors cannot slide half a step because a sentence was repeated.

**7.4 K=3 for judged trials, carried forward as a binding but questionable
rule.** The round-1 `judge_noise_floor` rule fired on `0.0 >= 0.0` and is
applied because pre-registration is binding and more judging is the safe
direction. **The evidence argues it is unnecessary**: σ_judge = 0.0000 across 96
judgements means replicates added literally nothing. Relaxing it is a legitimate
option — but it must be decided **in exp003a's pre-registration, in writing,
before exp003a runs**, never silently afterwards. It is flagged there as an open
operator decision.

## 8. Artefacts

```
experiments/exp003c_judge_calibration.yaml   pre-registration + Amendment 1
batteries/judge_calibration_v1.yaml          round-1 stimuli (6 items x 4 variants)
batteries/judge_calibration_v1_round2.yaml   round-2 stimuli (4 items x 2 variants)
lab/calibration.py                           packet builder + pre-registered analysis
tests/test_judge_calibration_stimuli.py      content-invariance enforcement
runs/exp003c/judge_packets/                  72 round-1 packets, verbatim as given
runs/exp003c/grades/                         72 round-1 judgements + telemetry
runs/exp003c/grades_round2/                  24 round-2 judgements + telemetry
runs/exp003c/analysis_round1.json            computed quantities, round 1
runs/exp003c/analysis_round2.json            computed quantities, round 2
```

Every judgement carries its score, verdict, reasoning, judge model, judge token
count, judge latency, and `judge_saw_reasoning`. Nothing was discarded.
