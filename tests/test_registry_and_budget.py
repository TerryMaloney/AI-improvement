"""Entity TTL logic and the budget ceiling.

The budget test at the bottom is the one the packet asked for by name: it lists
`BudgetCeiling` as "theoretical only; untested under a real runaway case".
"""

from datetime import date, timedelta

import pytest

from epistemic.budget import BudgetCeiling, BudgetExceeded
from epistemic.registry import (
    DEFAULT_VOLATILE_TTL_DAYS,
    SCHEDULED_OFF_CYCLE_BACKSTOP_DAYS,
    Bucket,
    EntityRecord,
    EntityRegistry,
    seed_registry,
)


class TestVolatileBucket:
    def test_fresh_value_is_not_rechecked(self):
        rec = EntityRecord("k", "A Seat", Bucket.VOLATILE, "X", last_verified=date(2026, 8, 1))
        needs, reason = rec.needs_reverification(date(2026, 8, 15))
        assert needs is False
        assert "within its" in reason

    def test_stale_value_is_rechecked(self):
        rec = EntityRecord("k", "A Seat", Bucket.VOLATILE, "X", last_verified=date(2026, 8, 1))
        needs, reason = rec.needs_reverification(date(2026, 10, 1))
        assert needs is True
        assert "stale" in reason

    def test_boundary_is_exclusive(self):
        start = date(2026, 1, 1)
        rec = EntityRecord("k", "A Seat", Bucket.VOLATILE, "X", last_verified=start)
        assert rec.needs_reverification(start + timedelta(days=DEFAULT_VOLATILE_TTL_DAYS))[0] is False
        assert rec.needs_reverification(start + timedelta(days=DEFAULT_VOLATILE_TTL_DAYS + 1))[0] is True

    def test_never_verified_always_needs_check(self):
        rec = EntityRecord("k", "A Seat", Bucket.VOLATILE)
        assert rec.needs_reverification(date(2026, 8, 1))[0] is True

    def test_uncalibrated_threshold_says_so(self):
        """The packet's §2.3 calibration debt must be visible in the output,
        not just in a comment."""
        rec = EntityRecord("k", "A Seat", Bucket.VOLATILE, "X", last_verified=date(2026, 1, 1))
        _, reason = rec.needs_reverification(date(2026, 8, 1))
        assert "uncalibrated" in reason
        assert rec.threshold_is_calibrated is False

    def test_threshold_becomes_calibrated_with_observations(self):
        rec = EntityRecord("k", "A Seat", Bucket.VOLATILE, "X",
                           last_verified=date(2026, 1, 1),
                           observed_intervals_days=[120, 300, 210])
        assert rec.threshold_is_calibrated is True


class TestScheduledBucket:
    def test_before_term_end_the_cached_value_stands(self):
        rec = EntityRecord("k", "A Seat", Bucket.SCHEDULED, "X",
                           last_verified=date(2026, 8, 1), term_end=date(2030, 5, 21))
        needs, reason = rec.needs_reverification(date(2026, 9, 1))
        assert needs is False
        assert "2030-05-21" in reason

    def test_after_term_end_it_expires(self):
        rec = EntityRecord("k", "A Seat", Bucket.SCHEDULED, "X",
                           last_verified=date(2026, 8, 1), term_end=date(2026, 9, 1))
        needs, reason = rec.needs_reverification(date(2026, 9, 2))
        assert needs is True
        assert "expired by its own schedule" in reason

    def test_slow_backstop_catches_early_departure(self):
        """'Safe until 2030' must not quietly mean 'unchecked until 2030' —
        fixed-term seats can still be vacated early."""
        rec = EntityRecord("k", "A Seat", Bucket.SCHEDULED, "X",
                           last_verified=date(2026, 1, 1), term_end=date(2030, 5, 21))
        past_backstop = date(2026, 1, 1).toordinal() + SCHEDULED_OFF_CYCLE_BACKSTOP_DAYS + 1
        needs, reason = rec.needs_reverification(date.fromordinal(past_backstop))
        assert needs is True
        assert "backstop" in reason


