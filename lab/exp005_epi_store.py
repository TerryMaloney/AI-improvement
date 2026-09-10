"""SQLite persistence for EXP005-EPI.

The database is an external audit log. Evidence rows are append-only. Beliefs and
revision snapshots can be regenerated from evidence + rules, so the store never
allows an evidence UPDATE or DELETE path.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import sqlite3
from pathlib import Path

from lab.exp005_epi import DerivedRule, EpistemicWorkspace, Evidence, ObjectivePolicy


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    proposition TEXT NOT NULL,
    asserted_value INTEGER NOT NULL CHECK(asserted_value IN (0,1)),
    source_id TEXT NOT NULL,
    lineage_id TEXT NOT NULL,
    reliability REAL NOT NULL,
    observed_at INTEGER NOT NULL,
    supersedes_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    canonical_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT PRIMARY KEY,
    canonical_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at INTEGER NOT NULL,
    fingerprint TEXT NOT NULL,
    snapshot_json TEXT NOT NULL
);
"""


class EpistemicStore:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.executescript(SCHEMA)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def initialize_objective(self, objective: ObjectivePolicy) -> None:
        payload = json.dumps(asdict(objective), sort_keys=True)
        row = self.db.execute("SELECT value FROM metadata WHERE key='objective'").fetchone()
        if row is None:
            self.db.execute("INSERT INTO metadata(key,value) VALUES('objective',?)", (payload,))
            self.db.commit()
            return
        if row[0] != payload:
            raise ValueError("objective state is immutable for an existing workspace")

    def append_evidence(self, evidence: Evidence) -> None:
        canonical = evidence.canonical()
        row = self.db.execute(
            "SELECT canonical_json FROM evidence WHERE evidence_id=?",
            (evidence.evidence_id,),
        ).fetchone()
        if row is not None:
            if row[0] == canonical:
                return
            raise ValueError(f"evidence id collision: {evidence.evidence_id}")
        self.db.execute(
            """INSERT INTO evidence(
                evidence_id, proposition, asserted_value, source_id, lineage_id,
                reliability, observed_at, supersedes_json, metadata_json, canonical_json
            ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                evidence.evidence_id, evidence.proposition, int(evidence.asserted_value),
                evidence.source_id, evidence.lineage_id, evidence.reliability,
                evidence.observed_at, json.dumps(evidence.supersedes),
                json.dumps(evidence.metadata, sort_keys=True), canonical,
            ),
        )
        self.db.commit()

    def append_rule(self, rule: DerivedRule) -> None:
        payload = json.dumps(asdict(rule), sort_keys=True, separators=(",", ":"))
        row = self.db.execute(
            "SELECT canonical_json FROM rules WHERE rule_id=?", (rule.rule_id,)
        ).fetchone()
        if row is not None:
            if row[0] == payload:
                return
            raise ValueError(f"rule id collision: {rule.rule_id}")
        self.db.execute("INSERT INTO rules(rule_id,canonical_json) VALUES(?,?)",
                        (rule.rule_id, payload))
        self.db.commit()

    def load_workspace(self) -> EpistemicWorkspace:
        row = self.db.execute("SELECT value FROM metadata WHERE key='objective'").fetchone()
        if row is None:
            raise ValueError("store has no objective")
        o = json.loads(row[0])
        ws = EpistemicWorkspace(ObjectivePolicy(
            objective_id=o["objective_id"],
            description=o["description"],
            permissions=tuple(o.get("permissions", ())),
        ))
        for (payload,) in self.db.execute(
            "SELECT canonical_json FROM evidence ORDER BY observed_at,evidence_id"
        ):
            e = json.loads(payload)
            ws.ingest(Evidence(
                evidence_id=e["evidence_id"],
                proposition=e["proposition"],
                asserted_value=bool(e["asserted_value"]),
                source_id=e["source_id"],
                lineage_id=e["lineage_id"],
                reliability=float(e["reliability"]),
                observed_at=int(e["observed_at"]),
                supersedes=tuple(e.get("supersedes", ())),
                metadata=e.get("metadata", {}),
            ))
        for (payload,) in self.db.execute("SELECT canonical_json FROM rules ORDER BY rule_id"):
            r = json.loads(payload)
            ws.add_rule(DerivedRule(
                rule_id=r["rule_id"], output=r["output"],
                premises=tuple((p, bool(v)) for p, v in r["premises"]),
                op=r.get("op", "all"), impact=float(r.get("impact", 1.0)),
            ))
        return ws

    def save_snapshot(self, ws: EpistemicWorkspace) -> int:
        snap = ws.snapshot()
        cur = self.db.execute(
            "INSERT INTO snapshots(created_at,fingerprint,snapshot_json) VALUES(?,?,?)",
            (int(snap["clock"]), ws.fingerprint(),
             json.dumps(snap, sort_keys=True, separators=(",", ":"))),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def evidence_count(self) -> int:
        return int(self.db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0])
