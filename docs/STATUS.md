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

## 2026-09-02 — STAGE 0A-M EXECUTED AND COMPLETE

**130/130 dispatches, 0 voids, 0 dispatch failures, all on `claude-opus-5` under freeze `a1f4efb`.** Report: `runs/exp004_stage0am/EXP004_STAGE0AM_REPORT.md`.

**Result: NULL at a realized sensitivity far below plan.** Neither primary class rejected. `date_anchored` n00=14 n01=1 n10=1 n11=9, D=2, p=0.750. `definition_anchored` n11=25, D=0, p=1.000. Arithmetic control 15/15, D=0. Licensed claim: no claim that any authored item is harmed by the retrieval-enabled procedure.

**Why the null is nearly uninformative — two independent power failures:**
- `definition_anchored` (25/25) and arithmetic (15/15) sat at a **complete ceiling** in both arms; zero discordance is possible there.
- `date_anchored` scored 10/25 in both arms mostly through a **grading artifact**: 28 of 50 trials named the correct anchored entity but were graded incorrect because the frozen `exact_entity` rule gives rejects precedence and Opus 5 supplies temporal context naming the successor.
- **Both discordant pairs are the same artifact.** In all four trials the solver named the correct entity; only whether it also mentioned the successor differed. The lone "harm" and lone "help" are elaboration style, not displacement.

**The grader was not changed after outcomes.** The defect is reported, not repaired.

**Retrieval was barely exercised:** attempted in 8/65 treated trials, declined in 57. Among the 8 that retrieved, 8/8 correct and their closed partners 8/8 — zero discordance. Realized effort near-identical across arms (P4 not supported); no served-model fallback (P2); availability-without-use showed no effect at near-zero power (P3).

**Dispatch repair that made execution possible:** identical command line per arm, `claude -p --agent <agent> --model opus --allowedTools WebSearch WebFetch`; realized surfaces closed `[]` / retrieval `[WebSearch, WebFetch]`; agent frontmatter deliberately unedited (an empty `tools:` risks "inherit all tools" and would break key quarantine). A **live** runtime correspondence gate now blocks production if realized surfaces drift — the static tests could not see this class of failure.

## 2026-09-02 — execution attempt blocked at runtime preflight (superseded)

**Stage 0A-M did not run. Production dispatches 0; treatment exposure NONE.** Three screen-class synthetic dispatches; no production stem shown to any model.

**Blocker:** `stage0am-solver-closed` cannot be spawned — `TodoWrite` is unrecognized in Claude Code 2.1.248, so the closed arm's tool list resolves to empty and the harness refuses a zero-tool agent. Realized surfaces: closed `[]`, retrieval `[WebSearch, WebFetch]`. The informational difference is still exactly the two retrieval tools, but the recorded "both arms carry TodoWrite" symmetry justification is **false at runtime**, and 1,397 green tests missed it because every check reads the file, none the runtime.

**Not repaired here:** every fix changes the treatment definition (tool surface of both arms) and no safe recognized non-informational tool was identified. Options and a recommendation are in `docs/results/STAGE0AM_RUNTIME_BLOCKER_2026-09-02.md`.

**Passed:** static suite 1,397/0; environment `E_current` = search-capable, fetch-blocked, **matching E exactly** (WebFetch 5/5 refused incl. example.com; WebSearch 2/2 OK); retrieval canary launched and returned gradeable JSON on `claude-opus-5`.

**Open:** arm model symmetry UNVERIFIED (closed arm never ran); fresh-context isolation UNTESTED.

**Prospective prediction scored:** the defect landed in a pre-declared R1′-high / churn-low cell (`live_agent_registry`). SUPPORTS R1′ over churn, n=1 — `experiments/meta_r1r2/observation_2026-09-02.md`.

## 2026-09-02 — last pre-results pass (zero dispatches)

- **Causal contract implemented** (`lab/causal_contract.py`, tests, example, Stage 0B draft, Stage 0A-M retrospective fixture). Prospective rule for future families; not a Stage 0A-M gate.
- **Grader golden corpus** (`tests/golden/…`, 51 hand-derived cases): the frozen grader passed **unchanged**; corpus pinned to grader sha `10adaf1dac94ea70`.
- **R1′/R2′ prospective table frozen** at `experiments/meta_r1r2/` (fingerprint in `FINGERPRINT.txt`, churn mechanical from git). Scored at the next independent audit; nothing from this pass counts.
- **Robust-EVOI wording corrected** (no optimistic max; lower bound over the plausible set + bounded calibration budget). **Configured vs realized effort** separated: configured = symmetry invariant; realized = mediator/outcome, never equalised.
- **Zero-dispatch tests:** P1 NOT TESTABLE (no dual-route cohort); P7 NOT TESTABLE mechanically; **M2 downgraded** — the memo's "no budget line in verified_flat" premise was false. R1′/R2′ **unchanged**. See `docs/results/`.

## 2026-09-01 note

- The dedicated `stage0am-solver-closed` / `stage0am-solver-web` agents became registered in the original session after a context reload landed on a later turn; the runtime gates in `docs/NEXT.md` can now be run from that session or a fresh one. No gate has been run yet.
- A research-discovery memo (`docs/FABLE_5_1_RESEARCH_DISCOVERY_2026-09-01.md`) proposes pre-registering Stage 0A-M *secondary* analyses before outcomes and three zero-design-change freeze-record additions (`effort_level`, live agent list, grader golden corpus). These are proposals; nothing frozen changed.

## Still prohibited

Until the candidate repair passes the full non-production suite and synthetic Claude canaries:
- no Stage 0A-M production dispatch;
- no production-item exposure;
- no production run directory;
- no outcome-based battery change;
- no runtime re-keying/reclassification;
- no Stage 0A-N or Stage 0B execution.

See `docs/NEXT.md`.
