# Next action — RUN the calibration bank to the frozen plan. Do NOT author production items.

> **Updated 2026-09-03 (fourth pass — pre-dispatch infrastructure repair).** The
> calibration-run attempt **stopped before authoring an item, dispatching once, or
> spending a cent**, because the committed ledger could not carry the key its own
> adjudication needs: a boolean or numeric row raised `KeyError` on
> `reference_verdict`, and the same alias pair was simultaneously being matched
> against search prose where `"no"` hits inside `"not"`. Both are repaired.
>
> **The answer key and the exposure-screen specification are now two objects**
> (`lab/stage0b_keys.py`), route-aware, separately validated and separately
> fingerprinted. The **calibration runner exists** and is committed before the
> first dispatch. **Route composition is precommitted**, which forces a 56-item
> holdout and tightens the grader bound to 0.052.
>
> **Batch 1 is now 96 authored → 72 screen-passing, 528 dispatches, ~$21.48**,
> with a human adjudication prerequisite of roughly **43 answers**. No item has
> been authored and no key has been verified.

Stage 0A-M is finished and independently reviewed. **Steps 1 and 2 of the chain
below are DONE as of 2026-09-03**: the searcher/exposure harness is built and
passes a 14-check live correspondence gate with 0 unobservable, and the
retrieval-divergence probe is implemented and has run on canaries. The decision
is now **A — READY TO AUTHOR/RUN THE CALIBRATION BANK**
(`docs/EXP004_STAGE0B_DESIGN_DRAFT.md` §12.7; the older decision B at §11 stands
as the correct call on the evidence it had).

**The next step is step 3 and nothing else.** Authoring production items against
an unvalidated recipe is exactly the mistake Stage 0A-M made — its battery turned
out to contain **zero** items Opus 5 answers incorrectly, and 130 dispatches were
spent discovering that. The bank is what validates the recipe.

## The dependency chain, in order. Do not start step N+1 before step N passes.

1. ~~Build the searcher agent and the results-injection harness.~~ **DONE
   2026-09-03.** `lab/stage0b_search.py`, `lab/stage0b_harness.py`,
   `lab/stage0b_runtime_gate.py`; evidence
   `experiments/exp004_stage0b/runtime_correspondence.json` (14/14 PASS, 0
   UNOBSERVABLE, 6 dispatches, $0.19).
   **What building it changed:** "return the result block verbatim" was false —
   see design draft §12. The recorded artifact is now the runtime's own
   `tool_result`, read out of `--output-format stream-json`, not the searcher
   model's retelling. The treatment is renamed
   `runtime_exposed_search_result_block_exposure`; the measured block contains
   **no snippets**, only titles/URLs plus a model-synthesised answer plus a
   runtime instruction that is stripped before injection.

2. ~~Implement the retrieval-divergence probe.~~ **DONE 2026-09-03.**
   `lab/stage0b_divergence_probe.py`; evidence
   `runs/exp004_stage0b_instrument/divergence_probe.json`. Canaries only: 4/4
   executed, 4/4 queries byte-faithful, 4/4 pre-recorded predictions matched, 3
   divergent. No solver, no answer, no outcome — asserted in the artifact.

3. **← YOU ARE HERE. Run the calibration bank** to the frozen plan in
   `docs/EXP004_STAGE0B_BATTERY_AUTHORING_PROTOCOL.md` §3.
   ~~(≥3× production size) ... Closed-book ... establishes `p` and the realized
   `c_disp`.~~ **SUPERSEDED 2026-09-03 (design draft §13.2–13.3):** the ≥3× rule
   had no derivation and was wrong in both directions, and closed-book dispatches
   cannot measure three of the four things the bank exists for.
   **Batch 1: 64 authored → 48 screen-passing items, six dispatches each on
   passers plus the screen, 400 dispatches, ~$14.32.** Measures `p` (band
   **0.90–1.00**, on the point estimate), **`q_C` on the C arm** (the renamed
   `c_disp`), **`r_D`** (the arm-D re-execution rate — *not* 1.0; see design draft
   §14.2), the screen pass rate `s`, and the grader's defect rate on fresh
   **closed and exposed** answers, **one observation per item**. R=1, fresh context
   per trial. **Calibration items are permanently barred from production**, and the
   16/48 authored development/holdout split is what keeps a grader repair from
   being validated on the answers that motivated it.

4. **Freeze the grader** (`lab/grading_v2.py`) only after the calibration bank
   has exercised its span parser on answers that are not Stage 0A-M's. It has so
   far been validated against 130 answers from a battery it was designed after,
   which is not independent evidence.

