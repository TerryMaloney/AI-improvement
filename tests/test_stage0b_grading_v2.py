"""Semantic golden corpus for the Stage 0B CANDIDATE grader.

Two things are asserted, and they are different:

  1. the candidate grader matches verdicts derived BY HAND from its stated
     semantics (the corpus), and
  2. the candidate grader actually repairs the two defects the Stage 0A-M
     independent review measured -- asserted directly against the frozen
     Stage 0A-M answers, which are the only real evidence available.

The frozen Stage 0A-M grader is untouched; nothing here regrades the run.
"""
from __future__ import annotations

import json
import pathlib

import pytest
import yaml

from lab.grading_v2 import (SPAN_CHAR_CAP, Verdict, answer_span, grade_v2,
                            is_abstention)

REPO = pathlib.Path(__file__).resolve().parent.parent
CORPUS = yaml.safe_load((REPO / "tests" / "golden" /
                         "stage0b_grader_semantic_corpus.yaml").read_text())
CASES = CORPUS["cases"]
RUN = REPO / "runs" / "exp004_stage0am"


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_candidate_grader_matches_hand_derived_semantics(case):
    got = grade_v2(case["route"], case["answer"], case["key"])
    assert got.value == case["expect"], f"{case['id']}: {case['why']}"


def test_corpus_covers_every_route_and_every_verdict():
    assert {c["route"] for c in CASES} == {"numeric", "exact_entity", "boolean"}
    assert {c["expect"] for c in CASES} == {"CORRECT", "INCORRECT", "ABSTAIN"}


def test_corpus_is_synthetic_and_cannot_leak_a_production_answer():
    keys = yaml.safe_load((REPO / "batteries" / "answers.anchored_v1.yaml").read_text())["answers"]
    aliases = {a.casefold() for k in keys.values()
               for a in list(k.get("accept", [])) + [str(r) for r in k.get("rejects", [])]}
    for c in CASES:
        blob = c["answer"].casefold()
        assert not any(len(a) > 3 and a in blob for a in aliases), \
            f"{c['id']} contains a production alias"


def test_known_limitations_are_recorded_not_hidden():
    """A limitation the corpus does not name is a limitation nobody will fix."""
    limits = [c["id"] for c in CASES if "KNOWN LIMITATION" in c["why"]]
    assert set(limits) == {"e06", "b06"}, limits


# --------------------------------------------------------------------------
# the two defects, asserted against the real frozen Stage 0A-M answers
# --------------------------------------------------------------------------

def _frozen_rows():
    return [json.loads(l) for l in (RUN / "graded.jsonl").read_text().splitlines() if l.strip()]


def _battery():
    return {q["id"]: q for q in
            yaml.safe_load((REPO / "batteries" / "anchored_v1.yaml").read_text())["questions"]}


def _keys():
    return yaml.safe_load((REPO / "batteries" / "answers.anchored_v1.yaml").read_text())["answers"]


def test_candidate_grader_repairs_the_entity_reject_precedence_defect():
    """All 28 entity trials that named the accepted entity first and were graded
    incorrect under reject-precedence are graded correct by the candidate."""
    rows, battery, keys = _frozen_rows(), _battery(), _keys()
    affected = [r for r in rows
                if battery[r["item_id"]]["grading_route"] == "exact_entity" and r["graded"] == 0]
    assert len(affected) == 28, len(affected)
    verdicts = [grade_v2("exact_entity", r["answer"], keys[r["item_id"]]) for r in affected]
    assert all(v is Verdict.CORRECT for v in verdicts)


def test_candidate_grader_repairs_the_boolean_negation_defect():
    """a09 answered 'Yes.' in both arms and was graded incorrect in both because
    'no longer' appeared four sentences later."""
    rows, battery, keys = _frozen_rows(), _battery(), _keys()
    affected = [r for r in rows
                if battery[r["item_id"]]["grading_route"] == "boolean" and r["graded"] == 0]
    assert {r["item_id"] for r in affected} == {"a09"}
    assert all(grade_v2("boolean", r["answer"], keys[r["item_id"]]) is Verdict.CORRECT
               for r in affected)


def test_the_full_verdict_delta_against_the_frozen_grader_is_exactly_known():
    """Characterise EVERY trial the candidate scores differently, in both
    directions. A verdict change nobody enumerated is the failure mode this test
    exists to prevent -- the frozen grader passed 1,397 tests while mis-scoring
    30 of 130 production trials.

    Repairs (0 -> CORRECT): the 28 entity reject-precedence trials and the 2
    a09 boolean-negation trials -- 30 in total, which is every incorrect grade
    in the run.

    Residuals (1 -> not CORRECT): exactly two, each pinned because it motivates
    a DIFFERENT Stage 0B fix, and a silent change in either would quietly remove
    that motivation:

      b18  the direct answer is buried ~360 characters into one long sentence
           -> motivates the answer-first packet instruction;
      a08  the solver's leading answer contests the item's premise ("none")
           -> motivates pre-production item calibration.
    """
    rows, battery, keys = _frozen_rows(), _battery(), _keys()
    repaired, residual = [], []
    for r in rows:
        v = grade_v2(battery[r["item_id"]]["grading_route"], r["answer"], keys[r["item_id"]])
        if r["graded"] == 0 and v is Verdict.CORRECT:
            repaired.append(r["trial_id"])
        elif r["graded"] == 1 and v is not Verdict.CORRECT:
            residual.append(r["trial_id"])
    assert len(repaired) == 30, sorted(repaired)
    assert sum(1 for r in rows if r["graded"] == 0) == 30, "every incorrect grade is repaired"
    assert sorted(residual) == ["a08-closed", "b18-retrieval_enabled"], sorted(residual)


def test_span_rule_properties():
    assert answer_span("Alpha Inc. reported a figure.") == "Alpha Inc. reported a figure."
    assert answer_span("Alpha Inc. As of then it stood.") == "Alpha Inc."
    assert answer_span("") == ""
    assert len(answer_span("x" * 5000)) == SPAN_CHAR_CAP
    assert is_abstention("I do not know.")
    assert not is_abstention("The answer is 12.")
