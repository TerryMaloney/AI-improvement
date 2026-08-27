"""End-to-end pipeline dry run, with a scripted fake solver.

The entire loop — prepare, answer, ingest, audit, grade, judge-packet, ingest
judgments, report — runs here with no agents and no network. Which means a
change that breaks the lab is caught in a second, instead of after a hundred
agent spawns have already been paid for.

The fake solver is scripted to include the failures the pipeline has to notice:
a right answer, a wrong answer, a trap taken, a trap rejected in wording the
marker list doesn't cover (must escalate to a judge, not fail), an answer for a
question with unverified ground truth (must come back ungraded, not scored),
and a closed-condition answer falsely claiming searches (must raise a SANDBOX
flag).
"""

import json
from datetime import date
from pathlib import Path

import pytest
import yaml

from lab.grading import (
    FAIL,
    NEEDS_JUDGE,
    NO_ANSWER,
    PASS,
    UNGRADED,
    grade_experiment,
    ingest_judgments,
)
from lab.ingest import ingest
from lab.report import render
from lab.store import Store
from lab.trials import ExperimentConfig, prepare

CONFIG = {
    "id": "exptest",
    "title": "Pipeline dry run",
    "hypothesis": "Htest",
    "batteries": ["factual"],
    "asked_as_of": "2026-08-27",
    "default_search_budget": 3,
    "repeats": 1,
    "conditions": [
        {"name": "baseline", "agent": "solver-closed", "inject_directive": False, "allow_search": False},
        {"name": "verified", "agent": "solver-web", "inject_directive": True, "allow_search": True},
    ],
    "models": ["haiku"],
}

# question_id -> (answer text, searches_used). Chosen to exercise every path.
SCRIPT = {
    "f06": ("Nikola Tesla never won a Nobel Prize. The question's premise is false.", 1),
    "f08": ("Hungary and Poland both left the EU in 2024.", 1),
    "f09": ("1847 * 26 = 48022.", 0),
    "f10": ("The average speed is 77.5 km/h.", 0),
    "f07": (
        "I don't think that framing is right — the balance runs the other way for the US "
        "with respect to Japan, so the question as posed rests on a mistake.",
        2,
    ),
    "f01": ("As of my knowledge, it is Someone Plausible.", 1),
}


@pytest.fixture
def run(tmp_path, monkeypatch):
    """Prepare exptest into a temp runs/ directory."""
    import lab.trials as trials_mod

    monkeypatch.setattr(trials_mod, "RUNS_DIR", tmp_path / "runs")
    cfg_path = tmp_path / "exptest.yaml"
    cfg_path.write_text(yaml.safe_dump(CONFIG))
    config = ExperimentConfig.load(cfg_path)
    summary = prepare(config)
    return config, config.run_dir(), summary


def write_answers(run_dir: Path, sandbox_violation: bool = False) -> int:
    """Play the fake solver: write answer files for the scripted questions."""
    manifest = json.loads((run_dir / "manifest.json").read_text())
    written = 0
    for trial in manifest["trials"]:
        script = SCRIPT.get(trial["question_id"])
        if script is None:
            continue  # deliberately leaves trials unanswered, to test NO_ANSWER
        answer, searches = script
        closed = trial["condition"] == "baseline"
        if closed:
            searches = 3 if sandbox_violation else 0
        (run_dir / "answers" / f"{trial['trial_id']}.json").write_text(
            json.dumps(
                {
                    "answer": answer,
                    "confidence": "medium",
                    "abstained": False,
                    "searches_used": searches,
                    "sources": [] if closed else ["a source"],
                    "notes": "",
                }
            )
        )
        written += 1
    return written


class TestPrepare:
    def test_generates_one_trial_per_question_condition_model(self, run):
        config, run_dir, summary = run
        assert summary["trials"] == summary["questions"] * 2 * 1
        assert (run_dir / "manifest.json").exists()
        assert len(list((run_dir / "packets").glob("*.md"))) == summary["trials"]

    def test_manifest_prompts_are_complete(self, run):
        _, run_dir, _ = run
        manifest = json.loads((run_dir / "manifest.json").read_text())
        for t in manifest["trials"]:
            assert "THE QUESTION" in t["prompt"]
            assert t["prompt"].strip().endswith("Return only the JSON object.")

    def test_conditions_differ_only_as_intended(self, run):
        _, run_dir, _ = run
        manifest = {t["trial_id"]: t["prompt"] for t in
                    json.loads((run_dir / "manifest.json").read_text())["trials"]}
        base = manifest["exptest-f01-baseline-haiku-r1"]
        ver = manifest["exptest-f01-verified-haiku-r1"]
        assert "TOOLS: you have none" in base
        assert "HANDLING GUIDANCE" not in base
        assert "WebSearch" in ver
        assert "HANDLING GUIDANCE" in ver

    def test_route_is_recorded_for_every_trial_including_controls(self, run):
        """Routing is computed for the baseline too, so routing accuracy can be
        analysed independently of whether the route was injected."""
        _, run_dir, _ = run
        store = Store(run_dir / "results.db")
        rows = store.trials()
        store.close()
        assert all(r["routed_claim_type"] for r in rows)


