# Next action — validate Stage 0A-M agent-symmetry repair, then freeze

**Do NOT run production yet.**

A pre-production audit found that the shared `solver-web` and `solver-closed` Claude agents had different epistemic system prompts. The Stage 0A-M contrast therefore would have changed prompting as well as retrieval access.

Candidate remediation commit:
`0fb8a7f7b856337d26116378b0d6c399c0ffc061`

Read first:
1. `docs/EXP004_STAGE0A_M_AGENT_SYMMETRY_REMEDIATION.md`
2. `experiments/exp004_stage0am/agent_symmetry.candidate.json`
3. `.claude/agents/stage0am-solver-closed.md`
4. `.claude/agents/stage0am-solver-web.md`
5. `tests/test_stage0am_agent_symmetry.py`
6. `docs/EXP004_STAGE0A_M_SPECIFICATION.md`
7. `docs/EXP004_STAGE0A_M_PREFLIGHT.md`

## Required validation before freeze

Use the candidate dedicated Stage 0A-M agents, not the shared agents.

1. Run the complete non-production test suite.
   - Require all tests green.
   - Confirm `tests/test_stage0am_agent_symmetry.py` passes.
   - Do not weaken a scientific invariant to restore green.

2. Run a synthetic closed-agent canary.
   - `stage0am-solver-closed`
   - no production stem
   - confirm successful launch and gradeable JSON
   - record exact served model/model id.

3. Run a synthetic retrieval-agent canary.
   - `stage0am-solver-web`
   - neutral non-production question
   - confirm successful launch and gradeable JSON
   - record exact served model/model id.
   - require the same model snapshot as the closed arm.

4. Re-run the already-frozen neutral retrieval-environment probe through `stage0am-solver-web`.
   - do not change probe targets or queries after seeing results;
   - record WebSearch/WebFetch reachability;
   - compare with prior `E = search-capable, fetch-blocked`;
   - if different, re-scope the environment BEFORE any production outcome.

5. Verify the committed symmetry record.
   - common agent body hash: `60a61de44f7837fe`
   - closed candidate agent file hash: `0acdce6151bdcdc1`
   - retrieval candidate agent file hash: `233b797412d3ee7f`
   - packet hashes: closed `1d47dc05e460a07b`, retrieval `4ad32bd810a1b542`
   - retrieval-only tool difference: `WebSearch`, `WebFetch`.

6. Record the validated agent/packet hashes in the final execution manifest or freeze record and mark `agent_symmetry.candidate.json` as validated/frozen.

7. Record the final freeze commit SHA.

8. Only after steps 1–7 pass, create the production run directory and execute the frozen 130-dispatch schedule.

## Scientific state that must not change

- battery fingerprint `1ec90754f1de2696`;
- grader fingerprint `10adaf1dac94ea70`;
- 25 date + 25 definition + 15 arithmetic items;
- R=1;
- 130 production dispatches;
- pointwise-null / finite-authored-set primary claim;
- ITT analysis;
- existing schedule/randomization;
- no reachability-conditioned item selection;
- no production re-keying/reclassification.

## Execution traps

- Use `stage0am-solver-closed` / `stage0am-solver-web`, NOT the shared `solver-closed` / `solver-web`.
- A retrieval-tool failure with a gradeable answer is retained and graded.
- Only a dispatch-level failure with no gradeable answer pair-voids.
- Do not claim a class-average inferential effect.
- Do not drop items for unreachable sources.
- Do not pool across different environments.
- Never expose a production stem in a dry run/canary.

## Current authorization boundary

Authorized now:
- non-dispatch tests;
- neutral synthetic agent canaries;
- neutral environment probe;
- final freeze bookkeeping if all checks pass.

Not authorized until those checks pass:
- any of the 130 production Stage 0A-M dispatches.
