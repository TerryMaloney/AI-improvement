"""Failure semantics: a retrieval-tool failure is data; a dead dispatch is not.

These tests exist because the specification carried a real contradiction into the
pre-freeze state. Section 6 kept a trial whose retrieval failed inside the
intent-to-treat arm; section 7 defined an egress refusal as a technical failure
that voided the item across both arms. Both cannot govern a solver whose WebFetch
was refused but which still answered -- which, in the measured environment, is the
ordinary case rather than an edge case.

Nothing here dispatches.
"""
from __future__ import annotations

import pytest

from lab.stage0am import (
    DISPATCH_FAILURES,
    RETRIEVAL_TOOL_OUTCOMES,
    TrialOutcome,
    analyse,
    pair_disposition,
    partition_pairs,
    retrieval_failure_rate,
    trial_is_gradeable,
)


def closed(item="i1", graded=1, dispatch_failure=None):
    return TrialOutcome(item_id=item, arm="closed", graded=graded,
                        dispatch_failure=dispatch_failure)


def retrieval(item="i1", graded=0, outcomes=("OK",), dispatch_failure=None):
    return TrialOutcome(item_id=item, arm="retrieval_enabled", graded=graded,
                        retrieval_outcomes=outcomes, dispatch_failure=dispatch_failure)


class TestTheSixRequiredCases:
    def test_1_webfetch_refused_but_answer_returned_is_retained_and_graded(self):
        r = retrieval(outcomes=("REFUSED_BY_PROXY",), graded=0)
        assert trial_is_gradeable(r)
        assert pair_disposition(closed(graded=1), r) == "RETAIN"
        retained, voided, _ = partition_pairs([(closed(graded=1), r)])
        assert retained == [(1, 0)] and voided == []

    def test_2_websearch_fails_but_answer_returned_is_retained_and_graded(self):
        for outcome in ("TOOL_ERROR", "TOOL_TIMEOUT"):
            r = retrieval(outcomes=(outcome,), graded=1)
            assert trial_is_gradeable(r)
            assert pair_disposition(closed(graded=1), r) == "RETAIN"

    def test_3_solver_dispatch_dies_before_answering_voids_the_pair(self):
        r = retrieval(graded=None, dispatch_failure="AGENT_TERMINATED")
        assert not trial_is_gradeable(r)
        assert pair_disposition(closed(graded=1), r) == "VOID_PAIR"
        retained, voided, cause = partition_pairs([(closed(graded=1), r)])
        assert retained == [] and voided == ["i1"]
        assert cause["retrieval_enabled"] == 1

    def test_4_closed_arm_dispatch_dies_before_answering_voids_the_pair(self):
        c = closed(graded=None, dispatch_failure="EMPTY_RESPONSE")
        assert pair_disposition(c, retrieval(graded=0)) == "VOID_PAIR"
        _, voided, cause = partition_pairs([(c, retrieval(graded=0))])
        assert voided == ["i1"] and cause["closed"] == 1

    def test_5_poor_or_unhelpful_retrieval_is_retained(self):
        for outcome in ("EMPTY_RESULTS", "UNHELPFUL_RESULTS"):
            r = retrieval(outcomes=(outcome,), graded=0)
            assert pair_disposition(closed(graded=1), r) == "RETAIN"

    def test_6_model_declining_all_retrieval_is_retained(self):
        r = retrieval(outcomes=("NOT_ATTEMPTED",), graded=1)
        assert pair_disposition(closed(graded=1), r) == "RETAIN"


class TestTheRuleIsNotConditionedOnToolSuccess:
    def test_every_retrieval_outcome_leaves_a_gradeable_trial_gradeable(self):
        """The whole point: no member of the retrieval vocabulary can void."""
        for outcome in RETRIEVAL_TOOL_OUTCOMES:
            assert trial_is_gradeable(retrieval(outcomes=(outcome,), graded=0))

    def test_every_dispatch_failure_makes_a_trial_ungradeable(self):
        for failure in DISPATCH_FAILURES:
            assert not trial_is_gradeable(retrieval(graded=None, dispatch_failure=failure))

    def test_a_dispatch_failure_voids_even_if_a_grade_was_somehow_recorded(self):
        """Belt and braces: the failure flag wins over a stray grade."""
        assert not trial_is_gradeable(retrieval(graded=1, dispatch_failure="DISPATCH_ERROR"))

    def test_an_all_refused_run_still_analyses_every_item(self):
        """The measured environment is fetch-blocked. If a blocked fetch voided
        items, this run would lose every pair and the 10% ceiling would
        invalidate an experiment that in fact produced 25 gradeable pairs."""
        pairs = [(closed(f"i{n}", graded=1),
                  retrieval(f"i{n}", graded=n % 2, outcomes=("REFUSED_BY_PROXY", "OK")))
                 for n in range(25)]
        retained, voided, _ = partition_pairs(pairs)
        assert len(retained) == 25 and voided == []
        result = analyse({"date_anchored": retained})
        assert result.primary["date_anchored"].n_items == 25

    def test_unknown_dispatch_failure_is_rejected_not_silently_ignored(self):
        with pytest.raises(ValueError, match="unknown dispatch failure"):
            trial_is_gradeable(retrieval(graded=None, dispatch_failure="MYSTERY"))

    def test_a_pair_must_be_one_item_and_one_arm_each(self):
        with pytest.raises(ValueError, match="pair spans two items"):
            pair_disposition(closed("i1"), retrieval("i2"))
        with pytest.raises(ValueError, match="one arm of each"):
            pair_disposition(closed(), closed())


