# exp001 — final report

**Experiment:** `exp001pilot` (the only exp001 run taken to completion)
**Model under test:** haiku, all conditions
**Battery:** `factual_v1`, 15 questions
**Design:** 2×2 factorial — directive on/off × search on/off
**Completed:** 2026-08-28
**Status:** COMPLETE. 60/60 trials answered, 60/60 graded, 0 ungraded, 0 audit flags.

This report separates four things that are easy to blur and expensive to blur:

> **A — OBSERVATION.** What was measured. Reproducible from the artefacts.
> **B — INTERPRETATION.** What I think an observation means. Defeasible.
> **C — HYPOTHESIS.** A claim this experiment raises but does not settle.
> **D — CONCLUSION.** What the experiment actually justifies. Deliberately short.

Nothing in section D rests on a single trial.

---

## 1. Exact N

| Condition | Directive | Search | Agent | N answered | N graded | N excluded |
|---|---|---|---|---|---|---|
| `baseline` | no | no | closed-book | **15** | 15 | 0 |
| `directive_only` | yes | no | closed-book | **15** | 15 | 0 |
| `search_only` | no | yes (flat budget 3) | web | **15** | 15 | 0 |
| `verified` | yes | yes (route-derived budget) | web | **15** | 15 | 0 |
| **Total** | | | | **60** | **60** | **0** |

One trial per question per condition; no repeats. Every question was attempted
in every condition. No trial was dropped for being inconvenient, ambiguous, or
failed — the two trials that died to a rate limit in the earlier partial run
were re-run, and the record of that failure is kept in
`incomplete_trials.json`.

**Grading provenance.** 37/60 were graded deterministically
(`contains_any`, `numeric`, `trap_detected`). 23/60 escalated to a blind judge.
0 were scored against unverified ground truth.

---

## 2. Headline results — A: OBSERVATION

| Condition | Accuracy | Pass | Partial | Fail | Self-reported searches | Observed tool calls |
|---|---|---|---|---|---|---|
| `baseline` | **60%** | 7 | 3 | 5 | 0 | 0 |
| `directive_only` | **70%** | 10 | 1 | 4 | 0 | 0 |
| `search_only` | **84%** | 11 | 3 | 1 | 18 | 39 |
| `verified` | **78%** | 10 | 3 | 2 | 15 | 30 |

Accuracy is mean score where PASS=1.0, PARTIAL=0.5, FAIL=0.0, over all 15
trials in the condition.

**The single most important number in this table is that `verified` (78%)
scored BELOW `search_only` (84%).** The full epistemic layer did not beat its
own search-only control.

### Cost

| Condition | Δ accuracy vs `baseline` | Extra observed tool calls | Observed calls per extra correct answer |
|---|---|---|---|
| `directive_only` | +10 pts | 0 | **0.0** |
| `search_only` | +24 pts | +39 | 10.8 |
| `verified` | +18 pts | +30 | 11.1 |

---

## 3. Per-question results — A: OBSERVATION

| Question | Category | baseline | directive_only | search_only | verified |
|---|---|---|---|---|---|
| f01 OpenAI CRO | volatile entity | FAIL | FAIL | PASS | PASS |
| f02 UK PM | volatile entity | FAIL | FAIL | PASS | PASS |
| f03 Fed Chair + term | scheduled entity | FAIL | FAIL | PASS | PASS |
| f04 NATO SG + first term | scheduled hybrid | PASS | PASS | PASS | PASS |
| f05 Berkshire CEO | stable entity | **FAIL** | **PASS** | PASS | PASS |
| f06 Tesla Nobel 🪤 | false premise | PASS | PASS | PASS | PASS |
| f07 US-Japan surplus 🪤 | false premise | PASS | PASS | PASS | **FAIL** |
| f08 EU exits 2024 🪤 | false premise | PARTIAL | PASS | **FAIL\*** | **FAIL\*** |
| f09 1847×26 | deterministic | PASS | PASS | PASS | PASS |
| f10 average speed | deterministic | PASS | PASS | PASS | PASS |
| f11 1918 flu deaths | contested range | PARTIAL | PASS | PARTIAL | PASS |
| f12 Twitter CEO 🪤 | stale + renamed | FAIL | FAIL | PASS | PARTIAL |
| f13 Georgia population | ambiguous referent | PASS | PASS | PASS | PASS |
| f14 Saturn moons | moving target | PARTIAL | PARTIAL | PARTIAL | PARTIAL |
| f15 COVID death toll | contested quantity | PASS | PASS | PARTIAL | PARTIAL |

