# Next action — RUN the calibration bank to the frozen plan. Do NOT author production items.

> **Updated 2026-09-03 (second pass).** The pre-calibration design reconciliation
> is done. Every quantity that will decide the production size is now defined on
> the arm it must be measured from, and every stopping rule is frozen and
> fingerprinted **before** the first calibration outcome exists. Batch 1 is
> **48 authored → 36 screen-passing items, 228 dispatches, ~$8.44.** The exact
> next action is at the bottom of this file.

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
   **Batch 1: 48 authored → 36 screen-passing items, six dispatches each on
   passers, 228 dispatches, ~$8.44.** Measures `p` (target band **0.90–1.00**),
   **`q_C` on the C arm** (the renamed `c_disp`), `q_D` (1.0 by construction),
   the screen pass rate `s`, and the grader's defect rate on fresh **closed and
   exposed** answers. R=1, fresh context per trial. **Calibration items are
   permanently barred from production**, and the 12/24 development/holdout split
   is what keeps a grader repair from being validated on the answers that
   motivated it.

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

1. Author **48 calibration items** to the recipe in the authoring protocol §2,
   `pool: calibration`, split 16 development / 32 holdout **before any dispatch**
   (the split is on the authored list, not on which items pass the screen).
2. Run **stage 1 only** — the fixed-query divergence screen, one search dispatch
   per authored item, no answerer. Record `s`.
3. Run **stage 2** on screen-passing items only: closed-book answerer,
   query-writer, C search, C exposed answerer, D exposed answerer.
4. **Adjudicate every answer by hand BEFORE running the grader**, and set
   `hand_verdict_recorded_first`. `lab.stage0b_calibration.validate_row` refuses
   a row graded without it.
5. Compute `lab.stage0b_calibration.calibration_statistics`, then
   `lab.stage0b_calibration.decide`. **Compute nothing else**, and change nothing
   in `lab/stage0b_calibration.py`: a statistic invented after seeing the data is
   a stopping rule invented after seeing the data.
6. Do **not** freeze the grader, re-derive power, or author a production item in
   the same session. Those are steps 4–6 and they start from a committed bank.

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
- **Do not use 15 or 20 negative controls.** Neither was derived; both leave a
  generic exposure tax of 0.10 — the entire minimum rejectable primary signal —
  unexcluded. The derived count is 30, and it is a function of the primary n.
- **Do not treat the Stage 0A-M null as evidence of safety.** Its own harm bounds
  are ≤0.113 (availability) and ≤0.312 (restricted to the 8 trials that actually
  retrieved).
- **No Stage 0B production dispatch** until steps 1–6 pass and the contract
  validates as `freeze_ready`. It currently validates as `draft` with 7 open
  fields, which is correct and must stay that way until they are genuinely closed.
