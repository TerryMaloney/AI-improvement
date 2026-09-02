# Next action — build the Stage 0B instrument, in this order. Do NOT author production items.

Stage 0A-M is finished and independently reviewed. Stage 0B is designed and the
decision is **B — MORE DESIGN WORK REQUIRED**
(`docs/EXP004_STAGE0B_DESIGN_DRAFT.md` §11).

**The single reason A was not chosen:** the item recipe cannot be validated,
because the calibration bank cannot be run, because the retrieval-divergence
probe is unimplemented, because the searcher and results-injection harness do
not exist. Authoring production items against an unvalidated recipe is exactly
the mistake Stage 0A-M made — its battery turned out to contain **zero** items
Opus 5 answers incorrectly, and 130 dispatches were spent discovering that.

## The dependency chain, in order. Do not start step N+1 before step N passes.

1. **Build the searcher agent and the results-injection harness.**
   A dedicated agent whose only job is to execute a given query and return the
   result block verbatim; the harness injects that block into the answering
   packet. Byte-identical agent body used by both arms C and D.
   **Correspondence test required before anything downstream:** a fixed synthetic
   query whose returned block is reproduced verbatim, with the raw searcher
   output persisted so any summarisation is visible.
   This is the largest gap and everything else waits on it.

2. **Implement the retrieval-divergence probe.**
   Executes an item's fixed query through the searcher and records the raw
   block, its SHA, and deterministic relevance flags. **No solver, no answer, no
   outcome** — that is what makes the screen pre-treatment. Log it in full
   anyway; "pre-treatment" is a claim that must be inspectable.

3. **Author and run the calibration bank** (≥3× production size), per
   `docs/EXP004_STAGE0B_BATTERY_AUTHORING_PROTOCOL.md`.
   Closed-book, R=1, fresh context per trial. Establishes the realized
   closed-book accuracy `p` against the target band **0.90–1.00**, and the
   realized `c_disp`. **Calibration items are permanently barred from
   production.**

4. **Freeze the grader** (`lab/grading_v2.py`) only after the calibration bank
   has exercised its span parser on answers that are not Stage 0A-M's. It has so
   far been validated against 130 answers from a battery it was designed after,
   which is not independent evidence.

5. **Re-derive power from the measured `p` and `c_disp`**, replacing the assumed
   design point in `runs/exp004_stage0b_design/power_simulation.json`. If the
   measured values move the required n materially, the design changes before any
   production dispatch, not after.

6. **Only then** author production items, freeze every fingerprint listed in the
   authoring protocol §5 — **including the freeze/grade/analyse driver, which
   must be committed before the first dispatch** — and re-run the causal-contract
   validator until the Stage 0B contract passes as `freeze_ready`.

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
- **Do not call the treatment "web retrieval".** `E` is search-capable and
  fetch-blocked; the treatment is `search_snippet_exposure`. No pooling across
  environments.
- **Do not treat the Stage 0A-M null as evidence of safety.** Its own harm bounds
  are ≤0.113 (availability) and ≤0.312 (restricted to the 8 trials that actually
  retrieved).
- **No Stage 0B production dispatch** until steps 1–6 pass and the contract
  validates as `freeze_ready`.
