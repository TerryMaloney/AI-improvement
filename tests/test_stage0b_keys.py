"""The answer key and the screen specification are two objects. Pinned here.

The defect these tests exist to make impossible: a calibration row that cannot
reconstruct its own adjudication key, discovered after the dispatches are paid
for; and one alias pair asked to serve both jobs, which is only coherent on one
of the three routes.
"""
from __future__ import annotations

import pytest

from lab.stage0b_adjudication import DETERMINATE, reference_verdict
from lab.stage0b_keys import (BARE_POLARITY, C1_SCOPE, INVALID_KEY_REASONS, S1,
                              AnswerKey, ScreenSpec, screen_invariant_S1,
                              screen_summary, value_surface_forms)

ENT = AnswerKey("exact_entity", accept=("Angela Merkel", "Merkel"),
                rejects=("Olaf Scholz", "Scholz"))
BOOL = AnswerKey("boolean", expected=False)
NUM = AnswerKey("numeric", value=9, tolerance=0, reject_values=(8,))


class TestTheAnswerKeyIsTypedAndComplete:

    @pytest.mark.parametrize("key", [ENT, BOOL, NUM])
    def test_every_route_validates(self, key):
        assert key.validate() == []

    @pytest.mark.parametrize("key,answer,expected", [
        (ENT, "Angela Merkel was Chancellor.", "CORRECT"),
        (ENT, "Olaf Scholz was Chancellor.", "INCORRECT"),
        (BOOL, "No.", "CORRECT"),
        (BOOL, "Yes.", "INCORRECT"),
        (NUM, "Nine planets.", "CORRECT"),
        (NUM, "Eight planets.", "INCORRECT"),
    ])
    def test_end_to_end_key_to_reference_verdict(self, key, answer, expected):
        adj = reference_verdict(key.route, answer, key.for_reference_verdict())
        assert adj.disposition == DETERMINATE and adj.verdict == expected

    def test_a_boolean_key_without_expected_is_refused(self):
        p = AnswerKey("boolean").validate()
        assert any("no `expected`" in m for m in p)

    def test_a_numeric_key_without_value_or_tolerance_is_refused(self):
        assert any("no `value`" in m for m in AnswerKey("numeric", tolerance=0).validate())
        assert any("no `tolerance`" in m
                   for m in AnswerKey("numeric", value=9, reject_values=(8,)).validate())

    def test_cross_route_fields_are_refused(self):
        assert any("belongs to another route" in m
                   for m in AnswerKey("exact_entity", accept=("a",), rejects=("b",),
                                      expected=True).validate())
        assert any("another route" in m
                   for m in AnswerKey("boolean", expected=True, accept=("a",)).validate())

    def test_the_separation_invariant_is_enforced(self):
        p = AnswerKey("numeric", value=9, tolerance=1, reject_values=(8,)).validate()
        assert any("separation invariant" in m for m in p)

    def test_an_entity_key_whose_aliases_contain_one_another_is_refused(self):
        p = AnswerKey("exact_entity", accept=("Merkel",),
                      rejects=("Angela Merkel",)).validate()
        assert any("contain one another" in m for m in p)

    def test_the_key_round_trips_through_json(self):
        for k in (ENT, BOOL, NUM):
            assert AnswerKey.from_json(k.to_json()) == k


class TestTheScreenSpecIsADifferentObject:

    def test_a_boolean_screen_may_not_be_bare_polarity(self):
        spec = ScreenSpec("boolean", displacing_propositions=("yes",),
                          affirming_propositions=("no",))
        p = spec.validate()
        assert any("bare polarity" in m for m in p)
        assert any("subject and predicate" in m for m in p)

    def test_bare_polarity_tokens_are_enumerated_not_guessed_at(self):
        assert {"yes", "no", "not", "never"} <= BARE_POLARITY

    def test_opposite_side_phrases_may_not_contain_one_another(self):
        v = screen_invariant_S1("boolean", ("finland was a member",),
                                ("finland was not a member",))
        assert v == [] or all("contain one another" not in m for m in v)
        v2 = screen_invariant_S1("exact_entity", ("Scholz",), ("Olaf Scholz",))
        assert any("contain one another" in m for m in v2)

    def test_a_numeric_screen_without_subject_terms_is_refused(self):
        p = ScreenSpec("numeric", displacing_value_forms=("8",)).validate()
        assert any("no subject_terms" in m for m in p)

    def test_a_screen_carrying_another_routes_fields_is_refused(self):
        p = ScreenSpec("boolean", displacing_propositions=("x was a member",),
                       displacing_aliases=("X",)).validate()
        assert any("entity-route fields" in m for m in p)

    def test_the_spec_round_trips_through_json(self):
        s = ScreenSpec("numeric", subject_terms=("planet",),
                       displacing_value_forms=("8", "eight"))
        assert ScreenSpec.from_json(s.to_json()) == s

    def test_value_surface_forms_include_the_word_form(self):
        assert value_surface_forms(8) == ["8", "eight"]


ENT_SPEC = ScreenSpec("exact_entity", displacing_aliases=("Olaf Scholz", "Scholz"),
                      affirming_aliases=("Angela Merkel", "Merkel"))
BOOL_SPEC = ScreenSpec("boolean",
                       displacing_propositions=("finland joined nato",
                                                "finland is a nato member"),
                       affirming_propositions=("finland was not a member of nato",))
