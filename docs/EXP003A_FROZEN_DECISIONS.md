# exp003a frozen decisions

**Status:** open register. Entries are added as instrument work discovers
behaviour that touches the estimand. The register closes at the step-6 preflight;
after that, changing an entry means a new experiment id, not an edit here.

## Why this file exists

Step 3 is an instrumentation build, and instrumentation has a specific hazard:
while making the lab more informative you can quietly change *what is being
measured*. The rule this register enforces:

> Instrumentation can become more informative, but it must not quietly change
> what exp003a is testing. Any behaviour that could affect the **estimand**, the
> **treatment**, the **judge**, or the **outcome definition** is frozen and
> documented as a pre-registration decision before exp003a runs.

So every discovery made during the build lands in one of three buckets:

| Bucket | Meaning | Who may act |
|---|---|---|
| **FROZEN** | Touches estimand/treatment/judge/outcome. Recorded verbatim, changed only by a pre-registration decision taken *before* the data it governs. | operator decision, recorded here |
| **FREE** | Storage, reporting, naming, or analysis that no solver or judge ever sees. | changed freely during the build |
| **OPEN** | Discovered, consequence understood, decision deliberately deferred to exp003a's pre-registration. | must be closed before step 7 |

A defect found in the instrument is **not** automatically a bug to fix. If
exp001/exp002 measured the defective instrument, the defect *is* the treatment
those experiments estimated. Silently repairing it makes exp003a incomparable to
them while looking like it did not.

---

## FD-1 — Closed-book directive packets contain a search budget for tools that do not exist

**Bucket:** FROZEN (touches treatment)
**Found:** step 3 reconnaissance, reading `runs/exp001pilot/packets/exp001pilot-f05-directive_only-haiku-r1.md`
**Scope:** every `directive_only` packet ever generated — 15/15 in exp001pilot,
and the corresponding cells of exp001. Verified by
`grep -c "SEARCH BUDGET" runs/exp001pilot/packets/*directive_only*.md` → 1 on every file.

### The defect

A `directive_only` trial is closed-book (`allow_search: false`) **and** directive-injected
(`inject_directive: true`). `lab.trials.build_prompt` emits, in the same prompt:

```
TOOLS: you have none. No search, no browsing, no files. Answer from what you
already know.
...
Set `searches_used` to 0.
```

and then, inside the injected guidance block:

```
SEARCH BUDGET: 2 searches. This is a ceiling, not a target — do not spend
searches you do not need, and do not exceed it. If you run out with the
question unresolved, say what is unresolved rather than filling the gap with
a guess.
```

**Cause:** `build_prompt` chooses `CLOSED_BLOCK` from `condition.allow_search`,
but appends `Route.prompt_block()` from `condition.inject_directive`, and
`Route.prompt_block()` unconditionally emits its budget line. The two branches
were never reconciled because no reviewer read a closed *and* directive-injected
packet end to end. The `WEB_BUDGET_BLOCK` path was written with an explicit
comment about not stating the budget twice; the closed path was not considered.

### Why it is not simply a bug

It is a contradiction in the *treatment text* of a condition that exp001 and
exp001pilot already estimated. `directive_only` as measured = "the epistemic
directive, including a budget line for tools the solver does not have". Removing
the line changes the treatment. Both readings are defensible and neither may be
chosen silently:

- **Keep it** — exp003a's `directive_only` stays comparable to exp001's.
- **Remove it** — exp003a's `directive_only` becomes a cleaner test of the
  directive, and is no longer the same treatment exp001 estimated.

### Decision

**FROZEN AS-IS for exp003a.** `Route.prompt_block()` is not changed. Reasons:

1. exp003a's job is mechanism disambiguation against exp001/exp002's observed
   effect. Changing the treatment mid-programme means a null result cannot
   distinguish "the mechanism does nothing" from "we tested a different thing".
