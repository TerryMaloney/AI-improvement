"""Entity-hazard TTL registry.

The idea the packet found most durable: *staleness is a property of the
specific entity, not of the category*. "Who runs X" is not one TTL. The OpenAI
CRO seat turned over twice in under two years; the US Fed Chair has a fixed
four-year term with a known end date. Treating both as "facts about people in
jobs" and giving them the same refresh interval is how a system serves a
confidently stale answer.

Three buckets (packet §3):

    VOLATILE   high turnover for THIS entity, no fixed term.
               Cheap to check (one search). Known weak point: the threshold is
               eyeballed — see the calibration note below.
    SCHEDULED  known term-end date. Free to reason about once the date is
               known: before the date, the cached value stands.
    STABLE     long typical tenure, but hazard is never zero. Periodic
               re-check, not a re-check on every query, and never "permanent".

CALIBRATION DEBT (packet §2.3): the 30-day VOLATILE default was chosen by
eyeballing two examples. `observed_intervals_days` exists so the lab can
accumulate real turnover intervals per entity and replace the guess with data.
Until that happens, `EntityRecord.threshold_is_calibrated` is False and the
registry says so out loud rather than letting a guessed number pass as a
measured one.

LEAKAGE RULE: a record's `value` is a cached fact. It must never reach a model
under test through a trial packet — that would be handing over the answer. The
router deliberately emits staleness verdicts *about* a record and never the
record's value. See `epistemic/router.py` and
`tests/test_no_answer_leakage.py`.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from pathlib import Path


class Bucket(str, Enum):
    VOLATILE = "VOLATILE"
    SCHEDULED = "SCHEDULED"
    STABLE = "STABLE"


# Defaults, all of them provisional and labelled as such.
DEFAULT_VOLATILE_TTL_DAYS = 30      # eyeballed from two examples. See above.
DEFAULT_STABLE_TTL_DAYS = 365       # "nonzero hazard" backstop, not a belief.
SCHEDULED_OFF_CYCLE_BACKSTOP_DAYS = 180
"""Even a fixed-term seat can be vacated early (resignation, death, removal).
A SCHEDULED record therefore still gets a slow backstop re-check, so that
"safe until 2030" cannot quietly mean "unchecked until 2030"."""


@dataclass
class EntityRecord:
    key: str
    """Stable identifier, e.g. 'openai_cro'."""

    description: str
    """Human-readable slot, e.g. 'OpenAI Chief Revenue Officer'."""

    bucket: Bucket
    value: str | None = None
    """Cached fact. NEVER include this in anything a model under test sees."""

    last_verified: date | None = None
    term_end: date | None = None
    """SCHEDULED only: the date the cached value is known to expire."""

    ttl_days: int | None = None
    """Override for the bucket default."""

    observed_intervals_days: list[int] = field(default_factory=list)
    """Real observed turnover gaps for THIS entity. The input to replacing the
    eyeballed VOLATILE threshold with a measured one."""

    provenance: str = ""
    notes: str = ""

    # ---------------------------------------------------------------- TTL

    @property
    def effective_ttl_days(self) -> int:
        if self.ttl_days is not None:
            return self.ttl_days
        if self.bucket is Bucket.VOLATILE:
            return DEFAULT_VOLATILE_TTL_DAYS
        if self.bucket is Bucket.STABLE:
            return DEFAULT_STABLE_TTL_DAYS
        return SCHEDULED_OFF_CYCLE_BACKSTOP_DAYS

    @property
    def threshold_is_calibrated(self) -> bool:
        """True only once this entity has enough observed turnover data to
        justify its threshold. Two eyeballed examples is not enough."""
        return len(self.observed_intervals_days) >= 3

    def age_days(self, as_of: date) -> int | None:
        if self.last_verified is None:
            return None
        return (as_of - self.last_verified).days

    def needs_reverification(self, as_of: date, redact: bool = False) -> tuple[bool, str]:
        """Return (needs_check, human-readable reason).

        `redact=True` produces the model-facing form. The unredacted form names
        the term-end date, which is operationally useful — and is also, for a
        question like "when does that term end?", *half the answer*. Handing
        that to the treatment condition and not the control would have inflated
        the treatment's score for a reason that has nothing to do with the
        procedure being tested. So the model-facing form states only that a
        scheduled end exists and whether it has passed.

        Caught by tests/test_no_answer_leakage.py, which is the point of
        writing that test against real packets rather than a toy example.
        """
        if self.last_verified is None:
            return True, f"{self.description}: never verified — must be checked before use"

        age = self.age_days(as_of)
        when = "its scheduled term end" if redact else (
            self.term_end.isoformat() if self.term_end else "an unknown date"
        )

        if self.bucket is Bucket.SCHEDULED and self.term_end is not None:
            if as_of >= self.term_end:
                return True, (
                    f"{self.description}: the scheduled term has ended ({when}) "
                    f"— the cached value is expired by its own schedule"
                )
            if age is not None and age > SCHEDULED_OFF_CYCLE_BACKSTOP_DAYS:
                return True, (
                    f"{self.description}: has a fixed term still running (to {when}), but the "
                    f"cached value is {age} days old and fixed terms can still end early — "
                    f"slow backstop re-check due"
                )
            return False, (
                f"{self.description}: SCHEDULED, with a fixed term running to {when} that has "
                f"not yet passed — cached value stands (verified {age} days ago)"
            )

        ttl = self.effective_ttl_days
        if age is not None and age > ttl:
            calib = "" if self.threshold_is_calibrated else " (threshold is uncalibrated — an estimate, not a measurement)"
            return True, (
                f"{self.description}: {self.bucket.value}, verified {age} days ago against a "
                f"{ttl}-day TTL — stale, re-verify{calib}"
            )
        return False, (
            f"{self.description}: {self.bucket.value}, verified {age} days ago, within its "
            f"{ttl}-day TTL"
        )

    # ------------------------------------------------------------ storage

    def to_row(self) -> tuple:
        return (
            self.key,
            self.description,
            self.bucket.value,
            self.value,
            self.last_verified.isoformat() if self.last_verified else None,
            self.term_end.isoformat() if self.term_end else None,
            self.ttl_days,
            json.dumps(self.observed_intervals_days),
            self.provenance,
            self.notes,
        )

    @classmethod
    def from_row(cls, row: tuple) -> "EntityRecord":
        return cls(
            key=row[0],
            description=row[1],
            bucket=Bucket(row[2]),
            value=row[3],
            last_verified=date.fromisoformat(row[4]) if row[4] else None,
            term_end=date.fromisoformat(row[5]) if row[5] else None,
            ttl_days=row[6],
            observed_intervals_days=json.loads(row[7]) if row[7] else [],
            provenance=row[8] or "",
            notes=row[9] or "",
        )


_SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    bucket TEXT NOT NULL,
    value TEXT,
    last_verified TEXT,
    term_end TEXT,
    ttl_days INTEGER,
    observed_intervals TEXT,
    provenance TEXT,
    notes TEXT
);
"""


