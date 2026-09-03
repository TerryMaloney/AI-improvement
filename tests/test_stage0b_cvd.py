"""C-vs-D inferential status — the rule that Stage 0A-M did not have.

Stage 0A-M reported D=2 as a null. At D=2 the smallest attainable two-sided p is
1/2. These tests pin the arithmetic that makes such a report impossible for
Stage 0B's secondary comparison, and pin the pre-freeze authorization gate.
"""
from __future__ import annotations

from fractions import Fraction

import pytest

from lab.stage0b_cvd import (ALPHA_SECONDARY, DELTA_GAP_PREREGISTERED,
                             DESIGN_POINT_SCENARIOS, MIN_DISCORDANT_FOR_A_CLAIM,
                             CvDScenario, analyse, authorize, can_reject_at,
                             exact_two_sided_p, n_for_power, report_realized,
                             smallest_attainable_p)


class TestTheArithmeticFloor:

    @pytest.mark.parametrize("d,expected", [
        (0, Fraction(1)), (1, Fraction(1)), (2, Fraction(1, 2)), (3, Fraction(1, 4)),
        (4, Fraction(1, 8)), (5, Fraction(1, 16)), (6, Fraction(1, 32)),
    ])
    def test_smallest_attainable_two_sided_p(self, d, expected):
        assert smallest_attainable_p(d) == expected

    def test_five_discordant_pairs_cannot_reject_two_sided_at_005(self):
        assert not can_reject_at(5)

    def test_six_discordant_pairs_can(self):
        assert can_reject_at(6)

    def test_the_claim_floor_is_the_first_count_that_can_reject(self):
        assert MIN_DISCORDANT_FOR_A_CLAIM == 6
        assert can_reject_at(MIN_DISCORDANT_FOR_A_CLAIM)
        assert not can_reject_at(MIN_DISCORDANT_FOR_A_CLAIM - 1)

    def test_stage0am_realized_discordance_could_not_have_rejected(self):
        assert smallest_attainable_p(2) == Fraction(1, 2)

    def test_the_two_sided_p_is_symmetric(self):
        assert exact_two_sided_p(7, 1) == exact_two_sided_p(1, 7)


class TestTheReportingRule:

    def test_a_low_discordant_count_is_reported_as_incapable_not_as_a_null(self):
        r = report_realized(2, 0)
        assert r["status"] == "UNINFORMATIVE — INCAPABLE OF REJECTING"
        assert "could not have rejected" in r["required_wording"]
        assert "no evidence" not in r["required_wording"].lower()

    def test_a_powered_null_says_it_could_have_rejected(self):
        r = report_realized(5, 5)
        assert r["status"] == "NULL, AND POWERED ENOUGH TO SAY SO"
        assert "could have rejected" in r["required_wording"]

    def test_a_rejection_is_reported_as_one(self):
        r = report_realized(8, 0)
        assert r["status"] == "REJECTED"
        assert Fraction(r["p"]) <= ALPHA_SECONDARY

    def test_every_status_carries_the_smallest_attainable_p(self):
        for n10, n01 in [(0, 0), (2, 0), (5, 5), (8, 0)]:
            assert "smallest_attainable_p" in report_realized(n10, n01)


class TestPreFreezeAuthorization:

    def test_at_the_recommended_n_the_claim_is_not_authorized(self):
        """The finding this module was written to surface: C-vs-D at n=50 has
        power 0.60 against the preregistered gap, not 0.80."""
        s = DESIGN_POINT_SCENARIOS["query construction matters by exactly the preregistered gap"]
        a = authorize(s, 50)
        assert a["verdict"] == "CLAIM_WITHDRAWN_BEFORE_RUN"
        assert any("power" in r for r in a["reasons"])
        assert 0.55 < a["analysis"]["power"] < 0.65

    def test_it_would_need_about_seventy_six_items(self):
        s = DESIGN_POINT_SCENARIOS["query construction matters by exactly the preregistered gap"]
        n = n_for_power(s)
        assert n is not None and 70 <= n <= 82
        assert authorize(s, n)["verdict"] == "CLAIM_AUTHORIZED"

    def test_a_large_gap_is_authorized_at_the_recommended_n(self):
        s = DESIGN_POINT_SCENARIOS["query construction matters a lot (model query drops the anchor)"]
        assert authorize(s, 50)["verdict"] == "CLAIM_AUTHORIZED"

    def test_a_gap_below_the_preregistered_one_is_refused_even_if_powered(self):
        """Otherwise the design would end up detecting a difference nobody
        preregistered as mattering."""
        s = CvDScenario(p=0.95, delta_C=0.30, delta_D=0.25)
        a = authorize(s, 400)
        assert a["verdict"] == "CLAIM_WITHDRAWN_BEFORE_RUN"
        assert any("preregistered" in r for r in a["reasons"])

    def test_withdrawal_keeps_arm_D(self):
        s = DESIGN_POINT_SCENARIOS["query construction matters by exactly the preregistered gap"]
        a = authorize(s, 50)
        assert "Arm D is still run" in a["if_withdrawn"]

    def test_the_null_world_falls_below_the_discordance_floor(self):
        s = DESIGN_POINT_SCENARIOS["nothing displaces anything (the A-vs-C null world)"]
        r = analyse(s, 50)
        assert r["E_discordant"] < MIN_DISCORDANT_FOR_A_CLAIM
        assert not r["meets_discordance_floor"]


class TestGraderNoiseHurtsCvDMoreThanThePrimary:

    def test_symmetric_grader_error_manufactures_balanced_discordance(self):
        """In the one-sided primary, symmetric FNs delete at-risk items with no trace
        in the discordant counts. Here they ADD balanced discordance, which the sign
        test spends its evidence on."""
        clean = CvDScenario(p=0.95, delta_C=0.30, delta_D=0.10)
        noisy = CvDScenario(p=0.95, delta_C=0.30, delta_D=0.10, g=0.20)
        rc, rn = analyse(clean, 50), analyse(noisy, 50)
        assert rn["E_discordant"] > rc["E_discordant"]      # more discordance
        assert rn["power"] < rc["power"] / 2                # far less power

    def test_at_stage0am_grader_rates_no_reachable_n_saves_it(self):
        s = CvDScenario(p=0.95, delta_C=0.30, delta_D=0.10, g=0.20)
        assert n_for_power(s, n_max=240) is None

    def test_the_alpha_is_its_own_family_and_does_not_touch_the_primary(self):
        assert ALPHA_SECONDARY == Fraction(1, 20)
        assert DELTA_GAP_PREREGISTERED == 0.20