class TestVoidAccountingIsReportedByArm:
    def test_void_cause_is_attributed_to_the_arm_that_failed(self):
        pairs = [
            (closed("a", graded=1), retrieval("a", graded=0)),
            (closed("b", graded=None, dispatch_failure="DISPATCH_ERROR"), retrieval("b", graded=0)),
            (closed("c", graded=1), retrieval("c", graded=None, dispatch_failure="AGENT_TERMINATED")),
            (closed("d", graded=None, dispatch_failure="TRANSPORT_TIMEOUT"),
             retrieval("d", graded=None, dispatch_failure="TRANSPORT_TIMEOUT")),
        ]
        retained, voided, cause = partition_pairs(pairs)
        assert len(retained) == 1 and sorted(voided) == ["b", "c", "d"]
        assert cause == {"closed": 1, "retrieval_enabled": 1, "both": 1}

    def test_retrieval_failure_rate_is_reported_never_used_to_filter(self):
        trials = [
            retrieval("a", outcomes=("REFUSED_BY_PROXY",)),
            retrieval("b", outcomes=("REFUSED_BY_PROXY", "OK")),
            retrieval("c", outcomes=("NOT_ATTEMPTED",)),
            closed("d"),
        ]
        rate = retrieval_failure_rate(trials)
        assert rate["n_treated"] == 3
        assert rate["declined_retrieval"] == 1
        assert rate["attempted_retrieval"] == 2
        assert rate["all_retrieval_calls_failed"] == 1
        assert rate["rate_all_failed_given_attempted"] == 0.5


class TestSpecificationMatchesTheCode:
    import pathlib
    import re as _re

    _RAW = (pathlib.Path(__file__).resolve().parent.parent
            / "docs" / "EXP004_STAGE0A_M_SPECIFICATION.md").read_text()
    SPEC = _re.sub(r"\s+", " ", _RAW).lower()          # the doc is wrapped at 80 cols
    SEVEN = _re.sub(r"\s+", " ", _RAW.split("## 7.")[1].split("## 8.")[0]).lower()

    def test_spec_names_both_failure_categories(self):
        assert "retrieval-tool outcome" in self.SEVEN
        assert "dispatch-level failure" in self.SEVEN

    def test_spec_states_the_discriminating_question(self):
        assert "did the dispatch yield a gradeable final answer" in self.SEVEN

    def test_an_egress_refusal_is_governed_as_a_retained_outcome(self):
        """The historical rule is quoted in section 7 so the resolution is
        legible, so it is not enough that the word 'void' has disappeared. What
        must hold is that the GOVERNING text puts an egress refusal on the
        retained side."""
        case_a = self.SEVEN.split("### a.")[1].split("### b.")[0]
        assert "refused by the egress proxy" in case_a
        assert "refused_by_proxy" in case_a
        assert "stays in the retrieval-enabled arm" in case_a
        assert "graded normally" in case_a
        assert "never" in case_a and "exclude" in case_a

    def test_the_voiding_category_is_scoped_to_missing_answers_only(self):
        case_b = self.SEVEN.split("### b.")[1].split("### both cases")[0]
        assert "no gradeable final answer exists" in case_b
        for member in ("dispatch_error", "agent_terminated", "transport_timeout",
                       "empty_response", "unparseable_response"):
            assert member in case_b
        for retrieval_outcome in ("refused_by_proxy", "unhelpful_results", "not_attempted"):
            assert retrieval_outcome not in case_b, \
                f"{retrieval_outcome} must not appear in the voiding category"

    def test_the_vocabularies_in_the_spec_match_the_vocabularies_in_the_code(self):
        for member in RETRIEVAL_TOOL_OUTCOMES:
            assert member.lower() in self.SEVEN, f"{member} undocumented in section 7"
        for member in DISPATCH_FAILURES:
            assert member.lower() in self.SEVEN, f"{member} undocumented in section 7"

    def test_the_void_rate_is_reported_by_arm(self):
        assert "broken down by which arm failed" in self.SEVEN

    def test_section_4_no_longer_claims_a_class_average_estimand(self):
        four = self._re.sub(r"\s+", " ", self._RAW.split("## 4.")[1].split("## 5.")[0]).lower()
        # The stale phrase is quoted in the correction, so its mere presence
        # proves nothing. What must hold is that it appears only as an attributed
        # historical quote, never as an assertion in its own right.
        assert "**estimand: the class-average effect**" not in four
        assert 'an earlier draft of this section read "estimand: the class-average effect"' in four
        assert "inferential target: violation of the pointwise null" in four
        assert "the class-average difference is a descriptive summary, not the estimand" in four
        assert "h0_mean is **not** tested" in four
