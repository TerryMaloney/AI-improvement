# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M: agent-symmetry repair passes every static check and the full suite. Runtime validation (canaries, fresh-context, egress probe via the dedicated agent) is BLOCKED in the current session because Claude Code loads `.claude/agents` at session start and this session predates the dedicated agents. A fresh session is required. Production dispatches 0; treatment exposure NONE.**

Scientific state preserved and re-verified 2026-09-01:
- 25 / 25 / 15 = 65 items, 130 planned dispatches, R=1;
- battery fingerprint `1ec90754f1de2696`; grader fingerprint `10adaf1dac94ea70`;
- common agent body `2e1fb5851b784b90`; agent files `f7423c6ecedd4568` / `770ebdc2adcc3c00`;
- packets `1d47dc05e460a07b` / `4ad32bd810a1b542`, 3 differing lines, all in TOOLS;
- full suite green (see freeze record and `tests/test_stage0am_freeze_record.py`).

## Red-team of the remediation (2026-09-01)

Survived: bodies byte-identical; `model: inherit` on both; tool difference exactly {WebSearch, WebFetch}; TodoWrite symmetric and non-informational; packets differ only in the TOOLS block; no hooks; no user-scope shadow of the dedicated agents (user scope holds only the shared `solver-*` agents, which is why they appeared twice in the agent list — harmless, but recorded).

Repaired: the two `description` fields carried arm labels ("closed arm" / "retrieval-enabled arm"). Bounded, not load-bearing — the packet already reveals tool availability — but metadata should not name the treatment; now identical. The symmetry record's body hash had been computed by a different method than the test uses (file hashes matched, bodies were identical); recomputed. One earlier test string-matched a paraphrase ("web search") and broke when the GPT session reworded the TOOLS block to name the tools; it now checks the actual invariant against the dedicated agent.

Accepted as improvements: the GPT session's TOOLS rewording — the closed arm's old "you have none" was literally false with TodoWrite present.

## Budget

See `experiments/exp004_stage0am/cost_ledger.md`. Production is **not affordable from this session** (~$49 projected at its ~200K-token context) and only marginally so from a fresh one (~$24–38). The budget-start rule requires a measured per-trial cost from the canaries before any production dispatch.

## Newly found arm-symmetry confound

The Stage 0A-M packet templates were nearly arm-symmetric, but the actual shared Claude subagents were not.

`.claude/agents/solver-web.md` adds web-arm-specific system instructions including premise checking, source-independence reasoning, dating claims and conflict-resolution guidance.

`.claude/agents/solver-closed.md` carries a different epistemic system prompt concerning stale knowledge, premise doubt, confidence and abstention.

Because custom Claude Code agent markdown bodies are system prompts, executing Stage 0A-M with those agents would contrast **instructions + retrieval access**, not retrieval permission alone. This was discovered before any production output existed.

## Candidate repair

Stage 0A-M now has dedicated agents:
- `.claude/agents/stage0am-solver-closed.md`
- `.claude/agents/stage0am-solver-web.md`

Their markdown bodies are byte-identical. Both use `model: inherit` and retain `TodoWrite`; the retrieval-enabled agent differs in tool access only by `WebSearch` and `WebFetch`.

Machine-readable candidate invariants/hashes:
`experiments/exp004_stage0am/agent_symmetry.candidate.json`

Regression tests:
`tests/test_stage0am_agent_symmetry.py`

Authoritative remediation note:
`docs/EXP004_STAGE0A_M_AGENT_SYMMETRY_REMEDIATION.md`

The shared solvers were deliberately left unchanged because older experiments may depend on their behavior.

## Retrieval environment already measured

The previous frozen probe established on the old shared solver-web path:
- WebFetch: 5/5 `REFUSED_BY_PROXY`, including `example.com`;
- WebSearch: 2/2 `OK`, with substantive extracted text.

`E` was therefore search-capable, fetch-blocked.

Because Stage 0A-M now uses a dedicated web agent, execution-time preflight must re-run the same neutral environment check through `stage0am-solver-web`. Reachability is expected to match but must be measured, not assumed.

## Still prohibited

Until the candidate repair passes the full non-production suite and synthetic Claude canaries:
- no Stage 0A-M production dispatch;
- no production-item exposure;
- no production run directory;
- no outcome-based battery change;
- no runtime re-keying/reclassification;
- no Stage 0A-N or Stage 0B execution.

See `docs/NEXT.md`.
