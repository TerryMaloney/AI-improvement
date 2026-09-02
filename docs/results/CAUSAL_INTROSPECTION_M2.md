# M2 — solver self-report of tool use: what the existing data actually show

Status: zero-dispatch result note, 2026-09-02. Reconstructed from
`runs/exp001/packets`, `runs/exp002/packets`, `runs/exp002/EXP002_REPORT.md`
(§A.5–A.6) and `.claude/agents/solver-web.md`. No new dispatch.

## Correction first

`docs/FABLE_5_1_RESEARCH_DISCOVERY_2026-09-01.md` §3 M2 and
`docs/EGP_AND_PREDICTION_FRONTIER_SYNTHESIS_2026-09-01.md` §7 stated that
`verified_flat` **removed** the solver-visible budget line and that the
under-report persisted, which was taken to disfavour a "motivated report"
explanation. **That premise is false.** [MEASURED]:

- `exp002-*-verified_flat-*` packets carry `SEARCH BUDGET: 3 searches. This is a
  ceiling, not a target …` (line 35);
- `exp001-*-verified-*` packets carry `SEARCH BUDGET: 2 searches …`;
- `exp001-*-search_only-*` packets carry `SEARCH BUDGET: 3 searches …`;
- the shared `solver-web` agent body additionally instructs: *"Your task prompt
  states a search budget. Treat it as a ceiling, not a target."*

`verified_flat` changed the ceiling from 2 to 3 and reworded the line (report
§A.6: "exactly two prompt lines per question, both `SEARCH BUDGET`"). Every
search condition had a visible budget cue. The earlier claim was an unverified
recollection that passed into two memos — an instance of the G7 failure mode
those memos describe.

## What was observed [MEASURED, exp002 §A.5]

| condition | observed tool calls | self-reported | ratio | violations observed / self-reported |
|---|---|---|---|---|
| search_only (ceiling 3) | 39 | 18 | 2.17× | 6 / 0 |
| verified (ceiling 2) | 30 | 15 | 2.00× | 7 / 0 |
| verified_flat (ceiling 3) | 37 | 18 | 2.06× | 5 / 0 |

Under-report is ~2×, one-directional (no trial over-reported), and **the
self-reported count never exceeds the ceiling** while the observed count does
in 18 trials.

## What remains explanatory

1. **Reconstructive report** — no access to the true count; reconstructed from
   salient calls.
2. **Ceiling-anchored report** — the visible budget acts as a cap on what is
   reported, whether by motivated compliance or by anchoring.
3. **Harness over-count** — the observed count includes retries/parallel calls
   the model does not experience as separate searches. (Not excluded by any
   existing artifact; §A.5 counts observed tool calls without deduplication
   against request ids.)

## What the existing data rule against, and what they do not

- They **do not** discriminate 1 from 2: the cue was present in all conditions,
  and the zero-self-reported-violations pattern is *consistent with* 2.
- They **do** show the under-report is invariant to the ceiling level (2 vs 3)
  and to the rewording — so an explanation that depends on the specific wording
  or level of the budget line is disfavoured; one that depends on the *presence*
  of any ceiling is not.
- They **do not** exclude 3.

## Exact claim supported

> On the exp001/exp002 search conditions, solver self-reported search counts
> under-count harness-observed tool calls by ≈2×, one-directionally, and never
> exceed the stated ceiling; the effect is invariant to the ceiling's level and
> wording. Existing artifacts cannot distinguish reconstructive reporting from
> ceiling-anchored reporting, and cannot exclude harness over-counting.

This is not a result about introspection in general. The discriminating
designs (per-call logging vs end-of-task total; a no-ceiling arm; request-id
deduplication of the observed count) remain to be run.
