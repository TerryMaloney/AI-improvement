# EXP005-EPI status — 2026-09-09

Branch: `openai/exp005-procedure-discovery`

## Current claim level

**Implemented construct + same-generator held-out controller signal.**

No LLM-backed outcome exists. No real-world accuracy claim is licensed.

## Built

- append-only evidence model;
- mutable belief state (`SUPPORTED / REJECTED / DISPUTED / UNKNOWN`);
- explicit source lineage;
- explicit evidence supersession;
- dependency DAG + truth-maintenance recomputation;
- revision history;
- recursive provenance;
- epistemic-debt verification priority;
- immutable objective/permission boundary;
- SQLite persistence and round-trip reconstruction;
- RecentContext comparator;
- NaiveRAG comparator;
- metadata-matched MatchedRAG comparator;
- five deterministic delayed-misinformation construct scenarios;
- seeded random hidden-world generator;
- fixed-budget verification policies: debt / uncertainty / dependency / random / oracle;
- prospective confirmation plan and held-out result;
- draft causal contract.

## Construct result

`runs/exp005_epi_construct/benchmark.json`

- EpistemicWorkspace: 8/8
- MatchedRAG: 8/8
- NaiveRAG: 7/8
- RecentContext: 3/8

Interpretation: **no accuracy advantage over a strong metadata-matched RAG has been established.** This is a useful negative control, not a disappointment. It prevents the project from mistaking richer metadata for a capability gain.

## Active-verification development signal

`runs/exp005_epi_construct/verification_policy_development.json`

200 synthetic development worlds, 3 verification actions:

- debt mean gain: 0.14733
- uncertainty-only: 0.12183
- dependency-only: 0.11842
- random: 0.07475

Same-pass design signal only.

## Prospective same-generator confirmation

Plan committed before outcomes:
`experiments/exp005_epi/verification_confirmation_plan.json`

Result:
`runs/exp005_epi_confirm/verification_policy_confirmation.json`

500 untouched worlds, same generator, same 3-action budget:

- debt - random mean gain = +0.07194 (required >= +0.03)
- debt - uncertainty mean gain = +0.02646 (required >= +0.01)
- debt harm rate = 0.002 (required <= 0.01)

Decision: **PASS**.

Licensed statement only:

> On unseen seeds from the same synthetic world generator, the frozen epistemic-debt controller outperformed the precommitted random and uncertainty-only verification baselines under the fixed synthetic loss and budget.

It does **not** establish cross-generator, LLM, source-lineage-inference, source-reliability, or real-world benefit.

## Tests

Focused local EXP005-EPI suite: **21 passed**.

The complete repository suite was not run from this ChatGPT environment because the connected GitHub tool does not expose a local clone. Do not rewrite this as “all repo tests pass.”

## Biggest unresolved assumptions

1. Source reliability is supplied by the synthetic generator.
2. Source lineage is supplied by the synthetic generator.
3. Atomic claim identity is supplied.
4. Propositions are boolean.
5. The generator and controller share research lineage.
6. MatchedRAG can equal the workspace on ordinary on-demand QA.
7. No model has yet extracted claims from language into this state.
8. No real search/tool result has yet crossed the evidence boundary.
9. The current verification tool is an oracle in synthetic worlds.

## Scientific interpretation

The most interesting surviving hypothesis has narrowed from:

> “persistent epistemic memory is more accurate than RAG”

into:

> “explicit persistent epistemic state may create useful control signals — especially load-bearing uncertainty — that improve where a limited verification budget is spent.”

That is the next mechanism to attack.