\* f08 in both search conditions is a **known grader artifact**, documented in §7.

### By category

| Category | baseline | directive_only | search_only | verified |
|---|---|---|---|---|
| volatile entity (2) | 0% | 0% | 100% | 100% |
| scheduled entity (1) | 0% | 0% | 100% | 100% |
| stable entity (1) | 0% | 100% | 100% | 100% |
| false premise (3) | 85% | 100% | 67%\* | 38%\* |
| deterministic (2) | 100% | 100% | 100% | 100% |
| contested / moving (3) | 82% | 83% | 55% | 67% |

---

## 4. False-premise detection — A: OBSERVATION

Three questions carry a false premise (f06, f07, f08); f12 carries a stale
referent. Scored as graded:

| Condition | Trap accuracy | Premise explicitly flagged (regex on answer text) |
|---|---|---|
| `baseline` | 70% | 25% |
| `directive_only` | 76% | 50% |
| `search_only` | 75% | 25% |
| `verified` | 45% | 25% |

**B — INTERPRETATION.** The trap numbers are the least trustworthy in this
report. Two of the four trap questions are affected by grading problems (f08 by
the artifact in §7, f07 by a judge decision I consider defensible but harsh),
and n=4 means one question moves the figure by 25 points. The
premise-flagging column is a raw regex over answer text and is a conduct
measure, not a correctness measure. I would not carry any trap number from
this experiment into a decision.

---

## 5. Search and tool-use statistics: self-reported vs observed — A: OBSERVATION

Self-report comes from the solver's `searches_used` field. Observed comes from
the harness's `tool_uses` counter, which the solver does not write.

| Condition | Self-reported total | Observed total | Ratio |
|---|---|---|---|
| `search_only` | 18 | 39 | **2.17×** |
| `verified` | 15 | 30 | **2.00×** |
| Both | 33 | 69 | **2.09×** |

Across 30 search-enabled trials:
- **18/30** self-reports were LOWER than observed tool calls
- **12/30** matched exactly
- **0/30** were higher than observed

Budget compliance, measured two ways:
- By **self-report**: 0 of 30 trials exceeded their stated ceiling.
- By **observed tool calls**: **13 of 30** exceeded it.

**B — INTERPRETATION.** The undercount is one-directional, which is what
distinguishes a systematic definitional gap from noise. The most plausible
reading is that solvers count *search topics* or *WebSearch calls* while the
harness counts every tool invocation including `WebFetch`. Under that reading
nobody lied; the field simply does not measure what its name implies.

**D — CONCLUSION.** Any cost figure in this project derived from
`searches_used` is a **lower bound, roughly half the true tool count**. The
cost columns in §2 are reported both ways for exactly this reason. This is
now a measured property of the instrument, not a caveat.

---

## 6. Judge reliability — A: OBSERVATION

Twelve (question, standard, response) triples were judged twice: once by the
round-1 judge and once, independently, by the tool-enforced `grader-judge`.
Neither judge saw the condition, the model, or the other's verdict.

| n paired | Verdict agreement | Mean abs. score difference | Max abs. difference | Differences ≥ 0.20 |
|---|---|---|---|---|
| 12 | **8/12 = 67%** | 0.133 | 0.40 | 3/12 |

Verdict changed on: `f08-baseline` (FAIL→PARTIAL), `f11-baseline`
(PASS→PARTIAL), `f12-baseline` (PARTIAL→FAIL), `f14-directive_only`
(PASS→PARTIAL).

