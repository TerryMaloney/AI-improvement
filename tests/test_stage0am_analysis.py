"""Stage 0A-M analysis, checked on synthetic data only.

No production item ever appears here. Every distribution is generated from a
seeded RNG so the numbers below are reproducible; they are asserted with margins
wide enough to be stable but tight enough to catch a real regression.
"""

from __future__ import annotations

import random
from math import comb

import pytest

from lab.stage0am import (
    analyse,
    discordance,
    exact_one_sided_p,
    harm_share_upper_bound,
    holm,
)

ALPHA = 0.05


def _draw(rng, cfg):
    """cfg is [(p_closed, p_retrieval), ...]; returns R=1 outcome pairs."""
    return [(int(rng.random() < pb), int(rng.random() < ps)) for pb, ps in cfg]


def _reject_rate(cfg, trials, seed, alpha=ALPHA):
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        n10, n01 = discordance(_draw(rng, cfg))
        if exact_one_sided_p(n10, n01) <= alpha:
            hits += 1
    return hits / trials


class TestExactPValue:
    def test_matches_the_binomial_tail_by_hand(self):
        # 9 baseline-favouring of 10 discordant: P(X>=9), X~Bin(10,1/2)
        expected = (comb(10, 9) + comb(10, 10)) / 2 ** 10
        assert exact_one_sided_p(9, 1) == pytest.approx(expected)

    def test_no_discordant_pairs_is_not_evidence(self):
        assert exact_one_sided_p(0, 0) == 1.0

    def test_all_discordance_one_way_is_the_smallest_attainable_p(self):
        assert exact_one_sided_p(12, 0) == pytest.approx(1 / 2 ** 12)

    def test_ties_do_not_enter(self):
        """Concordant items carry no information; adding them changes nothing."""
        pairs = [(1, 0)] * 6 + [(0, 1)] * 2
        p_bare = exact_one_sided_p(*discordance(pairs))
        p_padded = exact_one_sided_p(*discordance(pairs + [(1, 1)] * 40 + [(0, 0)] * 40))
        assert p_bare == p_padded


class TestTypeIUnderTheClassNull:
    """delta_i >= 0 for every item. The test must not exceed alpha anywhere."""

    @pytest.mark.parametrize("p", [0.3, 0.5, 0.7, 0.85, 0.95])
    def test_tied_items_at_a_range_of_difficulties(self, p):
        rate = _reject_rate([(p, p)] * 25, 4000, seed=hash(("tied", p)) % 2**31)
        assert rate <= 0.06, f"tied null at p={p} rejected {rate:.3f}"

    def test_heterogeneous_tied_difficulties(self):
        cfg = [(0.15 + 0.8 * i / 24, 0.15 + 0.8 * i / 24) for i in range(25)]
        assert _reject_rate(cfg, 4000, seed=11) <= 0.06

    def test_retrieval_helps_every_item_is_strongly_conservative(self):
        """The interior of the null: the test should almost never fire."""
        assert _reject_rate([(0.30, 0.85)] * 25, 4000, seed=12) <= 0.01

    def test_mixed_help_and_ties_still_holds(self):
        cfg = [(0.30, 0.85)] * 10 + [(0.85, 0.85)] * 15
        assert _reject_rate(cfg, 4000, seed=13) <= 0.06


class TestPowerAgainstRealHarm:
    def test_detects_a_large_uniform_class_effect(self):
        rate = _reject_rate([(0.85, 0.30)] * 25, 3000, seed=21)
        assert rate >= 0.90, f"expected strong power, got {rate:.3f}"

    def test_power_falls_with_partial_class_purity(self):
        pure = _reject_rate([(0.85, 0.40)] * 25, 3000, seed=22)
        mixed = _reject_rate([(0.85, 0.40)] * 12 + [(0.85, 0.85)] * 13, 3000, seed=23)
        assert pure > mixed

    def test_blind_to_within_class_sign_heterogeneity(self):
        """Documented limitation, asserted so nobody later claims otherwise:
        equal harmed and helped mass returns a null despite real headroom."""
        cfg = [(0.85, 0.30)] * 12 + [(0.30, 0.85)] * 12
        assert _reject_rate(cfg, 3000, seed=24) <= 0.06


class TestHolm:
    def test_step_down_order_and_thresholds(self):
        assert holm({"a": 0.001, "b": 0.04, "c": 0.9}, 0.05) == {"a": True, "b": False, "c": False}

    def test_all_reject_when_all_tiny(self):
        assert all(holm({"a": 1e-6, "b": 1e-6, "c": 1e-6}, 0.05).values())

    def test_single_hypothesis_is_uncorrected(self):
        assert holm({"a": 0.04}, 0.05) == {"a": True}

    def test_step_down_is_by_rank_not_by_insertion_order(self):
        """a=.001 and c=.002 both clear their step-down thresholds (.05/3, .05/2);
        b=.9 fails and stops the procedure. Ordering is by p-value, not by key."""
        out = holm({"a": 0.001, "b": 0.9, "c": 0.002}, 0.05)
        assert out == {"a": True, "c": True, "b": False}

    def test_a_failure_stops_everything_below_it(self):
        out = holm({"a": 0.001, "b": 0.9, "c": 0.03}, 0.05)
        assert out["a"] is True and out["c"] is False and out["b"] is False

    def test_family_wise_error_over_three_true_nulls(self):
        rng = random.Random(31)
        cfg = [(0.6, 0.6)] * 25
        hits = 0
        for _ in range(3000):
            ps = {name: exact_one_sided_p(*discordance(_draw(rng, cfg))) for name in "abc"}
            if any(holm(ps, ALPHA).values()):
                hits += 1
        assert hits / 3000 <= 0.06


class TestNegativeControlIsOutsideTheFamily:
    def test_control_is_never_marked_rejected(self):
        r = analyse({"date": [(1, 1)] * 20}, {"arith": [(1, 0)] * 20})
        assert r.negative_control["arith"].rejected is None

    def test_control_does_not_change_primary_thresholds(self):
        primary = {"date": [(1, 0)] * 7 + [(0, 1)] * 1}
        without = analyse(primary)
        with_ctrl = analyse(primary, {"arith": [(1, 0)] * 20})
        assert without.primary["date"].p_value == with_ctrl.primary["date"].p_value
        assert without.primary["date"].rejected == with_ctrl.primary["date"].rejected

    def test_a_class_cannot_be_both(self):
        with pytest.raises(ValueError):
            analyse({"x": [(1, 1)]}, {"x": [(1, 1)]})

    def test_control_reports_an_upper_bound_not_a_verdict(self):
        r = analyse({"date": [(1, 1)] * 10}, {"arith": [(1, 0)] * 2 + [(0, 1)] * 8})
        b = r.negative_control["arith"].harm_share_upper_95
        assert 0.0 < b < 1.0


class TestHarmShareBound:
    def test_bound_is_one_when_nothing_is_discordant(self):
        assert harm_share_upper_bound(0, 0) == 1.0

    def test_bound_is_one_when_all_discordance_is_baseline_favouring(self):
        assert harm_share_upper_bound(5, 0) == 1.0

    def test_bound_tightens_as_evidence_of_no_harm_accumulates(self):
        assert harm_share_upper_bound(1, 9) > harm_share_upper_bound(2, 38)

    def test_bound_covers_the_point_estimate(self):
        assert harm_share_upper_bound(3, 7) > 3 / 10


class TestReproducibility:
    def test_same_seed_same_answer(self):
        assert _reject_rate([(0.85, 0.4)] * 20, 500, seed=99) == \
               _reject_rate([(0.85, 0.4)] * 20, 500, seed=99)
