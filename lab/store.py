"""SQLite results store.

One database per experiment, at `runs/<exp>/results.db`. Per-experiment rather
than global because an experiment is the unit you re-run, archive, or throw
away; a shared database makes "re-run exp003 cleanly" a delete-with-WHERE
instead of a delete-the-file.

Cross-experiment comparison reads several of these at once — see lab/report.py.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS experiment (
    id TEXT PRIMARY KEY,
    config_json TEXT NOT NULL,
    prepared_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS trials (
    trial_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    battery_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    model TEXT NOT NULL,
    repeat INTEGER NOT NULL DEFAULT 1,
    agent TEXT NOT NULL,
    routed_claim_type TEXT,
    route_json TEXT,
    prompt TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS answers (
    trial_id TEXT PRIMARY KEY,
    answer_text TEXT,
    claim_type_selfreport TEXT,
    searches_used INTEGER,
    sources_json TEXT,
    confidence TEXT,
    abstained INTEGER DEFAULT 0,
    raw_json TEXT,
    duration_s REAL,
    received_at TEXT NOT NULL,
    FOREIGN KEY (trial_id) REFERENCES trials(trial_id)
);
CREATE TABLE IF NOT EXISTS grades (
    trial_id TEXT PRIMARY KEY,
    verdict TEXT NOT NULL,
    score REAL,
    method TEXT NOT NULL,
    grader TEXT NOT NULL,
    detail_json TEXT,
    graded_at TEXT NOT NULL,
    FOREIGN KEY (trial_id) REFERENCES trials(trial_id)
);
CREATE INDEX IF NOT EXISTS idx_trials_cond ON trials(condition, model);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class TrialRow:
    trial_id: str
    experiment_id: str
    question_id: str
    battery_id: str
    condition: str
    model: str
    repeat: int
    agent: str
    routed_claim_type: str | None
    route_json: str | None
    prompt: str


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *exc) -> None:
        self.conn.commit()
        self.conn.close()

    # ------------------------------------------------------------ writes

    def save_experiment(self, exp_id: str, config: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO experiment VALUES (?,?,?)",
            (exp_id, json.dumps(config, indent=2, default=str), _now()),
        )
        self.conn.commit()

    def save_trials(self, trials: list[TrialRow]) -> None:
        self.conn.executemany(
            "INSERT OR REPLACE INTO trials VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    t.trial_id, t.experiment_id, t.question_id, t.battery_id, t.condition,
                    t.model, t.repeat, t.agent, t.routed_claim_type, t.route_json, t.prompt, _now(),
                )
                for t in trials
            ],
        )
        self.conn.commit()

    def save_answer(self, trial_id: str, payload: dict, duration_s: float | None = None) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO answers VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                trial_id,
                payload.get("answer"),
                payload.get("claim_type"),
                payload.get("searches_used"),
                json.dumps(payload.get("sources") or []),
                payload.get("confidence"),
                1 if payload.get("abstained") else 0,
                json.dumps(payload, default=str),
                duration_s,
                _now(),
            ),
        )
        self.conn.commit()

    def save_grade(
        self, trial_id: str, verdict: str, score: float | None, method: str, grader: str, detail: dict
    ) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?)",
            (trial_id, verdict, score, method, grader, json.dumps(detail, default=str), _now()),
        )
        self.conn.commit()

    # ------------------------------------------------------------- reads

    def config(self) -> dict:
        row = self.conn.execute("SELECT config_json FROM experiment LIMIT 1").fetchone()
        return json.loads(row["config_json"]) if row else {}

    def trials(self) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM trials ORDER BY question_id, condition, model"))

    def trial(self, trial_id: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM trials WHERE trial_id=?", (trial_id,)).fetchone()

    def answered_ids(self) -> set[str]:
        return {r["trial_id"] for r in self.conn.execute("SELECT trial_id FROM answers")}

    def graded_ids(self) -> set[str]:
        return {r["trial_id"] for r in self.conn.execute("SELECT trial_id FROM grades")}

    def joined(self) -> list[sqlite3.Row]:
        """Every trial with its answer and grade, if present."""
        return list(
            self.conn.execute(
                """
                SELECT t.*, a.answer_text, a.claim_type_selfreport, a.searches_used,
                       a.sources_json, a.confidence, a.abstained, a.duration_s,
                       g.verdict, g.score, g.method AS grade_method, g.grader, g.detail_json
                FROM trials t
                LEFT JOIN answers a ON a.trial_id = t.trial_id
                LEFT JOIN grades  g ON g.trial_id = t.trial_id
                ORDER BY t.question_id, t.condition, t.model, t.repeat
                """
            )
        )
