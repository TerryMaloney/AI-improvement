"""EXPERIMENT_CAUSAL_CONTRACT validator: structural completeness, not science."""
from __future__ import annotations

import copy
import pathlib

import yaml

from lab.causal_contract import OPEN, load, validate

REPO = pathlib.Path(__file__).resolve().parent.parent
EXAMPLE = REPO / "experiments" / "_example_causal_contract" / "causal_contract.yaml"
STAGE0B = REPO / "experiments" / "exp004_stage0b" / "causal_contract.yaml"
RETRO = REPO / "experiments" / "exp004_stage0am" / "causal_contract.retrospective.yaml"


def test_minimal_example_is_valid_freeze_ready():
    assert validate(load(EXAMPLE), REPO) == []


def test_assumed_absent_edge_without_check_fails():
    c = load(EXAMPLE); c["assumed_absent_edges"][0]["check"] = {}
    assert any("check.type" in e for e in validate(c, REPO))


def test_missing_artifact_fails():
    c = load(EXAMPLE); c["assumed_absent_edges"][0]["check"]["artifact"] = "does/not/exist.md"
    assert any("artifact not found" in e for e in validate(c, REPO))


def test_check_type_requiring_test_without_test_fails():
    c = load(EXAMPLE); c["assumed_absent_edges"][0]["check"].pop("test")
    assert any("requires a test" in e for e in validate(c, REPO))


def test_incomplete_binding_fails():
    c = load(EXAMPLE); c["bindings"][0].pop("fingerprint")
    assert any("missing fingerprint" in e for e in validate(c, REPO))


def test_open_field_in_freeze_ready_fails_but_draft_passes():
    c = load(EXAMPLE); c["bindings"][0]["fingerprint"] = OPEN
    assert any("[OPEN] in a freeze_ready" in e for e in validate(c, REPO))
    c["status"] = "draft"
    assert validate(c, REPO) == []


def test_undeclared_node_in_edge_fails():
    c = load(EXAMPLE); c["required_edges"].append(["treatment", "missingness"])
    assert any("not declared" in e for e in validate(c, REPO))


def test_stage0b_draft_is_valid_as_a_draft_and_not_as_freeze_ready():
    c = load(STAGE0B)
    assert c["status"] == "draft"
    assert validate(c, REPO) == [], validate(c, REPO)
    c2 = copy.deepcopy(c); c2["status"] = "freeze_ready"
    assert validate(c2, REPO), "a draft with [OPEN] fields must not pass as freeze_ready"


def test_stage0am_retrospective_mapping_names_exactly_the_known_gaps():
    """Documentation fixture, not a gate. It must be a valid draft, and the
    [OPEN] artifacts must be exactly the two gaps the discovery memo predicted."""
    c = load(RETRO)
    assert c["status"] == "draft"
    assert validate(c, REPO) == [], validate(c, REPO)
    gaps = [e["edge"] for e in c["assumed_absent_edges"] if e["check"].get("artifact") == OPEN]
    assert sorted(gaps) == sorted([["cost_effort", "treatment"], ["model", "treatment"]])