class EntityRegistry:
    """In-memory registry with optional SQLite persistence.

    SQLite is deliberate (packet §2.4): "do not build a graph database for
    this". Growth path is `upsert()` on encounter, not a schema project.
    """

    def __init__(self, records: dict[str, EntityRecord] | None = None):
        self._records: dict[str, EntityRecord] = dict(records or {})

    # ------------------------------------------------------------- access

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, key: str) -> bool:
        return key in self._records

    def get(self, key: str) -> EntityRecord | None:
        return self._records.get(key)

    def all(self) -> list[EntityRecord]:
        return list(self._records.values())

    def upsert(self, record: EntityRecord) -> None:
        self._records[record.key] = record

    def record_verification(self, key: str, value: str, on: date) -> None:
        """Mark an entity as freshly verified. If the value changed, the gap
        since the last verification is banked as an observed turnover interval
        — this is how the eyeballed TTL eventually becomes a measured one."""
        rec = self._records[key]
        if rec.value is not None and rec.value != value and rec.last_verified is not None:
            rec.observed_intervals_days.append((on - rec.last_verified).days)
        rec.value = value
        rec.last_verified = on

    def needing_reverification(self, as_of: date) -> list[tuple[EntityRecord, str]]:
        out = []
        for rec in self._records.values():
            needs, reason = rec.needs_reverification(as_of)
            if needs:
                out.append((rec, reason))
        return out

    def match(self, question: str) -> list[EntityRecord]:
        """Very cheap entity lookup: does the question mention this record's
        match terms? Rules only — no embedding, no model call."""
        q = question.lower()
        hits = []
        for rec in self._records.values():
            terms = [t.strip().lower() for t in rec.description.split() if len(t.strip()) > 3]
            if terms and all(t in q for t in terms):
                hits.append(rec)
                continue
            # fall back to a looser match on the key's parts
            parts = [p for p in rec.key.split("_") if len(p) > 2]
            if parts and all(p in q for p in parts):
                hits.append(rec)
        return hits

    # -------------------------------------------------------- persistence

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            conn.executescript(_SCHEMA)
            conn.executemany(
                "INSERT OR REPLACE INTO entities VALUES (?,?,?,?,?,?,?,?,?,?)",
                [r.to_row() for r in self._records.values()],
            )

    @classmethod
    def load(cls, path: str | Path) -> "EntityRegistry":
        path = Path(path)
        registry = cls()
        if not path.exists():
            return registry
        with sqlite3.connect(path) as conn:
            conn.executescript(_SCHEMA)
            for row in conn.execute("SELECT * FROM entities"):
                rec = EntityRecord.from_row(row)
                registry.upsert(rec)
        return registry