class TestStableBucket:
    def test_hazard_is_never_zero(self):
        """The STABLE bucket's whole claim: long tenure is not infinite tenure."""
        rec = EntityRecord("k", "A Seat", Bucket.STABLE, "X", last_verified=date(2020, 1, 1))
        assert rec.needs_reverification(date(2026, 8, 1))[0] is True

    def test_recent_stable_check_is_enough(self):
        rec = EntityRecord("k", "A Seat", Bucket.STABLE, "X", last_verified=date(2026, 6, 1))
        assert rec.needs_reverification(date(2026, 8, 1))[0] is False


class TestRegistry:
    def test_seed_has_the_four_packet_entities(self):
        reg = seed_registry()
        assert {"openai_cro", "uk_pm", "fed_chair", "nato_sg"} <= {r.key for r in reg.all()}

    def test_match_finds_entity_in_question(self):
        reg = seed_registry()
        hits = reg.match("Who is currently the Chief Revenue Officer of OpenAI?")
        assert "openai_cro" in {r.key for r in hits}

    def test_match_is_not_promiscuous(self):
        reg = seed_registry()
        assert reg.match("What is 2 + 2?") == []

    def test_record_verification_banks_a_turnover_interval(self):
        """This is the mechanism that replaces the eyeballed 30-day threshold
        with a measured one."""
        reg = seed_registry()
        reg.record_verification("uk_pm", "Someone Else", date(2026, 9, 20))
        rec = reg.get("uk_pm")
        assert rec.observed_intervals_days == [62]
        assert rec.value == "Someone Else"

    def test_unchanged_value_banks_nothing(self):
        reg = seed_registry()
        reg.record_verification("uk_pm", "Andy Burnham", date(2026, 9, 20))
        assert reg.get("uk_pm").observed_intervals_days == []

    def test_sqlite_roundtrip(self, tmp_path):
        reg = seed_registry()
        reg.record_verification("uk_pm", "Someone Else", date(2026, 9, 20))
        path = tmp_path / "reg.db"
        reg.save(path)
        loaded = EntityRegistry.load(path)
        assert len(loaded) == len(reg)
        assert loaded.get("uk_pm").observed_intervals_days == [62]
        assert loaded.get("fed_chair").term_end == date(2030, 5, 21)

    def test_load_missing_file_is_empty_not_an_error(self, tmp_path):
        assert len(EntityRegistry.load(tmp_path / "nope.db")) == 0


class TestBudgetCeiling:
    def test_charges_accumulate(self):
        b = BudgetCeiling(max_calls=3, max_searches=2)
        b.charge("calls")
        assert b.remaining("calls") == 2

    def test_search_costs_both_a_search_and_a_call(self):
        b = BudgetCeiling(max_calls=5, max_searches=2)
        b.charge("searches")
        assert b.spent["searches"] == 1
        assert b.spent["calls"] == 1

    def test_raises_when_exceeded(self):
        b = BudgetCeiling(max_calls=1, max_searches=1)
        b.charge("calls")
        with pytest.raises(BudgetExceeded):
            b.charge("calls")

    def test_try_charge_degrades_instead_of_raising(self):
        b = BudgetCeiling(max_calls=1, max_searches=1)
        assert b.try_charge("calls") is True
        assert b.try_charge("calls") is False
        assert b.trips

    def test_search_limit_binds_before_call_limit(self):
        b = BudgetCeiling(max_calls=10, max_searches=1)
        b.charge("searches")
        assert b.can_charge("searches") is False
        assert b.can_charge("calls") is True

    def test_runaway_eig_spiral_terminates(self):
        """The case the packet flagged as untested: a controller that always
        wants one more retrieval. The ceiling must stop it without needing to
        win the argument about whether the next call is worth it."""
        b = BudgetCeiling(max_calls=6, max_searches=4, label="runaway")
        steps = 0
        while steps < 10_000:
            steps += 1
            expected_information_gain = 0.999  # always marginally worth it
            assert expected_information_gain > 0
            if not b.try_charge("searches"):
                break
        assert steps <= 5, f"ceiling failed to bind: {steps} iterations"
        assert b.exhausted or b.remaining("searches") == 0
        assert b.trips

    def test_unknown_kind_is_an_error_not_a_free_pass(self):
        with pytest.raises(ValueError):
            BudgetCeiling().charge("vibes")

    def test_snapshot_is_auditable(self):
        b = BudgetCeiling(max_calls=2, max_searches=1, label="x")
        b.try_charge("searches")
        b.try_charge("searches")
        snap = b.snapshot()
        assert snap["spent"]["searches"] == 1
        assert snap["trips"]