2. The contradiction is a *confound with a name*, which is better than a
   confound that has been repaired out of view. It is now an explicit competing
   explanation for any `directive_only` result: an instruction that references
   absent tools may reduce compliance with the whole block.
3. exp003a already contains the condition that isolates it. `A_only` carries a
   single directive component and no budget line; the `A_only` vs `directive_only`
   contrast therefore carries this confound as one of its differences, and that
   difference is now documented rather than latent.

**Consequences bound now, not later:**

- **FD-1a.** Any exp003a reporting of a closed-book `directive_only` or
  `search_directive` result must cite FD-1 in the caveats. Enforced by a report
  test, not by memory.
- **FD-1b.** Cells L and R (closed-book, deterministic) are the cells where this
  bites hardest, since no budget is spendable there at all. Their per-item specs
  must predict solver behaviour *under the contradictory prompt*, which is the
  prompt they will actually receive.
- **FD-1c.** A repaired variant is **not** added to exp003a as an extra
  condition. That would spend solver budget on an instrument question inside an
  experiment designed for a mechanism question, and would inflate the condition
  count past what the power table supports. It is logged as a candidate for a
  later dedicated instrument experiment.

---

## FD-2 — `searches_used` appears in prompt text as well as in storage

**Bucket:** split — FROZEN in prompts, FREE in storage/reporting
**Found:** step 3, scoping the deprecation the operator asked for

`searches_used` occurs in nine places. Four are inside the experimental
instrument and five are not:

| Location | Seen by a solver? | Bucket |
|---|---|---|
| `lab/trials.py` `RESPONSE_SCHEMA` | yes | **FROZEN** |
| `lab/trials.py` `COMMON_PREAMBLE` | yes | **FROZEN** |
| `lab/trials.py` `CLOSED_BLOCK` | yes | **FROZEN** |
| `lab/trials.py` `WEB_BUDGET_BLOCK` | yes | **FROZEN** |
| `lab/store.py` column name | no | FREE |
| `lab/ingest.py` payload key read | no (reads what the solver emitted) | FREE to re-map, FROZEN as a wire key |
| `lab/grading.py` conduct field | no | FREE |
| `lab/report.py` cost metric | no | FREE |
| `tests/test_pipeline.py` fixtures | no | FREE |

### Decision

The deprecation is carried out on the **storage and reporting side only**.

- The JSON key solvers are asked to emit stays `searches_used`. Renaming it in
  `RESPONSE_SCHEMA` would change the prompt, and a self-report field's *name* is
  plausibly load-bearing on what gets reported — "searches used" invites a count
  of searches; a renamed field invites something else. That is a treatment
  change wearing a refactor's clothes.
- The stored column becomes `searches_self_report`, the report labels it as a
  self-report, and **no cost figure is computed from it**. Cost is computed from
  `tool_calls_observed`, which comes from the harness.
- The gap between the two is retained and reported as its own measurement — does
  the solver know what it did? — and is never reconciled into a single number.

This satisfies "deprecate `searches_used`" in the sense that matters: it can no
longer reach a cost conclusion. It stays in the prompt because the prompt is the
instrument.

---

## FD-3 — Frozen result databases are never migrated

**Bucket:** FREE (no solver or judge sees a schema), but load-bearing on the
"do not rewrite history" instruction, so recorded here.

`runs/exp001pilot/results.db` predates the R2 telemetry columns. Calling
`Store.joined()` on it raises `sqlite3.OperationalError: no such column:
a.tool_calls_observed`. That error is mechanical proof exp001 was never
rewritten in place, and it is worth more than the convenience of a migration.

**Decision:** the store is made **read-adaptive** rather than the old databases
being migrated. `Store` introspects `PRAGMA table_info` and projects missing
columns as `NULL AS <name>`, so:

- old databases open and read with their original bytes untouched — no `ALTER`,
  no rewrite, no backfill;
- new databases get the honest column set;
- one downstream code path serves both, and a column absent in an old run reads
  as "not measured" rather than as a crash or, worse, a zero.