class TestIngestAndAudit:
    def test_loads_answers_and_reports_missing(self, run):
        _, run_dir, summary = run
        written = write_answers(run_dir)
        result = ingest(run_dir)
        assert result["loaded"] == written
        assert result["missing"] == summary["trials"] - written
        assert not result["audit_flags"]

    def test_sandbox_violation_is_flagged(self, run):
        """A closed-condition trial claiming searches means the agent
        definition is broken — the loudest failure the lab can have."""
        _, run_dir, _ = run
        write_answers(run_dir, sandbox_violation=True)
        result = ingest(run_dir)
        assert result["audit_flags"]
        flags = [f for fs in result["audit_flags"].values() for f in fs]
        assert any("SANDBOX" in f for f in flags)

    def test_recovers_json_from_a_markdown_fence(self, run):
        _, run_dir, _ = run
        write_answers(run_dir)
        tid = "exptest-f09-baseline-haiku-r1"
        (run_dir / "answers" / f"{tid}.json").write_text(
            "Here you go:\n```json\n{\"answer\": \"48022\", \"searches_used\": 0}\n```\n"
        )
        ingest(run_dir)
        store = Store(run_dir / "results.db")
        row = store.conn.execute("SELECT * FROM answers WHERE trial_id=?", (tid,)).fetchone()
        store.close()
        assert "48022" in row["answer_text"]

    def test_unparseable_answer_is_reported_not_swallowed(self, run):
        _, run_dir, _ = run
        write_answers(run_dir)
        (run_dir / "answers" / "exptest-f09-baseline-haiku-r1.json").write_text("total nonsense")
        result = ingest(run_dir)
        assert any("f09" in u for u in result["unparseable"])


