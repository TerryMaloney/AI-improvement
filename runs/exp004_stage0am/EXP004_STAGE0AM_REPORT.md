# Stage 0A-M — objective mechanism assay of retrieval-induced displacement

**Result: NULL, at a realized sensitivity far below the planned sensitivity.**
The preregistered negative retrieval effect was not detected. The assay produced
**2 discordant pairs out of 65 items**, and both are attributable to a grading
interaction rather than to retrieval.

| | |
|---|---|
| Executed | 2026-09-02, under freeze commit `a1f4efb` (single freeze commit across all 130 trials) |
| Dispatches | **130 / 130** — 65 items × 2 arms × R=1 |
| Solver model | `claude-opus-5`, both arms (`claude-haiku-4-5` also appears in both arms' `modelUsage` — symmetric harness background work, not the solver) |
| Dispatch | `claude -p --agent <agent> --model opus --output-format json --allowedTools WebSearch WebFetch` — identical command line per arm |
| Realized tool surface | closed `[]`, retrieval `[WebSearch, WebFetch]` — informational difference exactly `{WebSearch, WebFetch}`, verified live |
| Environment `E` | search-capable, fetch-blocked (matched the pre-recorded `E`) |
| Case-B dispatch failures | **0** · voided pairs **0** · void rate **0.0** |
| Permission denials | 0 |
| Battery / grader | `1ec90754f1de2696` / `10adaf1dac94ea70` |
| Raw outcomes frozen before grading | `65bdf4fd8d523d5c` (ledger `3a86ea6664e1a9c8`) |
| Cost | $2.51 |

---

## 1. Primary analysis — preregistered, exact one-sided conditional binomial, Holm across K=2

| class | n | n00 | n01 | n10 | n11 | D | raw p | Holm rejected | paired RD | harm-rate upper 95% |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| `date_anchored` | 25 | 14 | 1 | 1 | 9 | **2** | 0.750 | **No** | +0.0000 | 0.176 |
| `definition_anchored` | 25 | 0 | 0 | 0 | 25 | **0** | 1.000 | **No** | +0.0000 | 0.113 |

`n10` = closed correct, retrieval incorrect (the harm direction).

**Negative control, outside the Holm family:** `arithmetic_control` n=15,
n11=15, D=0, harm-rate upper 95% 0.181.

### Licensed claim, in the frozen §1.2 wording

> No rejection. We therefore make **no** claim that any authored item in either
> primary class has a lower probability of an objectively correct answer under
> the retrieval-enabled procedure than under closed-book.

### The frozen null language

This is a **failure to detect the preregistered negative retrieval effect at the
planned sensitivity** on this anchored assay. It is **not** evidence that
retrieval is safe, and — see §2 — the realized sensitivity was far below the
planned sensitivity, so it is barely evidence of anything about retrieval.

---

## 2. Why this null is nearly uninformative — the honest reading

The exact test uses only **discordant** pairs. The whole experiment produced two.

| class | both correct | both wrong | discordant |
|---|---:|---:|---:|
| `date_anchored` | 9 | 14 | **2** |
| `definition_anchored` | **25** | 0 | **0** |
| `arithmetic_control` | **15** | 0 | **0** |

Two independent problems destroyed the power the design was sized for:

**(a) `definition_anchored` and the arithmetic control sat at a complete
ceiling.** 25/25 and 15/15 correct in *both* arms. Zero discordance is possible
at a ceiling, so those classes contributed no information whatsoever. The
battery was authored to be a stress sample; for Opus 5 it was not stressful.

**(b) `date_anchored` scored 10/25 in *both* arms — and that is mostly a
grading artifact, not a knowledge failure.** Of the 50 date-anchored trials,
**28 named the correct anchored entity and were still graded incorrect**,
because the frozen `exact_entity` route gives `rejects` precedence and Opus 5
habitually supplies temporal context that names the successor:

> *"As of 1 June 2020, the President of Brazil was **Jair Bolsonaro**. He took
> office on 1 January 2019 and served until 31 December 2022, when he was
> succeeded by **Luiz Inácio Lula da Silva**."* → graded **incorrect**

Those 28 trials were pushed into `n00` (both arms wrong), where they carry no
information. The design's power calculation assumed baseline p≈0.85; realized
baseline accuracy in the only class with any variance was 0.40, and the shortfall
is largely instrumental.

**The two discordant pairs are themselves grading artifacts.** In all four
trials the solver named the correct anchored entity. What differed was only
whether it also mentioned the successor:

| item | arm | accept hit | reject hit | graded |
|---|---|---|---|---|
| a13 | closed | Bolsonaro | **Lula** | 0 |
| a13 | retrieval | Bolsonaro | — | 1 |
| a23 | closed | Sturgeon | — | 1 |
| a23 | retrieval | Sturgeon | **Yousaf** | 0 |

The single `n10` ("harm") and the single `n01` ("help") are both produced by
elaboration style interacting with reject-precedence. **Neither is evidence of
retrieval-induced displacement in either direction.**

The grader was **not** changed after outcomes were visible. This is reported as
the dominant alternative explanation and as a defect to repair before Stage 0B.

---

## 3. Descriptive / mechanism observations

Secondary and descriptive only. None alters the primary sample or claim.

**Retrieval use (ITT — declining to search is still treated).** The retrieval
arm attempted retrieval in **8 of 65** trials; it declined in 57. Among the 8
that did retrieve: 8/8 correct, and their closed partners were also 8/8 correct
— **zero discordance among the trials that actually retrieved.** The treatment
as delivered was overwhelmingly *availability without use*.

**Realized effort by arm** (mediator/cost outcome, not controlled, not equalised):

| arm | median output tok | mean output tok | thinking tok (total) | median wall | cost |
|---|---:|---:|---:|---:|---:|
| closed | 184 | 217 | 3,636 | 6.9 s | $1.06 |
| retrieval | 180 | 235 | 3,223 | 7.0 s | $1.45 |

**Answer length:** closed median 343 chars, retrieval 344. Essentially identical
— unlike exp001/exp002, where the search arm was markedly shorter.

**Prediction scoring** (from the pre-frozen research record):

- **P3** (tool availability changes answers without use) — **not supported, at
  near-zero power.** 57 trials had availability without use and produced 2
  discordant pairs, both grading artifacts.
- **P4** (realized effort loads on the retrieval arm) — **not supported.**
  Output tokens and thinking tokens were near-identical, closed marginally
  higher. Weak test: retrieval was barely exercised.
- **P2** (served-model fallback clusters) — **no fallback occurred.** All 130
  trials on `claude-opus-5`.

---

## 4. Alternative explanations for the null

**OBSERVED**
- Ceiling in 40 of 65 items (definition + arithmetic): no discordance possible.
- Reject-precedence on the entity route marked 28/50 correct-entity answers
  incorrect, symmetric across arms.
- Retrieval actually exercised in 8/65 treated trials.
- `E` = fetch-blocked: page retrieval was unavailable, so the treatment was
  search-only, materially weaker than unrestricted browsing.

**INFERRED**
- The assay's realized sensitivity was far below planned; a true effect of the
  size the design was powered for could plausibly have gone undetected.
- The anchored battery, authored as a stress sample, is not a stress sample for
  this model. The date class retains difficulty only through an instrument
  artifact, not through genuine anchoring pressure.

**SPECULATIVE**
- If the model rarely searches when it is confident, the ITT effect of
  *enabling* retrieval may be near zero on items it already answers well —
  distinct from the effect of *retrieved content*, which this run barely probed.

---

## 5. What must change before Stage 0B

1. **The entity route's reject-precedence rule needs re-specification.** The
   numeric route was already corrected (rejects no longer override a correct
   value). The entity route was deliberately left with precedence so that
   "Scholz, who succeeded Merkel" fails. This run shows the rule cannot
   distinguish that from "Merkel, who was succeeded by Scholz" — a correct,
   well-formed answer. Any fix must be specified and frozen *before* outcomes.
2. **Item difficulty must be re-established against the production model.**
   Ceiling items carry zero information. Difficulty calibration must be
   treatment-blind and must not select on reversal.
3. **Retrieval uptake is itself a design parameter.** An ITT design where 88% of
   the treated arm declines the treatment has little power to detect
   content-driven displacement; Stage 0B's fixed-query arm addresses this
   directly.