`NULL` and `0` must never be conflated here. "exp001 did not record tokens" and
"exp001 used zero tokens" are different claims and only one of them is true.

---

## FD-4 — Reachable retrieval states are an environment fact, probed per experiment

**Bucket:** FROZEN (touches outcome definition)
**Probe artefact:** `runs/egress_probe/probe-2026-08-28.json`, re-run during step 3
before cell D was planned.

### What was observed, not assumed

| Capability | Result |
|---|---|
| WebSearch | **works.** One query returned nine ranked results with titles, URLs and snippet text, carrying a figure readable from the snippets alone. |
| WebFetch | **blocked.** Three attempts on three unrelated hosts (`en.wikipedia.org`, `www.statice.is`, `example.com`) each returned `EGRESS_BLOCKED`. Three distinct hosts rules out a per-domain block. |

### What that makes reachable

The four states are **not one ladder**, and this environment is the case that
proves it. Implementing them as rungs produced an immediate false alarm: a solver
that reads a claim off a search snippet has attained `CLAIM_EVIDENCE_MATCH`
while never attaining `SOURCE_ACCESS`, which a linear model must call either
impossible or a sandbox breach. It is neither — it is the ordinary search-only
case, and it is exactly the weak-evidence situation worth naming.

| State | Reachable here? | Why |
|---|---|---|
| `RETRIEVAL` | yes | search returns results |
| `SOURCE_ACCESS` | **no** | no document can be opened |
| `CLAIM_EVIDENCE_MATCH` | yes, at `SNIPPET` depth only | a claim can be matched in snippet text |
| `VERIFICATION` | **no** | corroboration is counted only at document depth |

### Decision

1. Each state is an independent predicate, and a trial records the **set** it
   attained, not just a headline. `SOURCE_ACCESS` missing beneath a
   `CLAIM_EVIDENCE_MATCH` headline stays visible in the record.
2. A claim-evidence match carries its **depth** in the label itself
   (`CLAIM_EVIDENCE_MATCH@SNIPPET`), so no report can print the state without
   the qualifier that makes it weaker.
3. Corroboration counts only at document depth, and only across **declared,
   distinct** origins. Undeclared provenance counts for nothing: "we did not
   check" must never read as "they were different sources".
4. **No conclusion, positive or negative, may be drawn about `SOURCE_ACCESS` or
   `VERIFICATION` from any trial in this environment.** "Verification did not
   help" is not a licensed reading of an environment where verification could not
   occur. The licensed null is about retrieval at snippet depth. Enforced by
   `lab.states.negative_conclusion_licensed`, which a report must consult before
   naming a state.
5. Ingest refuses to assess a retrieval state when no probe is committed, rather
   than assessing against an assumed environment. A state computed against an
   assumption looks measured and is not.

## FD-5 — The placebo carries no numeric quota

**Bucket:** FROZEN (touches treatment)

The real directive ends with `SEARCH BUDGET: N searches...`. The obvious way to
match it structurally is to give the placebo its own numeric instruction — "cover
at least three considerations", "write two paragraphs".

**Decision: forbidden.** exp003c measured that response length moves a judged
score across a rubric boundary (Δ_length = −0.125, AMBER). A placebo containing a
length or count instruction would manipulate the exact variable exp003c just
showed matters, so `directive_placebo` would differ from `baseline` on *response
length* as well as on *instructed-ness* — and the placebo exists precisely to
hold everything except the epistemic mechanism constant.

The budget line is matched instead with inert prose of equal length, equal
formatting, and no quantity in it. The placebo's own word count is matched to the
directive's per question (±10%) by *selection among pre-written variants*, never
by instructing the solver about length.

---

## FD-6 — Judge configuration is frozen at its exp003c setting

**Bucket:** FROZEN (touches judge)

exp003c measured σ_judge = 0.0000 across 96 judgements. That determinism is a
property of *this* judge template, model, and packet construction. Any change to
`lab.grading.JUDGE_TEMPLATE`, the judge model, or whether the judge sees solver
reasoning invalidates the calibration and requires re-running exp003c before
exp003a's judged cells.