NUM_SPEC = ScreenSpec("numeric", subject_terms=("planet",),
                      displacing_value_forms=("8", "eight"),
                      affirming_value_forms=("9", "nine"), proximity_chars=60)


class TestTheEntityScreen:

    def test_reject_entity_asserted_is_divergent(self):
        assert screen_summary(ENT_SPEC, "Olaf Scholz is Chancellor.")["divergent"]

    def test_accept_entity_alone_is_not_divergent(self):
        r = screen_summary(ENT_SPEC, "Angela Merkel was Chancellor in March 2021.")
        assert not r["divergent"] and r["classification"] == "affirming_only"

    def test_both_present_is_divergent_and_labelled_both(self):
        r = screen_summary(ENT_SPEC, "Angela Merkel served until Olaf Scholz took office.")
        assert r["divergent"] and r["classification"] == "both"

    def test_an_unrelated_summary_is_neither(self):
        assert screen_summary(ENT_SPEC, "Germany held an election.")["classification"] \
            == "neither"


class TestTheBooleanScreen:
    """The route where one alias pair was demonstrably incoherent."""

    def test_bare_no_in_unrelated_prose_does_not_create_divergence(self):
        assert not screen_summary(BOOL_SPEC, "There is no doubt it was slow.")["divergent"]

    def test_not_a_member_does_not_assert_the_opposite_proposition(self):
        r = screen_summary(BOOL_SPEC, "Finland was not a member of NATO at that time.")
        assert not r["divergent"]

    def test_a_premise_bearing_displacing_proposition_is_divergent(self):
        assert screen_summary(BOOL_SPEC, "Finland joined NATO on 4 April 2023.")["divergent"]

    def test_a_denied_displacing_proposition_is_not_divergent(self):
        # S1(v). Without the negation guard this fires on a correct denial, which
        # is C1(b)'s lesson arriving on a different route.
        assert not screen_summary(
            BOOL_SPEC, "In 2022 Finland was not a member of NATO.")["divergent"]


class TestTheNumericScreen:
    """A numeral is evidence only when it is asserted OF the requested quantity."""

    def test_reject_value_asserted_of_the_quantity_is_divergent(self):
        assert screen_summary(
            NUM_SPEC, "The IAU recognises eight planets in the Solar System.")["divergent"]

    def test_the_correct_quantity_alone_is_not_a_reject(self):
        r = screen_summary(NUM_SPEC, "At that date the IAU recognised nine planets.")
        assert not r["divergent"] and r["classification"] == "affirming_only"

    def test_a_number_in_a_link_title_date_range_does_not_count(self):
        assert not screen_summary(
            NUM_SPEC, "Ada Lovelace (1815 - 1852) wrote about planets.")["divergent"]

    def test_an_incidental_number_far_from_the_subject_does_not_count(self):
        assert not screen_summary(
            NUM_SPEC,
            "The 8th edition was published; planets were discussed at length in a "
            "separate chapter of the report that followed.")["divergent"]

    def test_a_citation_number_does_not_count(self):
        assert not screen_summary(NUM_SPEC, "See vol. 8 for planets.")["divergent"]

    def test_multiple_numbers_are_handled_deterministically(self):
        r = screen_summary(NUM_SPEC,
                           "Once nine planets, the IAU now recognises eight planets.")
        assert r["divergent"] and r["classification"] == "both"
        assert r == screen_summary(NUM_SPEC,
                                   "Once nine planets, the IAU now recognises eight planets.")

    def test_the_screen_reads_only_the_synthesised_summary(self):
        assert screen_summary(NUM_SPEC, None)["read_region"] == \
            "runtime synthesised summary only"


class TestC1ScopeIsStatedRatherThanBroadened:

    def test_C1s_literal_scope_is_recorded(self):
        assert "accept_trap_markers" in C1_SCOPE["what_C1_literally_governs"]

    def test_the_transferring_parts_are_enumerated(self):
        assert any("bare topic word" in m for m in C1_SCOPE["what_transfers"])
        assert any("bare entity fragment" in m for m in C1_SCOPE["what_transfers"])

    def test_C1c_is_explicitly_NOT_transferred_and_the_reason_is_given(self):
        why = " ".join(C1_SCOPE["what_does_NOT_transfer"])
        assert "C1(c)" in why and "retroactively broaden" in why

    def test_the_stage0b_rule_exists_and_covers_the_numeric_mechanism(self):
        assert "S1" in C1_SCOPE["stage0b_rule"]
        assert "structured numeric mechanism" in S1


class TestInvalidKeysFailAuthoringMechanically:

    def test_every_ambiguity_class_the_review_named_has_a_reason(self):
        for r in ("CONFLICTING_SOURCES", "ANCHOR_AMBIGUOUS", "DEFINITION_AMBIGUOUS",
                  "TOLERANCE_UNDETERMINED", "PREMISE_NOT_RESOLVABLE",
                  "DISPLACING_ANSWER_NOT_UNIQUE"):
            assert r in INVALID_KEY_REASONS and INVALID_KEY_REASONS[r]

    def test_the_a08_lesson_is_carried_by_the_definition_class(self):
        assert "a08" in INVALID_KEY_REASONS["DEFINITION_AMBIGUOUS"]
