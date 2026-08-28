"""Telemetry, and the store's promise not to touch frozen experiments.

Two properties are load-bearing:

* **Observed-authoritative.** A cost figure comes from the harness or it does not
  exist. A solver's self-report never populates an observed field.
* **`NULL` is not `0`.** A column an old run never had reads as *not measured*.
  "exp001 did not record tokens" and "exp001 used zero tokens" are different
  claims and only one of them is true.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from lab.store import _ANSWER_COLUMNS, Store, TrialRow
from lab.telemetry import NOT_MEASURED, ROLES, from_payload, self_report, selfreport_gap

REPO_ROOT = Path(__file__).resolve().parent.parent
FROZEN = REPO_ROOT / "runs" / "exp001pilot" / "results.db"


class TestTelemetry:
    def test_harness_keys_populate_observed_fields(self):
        t = from_payload(
            {"tool_calls_observed": 3, "latency_ms": 1200, "input_tokens": 10,
             "output_tokens": 5, "model": "haiku"},
            "solver",
        )
        assert (t.tool_calls_observed, t.latency_ms, t.total_tokens) == (3, 1200, 15)
        assert t.cost_measured and t.tokens_measured

    def test_absent_measurements_are_none_not_zero(self):
        t = from_payload({}, "solver")
        assert t.tool_calls_observed is None and t.total_tokens is None
        assert not t.cost_measured and not t.tokens_measured

    def test_a_self_reported_count_never_becomes_an_observed_one(self):
        """The whole point: `searches_used` is a claim about behaviour, not a
        measurement of it."""
        t = from_payload({"searches_used": 7}, "solver")
        assert t.tool_calls_observed is None

    def test_totals_are_derived_from_parts_but_never_the_reverse(self):
        assert from_payload({"input_tokens": 4, "output_tokens": 6}, "judge").total_tokens == 10
        t = from_payload({"total_tokens": 10}, "judge")
        assert t.total_tokens == 10
        assert t.input_tokens is None and t.output_tokens is None

    def test_duration_seconds_fall_back_to_latency(self):
        assert from_payload({"duration_s": 2.5}, "solver").latency_ms == 2500

    def test_booleans_are_not_counts(self):
        """`True` arriving where a count belongs is a bug upstream; storing it
        as 1 would hide the bug inside a number."""
        assert from_payload({"tool_calls_observed": True}, "solver").tool_calls_observed is None

    def test_every_role_is_recordable_and_junk_is_not(self):
        for role in ROLES:
            assert from_payload({}, role).dispatch_role == role
        with pytest.raises(ValueError, match="unknown dispatch role"):
            from_payload({}, "solverr")

    def test_per_tool_split_is_recorded_as_unavailable_not_left_blank(self):
        assert "NOT_MEASURED" in from_payload({}, "solver").per_tool_split
        assert "aggregate" in NOT_MEASURED

    def test_self_report_lives_in_its_own_namespace(self):
        payload = {"searches_used": 2, "tool_calls_observed": 5, "confidence": "high"}
        assert self_report(payload) == {"searches_used": 2, "confidence": "high"}

    def test_the_gap_is_reported_and_not_reconciled(self):
        assert selfreport_gap({"searches_used": 2, "tool_calls_observed": 5}) == {
            "observed": 5, "self_reported": 2, "gap": 3
        }

    def test_a_missing_side_produces_no_gap_rather_than_a_gap_against_zero(self):
        assert selfreport_gap({"tool_calls_observed": 5}) is None
        assert selfreport_gap({"searches_used": 5}) is None


def _trial(tid="t1"):
    return TrialRow(
        trial_id=tid, experiment_id="e", question_id="q1", battery_id="b",
        condition="baseline", model="haiku", repeat=1, agent="solver-closed",
        routed_claim_type="EMPIRICAL", route_json="{}", prompt="P",
    )


class TestNewStore:
    def test_new_databases_get_the_honest_column_names(self, tmp_path):
        store = Store(tmp_path / "r.db")
        cols = store.columns("answers")
        assert "searches_self_report" in cols
        assert "searches_used" not in cols, "the deprecated name must not be recreated"
        for c in ("latency_ms", "total_tokens", "dispatch_role", "retrieval_state",
                  "evidence_ledger_json"):
            assert c in cols
        store.close()

    def test_answer_telemetry_round_trips(self, tmp_path):
        store = Store(tmp_path / "r.db")
        store.save_trials([_trial()])
        store.save_answer("t1", {
            "answer": "A", "searches_used": 1, "tool_calls_observed": 3,
            "input_tokens": 100, "output_tokens": 20, "latency_ms": 900, "model": "haiku",
        })
        row = store.joined()[0]
        assert (row["tool_calls_observed"], row["searches_self_report"]) == (3, 1)
        assert (row["total_tokens"], row["latency_ms"]) == (120, 900)
        assert row["dispatch_role"] == "solver" and row["solver_model"] == "haiku"
        store.close()

    def test_unmeasured_telemetry_stores_null_not_zero(self, tmp_path):
        store = Store(tmp_path / "r.db")
        store.save_trials([_trial()])
        store.save_answer("t1", {"answer": "A"})
        row = store.joined()[0]
        assert row["total_tokens"] is None
        assert row["tool_calls_observed"] is None
        store.close()

    def test_judge_dispatch_cost_is_persisted(self, tmp_path):
        """Judge calls were free in exp001/exp002's accounting and not free in
        reality."""
        store = Store(tmp_path / "r.db")
        store.save_trials([_trial()])
        store.save_grade(
            "t1", "PASS", 1.0, "judge", "grader-judge", {},
            telemetry=from_payload({"total_tokens": 800, "latency_ms": 400, "model": "haiku"}, "judge"),
            judge_saw_reasoning=False, k_replicates=3,
        )
        row = store.joined()[0]
        assert (row["judge_tokens"], row["judge_latency_ms"]) == (800, 400)
        assert row["judge_model"] == "haiku"
        assert row["judge_saw_reasoning"] == 0 and row["k_replicates"] == 3
        store.close()

    def test_retrieval_state_and_ledger_round_trip(self, tmp_path):
        from lab.states import EgressStatus, Evidence, EvidenceDepth, assess

        egress = EgressStatus(web_search=True, web_fetch=False)
        a = assess([Evidence(query="q", returned=True, depth=EvidenceDepth.SNIPPET,
                             addressed_claim=True, origin="bbc")], egress)
        store = Store(tmp_path / "r.db")
        store.save_trials([_trial()])
        store.save_answer("t1", {"answer": "A"}, retrieval=a.as_dict(),
                          evidence=[{"query": "q", "returned": True}])
        row = store.joined()[0]
        assert row["retrieval_state"] == "CLAIM_EVIDENCE_MATCH@SNIPPET"
        assert "SOURCE_ACCESS" in row["retrieval_state_json"]
        assert row["evidence_ledger_json"]
        store.close()


class TestFrozenDatabasesAreNeverMigrated:
    """`runs/exp001pilot/results.db` predates the telemetry columns. Reading it
    used to raise `no such column: a.tool_calls_observed` — an error that was
    mechanical proof exp001 had not been rewritten. Keeping that property is
    worth more than the convenience of an ALTER TABLE (FD-3)."""

    def test_the_frozen_database_still_exists(self):
        assert FROZEN.exists()

    def test_opening_it_does_not_change_a_single_byte(self):
        before = FROZEN.read_bytes()
        store = Store(FROZEN)
        store.joined()
        store.close()
        assert FROZEN.read_bytes() == before

    def test_it_still_has_its_original_narrow_schema(self):
        store = Store(FROZEN)
        cols = store.columns("answers")
        assert "searches_used" in cols, "the old name must not have been migrated away"
        assert "tool_calls_observed" not in cols
        assert "total_tokens" not in cols
        store.close()

    def test_it_reads_through_the_same_code_path_as_a_new_run(self):
        store = Store(FROZEN)
        rows = store.joined()
        assert len(rows) == 60
        store.close()

    def test_columns_it_never_had_read_as_not_measured(self):
        store = Store(FROZEN)
        rows = store.joined()
        assert all(r["tool_calls_observed"] is None for r in rows)
        assert all(r["total_tokens"] is None for r in rows)
        store.close()

    def test_the_old_column_is_projected_under_the_canonical_name(self):
        """One reader serves both populations without either pretending the old
        run measured something it did not."""
        store = Store(FROZEN)
        row = store.joined()[0]
        assert row["searches_self_report"] is not None
        with pytest.raises((IndexError, KeyError)):
            row["searches_used"]
        store.close()

    def test_a_write_cannot_add_columns_to_a_frozen_database(self, tmp_path):
        legacy = tmp_path / "legacy.db"
        conn = sqlite3.connect(legacy)
        conn.executescript(
            "CREATE TABLE trials (trial_id TEXT PRIMARY KEY, prompt TEXT);"
            "CREATE TABLE answers (trial_id TEXT PRIMARY KEY, searches_used INTEGER,"
            " received_at TEXT);"
            "CREATE TABLE grades (trial_id TEXT PRIMARY KEY, verdict TEXT, method TEXT,"
            " grader TEXT, graded_at TEXT);"
        )
        conn.commit()
        conn.close()
        store = Store(legacy)
        store.save_answer("t1", {"answer": "A", "searches_used": 2, "total_tokens": 99})
        assert "total_tokens" not in store.columns("answers")
        got = store.conn.execute("SELECT searches_used FROM answers").fetchone()
        assert got["searches_used"] == 2
        store.close()


def test_canonical_answer_columns_have_no_duplicates():
    names = [n for n, _ in _ANSWER_COLUMNS]
    assert len(names) == len(set(names))