**Decision:** the judge is frozen as calibrated. The four exp003c mitigations
(C1 length covariate, C2 the 0.25 not-established rule, C3 cell U as forced
categorical, C4 K=3) apply as bound in `docs/EXP003_IMPLEMENTATION_PLAN.md` §11.1.

---

## OPEN-1 — C4 (K=3 for judged trials)

**Bucket:** OPEN — deliberately deferred to exp003a's pre-registration.

C4 fired on a degenerate trigger: the rule `sigma_judge >= mean_item_range`
evaluated `0.0 >= 0.0` true. Round 2 then measured σ_judge = 0 across 96
judgements, i.e. the judge is deterministic on fixed input, so triplicate judging
of an identical packet buys nothing except three identical scores.

The case for relaxing to K=1 is that determinism was measured, not assumed. The
case against is that pre-registration is binding, exp003a's judge packets are not
byte-identical to exp003c's stimuli, and K=3 errs conservative.

**This decision is not taken during step 3.** It is taken in exp003a's
pre-registration, in writing, before exp003a's judge packets exist — per the
operator instruction: *leave it as an explicit exp003a preregistration decision;
don't silently alter it now.* The implementation therefore keeps K configurable
and defaults it to 3.

---

## OPEN-2 — Task labels are declared, not inferred

**Bucket:** OPEN, closing at step 4.

The six task-label axes are properties of an **item**, fixed when the item is
authored, and are inputs to the analysis plan (they define which cell an item
belongs to and which contrast it can support). Nothing may infer them from an
item's *results*.

Step 3 provides the vocabulary, the validation, and the operational tests. Step 4
assigns them to `diagnostic_v1` items and commits them **before** any condition
runs. A label changed after data exists is a re-analysis and must be reported as
one.

---

## FD-7 — The placebo's effect on response length is unverified until exp003a

**Bucket:** OPEN, closing at exp003a's first analysis.

FD-5 keeps explicit quantity instructions out of the placebo, and a test asserts
that no pool variant anywhere contains a numeral or a size term
(`length`, `paragraph`, `concise`, `thorough`, …). That is a check on the
*stimulus*. It is not a check on the *response*.

What actually matters is whether `directive_placebo` induces answers of a
different length from `baseline`, because exp003c measured that length moves a
judged score across a rubric boundary. That cannot be measured without solver
trials, and solver trials are not permitted before the preflight — so it cannot
be settled during step 3, and claiming the keyword test settles it would be
overclaiming.

**Bound now, before the data exists:**

exp003a's first analysis reports mean answer length by condition. If

    |mean_len(directive_placebo) − mean_len(baseline)|  >  |mean_len(directive_only) − mean_len(baseline)|

then the placebo moved response length at least as much as the treatment did,
the placebo has failed as a length control, and **every judged contrast against
`directive_placebo` is reported with that caveat attached**. The deterministic
cells are unaffected, since length does not enter an objective grader.

This is a pre-registered diagnostic with a pre-committed consequence, not a
promise to look.

---

## FD-8 — Historical reports are not re-rendered under new code

**Bucket:** FREE, recorded because it touches the "do not rewrite history" rule.

`lab/report.py` changed in step 3: cost figures now come from
`tool_calls_observed` instead of the solver's `searches_used`. Re-running
`python -m lab report exp002` would overwrite `runs/exp002/report.md` with
different numbers — a re-analysis presented as the original record.

**Decision:** stored reports stay as written. The new code was exercised against
exp002's database by rendering to memory and reading the output, never by writing
it back. Any future re-analysis of a frozen run is written to a new filename that
says so.

What that render surfaced is worth recording, because it is the evidence for
FD-2's deprecation rather than an argument for it:

| exp002 condition | Observed tool calls | Self-reported searches | Gap |
|---|---|---|---|
| `baseline` | not measured | 0 | — |
| `directive_only` | not measured | 0 | — |
| `search_only` | 39 | 18 | +21 |
| `verified` | 30 | 15 | +15 |
| `verified_flat` | 37 | 18 | +19 |

Every search-enabled condition under-reports by roughly half, and consistently.
The two quantities are not definitionally identical — a tool call need not be a
search — so this is not by itself evidence of misreporting. It **is** evidence
that the self-reported column cannot carry a cost conclusion, which is all the
deprecation requires. Note also that the closed conditions read `not measured`
for observed calls while reading `0` for self-report: exactly the `NULL`/`0`
distinction FD-3 exists to preserve, visible on real data.

---

## FD-9 — Three condition texts do not exist yet, and are treatments

**Bucket:** OPEN, closing before exp003a dispatches. Found during step 4 while
writing per-condition predictions.

`diagnostic_v1` names nine conditions. Six are built and frozen. Three are not,
and each is a **treatment**, so each needs its exact text or protocol committed
before the trials it governs — not assembled at dispatch time.

| Condition | Status | What must be frozen |
|---|---|---|
| `A_only` | **not built** | The memo defines it as "epistemic framing alone, on a length-matched carrier" (R-2). Operationally that is the routed directive's opening framing sentence, without the procedural bullets, the freshness section or the budget line, carried on a block length-matched to the full directive by the same generator that matches the placebo. The exact carrier text is a treatment and is not yet written. |
| `search_selfcheck` | **not built** | Two dispatches: answer, then a self-review of the solver's own answer. The review prompt is a treatment. What the reviewer sees — its own answer only, or the answer plus the retrieved snippets — changes what the condition measures and must be decided in writing, not at runtime. |
| `search_independent` | **not built** | Three dispatches: generator, claim-blind evidence gatherer, separate verifier. "Claim-blind" is the load-bearing property and needs an operational definition: the gatherer must not be told which claim it is gathering for, or the arm collapses into `search_selfcheck` with extra steps. |

### Decision

All three are written and committed as part of step 7's build, **before** any
dispatch, and their texts are appended to this register at that point. Until
then, `diagnostic_v1`'s predictions for those conditions are predictions about
a treatment whose wording is not fixed, and that is stated here rather than
discovered later.

Two constraints bind them now:

1. **`A_only` must be length-matched by the same machinery as the placebo.**
   If it is shorter than `directive_only`, the `A_only` vs `directive_only`
   contrast is confounded with length — reintroducing E4 into the one contrast
   built to exclude it.
2. **Neither multi-dispatch arm may be described as verification.** Both are
   snippet-level checking (FD-4). Their dispatch counts must be reported, since
   `search_independent` costs three dispatches per trial and a cost comparison
   that counts it as one is wrong by a factor of three.

---

## FD-10 — Two trap strings were removed for a defect the lab had already met

**Bucket:** FREE (answer-key craft), recorded because the reasoning generalises.

Step 4's answer key initially carried two `reject` strings that the existing
`test_answer_key_integrity` C1 rule refused. Investigating rather than
overriding it found that one was genuinely unsafe:

> `"because the coriolis effect causes water to spin"` appears **verbatim inside
> a correct denial** — "...not because the Coriolis effect causes water to spin
> down the drain...".

That is the same defect that made a correct answer about Tesla's Nobel
nominations FAIL in exp001, and which `grade_trap_detected`'s marker-first
ordering was rewritten to survive. A reject string a right answer can contain is
worse than no reject string, so D02 now has none and relies on markers plus
judge fallback. D05's was rephrased so that a denial cannot contain it
contiguously.

Separately, every cell-D trap marker was rewritten from a bare topic word
(`photoelectric`, `madman`, `too weak`) into a relational phrase
(`was for the photoelectric effect`, `is spoken by a madman`, `is far too
weak`), and a bare year was removed outright. The rule was not relaxed to admit
the markers; the markers were made to satisfy the rule.
