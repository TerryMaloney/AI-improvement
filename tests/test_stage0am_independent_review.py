"""Pins the INDEPENDENT review of Stage 0A-M to the persisted artifacts.

These are regression tests on a finished experiment. Their job is not to
re-derive the science but to make the review's load-bearing numbers break loudly
if any artifact under `runs/exp004_stage0am/` is ever edited -- which is exactly
what the freeze exists to prevent.

Nothing here regrades the run or touches the frozen result.
"""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

import pytest

from lab.stage0am_review import (cp_upper, entity_forensics, exact_one_sided_p, holm,
                                 integrity, load_all, min_attainable_p, posthoc_regrade,
                                 reconstruct, retrieval_uptake, smallest_rejecting_D,
                                 boolean_forensics, discordant_pairs)

REPO = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def data():
    return load_all()


# ---------------------------------------------------------------- statistics

def test_exact_test_and_holm_reimplementation_agrees_with_the_frozen_procedure():
    """The review re-implements the test. If the two ever disagree, the review's
    independence is worthless -- so assert they agree on a spread of inputs."""
    from lab.stage0am import exact_one_sided_p as frozen_p
    from lab.stage0am import holm as frozen_holm
    for n10 in range(0, 9):
        for n01 in range(0, 9):
            assert float(exact_one_sided_p(n10, n01)) == pytest.approx(frozen_p(n10, n01))
    pv = {"a": Fraction(3, 4), "b": Fraction(1)}
    assert holm(pv) == frozen_holm({k: float(v) for k, v in pv.items()})


def test_rejection_floor_is_a_property_of_D_alone():
    assert min_attainable_p(2) == Fraction(1, 4)
    assert smallest_rejecting_D(Fraction(1, 20)) == 5
    assert smallest_rejecting_D(Fraction(1, 40)) == 6


# ------------------------------------------------------------- phase 1

def test_execution_integrity(data):
    i = integrity(data)
    assert i["n_raw_files"] == i["n_ledger_rows"] == i["n_graded_rows"] == 130
    assert i["n_items"] == i["n_complete_pairs"] == 65
    assert i["incomplete_pairs"] == []
    assert i["per_file_hashes_match_freeze_record"]
    assert i["ledger_sha_recomputed"] == i["ledger_sha_in_freeze_record"]
    assert i["combined_sha_recomputed"] == i["combined_sha_in_freeze_record"]
    assert i["frozen_before_grading_flag"]
    assert i["grading_added_no_other_field_change"]
    assert i["grader_sha_recomputed"] == i["grader_sha_expected"]
    assert i["single_freeze_commit"] == [i["freeze_commit_expected"]]
    assert i["dispatch_failures"] == ["None"]
    assert i["ungradeable_rows"] == 0
    assert i["schedule_compliance_errors"] == []
    assert i["dispatch_order_is_1_to_n"]
    assert i["permission_denials_total"] == 0
    assert i["harness_errors_total"] == 0
    assert i["served_models_seen"]["claude-opus-5"] == 130


# ------------------------------------------------------------- phase 2

def test_primary_reconstruction_reproduces_the_official_result(data):
    r = reconstruct(data)
    assert r["regrade_matches_frozen_ledger"], r["regrade_mismatches"]
    d = r["classes"]["date_anchored"]
    assert (d["n00"], d["n01"], d["n10"], d["n11"], d["D"], d["n"]) == (14, 1, 1, 9, 2, 25)
    assert d["p_exact_fraction"] == "3/4"
    b = r["classes"]["definition_anchored"]
    assert (b["n11"], b["D"], b["n"]) == (25, 0, 25)
    assert b["p_exact_fraction"] == "1"
    c = r["classes"]["arithmetic_control"]
    assert (c["n11"], c["D"], c["n"]) == (15, 0, 15)
    assert not r["any_primary_rejected"]
    assert all(r["agrees_with_official_analysis_json"].values())
    assert not r["materially_disagrees"]


def test_the_run_could_not_have_rejected_at_its_realized_discordance(data):
    """At D=2 the smallest attainable p is 1/4. No orientation of the observed
    discordant pairs reaches any Holm threshold."""
    r = reconstruct(data)
    assert r["classes"]["date_anchored"]["min_attainable_p_at_realized_D"] == 0.25
    assert r["classes"]["definition_anchored"]["min_attainable_p_at_realized_D"] == 1.0


# ------------------------------------------------------------- phases 3-4

def test_every_entity_trial_named_the_correct_anchored_entity(data):
    e = entity_forensics(data)
    assert e["n_entity_trials"] == 32
    assert e["accept_present"] == 32 and e["accept_absent"] == 0
    assert e["graded_correct"] == 4
    assert e["accept_present_but_graded_incorrect"] == 28
    assert e["accept_and_reject_both_present"] == 28
    assert e["of_those_accept_strictly_first"] == 28
    assert e["of_those_graded_incorrect"] == 28


