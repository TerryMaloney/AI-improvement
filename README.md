# Epistemic Testing Lab

A testing lab for the **epistemic control system** described in
[`docs/handoff_packet.md`](docs/handoff_packet.md): a deterministic layer that
classifies what kind of claim a question makes, decides whether and how to
verify it, and enforces hard cost ceilings — so a model neither blindly trusts
itself nor expensively verifies everything.

The lab exists to answer one recurring kind of question, over and over:

> **Does procedure X make the model's answers more correct, at a cost that's
> worth it — compared to the model alone?**

Everything here is built for that loop: state a hypothesis → design an
experiment → run it → compare → record the outcome → form the next hypothesis.

## Coordination / current state

For a fresh GPT or Claude Code session, read these first:

1. [`docs/STATUS.md`](docs/STATUS.md) — compact current research state and blockers.
2. [`docs/NEXT.md`](docs/NEXT.md) — next authorized action, hard stops, and handoff format.
3. [`docs/RESEARCH_MAP.md`](docs/RESEARCH_MAP.md) — long-range research + execution roadmap.
4. [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md) — durable project-level decisions.
5. [`docs/hypotheses.md`](docs/hypotheses.md) — hypothesis ledger.
6. [`docs/handoff_packet.md`](docs/handoff_packet.md) — historical architecture/design context.

**GitHub is the canonical project memory.** Chat sessions are working contexts.
Experiment-specific frozen decisions and preregistrations remain authoritative
over coordination documents.

## How it works (no API key required)

Deterministic Python does everything reproducible. **Claude Code itself is the
model host**: an orchestrator session spawns sandboxed solver subagents as the
"models under test." The sandbox is enforced by tool restrictions, not trust:

| Agent | Tools | Role |
|---|---|---|
| `solver-closed` | none | Baseline condition — parametric knowledge only. Cannot search, cannot read files. |
| `solver-web` | WebSearch, WebFetch only | Verified condition — can search, but cannot read the repo (so it can never see ground truth). |
| `grader-judge` | none | Grades one answer against ground truth, inline, with no solver context. |

Ground truth is quarantined in `batteries/answers.yaml`, which only the grading
step reads. Trial packets handed to solvers are generated with answers
provably stripped (there's a test for it).

## Layout

- `epistemic/` — the system under test (classifier, entity TTL registry, budget ceiling, router)
- `lab/` — lab machinery (trial generation, storage, telemetry, grading, reports)
- `batteries/` — question sets; answers quarantined separately
- `experiments/` — experiment configs (YAML)
- `runs/` — per-experiment working dirs and experimental record
- `docs/hypotheses.md` — living hypothesis ledger
- `docs/lab_manual.md` — operator protocol and measurement caveats
- `.claude/agents/`, `.claude/skills/run-experiment/` — sandboxed agents and Claude experiment protocol

## Quickstart

```bash
pip install -e ".[dev]"
pytest

python -m lab prepare exp001
# ... orchestrator session runs solver agents per docs/lab_manual.md ...
python -m lab ingest exp001
python -m lab grade exp001
python -m lab report exp001
python -m lab compare exp001 exp002
```

Or, in a Claude Code session in this repo: `/run-experiment exp001`.

## Status

The historical handoff packet describes the project's original phase plan, but
the lab has advanced substantially since that snapshot. Use
[`docs/STATUS.md`](docs/STATUS.md) and [`docs/NEXT.md`](docs/NEXT.md) for the
current state and authorized next action.
