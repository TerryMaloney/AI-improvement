"""R3 aggregation rules — fixed in advance so they cannot be tuned to a result."""

import pytest

from lab.judging import DISPUTED, aggregate, noise_floor, reliability


def j(v, s):
    return {"verdict": v, "score": s}


class TestAggregation:
    def test_median_not_mean_so_one_outlier_cannot_drag_a_trial(self):
        a = aggregate("t", [j("PASS", 1.0), j("PASS", 0.9), j("FAIL", 0.0)])
        assert a.score == 0.9          # median
        assert a.score != pytest.approx(0.633, abs=0.01)  # not the mean
        assert a.verdict == "PASS"

    def test_majority_verdict_wins(self):
        a = aggregate("t", [j("PARTIAL", 0.5), j("PASS", 1.0), j("PARTIAL", 0.6)])
        assert a.verdict == "PARTIAL"

    def test_tie_is_disputed_not_rounded(self):
        """A 1-1 or 2-2 split must not silently resolve to the convenient side."""
        a = aggregate("t", [j("PASS", 1.0), j("FAIL", 0.0)])
        assert a.verdict == DISPUTED
        assert a.disputed is True

    def test_unanimous_is_flagged(self):
        a = aggregate("t", [j("PASS", 1.0), j("PASS", 0.95), j("PASS", 1.0)])
        assert a.unanimous is True
        assert a.disputed is False

    def test_spread_is_preserved(self):
        a = aggregate("t", [j("PASS", 1.0), j("PARTIAL", 0.5), j("PASS", 0.9)])
        assert a.spread == pytest.approx(0.5)


class TestReliability:
    def test_reports_spread_and_disputes(self):
        agg = [
            aggregate("a", [j("PASS", 1.0), j("PASS", 1.0), j("PASS", 1.0)]),
            aggregate("b", [j("PASS", 1.0), j("FAIL", 0.0), j("PARTIAL", 0.5)]),
        ]
        r = reliability(agg)
        assert r["n_multi_judged"] == 2
        assert r["unanimous_verdict"] == 1
        assert r["max_spread"] == pytest.approx(1.0)

    def test_noise_floor_scales_with_judged_share(self):
        """A condition where few trials are judge-graded inherits less noise
        from the judge than one where most are."""
        agg = [aggregate(str(i), [j("PASS", 1.0), j("PARTIAL", 0.5)]) for i in range(5)]
        heavy = noise_floor(agg, n_trials_per_condition=5)   # all judged
        light = noise_floor(agg, n_trials_per_condition=20)  # quarter judged
        assert heavy > light > 0

    def test_no_multi_judged_trials_means_no_judge_noise(self):
        agg = [aggregate("a", [j("PASS", 1.0)])]
        assert noise_floor(agg, 15) == 0.0
        assert reliability(agg)["n_multi_judged"] == 0