5. **Re-derive power from the measured `p` and `q_C`**, replacing the assumed
   design point in `runs/exp004_stage0b_design/power_simulation.json`. If the
   measured values move the required n materially, the design changes before any
   production dispatch, not after.
   **This step now has a second, binding part.** Run
   `lab.stage0b_cvd.authorize()` on the measured `p`, δ_C and δ_D. On the
   *assumed* design point it FAILS: C-vs-D at n=50 has power 0.60 against the
   preregistered gap of 0.20, and needs n=76; under a Stage 0A-M-like symmetric
   20% grader error it is unpowered at every n up to 240. If it fails on the
   measured values too, **the query-construction claim is withdrawn before the
   run** and C-vs-D is reported descriptively. Arm D is retained either way.

6. **Only then** author production items, freeze every fingerprint listed in the
   authoring protocol §5 — **including the freeze/grade/analyse driver, which
   must be committed before the first dispatch** — and re-run the causal-contract
   validator until the Stage 0B contract passes as `freeze_ready`.

## The exact next action for the calibration-run session

0. **Confirm the human adjudication prerequisite first.** Roughly **43 of 216**
   batch-1 answers will escalate to Terry, and they must be adjudicated **before**
   the candidate grader is run on them. If that capacity is not available, do not
   dispatch the bank — skipping adjudication is not the alternative, because a
   defect rate measured against the grader's own rule is not a measurement.
1. Author **96 calibration items** to the recipe in the authoring protocol §2,
   with a **typed answer key (§2.2)**, a **separate typed screen spec (§2.3)** and
   **verified key sources (§2.4)** per item. `pool: calibration`. The
   development/holdout split and the **route quotas** (§3.4a: 0.50 / 0.25 / 0.25,
   with a 14-item per-route floor in the holdout and boolean polarity balanced) are
   fixed on the authored list **before any dispatch**.
   Run `python -m lab.stage0b_calibration_runner --stage validate --bank <file>`
   until it reports zero problems. It **refuses to dispatch against an invalid
   bank**, and it will not repair one.
2. `--stage screen` — the fixed-query divergence screen, one search dispatch per
   authored item, no answerer. Record `s`.