A thirteenth, accidental replication (`f15-verified`, same judge type, same
packet, two runs) returned PARTIAL/0.55 and PARTIAL/0.45 — same verdict, 0.10
apart. Preserved in `grades_duplicate_runs/`.

**D — CONCLUSION.** **The judge is not a precise instrument.** One judged
trial is worth ±0.13 in score and carries a 1-in-3 chance of a different
verdict label. With 23 of 60 trials judge-graded, a condition difference of
under roughly 8 accuracy points is **inside grading noise** and must not be
read as an effect. This retires H-judge as *not supported*, on measurement
rather than anecdote.

---

## 7. Grading artifact affecting f08 — A: OBSERVATION

Both search-enabled f08 answers were auto-graded FAIL with the reason
`answer asserts rejected content: 'Poland and'`.

The `search_only` answer says:

> "No European Union member states left the bloc in 2024. ... While there were
> political tensions in 2024, particularly between **Poland and** Hungary,
> neither country actually withdrew from the EU."

The `verified` answer says:

> "The premise of this question is false. No European Union member states left
> the bloc in 2024. ... While some EU member states like **Poland and** the
> Netherlands have had political movements discussing potential withdrawal,
> none have actually left."

Both correctly reject the premise. Both were failed for a substring occurring
inside a clause that explicitly says the opposite. The answer key's `reject`
list for f08 contains `"Poland and"`, intended to catch *"Poland and Hungary
left"*, and it cannot distinguish an assertion from a denial.

**This is the same defect class already fixed for f06** (where bare years on
the reject list failed a correct answer). The fix was applied to f06's entries
only; f08's were not audited at the same time.

**I did not rescore it.** exp001 is frozen, and changing scoring criteria after
seeing results is exactly the move that makes an experiment unfalsifiable.
Instead, the sensitivity analysis:

| Condition | As graded | If f08 scored on what its text says |
|---|---|---|
| `baseline` | 60% | 60% |
| `directive_only` | 70% | 70% |
| `search_only` | 84% | **91%** |
| `verified` | 78% | **85%** |

**B — INTERPRETATION.** The artifact costs each search condition 6.7 points and
**does not change the ordering** — `search_only ≥ verified` either way. The
headline finding survives the artifact. The false-premise category numbers do
not, and should be discarded.

---

## 8. Confidence calibration — A: OBSERVATION

| Stated confidence | n | Mean graded score |
|---|---|---|
| high | 30 | **0.93** |
| medium | 19 | **0.66** |
| low | 11 | **0.34** |

Monotonic, well separated, and close to face value. Exactly one high-confidence
trial scored below 0.5 (`verified` f08 — the §7 artifact). Three low-confidence
trials scored 1.0, all of them f07, where the model was right to be unsure
about the numbers and right about the premise.

**B — INTERPRETATION.** On this battery, this model's stated confidence tracked
its graded quality well. This was not a target of the experiment and is the one
result here I would call encouraging without qualification — though it is
measured against a grader whose own reliability is 67% (§6), which limits how
sharp the calibration claim can be.

---

## 9. The cases the experiment was built to look at

### 9.1 f05 — Warren Buffett → Greg Abel

**A — OBSERVATION.** Same model, same closed book, no tools in either arm.

- `baseline`: *"Warren Buffett is the Chief Executive Officer of Berkshire Hathaway."* → FAIL
- `directive_only`: *"Greg Abel is the Chief Executive Officer... Warren Buffett, who had served as CEO since 1965, announced his transition away from the CEO role, with Greg Abel taking over."* → PASS

Ground truth: Abel became CEO 2026-01-01. Both search conditions also passed.

**B — INTERPRETATION.** The directive added no information the model lacked —
the succession was in its training data, since it produced it under the
directive. What differed was which stored answer surfaced: the famous
sixty-year answer or the current one.

**C — HYPOTHESIS (not settled here).** Claim-type framing changes retrieval
priority within parametric memory, favouring recency over familiarity.

