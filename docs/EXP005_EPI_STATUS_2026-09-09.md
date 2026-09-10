# EXP005-EPI status — 2026-09-09

Branch: `openai/exp005-procedure-discovery`

## Current claim level

**Implemented construct + same-generator held-out support + cross-generator synthetic support for the active-verification controller.**

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
- seeded random hidden-world Generator A;
- structurally different Generator B with temporal changes, false corrections, domain-conditioned source quality, chain/hub topology, copied-source clusters, and impact/dependency decorrelation;
- fixed-budget verification policies: debt / uncertainty / dependency / random / oracle;
- prospective same-generator confirmation plan/result;
- prospective cross-generator confirmation plan/result;
- draft causal contract.

## Construct result

`runs/exp005_epi_construct/benchmark.json`

- EpistemicWorkspace: 8/8
- MatchedRAG: 8/8
- NaiveRAG: 7/8
- RecentContext: 3/8

Interpretation: **no accuracy advantage over a strong metadata-matched RAG has been established.** This is a useful negative control. It prevents the project from mistaking richer metadata for a capability gain.

## Active-verification development signal

`runs/exp005_epi_construct/verification_policy_development.json`

200 Generator-A development worlds, 3 verification actions:

- debt mean gain: 0.14733
- uncertainty-only: 0.12183
- dependency-only: 0.11842
- random: 0.07475

Same-pass development signal only.

## Same-generator confirmation

Plan committed before outcomes:
`experiments/exp005_epi/verification_confirmation_plan.json`

Result:
`runs/exp005_epi_confirm/verification_policy_confirmation.json`

500 untouched Generator-A worlds, same 3-action budget:

- debt - random mean gain = +0.07194 (required >= +0.03)
- debt - uncertainty mean gain = +0.02646 (required >= +0.01)
- debt harm rate = 0.002 (required <= 0.01)

Decision: **PASS**.

Licensed statement:

> On unseen seeds from Generator A, the frozen epistemic-debt controller outperformed the precommitted random and uncertainty-only verification baselines under the fixed synthetic loss and budget.

## Cross-generator confirmation

Generator B and its invariant tests were committed before any controller outcome on B:
`lab/exp005_epi_worlds_b.py`

Plan committed before outcomes:
`experiments/exp005_epi/transfer_b_confirmation_plan.json`

Result:
`runs/exp005_epi_confirm/transfer_b_confirmation.json`

500 Generator-B worlds, 3 verification actions:

- debt - random mean gain = +0.04639 (required >= +0.02)
- debt - uncertainty mean gain = +0.02866 (required >= 0)
- debt harm rate = 0.002 (required <= 0.02)

Decision: **PASS**.

Licensed statement only:

> Across two structurally different synthetic world generators, the frozen epistemic-debt controller improved where a fixed three-action verification budget was spent relative to random verification, and it retained an advantage over uncertainty-only verification under the precommitted Generator-B transfer test.

This is **cross-generator synthetic support**, not an LLM or real-world result. Generator B was authored by the same research process after Generator-A development/confirmation existed, so it is not an independent replication.

## Tests

Focused local EXP005-EPI suite: **26 passed**.

The complete repository suite was not run from this ChatGPT environment because the connected GitHub tool does not expose a local clone. Do not rewrite this as “all repo tests pass.”

## Biggest unresolved assumptions

1. Source reliability is supplied by the synthetic generators.
2. Source lineage is supplied by the synthetic generators.
3. Atomic claim identity is supplied.
4. Propositions are boolean.
5. The verification tool reveals hidden truth with reliability 0.995.
6. MatchedRAG can equal the workspace on ordinary on-demand QA.
7. No model has yet extracted claims from language into this state.
8. No real search/tool result has yet crossed the evidence boundary.
9. Generator B is structurally different but not independently authored.
10. The current loss function and impact weights are synthetic constructs.

## Scientific interpretation

The hypothesis has narrowed from:

> “persistent epistemic memory is more accurate than RAG”

into:

> “explicit persistent epistemic state can expose a useful control variable — epistemic debt, combining uncertainty, staleness, source fragility, dependency load and decision impact — that improves allocation of a limited verification budget across multiple synthetic world families.”

That is now worth carrying into the next layer: natural-language evidence and model-based claim extraction, while keeping the memory/controller comparison isolated from extraction errors.
