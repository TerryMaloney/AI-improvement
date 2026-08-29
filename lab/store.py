"""SQLite results store.

One database per experiment, at `runs/<exp>/results.db`. Per-experiment rather
than global because an experiment is the unit you re-run, archive, or throw
away; a shared database makes "re-run exp003 cleanly" a delete-with-WHERE
instead of a delete-the-file.

Cross-experiment comparison reads several of these at once — see lab/report.py.

**Old databases are never migrated.** `runs/exp001pilot/results.db` predates the
telemetry columns, and calling the old `joined()` on it raised
`no such column: a.tool_calls_observed`. That error was mechanical proof exp001
had not been rewritten in place, and keeping that property is worth more than the
convenience of an `ALTER TABLE`. So the store is **read-adaptive** instead: it
introspects `PRAGMA table_info`, writes only to columns that exist, and projects
absent columns as `NULL AS <name>` so one code path serves both populations.

The rule that makes this safe: **`NULL` is not `0`.** A column missing from an
old run reads as *not measured*, never as a measured zero. See FD-3.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from lab.telemetry import Telemetry, from_payload as telemetry_from_payload

# Columns are declared as data, not as one frozen CREATE string, because the
# store has to serve two populations at once: databases written before these
# columns existed, and databases written after. See `Store._project` for how.
_TRIAL_COLUMNS = [
    ("trial_id", "TEXT PRIMARY KEY"),
    ("experiment_id", "TEXT NOT NULL"),
    ("question_id", "TEXT NOT NULL"),
    ("battery_id", "TEXT NOT NULL"),
    ("condition", "TEXT NOT NULL"),
    ("model", "TEXT NOT NULL"),
    ("repeat", "INTEGER NOT NULL DEFAULT 1"),
    ("agent", "TEXT NOT NULL"),
    ("routed_claim_type", "TEXT"),
    ("route_json", "TEXT"),
    ("prompt", "TEXT NOT NULL"),
    # Every dispatch is classified BEFORE it is generated, and the class is
    # stored with the trial. A screening dispatch and an experimental dispatch
    # can be byte-identical prompts; only this column tells them apart, and it is
    # what stops a screen's data being reused as the experiment's control.
    ("dispatch_class", "TEXT"),
    # The router as an explicit experimental component. `route_mode` says whether
    # this trial received the directive the classifier selected (`routed`, the
    # deployed behaviour) or the one its specification predicts about
    # (`intended`). Conflating the two is the error the whole D-prime design
    # exists to prevent, so both types travel with every row.
    ("route_mode", "TEXT"),
    ("intended_claim_type", "TEXT"),
    ("block_kind", "TEXT"),
    ("created_at", "TEXT NOT NULL"),
]

_ANSWER_COLUMNS = [
    ("trial_id", "TEXT PRIMARY KEY"),
    ("answer_text", "TEXT"),
    ("claim_type_selfreport", "TEXT"),
    # NOT a cost metric. Deprecated as one in step 3; see FD-2 for why the
    # PROMPT still asks for `searches_used` under that name while storage does
    # not. Renaming here is free because no solver ever sees a column name.
    ("searches_self_report", "INTEGER"),
    ("tool_calls_observed", "INTEGER"),
    ("budget_ceiling", "INTEGER"),
    ("budget_violation_observed", "INTEGER DEFAULT 0"),
    ("retrieval_failures_json", "TEXT"),
    ("sources_json", "TEXT"),
    ("confidence", "TEXT"),
    ("abstained", "INTEGER DEFAULT 0"),
    ("raw_json", "TEXT"),
    ("duration_s", "REAL"),
    # Step 3 telemetry. Every one of these is NULL when not measured, and NULL
    # is never read as zero — "exp001 did not record tokens" and "exp001 used
    # zero tokens" are different claims and only one of them is true.
    ("latency_ms", "INTEGER"),
    ("input_tokens", "INTEGER"),
    ("output_tokens", "INTEGER"),
    ("total_tokens", "INTEGER"),
    ("dispatched_at", "TEXT"),
    ("dispatch_role", "TEXT"),
    ("solver_model", "TEXT"),
    # Retrieval-state machine (lab/states.py). The label carries its evidence
    # depth; the json carries the attained set, the reachable set and the flags.
    ("retrieval_state", "TEXT"),
    ("retrieval_state_json", "TEXT"),
    ("evidence_ledger_json", "TEXT"),
    ("received_at", "TEXT NOT NULL"),
]

_GRADE_COLUMNS = [
    ("trial_id", "TEXT PRIMARY KEY"),
    ("verdict", "TEXT NOT NULL"),
    ("score", "REAL"),
    ("method", "TEXT NOT NULL"),
    ("grader", "TEXT NOT NULL"),
    ("detail_json", "TEXT"),
    ("judge_tokens", "INTEGER"),
    ("judge_latency_ms", "INTEGER"),
    ("judge_model", "TEXT"),
    ("judge_saw_reasoning", "INTEGER"),
    ("k_replicates", "INTEGER"),
    ("graded_at", "TEXT NOT NULL"),
]

# Canonical read names, each with the source columns that may supply them,
# newest first. This is where the rename lands for readers: a database written
# before step 3 supplies `searches_used`, one written after supplies
# `searches_self_report`, and every caller sees the latter.
_ANSWER_ALIASES: dict[str, list[str]] = {
    "searches_self_report": ["searches_self_report", "searches_used"],
}


def _create(table: str, columns: list[tuple[str, str]], extra: str = "") -> str:
    cols = ",\n    ".join(f"{n} {d}" for n, d in columns)
    return f"CREATE TABLE IF NOT EXISTS {table} (\n    {cols}{extra}\n);"


_SCHEMA = "\n".join([
    """CREATE TABLE IF NOT EXISTS experiment (
    id TEXT PRIMARY KEY,
    config_json TEXT NOT NULL,
    prepared_at TEXT NOT NULL
);""",
    _create("trials", _TRIAL_COLUMNS),
    _create("answers", _ANSWER_COLUMNS,
            ",\n    FOREIGN KEY (trial_id) REFERENCES trials(trial_id)"),
    _create("grades", _GRADE_COLUMNS,
            ",\n    FOREIGN KEY (trial_id) REFERENCES trials(trial_id)"),
])

# Deliberately NOT part of _SCHEMA. `CREATE TABLE IF NOT EXISTS` is a no-op on an
# existing database, but `CREATE INDEX` names columns, and on a database that
# predates them it raises `no such column: condition` — which would mean an old
# run could no longer be OPENED, let alone read. The index is created only when
# the columns it needs are present.
_INDEX = ("idx_trials_cond", "trials", ("condition", "model"))


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
    dispatch_class: str = "solver_experiment"
    route_mode: str = "routed"
    block_kind: str | None = None
    intended_claim_type: str | None = None


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        # CREATE TABLE IF NOT EXISTS only. On an existing database this is a
        # no-op, which is the point: no ALTER, no backfill, no rewrite of a
        # frozen experiment's bytes.
        self.conn.executescript(_SCHEMA)
        self._cols = {
            t: [r["name"] for r in self.conn.execute(f"PRAGMA table_info({t})")]
            for t in ("trials", "answers", "grades")
        }
        name, table, cols = _INDEX
        if all(c in self._cols[table] for c in cols):
            self.conn.execute(
                f"CREATE INDEX IF NOT EXISTS {name} ON {table}({','.join(cols)})"
            )
            self.conn.commit()

    def columns(self, table: str) -> list[str]:
        """What this particular database actually has. Differs between a
        pre-step-3 run and a post-step-3 one, by design."""
        return list(self._cols[table])

    def _project(self, table: str, prefix: str, aliases: dict[str, list[str]]) -> str:
        """SELECT list giving every canonical column a value, NULL when absent.

        This is what lets a report read exp001pilot and exp003a with the same
        code without either pretending exp001pilot measured something it did not.
        """
        have = self._cols[table]
        canonical = [n for n, _ in (
            _ANSWER_COLUMNS if table == "answers" else _GRADE_COLUMNS
        )]
        out = []
        for name in canonical:
            sources = aliases.get(name, [name])
            found = next((c for c in sources if c in have), None)
            out.append(f"{prefix}.{found} AS {name}" if found else f"NULL AS {name}")
        return ", ".join(out)

    def _insert(self, table: str, values: dict) -> None:
        """Write only the columns this database has.

        A frozen database opened for reading and then written to would gain
        columns it never had; refusing to write unknown columns keeps a stray
        write from becoming a schema change.
        """
        cols = [c for c in self._cols[table] if c in values]
        placeholders = ",".join("?" for _ in cols)
        self.conn.execute(
            f"INSERT OR REPLACE INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
            [values[c] for c in cols],
        )
        self.conn.commit()

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
        for t in trials:
            self._insert("trials", {
                "trial_id": t.trial_id, "experiment_id": t.experiment_id,
                "question_id": t.question_id, "battery_id": t.battery_id,
                "condition": t.condition, "model": t.model, "repeat": t.repeat,
                "agent": t.agent, "routed_claim_type": t.routed_claim_type,
                "route_json": t.route_json, "prompt": t.prompt,
                "dispatch_class": t.dispatch_class, "route_mode": t.route_mode,
                "block_kind": t.block_kind, "intended_claim_type": t.intended_claim_type,
                "created_at": _now(),
            })

    def save_answer(
        self,
        trial_id: str,
        payload: dict,
        duration_s: float | None = None,
        telemetry: "Telemetry | None" = None,
        retrieval: dict | None = None,
        evidence: list | None = None,
    ) -> None:
        """Persist one solver dispatch.

        Cost accounting rules, enforced here rather than trusted downstream:

        * `tool_calls_observed` is the PRIMARY cost metric and comes from the
          harness. `searches_self_report` is the solver's own account, stored
          beside it and never used as cost (FD-2). The GAP between the two is a
          measurement in its own right — does the model know what it did? — and
          is reported rather than reconciled.
        * Telemetry fields are `None` when not measured. Nothing here converts an
          absent measurement into a zero.
        """
        observed = payload.get("tool_calls_observed")
        ceiling = payload.get("budget_ceiling")
        violation = (
            1 if (isinstance(observed, int) and isinstance(ceiling, int) and observed > ceiling)
            else 0
        )
        tm = telemetry or telemetry_from_payload(payload, "solver")
        self._insert("answers", {
            "trial_id": trial_id,
            "answer_text": payload.get("answer"),
            "claim_type_selfreport": payload.get("claim_type"),
            # Old databases still carry this under its old name; `_insert` writes
            # whichever of the two this particular database has.
            "searches_self_report": payload.get("searches_used"),
            "searches_used": payload.get("searches_used"),
            "tool_calls_observed": observed,
            "budget_ceiling": ceiling,
            "budget_violation_observed": violation,
            "retrieval_failures_json": json.dumps(payload.get("retrieval_failures") or []),
            "sources_json": json.dumps(payload.get("sources") or []),
            "confidence": payload.get("confidence"),
            "abstained": 1 if payload.get("abstained") else 0,
            "raw_json": json.dumps(payload, default=str),
            "duration_s": duration_s,
            "latency_ms": tm.latency_ms,
            "input_tokens": tm.input_tokens,
            "output_tokens": tm.output_tokens,
            "total_tokens": tm.total_tokens,
            "dispatched_at": tm.dispatched_at,
            "dispatch_role": tm.dispatch_role,
            "solver_model": tm.model,
            "retrieval_state": (retrieval or {}).get("label"),
            "retrieval_state_json": json.dumps(retrieval) if retrieval else None,
            "evidence_ledger_json": json.dumps(evidence, default=str) if evidence else None,
            "received_at": _now(),
        })

    def save_grade(
        self,
        trial_id: str,
        verdict: str,
        score: float | None,
        method: str,
        grader: str,
        detail: dict,
        telemetry: "Telemetry | None" = None,
        judge_saw_reasoning: bool | None = None,
        k_replicates: int | None = None,
    ) -> None:
        """Persist one grade, with the judge dispatch's own cost.

        Judge dispatches were free in exp001/exp002's accounting and not free in
        reality. An experiment whose reported cost excludes its grading is not
        reporting its cost.
        """
        tm = telemetry
        self._insert("grades", {
            "trial_id": trial_id,
            "verdict": verdict,
            "score": score,
            "method": method,
            "grader": grader,
            "detail_json": json.dumps(detail, default=str),
            "judge_tokens": tm.total_tokens if tm else None,
            "judge_latency_ms": tm.latency_ms if tm else None,
            "judge_model": (tm.model if tm else None) or detail.get("judge_model"),
            "judge_saw_reasoning": None if judge_saw_reasoning is None else int(judge_saw_reasoning),
            "k_replicates": k_replicates,
            "graded_at": _now(),
        })

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

    def dispatch_classes(self) -> dict[str, int]:
        """How many trials of each dispatch class this database holds.

        Read by the preflight and by the report. A primary analysis over a
        database containing anything other than `solver_experiment` rows is a
        contaminated analysis, and the caller is expected to refuse rather than
        filter — filtering silently would make the contamination invisible.
        """
        if "dispatch_class" not in self._cols["trials"]:
            return {}
        return {
            r["dispatch_class"] or "unclassified": r["n"]
            for r in self.conn.execute(
                "SELECT dispatch_class, COUNT(*) AS n FROM trials GROUP BY dispatch_class"
            )
        }

    def assert_single_dispatch_class(self, expected: str) -> None:
        """Refuse to serve a database that mixes dispatch classes.

        The hard invariant behind the probe/experiment boundary. Screening
        observations select items on their baseline performance; reusing them as
        experimental control data would condition the control on the selection
        criterion and bias every contrast through regression to the mean.

        This RAISES rather than filtering. Filtering would let a contaminated
        database produce a clean-looking analysis, which is the failure the
        invariant exists to prevent — the caller must fix the database, not have
        the problem quietly removed from the numbers.
        """
        classes = self.dispatch_classes()
        if not classes:
            return  # pre-step-3 database: no class column, nothing to mix
        foreign = {k: v for k, v in classes.items() if k != expected}
        if foreign:
            raise ValueError(
                f"{self.path}: this analysis expects only `{expected}` trials, but the "
                f"database also contains {foreign}. Screening and qualification dispatches "
                f"may not enter a primary analysis. Refusing rather than filtering: a "
                f"filtered result would look clean and be contaminated."
            )

    def joined(self) -> list[sqlite3.Row]:
        """Every trial with its answer and grade, if present.

        Both projections are built from `PRAGMA table_info`, so this works on a
        database written before the telemetry columns existed — which is exactly
        the case that used to raise `no such column: a.tool_calls_observed`. The
        missing columns come back as NULL, meaning *not measured*.
        """
        answers = self._project("answers", "a", _ANSWER_ALIASES)
        grades = self._project("grades", "g", {})
        # `method` and `grader` collide with nothing in trials but read better
        # under their historical report-facing names.
        grades = grades.replace("g.method AS method", "g.method AS grade_method")
        grades = grades.replace("NULL AS method", "NULL AS grade_method")
        return list(
            self.conn.execute(
                f"""
                SELECT t.*, {answers}, {grades}
                FROM trials t
                LEFT JOIN answers a ON a.trial_id = t.trial_id
                LEFT JOIN grades  g ON g.trial_id = t.trial_id
                ORDER BY t.question_id, t.condition, t.model, t.repeat
                """
            )
        )