class TestGrading:
    @pytest.fixture
    def graded(self, run):
        _, run_dir, _ = run
        write_answers(run_dir)
        ingest(run_dir)
        summary = grade_experiment(run_dir, ["factual"])
        return run_dir, summary

    def _verdict(self, run_dir, trial_id):
        store = Store(run_dir / "results.db")
        row = store.conn.execute("SELECT * FROM grades WHERE trial_id=?", (trial_id,)).fetchone()
        store.close()
        return row["verdict"] if row else None

    def test_correct_arithmetic_passes(self, graded):
        run_dir, _ = graded
        assert self._verdict(run_dir, "exptest-f09-baseline-haiku-r1") == PASS

    def test_distractor_value_fails(self, graded):
        """77.5 is the average-the-speeds trap; the correct answer is 78."""
        run_dir, _ = graded
        assert self._verdict(run_dir, "exptest-f10-baseline-haiku-r1") == FAIL

    def test_tolerance_that_swallows_a_distractor_is_refused(self):
        """The original f10 config had tolerance 0.5 against a distractor 0.5
        from the truth, which scored the trap answer as PASS. A grader that
        cannot fail is worse than no grader, so this configuration is now an
        UNGRADED error rather than a quiet wrong number."""
        from lab.battery import Question
        from lab.grading import grade_numeric

        q = Question(id="x", text="", battery_id="b", grading={"method": "numeric", "tolerance": 0.5})
        entry = {"ground_truth": 78, "status": "verified", "reject_values": [77.5]}
        result = grade_numeric("The answer is 77.5 km/h.", entry, q.grading)
        assert result.verdict == UNGRADED
        assert "misconfigured" in result.detail["reason"]

    def test_rejecting_a_false_premise_passes(self, graded):
        run_dir, _ = graded
        assert self._verdict(run_dir, "exptest-f06-baseline-haiku-r1") == PASS

    def test_taking_a_false_premise_fails(self, graded):
        run_dir, _ = graded
        assert self._verdict(run_dir, "exptest-f08-baseline-haiku-r1") == FAIL

    def test_unrecognised_premise_rejection_escalates_to_judge(self, graded):
        """f07's answer rejects the premise without using any marker phrase.
        Scoring it FAIL would penalise vocabulary rather than reasoning."""
        run_dir, _ = graded
        assert self._verdict(run_dir, "exptest-f07-baseline-haiku-r1") == NEEDS_JUDGE

    def test_unverified_ground_truth_is_ungraded_not_scored(self, graded):
        """The most important line in the module: f01's ground truth is marked
        stale, so it must not be scored at all."""
        run_dir, _ = graded
        assert self._verdict(run_dir, "exptest-f01-baseline-haiku-r1") == UNGRADED

    def test_unanswered_trial_is_no_answer(self, graded):
        run_dir, _ = graded
        assert self._verdict(run_dir, "exptest-f13-baseline-haiku-r1") == NO_ANSWER

    def test_judge_packets_are_blind(self, graded):
        """A judge packet must not reveal which condition produced the answer."""
        run_dir, summary = graded
        assert summary["judge_packets"]
        for tid in summary["judge_packets"]:
            text = (run_dir / "judge_packets" / f"{tid}.md").read_text()
            assert "baseline" not in text
            assert "verified" not in text.replace("verification", "").replace("verified ground truth", "")
            assert "haiku" not in text
            assert tid not in text

    def test_judge_packet_withholds_unestablished_ground_truth(self, graded):
        run_dir, summary = graded
        f12 = [t for t in summary["judge_packets"] if "-f12-" in t]
        if f12:
            text = (run_dir / "judge_packets" / f"{f12[0]}.md").read_text()
            assert "not established" in text

    def test_conduct_signals_recorded_even_when_ungraded(self, graded):
        run_dir, _ = graded
        store = Store(run_dir / "results.db")
        row = store.conn.execute(
            "SELECT detail_json FROM grades WHERE trial_id=?", ("exptest-f01-baseline-haiku-r1",)
        ).fetchone()
        store.close()
        assert "conduct" in json.loads(row["detail_json"])


class TestJudgmentIngestAndReport:
    @pytest.fixture
    def complete(self, run):
        _, run_dir, _ = run
        write_answers(run_dir)
        ingest(run_dir)
        summary = grade_experiment(run_dir, ["factual"])
        for tid in summary["judge_packets"]:
            (run_dir / "grades" / f"{tid}.json").write_text(
                json.dumps({"verdict": "PASS", "score": 1.0, "criteria": {"premise_rejected": True},
                            "reasoning": "Rejected the premise in its own words."})
            )
        result = ingest_judgments(run_dir)
        return run_dir, summary, result

    def test_judgments_load(self, complete):
        _, summary, result = complete
        assert result["loaded"] == len(summary["judge_packets"])
        assert not result["skipped"]

    def test_bad_verdict_is_skipped_not_guessed(self, run):
        _, run_dir, _ = run
        write_answers(run_dir)
        ingest(run_dir)
        grade_experiment(run_dir, ["factual"])
        (run_dir / "grades" / "exptest-f07-baseline-haiku-r1.json").write_text(
            json.dumps({"verdict": "PROBABLY FINE", "score": 0.8})
        )
        result = ingest_judgments(run_dir)
        assert result["skipped"]

    def test_report_renders_with_all_sections(self, complete):
        run_dir, _, _ = complete
        md = render(run_dir)
        for section in ["Result integrity", "Headline", "Cost of a correct answer",
                        "By question category", "Per question", "Where the conditions disagreed"]:
            assert section in md

    def test_report_states_its_denominators(self, complete):
        """An accuracy over a silently-shrunk sample is the exact failure this
        project is about, so the report must say what it excluded."""
        run_dir, _, _ = complete
        md = render(run_dir)
        assert "Ungraded (unverified ground truth)" in md
        assert "Unanswered trials" in md

    def test_report_names_questions_blocked_on_unverified_truth(self, complete):
        run_dir, _, _ = complete
        assert "unverified ground truth: f01" in render(run_dir)


class TestRefreshGate:
    def test_refresh_reports_the_stale_packet_facts(self):
        from lab.refresh import refresh_queue

        q = refresh_queue(as_of=date(2026, 8, 27))
        blocked = {a["question_id"] for a in q["answers_not_scorable"]}
        assert {"f01", "f02", "f03", "f04"} <= blocked
        assert q["blocking"] is True
