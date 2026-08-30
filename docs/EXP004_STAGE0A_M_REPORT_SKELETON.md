# Stage 0A-M report skeleton — FROZEN BEFORE OUTCOMES

No section may be deleted, reordered or added on the basis of what the run shows.
Sections that turn out empty are retained and marked "none observed".

## 1. CONFIRMATORY RESULT

Primary claim wording, used verbatim for any class that rejects:

> **Among the preregistered authored items in this class, at least one item has a
> lower probability of an objectively correct answer under the retrieval-enabled
> procedure than under closed-book.**

If no class rejects, use verbatim:

> **We did not detect the preregistered negative retrieval effect on the anchored
> stress assay at the planned sensitivity.** At n=25 per class the design had
> approximately 0.87 power against a uniform 0.45 per-item effect and about 0.73
> if roughly 85% of a class carries the effect; it had materially less against
> smaller or sparser effects, and none against effects offset within a class by
> helped items. The result does not show that retrieval is harmless, that
> anchored displacement does not occur, that unanchored or naturalistic tasks are
> safe, or that a retrieval controller is unnecessary. It does not distinguish a
> genuinely absent effect from one suppressed by the anchoring that makes this
> assay objectively gradable.

## 2. CLASS-SPECIFIC RESULTS
Per class: n, discordant counts n10/n01, exact one-sided p, Holm decision at K=2,
and the class-average risk difference **as a descriptive estimate carrying no
inferential claim**.

## 3. NEGATIVE CONTROL / DIAGNOSTICS
Arithmetic control harm rate n10/n with its exact Clopper-Pearson upper bound,
reported beside each primary class's harm rate. Diagnostic only: a comparable
control harm rate **weakens** the anchored-displacement reading and **supports** a
generic tool-use explanation without proving it. No invalidation follows.

## 4. QUERY / TOOL DIAGNOSTICS
Verbatim queries, query counts, tool successes, retrieved evidence. Reported;
never used to select or exclude items.

## 5. DEPENDENCE DIAGNOSTICS
Runs test on orientation in dispatch order; orientation rate by run-position
tercile, by arm-order assignment, and by class. **Very low power at D around 13.**
Diagnostics only — they never exclude an item, a class or a run, and there is no
"dependence passed" gate.

## 6. FAILURE AND MISSINGNESS — TWO SEPARATE TABLES, NEVER SUMMED

**6a. Retrieval-tool outcomes (case A — retained, graded).** Counts by outcome
across the retrieval-enabled arm: `OK`, `REFUSED_BY_PROXY`, `TOOL_ERROR`,
`TOOL_TIMEOUT`, `EMPTY_RESULTS`, `UNHELPFUL_RESULTS`, `NOT_ATTEMPTED`; plus the
rate at which every retrieval call in a trial failed, given that retrieval was
attempted. **These are treatment outcomes. No item was excluded for any of
them.** In the measured environment (`E` = search-capable, fetch-blocked) a
non-zero `REFUSED_BY_PROXY` count is expected and is not a defect.

**6b. Dispatch-level failures (case B — voided).** Voided items with the frozen
cause, **broken down by which arm failed**: closed / retrieval-enabled / both.
Arm-correlated dispatch mortality is reported as a finding. Run invalid above
10% of items voided — a ceiling that scopes to 6b only.

State explicitly: *the 6a rate and the 6b rate are never added together, and 6a
never contributes to the 10% ceiling.*


## 7. COST / LATENCY
Observed tool calls, tokens, wall-clock. Observed telemetry is authoritative over
model self-report.

## 8. ALTERNATIVE EXPLANATIONS
Query-generation failure (the leading candidate, tested by Stage 0B arm C);
generic tool-use tax; environment state during the run; anchoring effects.

## 9. STRESS-SAMPLE LIMITATION
Included regardless of result. The items are deliberately authored stress cases,
not a sample from any population. No prevalence claim follows.

## 10. WHAT THIS ESTABLISHES
Scoped to the frozen authored items, the retrieval-enabled procedure
(intent-to-treat), and the anchored construct.

## 11. WHAT THIS DOES NOT ESTABLISH
Not naturalistic prevalence; not general retrieval harm; not controller or router
value; not within-class sign heterogeneity; not existing-router performance; not
learned-router discoverability; not false-premise behaviour; not ordinary
free-form temporal reasoning; not a generalisation from the authored items to the
semantic class.

## 12. NEXT EXPERIMENT
Stage 0B advancement rule: Holm-adjusted p <= 0.05 and D >= 8. Query quality is
not an advancement criterion.