**D — WHAT THIS DOES NOT SHOW.** This is **one trial**. It is a vivid
illustration of a mechanism, not evidence that the mechanism operates at
scale. In the same experiment the directive changed *nothing* on f01, f02 and
f03 — three other stale-entity questions where the closed-book model failed
identically with and without the directive. **One example improving does not
mean `directive_only` improves the model.** The condition-level claim rests on
§2 and is qualified in §11, not on this trial.

### 9.2 f14 — the Saturn source conflict

**A — OBSERVATION.** All four conditions scored PARTIAL. Both closed-book
conditions gave 146 with an as-of date. Both search conditions retrieved 293
and dated it June 2026.

The conflict recorded in ground truth (285 traceable vs 293 asserted) was
**independently reproduced by the solvers**: `search_only` surfaced 285 (March
2026), 292 (April 2026) and 293 (June 2026); `verified` reproduced the same
spread and named it in its notes, attributing it to IAU confirmation timing,
and lowered its own confidence to medium.

Judges then failed both search conditions on the same ground — asserting 293
flatly rather than presenting the 285–293 range the standard says is the
correct answer.

**B — INTERPRETATION.** This is the cleanest case in the experiment of the
lab working as designed: a genuine live source conflict, recorded rather than
collapsed, reproduced independently by the system under test, and penalised
consistently when the system flattened it. The `verified` answer came closest
to the standard — it named the disagreement — and still did not put the range
in the answer field where the grader reads.

### 9.3 f11 and f15 — retrieval that disagreed with itself, and with the record

**A — OBSERVATION, f11 (1918 flu).** Same question, same model, same tool, two
conditions, opposite narratives:

- `search_only`: *"estimated between 15-17.4 million ... according to more recent scholarly research, though older estimates cited 50-100 million"* → PARTIAL (0.72)
- `verified`: *"Approximately 50 million to 100 million ... earlier estimates from the 1920s suggested around 21.6 million, but modern reassessments ... indicate substantially higher figures"* → PASS (0.90)

One says modern scholarship revised the number **down**; the other says
modern scholarship revised it **up**. Both cite the search results they got.

**A — OBSERVATION, f15 (COVID).** Both search conditions retrieved an
excess-mortality figure of "over 8.5 million". Ground truth records WHO's
estimate of ~14.9 million excess deaths for 2020–2021 alone. Both closed-book
conditions gave 15–20 million and scored PASS/0.95 and PASS/1.0; both search
conditions gave 8.5 million and scored PARTIAL/0.35 and PARTIAL/0.55.

**B — INTERPRETATION.** On f15, **searching made the answer worse**. Both
search arms converged on the same low figure, which is consistent with a
shared retrieval source rather than independent confirmation — the "AI
stacking" failure the original packet names, observed here inside the
instrument. On f11, retrieval instability alone produced a two-step verdict
swing between conditions that differ only in the directive, which means the
f11 row cannot be attributed to the directive at all.

**C — HYPOTHESIS.** Search-enabled conditions are more vulnerable than
closed-book ones on *contested* quantities, because retrieval surfaces one
confident secondary source and displaces a better-calibrated prior. The
category table is consistent with this (contested/moving: baseline 82%,
directive 83%, search 55%, verified 67%) but n=3.

### 9.4 f10 — the model overruled the classifier

**A — OBSERVATION.** The classifier routed f10 (a pure word problem) as
EMPIRICAL with a 2-search budget — a misroute by the battery's own
`expected_claim_type`. In `verified`, the model responded:

> "the classification suggests it's an empirical claim, but this is actually a
> straightforward mathematical problem"

and spent **0 observed tool calls**. The directive's ROUTING CAVEATS clause
explicitly invites this. All four conditions scored PASS on f10.

**B — INTERPRETATION.** The safe-default asymmetry (unsure → EMPIRICAL) cost
nothing here because the model corrected it. That is the escape hatch working
once, on one question, with a misroute obvious enough to catch.

---

## 10. Infrastructure and sandbox findings

