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

- `epistemic/` — the system under test (Phase 2: classifier, entity TTL registry, budget ceiling, router)
- `lab/` — the lab machinery (trial generation, SQLite results store, grading, reports)
- `batteries/` — question sets; answers quarantined separately
- `experiments/` — experiment configs (YAML)
- `runs/` — per-experiment working dirs: trial packets, raw answers, reports (the experimental record)
- `docs/hypotheses.md` — the living hypothesis ledger
- `docs/lab_manual.md` — the full operator protocol and honest measurement caveats
- `.claude/agents/`, `.claude/skills/run-experiment/` — the sandboxed agents and the protocol any Claude session follows to run an experiment

## Quickstart

```bash
pip install -e ".[dev]"
pytest                                   # everything runs offline, no agents needed

python -m lab prepare exp001             # generate trial packets for an experiment
# ... orchestrator session runs solver agents per docs/lab_manual.md ...
python -m lab ingest exp001              # load raw answers into the store
python -m lab grade exp001               # deterministic grading + judge packets
python -m lab report exp001              # write runs/exp001/report.md
python -m lab compare exp001 exp002      # cross-experiment diff
```

Or, in a Claude Code session in this repo: `/run-experiment exp001`.

## Status

See `docs/hypotheses.md` for what's open, `docs/handoff_packet.md` §7 for phase
history. Phase 3 (baseline vs. verified, for real) starts with `exp001`.
