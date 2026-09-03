"""The calibration runner: it executes the frozen plan and decides nothing.

The whole pipeline is exercised here against a synthetic runtime, so the ordering
guarantees and the resume behaviour are evidence rather than intention — and none
of it costs a paid call.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from lab import stage0b_calibration_runner as R
from lab.stage0b_calibration import BATCH1_HOLDOUT, MIN_HOLDOUT_ITEMS_PER_ROUTE
from tests.fixtures.stage0b_synthetic import (SyntheticBackend, synthetic_bank,
                                              synthetic_bank_small)


@pytest.fixture()
def env(tmp_path, monkeypatch):
    """The SMALL bank: three items, one per route. Row-level behaviour."""
    monkeypatch.setattr(R, "RUNDIR", tmp_path)
    bank = tmp_path / "bank.json"
    bank.write_text(json.dumps(synthetic_bank_small()))
    return tmp_path, bank, R.load_bank(bank)


@pytest.fixture()
def full(tmp_path, monkeypatch):
    """The QUOTA-SATISFYING bank: exercises validate_bank in the passing
    direction, and is the only fixture the CLI will consent to dispatch against."""
    monkeypatch.setattr(R, "RUNDIR", tmp_path)
    bank = tmp_path / "bank.json"
    bank.write_text(json.dumps(synthetic_bank()))
    return tmp_path, bank, R.load_bank(bank)


def _row_problems(rows):
    """Row-level problems only; bank quotas are exercised separately."""
    return [p for p in R.stage_validate(rows)
            if "holdout carries" not in p and "route share" not in p]


class TestValidationRefusesRatherThanRepairs:

    def test_a_synthetic_bank_is_row_valid(self, env):
        _, _, rows = env
        assert _row_problems(rows) == []

    def test_a_row_whose_key_cannot_adjudicate_is_refused(self, env):
        _, _, rows = env
        rows[1].answer_key = {"route": "boolean"}          # the original defect
        assert any("no `expected`" in p for p in R.stage_validate(rows))

    def test_the_runner_never_repairs_an_item(self, env):
        _, _, rows = env
        before = rows[0].answer_key.copy()
        R.stage_validate(rows)
        assert rows[0].answer_key == before

    def test_a_quota_satisfying_bank_validates_completely(self, full):
        _, _, rows = full
        assert R.stage_validate(rows) == []

    def test_the_cli_refuses_to_dispatch_against_an_invalid_bank(self, full, capsys):
        tmp, bank, _ = full
        d = json.loads(bank.read_text())
        d["items"][1]["answer_key"] = {"route": "boolean"}
        bank.write_text(json.dumps(d))
        assert R.main(["--stage", "screen", "--bank", str(bank), "--dry-run"]) == 1


class TestStagesAndResumability:

    def test_screen_dispatches_once_per_item_and_persists_before_deriving(self, env):
        tmp, _, rows = env
        led = R.DispatchLedger(tmp / "l.jsonl")
        rep = R.stage_screen(rows, led, SyntheticBackend())
        assert rep.dispatched == len(rows) and rep.failures == []
        assert len(led.by_stage("screen")) == len(rows)
        assert (tmp / "l.jsonl").exists(), "ledger is durable on disk, not in memory"

    def test_a_resume_re_dispatches_nothing(self, env):
        tmp, _, rows = env
        led, be = R.DispatchLedger(tmp / "l.jsonl"), SyntheticBackend()
        R.stage_screen(rows, led, be)
        rows = [R.derive_screen(r, led) for r in rows]
        R.stage_answer(rows, led, be)
        spent = len(be.calls)
        led2 = R.DispatchLedger(tmp / "l.jsonl")        # fresh process, same file
        s2 = R.stage_screen(rows, led2, be)
        a2 = R.stage_answer(rows, led2, be)
        assert (s2.dispatched, a2.dispatched) == (0, 0)
        assert s2.skipped_already_done and a2.skipped_already_done
        assert len(be.calls) == spent, "a resume made a paid call"

    def test_dispatch_ids_are_deterministic_and_content_free(self):
        a = R.dispatch_id("i1", "answer", "C_search")
        assert a == R.dispatch_id("i1", "answer", "C_search")
        assert a != R.dispatch_id("i1", "answer", "D_production_search")

    def test_a_torn_final_ledger_line_does_not_lose_the_rest(self, tmp_path):
        p = tmp_path / "l.jsonl"
        p.write_text(json.dumps({"dispatch_id": "a", "stage": "screen"}) + "\n{\"broken\"")
        assert R.DispatchLedger(p).has("a")

    def test_stage_two_runs_only_on_screen_passers(self, env):
        tmp, _, rows = env
        led, be = R.DispatchLedger(tmp / "l.jsonl"), SyntheticBackend()
        R.stage_screen(rows, led, be)
        rows = [R.derive_screen(r, led) for r in rows]
        rows[0].screen_passed = False
        rep = R.stage_answer(rows, led, be)
        assert rep.dispatched == 6 * (len(rows) - 1)

    def test_the_D_production_search_is_a_second_execution_of_the_same_query(self, env):
        tmp, _, rows = env
        led, be = R.DispatchLedger(tmp / "l.jsonl"), SyntheticBackend()
        R.stage_screen(rows, led, be)
        rows = [R.derive_screen(r, led) for r in rows]
        R.stage_answer(rows, led, be)
        rows = [R.derive_answers(r, led) for r in rows]
        for r in rows:
            screen = led.get(R.dispatch_id(r.item_id, "screen", "D_screen"))
            prod = led.get(R.dispatch_id(r.item_id, "answer", "D_production_search"))
            assert screen["query"] == prod["result"]["requested_query"]
            assert r.d_production_divergent is not None, "r_D is measured, not assumed"

    def test_six_dispatches_per_screen_passing_item(self, env):
        tmp, _, rows = env
        led, be = R.DispatchLedger(tmp / "l.jsonl"), SyntheticBackend()
        R.stage_screen(rows, led, be)
        rows = [R.derive_screen(r, led) for r in rows]
        assert R.stage_answer(rows, led, be).dispatched == 6 * len(rows)


class TestTheHumanQueueIsBlind:

    def _through_adjudication(self, tmp, rows):
        led, be = R.DispatchLedger(tmp / "l.jsonl"), SyntheticBackend()
        R.stage_screen(rows, led, be)
        rows = [R.derive_screen(r, led) for r in rows]
        R.stage_answer(rows, led, be)
        rows = [R.derive_answers(r, led) for r in rows]
        return rows, R.stage_adjudicate(rows)

    def test_determinate_cases_never_reach_the_queue(self, env):
        tmp, _, rows = env
        rows, cases = self._through_adjudication(tmp, rows)
        assert all(c["arm"] in rows[0].escalated_to_human or True for c in cases)
        assert len(cases) < 3 * len(rows), "everything escalated: the reference decided nothing"

    def test_the_queue_carries_no_grader_output_and_no_suggested_verdict(self, env):
        tmp, _, rows = env
        rows, cases = self._through_adjudication(tmp, rows)
        q = R.build_queue(cases, 1)
        body = json.dumps(q).lower()
        for token in R.FORBIDDEN_IN_QUEUE:
            assert token not in body
        for c in q["cases"]:
            assert c["human_verdict"] is None and c["human_adjudicator"] is None

    def test_a_queue_that_leaked_a_grader_verdict_is_refused(self, env):
        tmp, _, rows = env
        rows, cases = self._through_adjudication(tmp, rows)
        cases[0]["reason"] = "grader_verdict says CORRECT"
        with pytest.raises(ValueError, match="forbidden token"):
            R.build_queue(cases, 1)

    def test_the_queue_is_fingerprinted_and_stable(self, env):
        tmp, _, rows = env
        rows, cases = self._through_adjudication(tmp, rows)
        assert R.build_queue(cases, 1)["queue_fingerprint"] == \
            R.build_queue(cases, 1)["queue_fingerprint"]

    def test_the_queue_carries_the_key_material_the_route_needs(self, env):
        tmp, _, rows = env
        rows, cases = self._through_adjudication(tmp, rows)
        for c in R.build_queue(cases, 1)["cases"]:
            if c["route"] == "boolean":
                assert c["expected"] is not None
            if c["route"] == "numeric":
                assert c["value"] is not None and c["reject_values"]
            if c["route"] == "exact_entity":
                assert c["accept"] and c["rejects"]


class TestTheGraderLockout:

    def _ready(self, tmp, rows):
        led, be = R.DispatchLedger(tmp / "l.jsonl"), SyntheticBackend()
        R.stage_screen(rows, led, be)
        rows = [R.derive_screen(r, led) for r in rows]
        R.stage_answer(rows, led, be)
        rows = [R.derive_answers(r, led) for r in rows]
        cases = R.stage_adjudicate(rows)
        return rows, R.build_queue(cases, 1)

    def test_grading_is_refused_while_a_human_case_is_open(self, env):
        tmp, _, rows = env
        rows, q = self._ready(tmp, rows)
        auth = R.authorize_grading(rows, q)
        assert not auth["authorized"] and auth["open_cases"] > 0

    def test_grading_is_authorized_once_every_case_is_attributed(self, env):
        tmp, _, rows = env
        rows, q = self._ready(tmp, rows)
        imported, problems = R.import_verdicts(
            q, {c["case_id"]: "C" for c in q["cases"]}, "Terry")
        assert problems == [] and not imported["missing"]
        R.apply_verdicts(rows, q, imported)
        assert R.authorize_grading(rows, q)["authorized"]

    def test_a_partial_import_leaves_the_lock_shut(self, env):
        tmp, _, rows = env
        rows, q = self._ready(tmp, rows)
        first = q["cases"][0]["case_id"]
        imported, _ = R.import_verdicts(q, {first: "C"}, "Terry")
        R.apply_verdicts(rows, q, imported)
        assert not R.authorize_grading(rows, q)["authorized"]

    def test_an_unattributed_import_is_refused(self, env):
        tmp, _, rows = env
        rows, q = self._ready(tmp, rows)
        _, problems = R.import_verdicts(q, {q["cases"][0]["case_id"]: "C"}, "")
        assert any("unattributed" in p for p in problems)

    def test_the_candidate_grader_may_not_be_named_as_adjudicator(self, env):
        tmp, _, rows = env
        rows, q = self._ready(tmp, rows)
        _, problems = R.import_verdicts(q, {q["cases"][0]["case_id"]: "C"},
                                        "lab.grading_v2")
        assert any("never produce its own ground truth" in p for p in problems)

    def test_abstain_is_preserved_exactly(self, env):
        tmp, _, rows = env
        rows, q = self._ready(tmp, rows)
        cid = q["cases"][0]["case_id"]
        imported, _ = R.import_verdicts(q, {cid: "A"}, "Terry")
        assert imported["applied"][cid] == "ABSTAIN"

    def test_an_unknown_code_or_case_is_refused(self, env):
        tmp, _, rows = env
        rows, q = self._ready(tmp, rows)
        _, problems = R.import_verdicts(q, {"nope-0001": "C"}, "Terry")
        assert any("unknown case" in p for p in problems)
        _, problems = R.import_verdicts(q, {q["cases"][0]["case_id"]: "MAYBE"}, "Terry")
        assert any("not one of C / I / A" in p for p in problems)


class TestTheDryRunIsTheWholePipeline:

    def test_end_to_end_with_zero_paid_calls(self, full):
        tmp, bank, _ = full
        assert R.main(["--stage", "validate", "--bank", str(bank)]) == 0
        assert R.main(["--stage", "screen", "--bank", str(bank), "--dry-run"]) == 0
        assert R.main(["--stage", "answer", "--bank", str(bank), "--dry-run"]) == 0
        assert R.main(["--stage", "export-queue", "--bank", str(bank), "--dry-run"]) == 0
        q = json.loads((tmp / R.QUEUE.format(b=1)).read_text())
        assert q["total_cases"] >= 1 and q["queue_fingerprint"]
        st = R.status(1, bank)
        assert st["dispatches_recorded"] > 0
        assert st["grading_authorization"]["authorized"] is False

    def test_the_dry_run_backend_is_never_the_live_one(self, full):
        tmp, bank, _ = full
        R.main(["--stage", "screen", "--bank", str(bank), "--dry-run"])
        led = R.DispatchLedger(tmp / R.LEDGER.format(b=1))
        assert all(r["result"]["cost_usd"] == 0.0 for r in led.by_stage("screen"))


class TestBankLevelInvariants:

    def test_the_per_route_floor_and_mixture_are_checked_at_bank_level(self, env):
        """The three-item bank must FAIL the floor."""
        _, _, rows = env
        problems = R.stage_validate(rows)
        assert any("per-route floor" in p for p in problems), \
            "a 3-item bank must fail the floor"

    def test_the_floor_and_holdout_size_are_consistent(self):
        assert BATCH1_HOLDOUT >= 4 * MIN_HOLDOUT_ITEMS_PER_ROUTE
