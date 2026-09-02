"""Behavioural golden corpus for the frozen Stage 0A-M grader.

P6 predicted that a 'harmless' grader edit could change a verdict while ordinary
unit tests stay green. This corpus pins expected verdicts that were derived from
the frozen semantics BY HAND (see the YAML header), so any change in behaviour is
visible. It does not modify the grader; it observes it.
"""
from __future__ import annotations

import hashlib
import pathlib

import pytest
import yaml

from lab.anchored_grading import grade_boolean, grade_exact_entity, grade_numeric

REPO = pathlib.Path(__file__).resolve().parent.parent
CORPUS_PATH = REPO / "tests" / "golden" / "stage0am_grader_golden_corpus.yaml"
CORPUS = yaml.safe_load(CORPUS_PATH.read_text())
CASES = CORPUS["cases"]


def _run(case):
    k, a = case["key"], case["answer"]
    if case["route"] == "numeric":
        return grade_numeric(a, k["value"], k["tolerance"], k.get("rejects", []))
    if case["route"] == "exact_entity":
        return grade_exact_entity(a, k["accept"], k.get("rejects", []))
    if case["route"] == "boolean":
        return grade_boolean(a, k["expected"])
    raise ValueError(case["route"])


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_current_grader_matches_golden_corpus(case):
    assert _run(case) is case["expect"], f"{case['id']}: {case['why']} | answer={case['answer']!r}"


def test_corpus_covers_every_route_and_is_synthetic():
    routes = {c["route"] for c in CASES}
    assert routes == {"numeric", "exact_entity", "boolean"}
    assert len(CASES) >= 50
    # no production stem text: production stems are questions; the corpus holds answers only
    assert not any("?" in c["answer"] for c in CASES)


def test_grader_fingerprint_matches_manifest_so_corpus_is_pinned_to_the_frozen_grader():
    import json
    m = json.loads((REPO / "experiments" / "exp004_stage0am" / "manifest.json").read_text())
    sha = hashlib.sha256((REPO / "lab" / "anchored_grading.py").read_bytes()).hexdigest()[:16]
    assert sha == m["grading_semantics"]["sha256_16"], \
        "grader changed: re-fingerprint the manifest AND re-derive the golden corpus by hand"
