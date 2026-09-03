"""Stage 0B ground truth — the reference adjudicator, and its independence.

The bound on the grader's defect rate is worth exactly as much as the verdicts it
is compared against. These tests pin the two properties that give it any value:
the reference does not import the rule under test, and it refuses to decide the
cases where a deterministic rule is known to be unreliable.
"""
from __future__ import annotations

import inspect

import pytest

from lab import stage0b_adjudication as adj
from lab import stage0b_calibration as cal

ENTITY = {"accept": ["Bolsonaro"], "rejects": ["Lula"]}


class TestTheReferenceIsIndependentOfTheRuleUnderTest:

    def test_it_does_not_import_the_candidate_grader(self):
        src = inspect.getsource(adj)
        assert "grading_v2" not in src.replace(
            "`lab/grading_v2.py` is deliberately NOT imported here", "")
        assert not any(m.startswith("grade") for m in dir(adj))

    def test_it_reads_a_fixed_window_not_the_graders_sentence_span(self):
        # The grader's span is the first SENTENCE capped at 240 chars, with
        # abbreviation handling. The reference uses a flat 240-character window and
        # whole-answer ordering, so it cannot agree with the span rule for the span
        # rule's own reasons.
        assert adj.OPENING_CHARS == 240
        assert "answer_span" not in inspect.getsource(adj)

    def test_the_ledger_refuses_a_grader_authored_ground_truth(self):
        row = cal.CalibrationRow(
            item_id="cal001", pool="calibration", subset="development", batch=1,
            production_barred=True, stem="s", route="exact_entity",
            answer_key={"route": "exact_entity", "accept": ["A"], "rejects": ["B"]},
            screen_spec={"route": "exact_entity", "displacing_aliases": ["B"],
                         "affirming_aliases": ["A"]},
            key_sources=[{"identifier": "u", "title": "t", "establishes": "e",
                          "accessed": "2026-09-03", "tier": "authoritative_primary",
                          "verifier": "test"}],
            key_provenance="doc#1", query_subject="x", anchor_as_written="in 2015",
            grader_verdict_closed="CORRECT", grader_fingerprint="abc",
            hand_verdict_recorded_first=True, hand_adjudicator="lab.grading_v2")
        assert any("may never produce its own ground truth" in p
                   for p in cal.validate_row(row))

    def test_the_ledger_refuses_an_unattributed_ground_truth(self):
        row = cal.CalibrationRow(
            item_id="cal002", pool="calibration", subset="development", batch=1,
            production_barred=True, stem="s", route="exact_entity",
            answer_key={"route": "exact_entity", "accept": ["A"], "rejects": ["B"]},
            screen_spec={"route": "exact_entity", "displacing_aliases": ["B"],
                         "affirming_aliases": ["A"]},
            key_sources=[{"identifier": "u", "title": "t", "establishes": "e",
                          "accessed": "2026-09-03", "tier": "authoritative_primary",
                          "verifier": "test"}],
            key_provenance="doc#1", query_subject="x", anchor_as_written="in 2015",
            grader_verdict_closed="CORRECT", grader_fingerprint="abc",
            hand_verdict_recorded_first=True)
        assert any("WHO produced the reference verdict" in p
                   for p in cal.validate_row(row))