3. `--stage answer` — screen passers only, six dispatches: closed-book answerer,
   query-writer, C search, **D production search** (a second, fresh fixed-query
   execution — this is the block arm D's answerer receives), C exposed answerer, D
   exposed answerer. The runner is resumable: a dropped session costs the dispatch
   in flight and nothing else.
4. `--stage export-queue` — deterministic reference adjudication, then the frozen
   human queue with its fingerprint. Send every escalation to Terry; import with
   `--stage import-verdicts --adjudicator Terry`. `authorize_grading()` is the only
   door to grading and stays shut while any case is open.
5. Compute `lab.stage0b_calibration.calibration_statistics`, then
   `lab.stage0b_calibration.decide`. **Compute nothing else**, and change nothing
   in `lab/stage0b_calibration.py` or `lab/stage0b_adjudication.py`: a statistic
   invented after seeing the data is a stopping rule invented after seeing the
   data.
6. Do **not** freeze the grader, re-derive power, author a production item, or fix
   the negative-control count in the same session. Those are steps 4–6 and they
   start from a committed bank.

## Traps already closed — do not reopen

- **Do not repair the Stage 0A-M grader, ledger, analysis or report.** They are
  frozen and the run is scored under them. The repair lives in `grading_v2.py`
  and applies to Stage 0B only.
- **Do not cite `analysis.json`'s `retrieval_failure_rate`.** It reports
  `attempted_retrieval: 0` because `analyse_run` fed it empty tuples. The true
  value is 8. Bind Stage 0B's retrieval fields to `num_turns` and
  `modelUsage[*].webSearchRequests` — `usage.server_tool_use` is 0 in all 130
  trials and is not a usable indicator on this harness path.
- **Do not add an optional-retrieval arm.** At Stage 0A-M's realized uptake it is
  unpowered at every n ≤ 120, and the question it answers is already answered.
- **Do not make items harder to escape the ceiling.** At baseline ≤0.65 the
  design is unreachable at n ≤ 120, because repairs cancel harms in a one-sided
  paired test. The target band is high, not middling.
- **Do not reuse `date_anchored` or `definition_anchored` for confirmation.** Both
  are production-exposed and at complete ceiling. `date_anchored` is retained as
  a grader regression corpus only.
- **Do not call the treatment "web retrieval", and no longer call it
  "search_snippet_exposure" either.** Measured 2026-09-03: the runtime block
  contains no snippets. The treatment is
  `runtime_exposed_search_result_block_exposure`. On the Stage 0B path WebFetch is
  not granted at all, so `E` is search-capable and fetch-*absent by construction*
  as well as proxy-blocked. No pooling across environments.
- **Do not treat a search-artifact hash as a reproducibility guarantee.** Two
  dispatches of an identical query return different bytes; only the `Links:` array
  was stable. The hash is per-trial provenance.
- **Do not read `usage.server_tool_use` as a search indicator.** It reports 0 on a
  dispatch that demonstrably searched. Use
  `sum(modelUsage[*].webSearchRequests)` over ALL models — WebSearch is billed to
  `claude-haiku-4-5`, not to the solver.
- **Do not count the Stage 0A-M grader defect as a prospective R1′ confirmation.**
  The frozen table classifies `grader` as checked, symmetric, R1′-**low**; a defect
  there is `HURT_BOTH`. Corrected 2026-09-03 in
  `experiments/meta_r1r2/observation_2026-09-03_grader.md`. Prospective
  confirmations of R1′ remain n=1.
- **Do not re-derive a calibration size from a multiplier.** "≥3× production" was
  asserted in four documents and computed in none, and it was wrong in both
  directions at once: too small to measure `q_C`, `q_D` or the grader on exposed
  answers, and too large under the realized six-dispatch structure. The bank is
  sized from the decisions it resolves (authoring protocol §3.1).
- **Do not substitute the fixed-query divergence rate for the C-arm rate.** They
  are different queries producing different blocks. The primary A-vs-C power
  calculation reads `q_C`, which is why a query-writer dispatch and a C search are
  in the per-item structure at all.
- **Do not size production as though the grader bound were zero.** At n=50 the
  design holds 80% power only while `g_one` ≤ 0.014, and bounding that needs 213
  clean pairs — four times the run. Production is sized AT the achievable bound;
  the recommended n=50 in design draft §7.2 is superseded.
- **Do not claim C-vs-D isolates retrieved content.** The runtime block echoes the
  query, so C and D differ through the query text, the synthesised answer and the
  link list at once. The claim is narrowed to the total effect of the
  query-construction procedure, and decomposition is a named follow-on.
- **Do not use 15 or 20 negative controls, and do not treat 30 as final.** Neither
  of the old numbers was derived; both leave a generic exposure tax of 0.10 — the
  entire minimum rejectable primary signal — unexcluded. The rule is derived and
  the count is a **function of the final primary n** (50→30, 72→42, 90→54), which
  does not exist until the bank has run. No control item is authored until then.
- **Do not let the answer key and the screen spec become one field again.** They
  are two scientific objects. The key decides whether an ANSWER is correct; the
  screen decides whether a SEARCH SUMMARY asserts the displacing claim. They
  coincide only on `exact_entity`, and collapsing them cost this design a whole
  run's worth of authoring before the pre-dispatch check caught it.
- **Do not screen a boolean item on bare polarity.** `"no"` matches inside
  `"not"`; `"yes"` never appears as a claim. Use premise-bearing propositions, and
  keep the negation guard — without it the screen fires on correct denials.
- **Do not screen a numeric item on a bare numeral.** It matches years, ranges and
  citations. Use subject-term proximity with excluded contexts.
- **Do not declare C1(c) a universal rule.** It governs strings matched against a
  MODEL ANSWER. The Stage 0B numeric screen matches SEARCH PROSE through a
  structured mechanism. S1 is the Stage 0B rule.
- **Do not author an entity-only bank.** The only grader defect ever measured here
  was on the boolean route (`a09`). An entity-only bank cannot detect a recurrence
  while reporting a bound that looks complete.
- **Do not let a key-verification query become a fixed experimental query.** That
  optimises the treatment against the search index using observations made while
  building the key.
- **Do not repair an ambiguous key by picking the most reasonable answer.** It
  fails authoring mechanically, with its reason recorded.
- **Do not pool (A,C) with (A,D) into two grader observations.** They share the
  closed-arm verdict completely, so one closed-arm defect gets counted twice; the
  resulting bound is narrower than the evidence supports, and for an instrument
  defect that under-sizes production. The unit is the ITEM, and the bound is the
  (A,C) pair alone.
- **Do not say `q_D = 1.0 by construction`.** The screen tests one execution, the
  artifact is not reproducible, and arm D re-runs its query at answering time, so
  the screened block is never the injected block. The parameter is `r_D` and it is
  measured. A non-divergent re-execution is the measurement, not a failure.
- **Do not require the p lower bound to clear 0.90.** That certification rejects a
  recipe sitting on the design point 5 times in 6 at n=36. The band is checked on
  the point estimate; sizing uses the lower bound.
- **Do not let the candidate grader produce its own ground truth**, and do not let
  the orchestrating model adjudicate an answer whose grader verdict it has already
  seen. Both are schema errors.
- **Do not call any Stage 0B threshold "preregistered".** Stage 0B has no frozen
  preregistration; these are pre-calibration commitments.
- **Do not treat the Stage 0A-M null as evidence of safety.** Its own harm bounds
  are ≤0.113 (availability) and ≤0.312 (restricted to the 8 trials that actually
  retrieved).
- **No Stage 0B production dispatch** until steps 1–6 pass and the contract
  validates as `freeze_ready`. It currently validates as `draft` with 7 open
  fields, which is correct and must stay that way until they are genuinely closed.