def test_the_boolean_route_carries_a_second_undocumented_artifact(data):
    """Not named in the Stage 0A-M report: a09 opened with the correct polarity
    token in BOTH arms and was graded incorrect in both, because 'no longer'
    appears four sentences later."""
    b = boolean_forensics(data)
    assert b["n_boolean_trials"] == 14
    assert b["all_answers_lead_with_a_polarity_token"]
    assert b["leading_token_correct"] == 14
    assert b["leading_token_correct_but_graded_incorrect"] == 2
    assert sorted(b["affected_trials"]) == ["a09-closed", "a09-retrieval_enabled"]


def test_under_a_repaired_grader_the_whole_run_is_at_ceiling(data):
    """POST-HOC and diagnostic only. It is the finding that decides the battery's
    fate: not one of 130 trials gave a substantively wrong answer, so the date
    class's apparent difficulty was entirely instrumental."""
    c = posthoc_regrade(data)
    assert c["total_correct"] == c["total_trials"] == 130
    assert c["every_class_has_zero_discordance"]
    assert all(t["D"] == 0 for t in c["tables"].values())
    assert "POST-HOC" in c["LABEL"]


# ------------------------------------------------------------- phase 5

def test_both_discordant_pairs_are_grading_artifacts_not_displacement(data):
    d = discordant_pairs(data)
    assert sorted(p["item"] for p in d) == ["a13", "a23"]
    for p in d:
        assert p["both_arms_named_the_accepted_entity"]
        assert p["retrieval_arm_performed_no_retrieval"]
        assert p["classification"] == "GRADING / ELABORATION ARTIFACT"


# ------------------------------------------------------------- phase 6

def test_retrieval_uptake_and_where_it_landed(data):
    u = retrieval_uptake(data)
    assert u["n_treated"] == 65
    assert u["attempted_retrieval"] == 8
    assert u["not_attempted"] == 57
    assert u["web_fetch_attempted"] == 0
    assert u["num_turns_gt_1_iff_search_recorded"]
    assert u["search_requests_billed_to_solver_model"] == 0
    assert u["top_level_server_tool_use_web_search_total"] == 0
    # every attempt landed in the class that had no outcome variance
    assert u["attempts_by_class"]["definition_anchored"] == "8/25"
    assert u["attempts_by_class"]["date_anchored"] == "0/25"
    assert u["attempts_by_class"]["arithmetic_control"] == "0/15"
    assert u["among_attempted"]["discordant"] == 0


def test_official_analysis_json_reports_a_vacuous_retrieval_rate(data):
    """`analysis.json` says attempted_retrieval=0 because `analyse_run` fed
    `retrieval_failure_rate` empty tuples for every trial. The primary result does
    not depend on it, but the field is not a measurement and must not be cited."""
    u = retrieval_uptake(data)
    assert u["official_analysis_json_claim"]["attempted_retrieval"] == 0
    assert u["official_analysis_json_claim"]["declined_retrieval"] == 65
    assert u["official_claim_is_vacuous"]


# ------------------------------------------------------------- bounds

def test_the_harm_bounds_the_run_actually_earned(data):
    assert cp_upper(0, 25) == pytest.approx(0.1129, abs=1e-4)
    assert cp_upper(0, 15) == pytest.approx(0.1810, abs=1e-4)
    assert cp_upper(1, 25) == pytest.approx(0.1761, abs=1e-4)
    # the only bound about CONSUMED retrieval rests on 8 trials
    assert cp_upper(0, 8) == pytest.approx(0.3123, abs=1e-4)


def test_the_persisted_review_artifact_is_current():
    """If the review module changes, the committed JSON must be regenerated."""
    from lab.stage0am_review import review
    path = REPO / "runs" / "exp004_stage0am" / "independent_review.json"
    assert path.exists(), "run: python -m lab.stage0am_review"
    on_disk = json.loads(path.read_text())
    fresh = json.loads(json.dumps(review(), default=str))
    assert on_disk == fresh, "stale independent_review.json: re-run lab.stage0am_review"


def test_the_review_never_writes_a_frozen_artifact():
    src = (REPO / "lab" / "stage0am_review.py").read_text()
    for frozen in ("trials.jsonl", "graded.jsonl", "analysis.json",
                   "raw_outcomes.frozen.json", "anchored_grading.py"):
        assert f'write_text' not in src.split(frozen)[0][-200:], frozen
    assert src.count("write_text") == 1, "the review writes exactly one file"
