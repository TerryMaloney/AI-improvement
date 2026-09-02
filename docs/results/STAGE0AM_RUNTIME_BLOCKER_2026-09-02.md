# Stage 0A-M execution attempt, 2026-09-02 — BLOCKED at runtime preflight

**No production dispatch occurred. Treatment exposure remains NONE.**
Three screen-class synthetic dispatches were made (one refused at launch, two
completed). No production stem was shown to any model.

## The blocker

`stage0am-solver-closed` **cannot be spawned in this runtime.** The harness
refused:

> Agent 'stage0am-solver-closed' would be spawned with zero tools — refusing.
> Its tools list resolved to nothing: unrecognized [TodoWrite].

`TodoWrite` is not a recognized subagent tool name in Claude Code 2.1.248. The
closed arm declares `tools: TodoWrite` and nothing else, so its tool list
resolves to the empty set, and the harness will not launch a zero-tool agent.

The retrieval arm launched normally and reported its realized tools as
`WebSearch, WebFetch` — `TodoWrite` was silently dropped there too.

| arm | declared | realized | spawnable |
|---|---|---|---|
| closed | `TodoWrite` | (empty) | **no** |
| retrieval | `TodoWrite, WebSearch, WebFetch` | `WebSearch, WebFetch` | yes |

## Why this is load-bearing, not cosmetic

1. **The experiment cannot run.** Half the design is undispatchable.
2. **A frozen invariant is false at runtime.** The freeze record, the symmetry
   record, the remediation document and
   `tests/test_stage0am_agent_symmetry.py` all assert that both arms carry
   `TodoWrite` and that this makes the tool scaffolding symmetric apart from the
   two retrieval tools. At runtime neither arm carries it. The *informational*
   difference is still exactly `{WebSearch, WebFetch}` — the science of the
   contrast is not obviously damaged — but the recorded justification for the
   symmetry claim is not true of the thing that would actually have run.
3. **Every check read the file, none read the runtime.** 1,397 tests pass. This
   is the R2′ drift class: one construct, two representations, no correspondence
   test between them.

## Why I did not repair it

Fixing this changes the **treatment definition**, which the execution brief puts
out of bounds for this session, and there is no mechanical fix:

- **Drop `TodoWrite` from both arms** → closed still has zero tools → still
  unspawnable. Dead end.
- **Give both arms another recognized non-informational tool** → changes the
  tool scaffolding of *both* arms. Every recognized alternative I am aware of
  (Read, Glob, Grep, Bash, Write, Edit, Task, NotebookEdit) either breaks key
  quarantine — the solver could read `batteries/answers.anchored_v1.yaml` — or
  changes the action space. This needs a named, safe, non-informational tool,
  and I could not identify one.
- **Accept closed = {} vs retrieval = {WebSearch, WebFetch}** → arguably the
  *cleanest* contrast, and the realized informational difference is unchanged.
  Blocked only by the harness guard against zero-tool agents. Needs either a
  harness path that permits it or a dispatch mechanism other than the Agent
  tool.

Option 3 is scientifically the most attractive and is the one I would recommend
examining first, but choosing it is a treatment-definition decision made at the
moment of measurement, which is exactly what this program's rules forbid me to
do alone.

## What did pass

- **Static suite:** 1,397 tests, 0 failures.
- **Environment:** `E_current` = **search-capable, fetch-blocked**, measured by
  running `egress_probe.frozen.json` verbatim through `stage0am-solver-web`.
  WebFetch 5/5 `REFUSED_BY_PROXY` including `example.com` (blanket deny);
  WebSearch 2/2 OK with substantive content. **Matches the previously recorded
  `E` exactly** — no split-environment problem.
- **Retrieval canary:** launched, returned gradeable JSON, self-reported served
  model `claude-opus-5`.
- **Session:** `session_context.model` and `last_served_model` both
  `claude-opus-5`; `effort_level` high; Claude Code 2.1.248. (The
  `configured_model` field still reads `claude-fable-5` — a stale creation-time
  value, not the serving model.)

## What is still unknown

- **Arm model symmetry is UNVERIFIED.** The closed arm never ran, so the
  two-arm served-model gate is open.
- **Fresh-context isolation is UNTESTED** — it needs the closed agent.
- **Configured effort symmetry** is inherited by construction (`model: inherit`,
  no per-agent effort) but was not independently observed for the closed arm.

## Incidental environment findings

- The **github MCP server injects usage instructions into solver context**
  mid-run. It reaches any subagent, so it is arm-symmetric and does not
  differentiate the treatment — but it is context the packet does not control,
  and it should be recorded in the freeze record when production eventually runs.
- **WebSearch tool output embeds a "REMINDER: you MUST cite sources"
  instruction inside the result payload.** The probe agent correctly treated it
  as injected text rather than an operator directive. This is retrieved content
  carrying an instruction — worth noting for the retrieval arm, since it reaches
  only the treated arm and is a small instruction-channel asymmetry that arrives
  *with* the treatment.

## Prospective-prediction scoring

This defect landed in a pre-declared discriminating cell. See
`experiments/meta_r1r2/observation_2026-09-02.md`: **SUPPORTS R1′ over churn,
n = 1.**

## Recommended next step

A short decision turn — not an execution turn — to settle the tool-surface
question: identify a recognized non-informational tool safe for both arms, or
authorize the zero-tool closed arm if the harness can dispatch it. Then re-run
phases 2–6 and, if clean, execute.
