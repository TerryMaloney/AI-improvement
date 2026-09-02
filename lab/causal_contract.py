"""EXPERIMENT_CAUSAL_CONTRACT -- make an experiment's causal assumptions inspectable.

Every experiment family declares, in ``experiments/<id>/causal_contract.yaml``:

  nodes:            the causal nodes the design talks about (fixed vocabulary)
  required_edges:   edges the design intends to be present
  assumed_absent_edges:
                    edges the design RELIES ON being absent -- each must name a
                    check (type + artifact [+ test]) that earns the assumption
  bindings:         every load-bearing construct with claim / implementation /
                    fingerprint / correspondence_test
  status:           draft | freeze_ready

The validator enforces structural completeness. It does not pretend unresolved
science is resolved: a ``draft`` may carry ``[OPEN]`` fields and still be valid;
a ``freeze_ready`` contract may not.

Schema (all keys lower-case):

  experiment: str
  status: "draft" | "freeze_ready"
  nodes: [str]                       # subset of NODE_VOCABULARY
  required_edges: [[from, to]]
  assumed_absent_edges:
    - edge: [from, to]
      check:
        type: one of CHECK_TYPES
        artifact: repo-relative path[:fragment]   # must exist at validation
        test: "tests/x.py::name"                  # required for correspondence_test,
                                                  # byte_identity, fingerprint, deterministic_route
        note: str (optional)
  bindings:
    - construct: str
      claim: path[#section]
      implementation: path[:symbol]
      fingerprint: path[:key] | "[OPEN]"
      correspondence_test: "tests/x.py::name" | "[OPEN]"
  open_fields: [str]  (optional; free text describing what is [OPEN])

Nothing here dispatches.
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Any

import yaml

NODE_VOCABULARY = frozenset({
    "treatment", "model", "served_model", "system_instructions", "tool_definitions",
    "tool_use", "environment", "item", "evaluator", "selection", "outcome",
    "missingness", "cost_effort", "shared_latent",
})

CHECK_TYPES = frozenset({
    "byte_identity", "schema_equality", "fingerprint", "deterministic_route",
    "live_probe", "recorded_value", "design", "proof_or_rule", "correspondence_test",
})

# check types that must also name an executable test
TEST_REQUIRED = frozenset({"byte_identity", "fingerprint", "deterministic_route",
                           "correspondence_test", "schema_equality"})

OPEN = "[OPEN]"


def _strip_fragment(ref: str) -> str:
    """'path#section' or 'path:symbol' -> 'path'. Test refs 'path::name' -> 'path'."""
    ref = ref.split("::")[0]
    for sep in ("#", ":"):
        if sep in ref:
            ref = ref.split(sep)[0]
    return ref


def _exists(repo: pathlib.Path, ref: str) -> bool:
    if not ref or ref == OPEN:
        return False
    return (repo / _strip_fragment(ref)).exists()


def load(path: pathlib.Path) -> dict:
    return yaml.safe_load(pathlib.Path(path).read_text())


def validate(contract: dict, repo: pathlib.Path) -> list[str]:
    """Return a list of errors. Empty list == valid for its declared status."""
    errors: list[str] = []
    status = contract.get("status")
    if status not in ("draft", "freeze_ready"):
        errors.append(f"status must be draft|freeze_ready, got {status!r}")
    freeze = status == "freeze_ready"

    nodes = set(contract.get("nodes") or [])
    unknown = nodes - NODE_VOCABULARY
    if unknown:
        errors.append(f"unknown nodes: {sorted(unknown)}")

    def check_edge(e, where):
        if not (isinstance(e, list) and len(e) == 2):
            errors.append(f"{where}: edge must be [from, to], got {e!r}")
            return
        for n in e:
            if n not in nodes:
                errors.append(f"{where}: node {n!r} not declared in nodes")

    for e in contract.get("required_edges") or []:
        check_edge(e, "required_edges")

    for i, entry in enumerate(contract.get("assumed_absent_edges") or []):
        where = f"assumed_absent_edges[{i}]"
        check_edge(entry.get("edge"), where)
        chk = entry.get("check") or {}
        ctype = chk.get("type")
        if ctype not in CHECK_TYPES:
            errors.append(f"{where}: check.type must be one of {sorted(CHECK_TYPES)}, got {ctype!r}")
            continue
        art = chk.get("artifact")
        if not art:
            errors.append(f"{where}: check has no artifact")
        elif art == OPEN:
            if freeze:
                errors.append(f"{where}: artifact is [OPEN] in a freeze_ready contract")
        elif not _exists(repo, art):
            errors.append(f"{where}: artifact not found: {art}")
        if ctype in TEST_REQUIRED:
            test = chk.get("test")
            if not test:
                errors.append(f"{where}: check.type {ctype} requires a test")
            elif test == OPEN:
                if freeze:
                    errors.append(f"{where}: test is [OPEN] in a freeze_ready contract")
            elif not _exists(repo, test):
                errors.append(f"{where}: test file not found: {test}")

    for i, b in enumerate(contract.get("bindings") or []):
        where = f"bindings[{i}]({b.get('construct', '?')})"
        for field in ("construct", "claim", "implementation", "fingerprint", "correspondence_test"):
            v = b.get(field)
            if v in (None, ""):
                errors.append(f"{where}: missing {field}")
            elif v == OPEN:
                if freeze:
                    errors.append(f"{where}: {field} is [OPEN] in a freeze_ready contract")
            elif field in ("claim", "implementation", "fingerprint", "correspondence_test") and not _exists(repo, v):
                errors.append(f"{where}: {field} not found: {v}")

    if freeze and contract.get("open_fields"):
        errors.append("freeze_ready contract still lists open_fields")
    return errors


def main(argv: list[str]) -> int:
    repo = pathlib.Path(__file__).resolve().parent.parent
    rc = 0
    for p in argv[1:]:
        errs = validate(load(pathlib.Path(p)), repo)
        print(f"{p}: {'VALID' if not errs else 'INVALID'}")
        for e in errs:
            print("  -", e)
        rc |= bool(errs)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