### 10.1 The tool-sandbox bug was real, and the fix is now verified behaviourally

**A — OBSERVATION.** `tools: []` in agent frontmatter grants **every** tool,
not none. Both closed-book solvers and the judge were declared that way in the
first pilot pass and were not sandboxed at all. The test that should have
caught it asked "are any forbidden tools listed?" — an empty list lists
nothing, so it passed.

Verification this session was behavioural, not configural: a canary file with a
random 20-character token, and an explicit operator instruction to *attempt*
the read and report the literal outcome. The first `solver-closed` response
declined to try, citing its own system prompt — a refusal, not a capability
finding, which would have been a false pass. It was re-prompted with its
instructions framed as an unverified assertion and ordered to emit the calls
anyway.

| Agent | Declared tools | Observed `tool_uses` | Canary token returned |
|---|---|---|---|
| `solver-closed` | `TodoWrite` | 0 (2 rounds, 2nd under explicit order) | no |
| `solver-web` | `WebSearch, WebFetch` | 1, WebSearch **succeeded** | no |
| `grader-judge` | `TodoWrite` | 0 | no |

**D — CONCLUSION.** The per-agent tool filter is real and applied: the same
mechanism admitted `WebSearch` and withheld `Read` for `solver-web` in one
run. That asymmetry is the finding. For the two no-tool agents the evidence is
zero observed calls plus self-report — there is no positive demonstration of a
*blocked* call, and there cannot be, since an absent tool gives the harness
nothing to error on. Full protocol in `docs/sandbox_verification.md`.

### 10.2 Mixed sandbox regime within this experiment

**A — OBSERVATION.** `baseline` and `directive_only` (30 trials) ran under
`general-purpose` agents with prompt-level tool constraints, because the
purpose-built agents load only at session start and were created mid-session.
`search_only` and `verified` (30 trials) ran under the verified
tool-enforced `solver-web`. The six `search_only` trials that had run under the
old regime were re-run under the new one; the originals are preserved in
`answers_regime_generalpurpose/`.

**B — INTERPRETATION.** The residual risk is that a closed-book trial searched
undetected. That would inflate `baseline` and `directive_only`, which biases
*against* the search conditions — the opposite direction from the headline
finding, so the finding survives. It does mean the 60% and 70% figures are
upper bounds on closed-book performance.

### 10.3 Retrieval was materially restricted

**A — OBSERVATION.** `WebFetch` was blocked by the environment's egress proxy
for at least: census.gov, statista.com, cdc.gov, stanford.edu,
clevelandclinic.org, fortune.com, wikipedia.org, iau.org, apod.nasa.gov,
worldometers.info, ourworldindata.org, worldpopulationreview.com,
statisticstimes.com. Solvers repeatedly fell back to search-result snippets.

**B — INTERPRETATION.** This is a property of the environment, not the model.
It plausibly contributes to §9.3: solvers could reach secondary aggregators but
not the primary sources (WHO, IAU, Census) that would have settled the
conflicts. **The search conditions were tested with degraded retrieval**, and
their numbers should be read as a floor.

### 10.4 f07 could not be answered by anyone

**A — OBSERVATION.** The 2021 US–Japan trade figure was unreachable in every
search condition; Census was blocked. `search_only` and `verified` both
abstained on the numbers after spending 3 and 2 self-reported searches (5 and 3
observed).

---

## 11. Hypotheses — what this experiment did to each

