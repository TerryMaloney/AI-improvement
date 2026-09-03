# EXPERIMENT_CAUSAL_CONTRACT

Status: implemented 2026-09-02. Applies **prospectively** to future experiment
families. Stage 0A-M is mapped retrospectively as a documentation fixture only
(`experiments/exp004_stage0am/causal_contract.retrospective.yaml`); it is not a
Stage 0A-M production gate.

## What it is

One YAML file per experiment family, `experiments/<id>/causal_contract.yaml`,
that makes the experiment's own causal assumptions inspectable before
production:

- **nodes** — fixed vocabulary (`lab.causal_contract.NODE_VOCABULARY`);
- **required_edges** — edges the design intends;
- **assumed_absent_edges** — the edges the design *relies on being absent*.
  Each must name a `check` with a `type` (`byte_identity`, `schema_equality`,
  `fingerprint`, `deterministic_route`, `live_probe`, `recorded_value`,
  `design`, `proof_or_rule`, `correspondence_test`), an `artifact` that exists,
  and — for the executable types — a `test`;
- **bindings** — every load-bearing construct with `claim`, `implementation`,
  `fingerprint`, `correspondence_test`;
- **status** — `draft` may carry `[OPEN]`; `freeze_ready` may not.

## Validator

`python -m lab.causal_contract experiments/<id>/causal_contract.yaml`

Fails when an assumed-absent edge has no check or its artifact is missing, a
binding is incomplete, a required test file is missing, or a `freeze_ready`
contract still carries `[OPEN]`. Tests: `tests/test_causal_contract.py`.

## First uses

- Minimal example: `experiments/_example_causal_contract/causal_contract.yaml`.
- **Stage 0B draft** — `experiments/exp004_stage0b/causal_contract.yaml` — the
  first genuine prospective use. It records which assumptions Stage 0B must
  earn, with `[OPEN]` where the design is not frozen. It authorizes nothing.

## Vocabulary change, 2026-09-03

`query_writer` was added to `NODE_VOCABULARY`. Stage 0B's arm C is a
multi-dispatch trial that puts a **second model** inside one arm, whose output
may reach the answerer only through an executed search. Without a node for it,
the two edges that matter — `query_writer → outcome` (assumed absent, closed by a
live probe) and `query_writer → tool_use` (the one licensed path) — cannot be
written down at all. An assumption that cannot be written down is exactly the
class this contract exists to surface, so the vocabulary grew rather than the
assumption going unrecorded. Existing contracts are unaffected: the vocabulary is
a permitted set, not a required one.

## Why so small

It does not ask for a full causal model. It asks for the list of edges you are
assuming away and the artifact that earns each one. That is the list that,
had it existed, would have caught the asymmetric-agent, judge-route,
egress-environment and effort-symmetry gaps before anyone looked.
