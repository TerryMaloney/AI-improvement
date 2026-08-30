# Stage 0A-M solver-agent symmetry remediation — 2026-08-30

**Status: CANDIDATE PRE-TREATMENT REPAIR. NOT FROZEN. PRODUCTION DISPATCHES: 0.**

This document is an execution-time addendum to
`docs/EXP004_STAGE0A_M_SPECIFICATION.md`. It supersedes only the Stage 0A-M
assignment of the shared `.claude/agents/solver-closed.md` and
`.claude/agents/solver-web.md` agents. It does not change the battery, keys,
grader, statistical test, sample size, schedule, treatment estimand, or report
claim.

## Finding

A pre-production execution audit found that the shared Claude subagents were not
an arm-symmetric implementation of the frozen treatment.

The experiment's packet templates were designed to differ only in retrieval
permission, but the agent definitions add a second instruction layer:

- `solver-web` contains web-arm-only instructions including premise checking,
  source-independence reasoning, dating changing claims, and conflict-resolution
  guidance.
- `solver-closed` contains a different set of epistemic instructions about stale
  knowledge, premise doubt, confidence, abstention, and recalled sources.

Because custom Claude Code subagent markdown bodies are system prompts, using
those two agents would change **instructions plus retrieval access** between
arms. That would make a difference in answer correctness impossible to attribute
to the intended retrieval-enabled procedure alone. The mismatch was found before
any production item had been shown to a solver.

## Repair

Stage 0A-M must use these experiment-specific agents instead:

- closed: `.claude/agents/stage0am-solver-closed.md`
- retrieval-enabled: `.claude/agents/stage0am-solver-web.md`

Their markdown bodies are byte-identical. Both use `model: inherit`, so the
execution-time parent model pin applies to both. Both retain the same
non-informational `TodoWrite` tool. The retrieval-enabled arm differs in tool
access only by `WebSearch` and `WebFetch`.

The task packets continue to carry the arm-specific external-information
permission. Their non-TOOLS content is identical.

Machine-readable hashes and invariants are in:

`experiments/exp004_stage0am/agent_symmetry.candidate.json`

Regression tests are in:

`tests/test_stage0am_agent_symmetry.py`

## Why the shared agents are not edited

The existing shared solvers are used by earlier epistemic-lab conditions and
encode behavior that may be intentional there. Rewriting them would silently
change older experiments. Stage 0A-M therefore gets dedicated agents rather than
mutating shared infrastructure.

## Treatment interpretation

This repair does **not** remove the unavoidable effect of granting tools
themselves: Claude receives different tool definitions/system tool scaffolding
when WebSearch/WebFetch are available. That is part of the retrieval-enabled
intent-to-treat intervention.

What is removed is an avoidable additional treatment: arm-specific epistemic
reasoning instructions unrelated to the mere availability of retrieval.

## Required before freeze

This candidate repair is not self-certifying. Before the first production
dispatch, the executing Claude Code session must:

1. run the complete non-production test suite and require all tests green;
2. confirm `tests/test_stage0am_agent_symmetry.py` passes;
3. invoke each dedicated agent on synthetic non-production canaries and verify
   both launch successfully;
4. verify both resolve to the same exact served model/model snapshot;
5. re-run the already-frozen egress/environment check through
   `stage0am-solver-web` and confirm or re-scope environment `E` before outcomes;
6. record the final agent-definition hashes and packet hashes in the execution
   manifest/freeze record;
7. record the final freeze commit SHA;
8. only then create the production run directory.

If the full suite or either synthetic canary fails, production remains blocked.

## Frozen scientific state preserved

Unchanged:

- battery fingerprint: `1ec90754f1de2696`;
- grader fingerprint: `10adaf1dac94ea70`;
- 25 date-anchored + 25 definition-anchored + 15 arithmetic controls;
- 130 planned production dispatches;
- R=1;
- pointwise-null / finite-authored-set primary claim;
- ITT treatment analysis;
- no reachability-conditioned item selection;
- paired schedule/randomization;
- production treatment exposure: **NONE** at discovery of this defect.

This is a pre-treatment measurement repair, not an outcome-responsive redesign.
