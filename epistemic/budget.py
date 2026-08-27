"""Hard cost ceiling — a permanent rail, not an optimisation.

The failure this defends against (packet §4) is an EIG spiral: a controller
that computes expected information gain, finds it is always marginally positive
for one more retrieval, and never stops. The defence is deliberately *stupid*:
a call counter that does not consult the EIG math, cannot be argued with, and
does not care how promising the next call looks. If a smarter component could
talk the ceiling into one more call, it would not be a ceiling.

The packet flagged this class as "exists but untested under a real runaway
case". `tests/test_budget.py` now runs exactly that case — an agent loop that
always requests another call — and asserts termination in bounded steps.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


class BudgetExceeded(RuntimeError):
    """Raised by `charge()` when a spend would cross the ceiling.

    Crossing the ceiling is not an error in the system — it is the system
    working. Callers should catch this and abstain or answer with what they
    have, recording that the ceiling bound the result.
    """

    def __init__(self, kind: str, spent: int, limit: int, label: str = ""):
        self.kind, self.spent, self.limit, self.label = kind, spent, limit, label
        where = f" [{label}]" if label else ""
        super().__init__(f"budget ceiling hit{where}: {kind} would exceed limit ({spent}/{limit})")


@dataclass
class BudgetCeiling:
    """A per-question spend ceiling.

    `max_calls` counts every model/tool invocation; `max_searches` is the
    tighter sub-limit on external retrieval, which is the expensive one.
    `max_seconds` is a wall-clock backstop for the case where the call count
    stays low but individual calls hang.
    """

    max_calls: int = 6
    max_searches: int = 4
    max_seconds: float | None = None
    label: str = ""

    spent: dict[str, int] = field(default_factory=lambda: {"calls": 0, "searches": 0})
    started_at: float = field(default_factory=time.monotonic)
    trips: list[str] = field(default_factory=list)
    """Every refused spend, in order. This is audit-trail material: a question
    that repeatedly trips the ceiling is a signal about the question, not just
    about the budget."""

    _LIMIT_ATTR = {"calls": "max_calls", "searches": "max_searches"}

    # ------------------------------------------------------------- limits

    def limit_for(self, kind: str) -> int:
        try:
            return getattr(self, self._LIMIT_ATTR[kind])
        except KeyError:
            raise ValueError(f"unknown budget kind: {kind!r}") from None

    def remaining(self, kind: str) -> int:
        return max(0, self.limit_for(kind) - self.spent.get(kind, 0))

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.started_at

    @property
    def out_of_time(self) -> bool:
        return self.max_seconds is not None and self.elapsed >= self.max_seconds

    @property
    def exhausted(self) -> bool:
        return self.remaining("calls") == 0 or self.out_of_time

    # ------------------------------------------------------------- spends

    def can_charge(self, kind: str, n: int = 1) -> bool:
        if self.out_of_time:
            return False
        # A search costs a search AND a call. Both must clear.
        if kind == "searches" and self.remaining("calls") < n:
            return False
        return self.remaining(kind) >= n

    def charge(self, kind: str, n: int = 1) -> None:
        """Spend, or raise. Use this when the caller cannot sensibly continue."""
        if self.out_of_time:
            self.trips.append(f"time: {self.elapsed:.1f}s >= {self.max_seconds}s")
            raise BudgetExceeded("seconds", int(self.elapsed), int(self.max_seconds or 0), self.label)
        if not self.can_charge(kind, n):
            spent = self.spent.get(kind, 0) + n
            self.trips.append(f"{kind}: {spent} > {self.limit_for(kind)}")
            raise BudgetExceeded(kind, spent, self.limit_for(kind), self.label)
        self.spent[kind] = self.spent.get(kind, 0) + n
        if kind == "searches":
            self.spent["calls"] = self.spent.get("calls", 0) + n

    def try_charge(self, kind: str, n: int = 1) -> bool:
        """Spend if possible, else record the refusal and return False. Use
        this when the caller should degrade gracefully rather than blow up."""
        try:
            self.charge(kind, n)
            return True
        except BudgetExceeded:
            return False

    def snapshot(self) -> dict:
        return {
            "label": self.label,
            "limits": {"calls": self.max_calls, "searches": self.max_searches, "seconds": self.max_seconds},
            "spent": dict(self.spent),
            "elapsed_s": round(self.elapsed, 3),
            "exhausted": self.exhausted,
            "trips": list(self.trips),
        }
