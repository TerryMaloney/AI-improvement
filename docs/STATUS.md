# Current Research Status

> Coordination document only. Experiment-specific frozen artifacts remain authoritative for their scope.

## Current phase

**Stage 0A-M is NOT YET FROZEN. A pre-production execution audit found and repaired a load-bearing arm-symmetry confound; the repair candidate now requires full-suite and synthetic Claude validation before execution.**

Latest candidate remediation commit: `0fb8a7f7b856337d26116378b0d6c399c0ffc061`.

Scientific state preserved:
- 25 date-anchored / 25 definition-anchored / 15 arithmetic controls = 65 items;
- 130 planned production dispatches;
- 50/50 primary keys source-verified; 65/65 production-eligible;
- battery fingerprint `1ec90754f1de2696`;
- grader fingerprint `10adaf1dac94ea70`;
- **production dispatches 0; treatment exposure NONE**.

The last fully executed non-production suite before this remediation was **1324 passed, 0 failed** at `9c57635`. The new remediation has focused static checks authored but the complete repository suite has NOT been run in the GPT environment and must be re-run before freeze.

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