def seed_registry() -> EntityRegistry:
    """The seed entities, all re-verified 2026-08-27.

    Packet §5 carried four values forward from the design session and noted
    that none had been re-checked. They have now been, and all four held. The
    check was still worth running: "it turned out to be right" is a result, not
    a reason to have skipped it, and the fifth entity added here (Berkshire) is
    the one that had in fact changed.

    Re-verify before relying on any of this. `python -m lab refresh` says what
    is past its TTL.
    """
    return EntityRegistry(
        {
            r.key: r
            for r in [
                EntityRecord(
                    key="openai_cro",
                    description="OpenAI Chief Revenue Officer",
                    bucket=Bucket.VOLATILE,
                    value="Dali Rajic",
                    last_verified=date(2026, 8, 27),
                    # FIRST REAL CALIBRATION DATA for the VOLATILE threshold
                    # (packet §2.3, ledger H2). Rajic succeeded Denise Dresser,
                    # who held the seat about nine months; the prior transition
                    # is what made the packet call this seat volatile.
                    # Note what this suggests: observed turnover here is ~270
                    # days against a 30-day TTL, i.e. the eyeballed threshold
                    # is roughly 9x more conservative than this entity needs.
                    # One entity is not a calibration — but it is the first
                    # datum that was ever measured rather than guessed.
                    observed_intervals_days=[270],
                    provenance="verified 2026-08-27 against openai.com plus Axios/TechCrunch/"
                    "Bloomberg/Fortune coverage dated 2026-08-13",
                    notes="Seat changed twice in under two years. The 'AI stacking' failure "
                    "was confirmed in the wild on this exact story.",
                ),
                EntityRecord(
                    key="uk_pm",
                    description="United Kingdom Prime Minister",
                    bucket=Bucket.VOLATILE,
                    value="Andy Burnham",
                    last_verified=date(2026, 8, 27),
                    provenance="verified 2026-08-27 against CNN/ABC/CFR; took office 2026-07-20",
                    notes="7 PMs in 10 years. Also the source of the independence-check "
                    "false-positive risk (many outlets, one underlying source).",
                ),
                EntityRecord(
                    key="fed_chair",
                    description="United States Federal Reserve Chair",
                    bucket=Bucket.SCHEDULED,
                    value="Kevin Warsh",
                    last_verified=date(2026, 8, 27),
                    term_end=date(2030, 5, 21),
                    provenance="verified 2026-08-27 against federalreserve.gov: oath taken "
                    "2026-05-22, four-year term ending 2030-05-21",
                    notes="Fixed term, and the term end is now a primary-source fact rather "
                    "than an inference. Lowest-priority re-check of the five, but not zero: "
                    "see SCHEDULED_OFF_CYCLE_BACKSTOP_DAYS.",
                ),
                EntityRecord(
                    key="nato_sg",
                    description="NATO Secretary General",
                    bucket=Bucket.SCHEDULED,
                    value="Mark Rutte",
                    last_verified=date(2026, 8, 27),
                    term_end=date(2028, 10, 1),
                    provenance="verified 2026-08-27 against nato.int: took office 2024-10-01. "
                    "Term end remains INFERRED from the four-year initial period — the post is "
                    "extendable by mutual consent, so there is no fixed constitutional end date",
                    notes="Packet calls this 'scheduled-hybrid': 4yr renewable. The renewal "
                    "option is exactly the case a pure SCHEDULED reading gets wrong, which is "
                    "why the term_end here is honestly labelled an inference.",
                ),
                EntityRecord(
                    key="berkshire_ceo",
                    description="Berkshire Hathaway Chief Executive Officer",
                    bucket=Bucket.STABLE,
                    value="Greg Abel",
                    last_verified=date(2026, 8, 27),
                    provenance="verified 2026-08-27 against CNBC/Forbes and Berkshire's 2026 "
                    "reporting: Abel became CEO effective 2026-01-01",
                    notes="The STABLE bucket's justification in one record: the same answer "
                    "from 1965 to 2025, then a change. A bucket that treated long tenure as "
                    "permanence would have been wrong here for the first time in sixty years, "
                    "which is precisely when being wrong is most expensive.",
                ),
            ]
        }
    )