| Hypothesis | Status after exp001 | Evidence |
|---|---|---|
| **H1** — the layer beats the model alone at comparable cost | **WEAKENED** | `verified` beat `baseline` (+18 pts) but not at comparable cost (0 → 30 observed tool calls), and did not beat its own `search_only` control (78% vs 84%). The "at comparable cost" clause fails outright. |
| **H1a** — the directive alone helps, without retrieval | **NOT ESTABLISHED** | +10 pts (60%→70%), zero tool cost, direction consistent with the earlier partial run (+13). But the gap is close to the ±8-point judge-noise floor from §6, n=15, single run, no repeats. Not refuted either. |
| **H1b** — search accounts for most of the gain | **SUPPORTED** | `search_only` alone reached 84%, above the full treatment. All 5 closed-book failures were current-fact questions; search fixed every one (volatile 0%→100%, scheduled 0%→100%). |
| **H2** — 30-day VOLATILE TTL is right | **UNTOUCHED** | Not tested by this design. |
| **H3** — TTL bucketing generalises | **UNTOUCHED** | Not tested by this design. |
| **H4** — benefit larger for smaller models | **UNTESTED** | haiku only. No cross-model data exists. |
| **H5** — safe-default asymmetry is cheap | **WEAK EVIDENCE, ONE TRIAL** | The one misroute (f10) cost 0 searches because the model corrected it (§9.4). 14/15 questions routed EMPIRICAL, so the classifier is barely discriminating on this battery. |
| **H-judge** — the judge is a reliable instrument | **NOT SUPPORTED** | 67% verdict agreement on 12 paired judgements, mean \|Δscore\| 0.133, max 0.40 (§6). |

---

## 12. D — CONCLUSIONS THE EXPERIMENT ACTUALLY JUSTIFIES

Five, and only five.

1. **Retrieval, not procedure, is what fixed the failures on this battery.**
   Every closed-book failure was a current-fact question, and search fixed all
   of them. No amount of directive recovered a fact the model did not hold.
   This is the strongest and most robust result here — it survives the f08
   artifact, the judge noise, and the mixed sandbox regime.

2. **The full epistemic layer did not beat search alone.** 78% vs 84% as
   graded; 85% vs 91% under the f08 sensitivity analysis. The ordering is
   stable under every correction I applied. The layer's central promise — that
   *routed, budgeted* verification beats naive verification — is **not
   supported by this experiment**.

3. **Self-reported tool use understates real tool use by about 2×, one-
   directionally.** Every cost claim in this project built on `searches_used`
   is a lower bound. Measured, not inferred.

4. **The judge cannot resolve differences smaller than roughly 8 accuracy
   points.** Any future finding in that band, on a judge-graded battery of this
   size, is noise.

5. **The sandbox bug was real, and the fix is behaviourally verified for
   `solver-web`.** The tool filter demonstrably admits one tool and withholds
   another for the same agent in the same run.

### What this experiment does NOT justify

- It does **not** justify saying the epistemic layer works. On its own control
  it lost.
- It does **not** justify saying `directive_only` improves the model. +10 points
  on n=15 with a ±8-point noise floor is suggestive, not demonstrated, and the
  f05 Buffett→Abel case is one trial that must not be generalised.
- It does **not** justify any claim about model size, TTL thresholds, entity
  bucketing, or the abstract battery — none were tested.
- It does **not** justify the trap-detection numbers, which two independent
  grading problems make uninterpretable.
- It does **not** establish that the methodology as a whole works. It
  establishes that the methodology can produce a clean negative result about
  itself, which is a different and more preliminary thing.

---

## 13. Artefacts

```
runs/exp001pilot/
├── EXP001_FINAL_REPORT.md            this document
├── report.md                          machine-generated report
├── manifest.json                      all 60 trials with verbatim prompts
├── results.db                         trials, answers, grades
├── answers/                           60 raw solver outputs + observed tool counts
├── answers_regime_generalpurpose/     6 search_only trials under the old sandbox
├── grades/                            23 round-2 blind judge verdicts
├── grades_round1_generalpurpose/      12 round-1 verdicts (reliability pair)
├── grades_duplicate_runs/             1 accidental within-judge replication
├── judge_packets/                     23 blind packets as given to judges
└── incomplete_trials.json             the 2 rate-limit failures, preserved
docs/sandbox_verification.md           behavioural sandbox probe protocol
```

Every raw solver output retains its self-reported counts, observed tool counts,
retrieved sources, infrastructure notes, and any source conflict it surfaced.
Nothing was overwritten to make a number look better.
