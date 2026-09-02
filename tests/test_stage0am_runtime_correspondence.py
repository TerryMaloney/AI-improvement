"""The runtime correspondence gate's recorded evidence must authorize production.

A passing static frontmatter test may never again authorize production on its
own: on 2026-09-02 every static check passed while the closed arm was
undispatchable. These tests assert that LIVE evidence exists, that it passed,
and that it recorded the realized surfaces -- not the declared ones.
"""
from __future__ import annotations

import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE = REPO / "experiments" / "exp004_stage0am" / "runtime_correspondence.json"


@pytest.fixture(scope="module")
def ev():
    assert EVIDENCE.exists(), "no live runtime-correspondence evidence; run lab.stage0am_runtime_gate"
    return json.loads(EVIDENCE.read_text())


def test_gate_passed(ev):
    assert ev["status"] == "PASS" and ev["errors"] == []


def test_realized_surfaces_are_recorded_and_correct(ev):
    assert ev["arms"]["closed"]["realized_tools"] == []
    assert sorted(ev["arms"]["retrieval_enabled"]["realized_tools"]) == ["WebFetch", "WebSearch"]


def test_informational_difference_is_exactly_retrieval(ev):
    closed = set(ev["arms"]["closed"]["realized_tools"])
    web = set(ev["arms"]["retrieval_enabled"]["realized_tools"])
    assert web - closed == {"WebSearch", "WebFetch"}
    assert closed - web == set()


def test_declared_and_realized_are_recorded_separately(ev):
    """The whole point: the record must show BOTH, so drift is visible."""
    for arm in ("closed", "retrieval_enabled"):
        a = ev["arms"][arm]
        assert a["declared_tools"] and a["realized_tools"] is not None
    assert ev["arms"]["closed"]["declared_tools"] != ev["arms"]["closed"]["realized_tools"], \
        "TodoWrite is unrecognized at runtime; if this ever becomes equal, re-audit the closed arm"


def test_neither_arm_can_read_files(ev):
    for arm in ("closed", "retrieval_enabled"):
        assert ev["arms"][arm]["can_read_files"] is False


def test_both_arms_share_one_solver_model(ev):
    solver = {m for arm in ev["arms"].values() for m in arm["models_used"] if "haiku" not in m}
    assert len(solver) == 1, f"arms did not share one solver model: {solver}"
    assert ev["arms"]["closed"]["models_used"] == ev["arms"]["retrieval_enabled"]["models_used"]


def test_dispatch_mode_is_identical_for_both_arms(ev):
    assert "identical for both arms" in ev["dispatch_mode"]
    assert "--allowedTools WebSearch WebFetch" in ev["dispatch_mode"]