class TestItDecidesOnlyWhatTheKeyCanDecide:

    def test_an_accept_alias_alone_is_determinate(self):
        a = adj.reference_verdict("exact_entity", "Bolsonaro held the office.", ENTITY)
        assert (a.disposition, a.verdict) == (adj.DETERMINATE, "CORRECT")

    def test_a_reject_alias_alone_is_determinate(self):
        a = adj.reference_verdict("exact_entity", "Lula held the office.", ENTITY)
        assert (a.disposition, a.verdict) == (adj.DETERMINATE, "INCORRECT")

    def test_accept_before_reject_is_determinate_and_elaboration_does_not_flip_it(self):
        a = adj.reference_verdict(
            "exact_entity", "Bolsonaro was president, and was later succeeded by Lula.",
            ENTITY)
        assert (a.disposition, a.verdict) == (adj.DETERMINATE, "CORRECT")

    def test_a_reject_leading_an_accept_escalates_rather_than_guessing(self):
        a = adj.reference_verdict(
            "exact_entity", "Lula, who succeeded Bolsonaro, was president.", ENTITY)
        assert a.needs_human and a.reason == "REJECT_LEADS_ACCEPT"

    def test_a_leading_contrastive_negation_escalates(self):
        # The grader's own documented limitation. A reference that decided this
        # case would certify the grader against its blind spot.
        a = adj.reference_verdict(
            "exact_entity", "Not Lula — Bolsonaro held the office.", ENTITY)
        assert a.needs_human and a.reason == "CONTRASTIVE_NEGATION"

    def test_a_contested_premise_escalates_and_is_a_recipe_finding(self):
        a = adj.reference_verdict(
            "exact_entity", "Strictly speaking, none — there was no such office.", ENTITY)
        assert a.needs_human and a.reason == "PREMISE_CONTEST"
        assert "recipe" in adj.ESCALATION_REASONS["PREMISE_CONTEST"]

    def test_an_answer_outside_the_keys_alias_coverage_escalates(self):
        a = adj.reference_verdict("exact_entity", "Someone else entirely.", ENTITY)
        assert a.needs_human and a.reason == "NO_KEY_MATCH"

    def test_an_explicit_abstention_is_determinate(self):
        a = adj.reference_verdict("exact_entity", "I don't know who held it.", ENTITY)
        assert (a.disposition, a.verdict) == (adj.DETERMINATE, "ABSTAIN")

    def test_an_empty_answer_is_determinate(self):
        assert adj.reference_verdict("exact_entity", "", ENTITY).verdict == "ABSTAIN"


class TestBooleanAndNumericRoutes:

    def test_a_plain_polarity_token_decides(self):
        assert adj.reference_verdict("boolean", "Yes, it did.", {"expected": True}
                                     ).verdict == "CORRECT"
        assert adj.reference_verdict("boolean", "No.", {"expected": True}
                                     ).verdict == "INCORRECT"

    def test_a_second_polarity_token_in_the_opening_escalates(self):
        a = adj.reference_verdict("boolean", "Yes, although it was not ratified.",
                                  {"expected": True})
        assert a.needs_human and a.reason == "CONTRASTIVE_NEGATION"

    def test_a_boolean_with_no_polarity_token_escalates(self):
        a = adj.reference_verdict("boolean", "It happened in 1994.", {"expected": True})
        assert a.needs_human and a.reason == "NO_POLARITY"

    def test_an_in_tolerance_value_alone_decides(self):
        a = adj.reference_verdict("numeric", "The answer is 8.",
                                  {"value": 8, "tolerance": 0, "reject_values": [9]})
        assert (a.disposition, a.verdict) == (adj.DETERMINATE, "CORRECT")

    def test_a_reject_value_alone_decides(self):
        a = adj.reference_verdict("numeric", "The answer is 9.",
                                  {"value": 8, "tolerance": 0, "reject_values": [9]})
        assert (a.disposition, a.verdict) == (adj.DETERMINATE, "INCORRECT")

    def test_both_values_present_escalates(self):
        a = adj.reference_verdict("numeric", "It is 8 today, though 9 since the change.",
                                  {"value": 8, "tolerance": 0, "reject_values": [9]})
        assert a.needs_human and a.reason == "MULTIPLE_NUMERIC_CANDIDATES"

    def test_an_unknown_route_is_refused(self):
        with pytest.raises(ValueError):
            adj.reference_verdict("freeform", "x", {})


class TestTheManualPrerequisiteIsStatedBeforeDispatch:

    def test_the_plan_names_who_may_never_adjudicate(self):
        never = adj.adjudication_plan(48)["who_adjudicates"]["never"]
        assert any("candidate grader" in n for n in never)
        assert any("already seen" in n for n in never)

    def test_the_forecast_is_declared_to_be_a_forecast_and_sizes_nothing(self):
        f = adj.adjudication_plan(48)["manual_burden_forecast"]
        assert "sizes no sample" in f["note"]
        assert f["forecast_human_adjudications"] == round(
            48 * 3 * adj.FORECAST_ESCALATION_RATE)

    def test_the_prerequisite_is_stated_as_a_precondition_of_dispatch(self):
        plan = adj.adjudication_plan(cal.BATCH1_TARGET_SCREENED)
        assert "BEFORE the candidate grader is run" in plan["MANUAL_PREREQUISITE"]
        assert "not to skip adjudication" in plan["MANUAL_PREREQUISITE"]

    def test_the_calibration_report_carries_the_plan(self):
        assert "MANUAL_PREREQUISITE" in cal.report()["adjudication"]

    def test_the_ordering_rule_is_stated(self):
        assert "BEFORE the candidate grader runs" in adj.adjudication_plan(48)["ordering"]
