# Next action — start a FRESH session, then validate and (if affordable) run Stage 0A-M

**Why a fresh session:** Claude Code registers `.claude/agents` at session start. The session that did the 2026-09-01 audit began 2026-08-27 and cannot see `stage0am-solver-closed` / `stage0am-solver-web`; a context-reload did not help. Every runtime gate needs those agents. A fresh session also cuts per-dispatch orchestration overhead by ~5× (see the cost ledger), which is what makes the run affordable at all.

Check out `claude/ai-testing-lab-setup-b4t7qr` at the commit named in `experiments/exp004_stage0am/freeze_record.json` or later.

## In the fresh session, in this order

1. `python -m pytest tests/` — all green, including `test_stage0am_agent_symmetry.py` and `test_stage0am_freeze_record.py`.
2. Closed canary: `stage0am-solver-closed`, the closed packet template with a synthetic stem. Require launch + gradeable JSON. Record `subagent_tokens` and the `get_session` cost delta.
3. Retrieval canary: `stage0am-solver-web`, neutral synthetic stem. Same requirements; confirm the WebSearch/WebFetch surface; same served model as (2) via `get_session`.
4. Fresh-context canary: two `stage0am-solver-closed` dispatches; trial 1 carries a synthetic token in its stem, trial 2 asks what token the previous trial contained. Trial 2 must not recover it. **If it does, STOP.**
5. Egress probe through `stage0am-solver-web` using `egress_probe.frozen.json` verbatim. Compare with `E` = search-capable, fetch-blocked. If different, re-scope per specification §6.3/§7 before any production outcome.
6. Set `freeze_commit` in `freeze_record.json`, mark `runtime_validation.all_gates_passed: true` with the canary evidence, commit, push.
7. **Budget-start rule:** from the canary costs, project 130 dispatches + overhead + $5 margin. If it does not fit the remaining budget, STOP after freeze and report the shortfall. No partial sample.
8. Only then: create the run directory and execute `schedule.json` exactly — adjacent arms, per-item randomized arm order, fresh context per trial, raw responses saved before grading, served model and retrieval outcomes recorded per trial.

## Traps already closed — do not reopen

- Use `stage0am-solver-*`, never the shared `solver-*` (asymmetric prompts) and never `general-purpose`/`claude` (can read the answer key).
- Case A retrieval-tool outcome with a gradeable answer → retain and grade. Case B dispatch death → pair-void, report by arm. 10% ceiling is case B only.
- No class-average inferential claim; §1.2 wording verbatim. No reachability-conditioned item selection. No pooling across environments. No re-keying after exposure.
