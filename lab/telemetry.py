"""Per-dispatch telemetry — what a call actually cost, as observed.

Every model call the lab makes is a **dispatch**, and every dispatch has a role:
`solver`, `judge`, `scout`, or `verifier`. Until now only solver dispatches were
recorded at all, and the only cost number in the reports came from the solver's
own `searches_used` field. Two problems with that, one obvious and one not:

* The obvious one: a self-report is a claim about behaviour, not a measurement of
  it. exp001 had zero budget violations by self-report and thirteen by observed
  tool calls.

* The subtle one: judge dispatches were free in the accounting and not free in
  reality. An experiment whose "cost" excludes 170 judge calls is not reporting
  its cost, and a procedure that wins on solver cost while tripling grading cost
  has not been shown to be cheaper than anything.

So: telemetry is **observed-authoritative**. A field is populated from harness
keys or it is `None`, and `None` means *not measured* — never zero. The solver's
self-report is preserved in its own namespace and never merged into an observed
field. The gap between them is retained as a measurement in its own right (does
the model know what it did?) rather than reconciled away.

See `docs/EXP003A_FROZEN_DECISIONS.md` FD-2 for why the *prompt* still asks for
`searches_used` under that name even though storage and reporting no longer do.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone

ROLES = ("solver", "judge", "scout", "verifier")

# Keys the HARNESS writes into a dispatch record. Nothing else may populate an
# observed field. Kept as an explicit allow-list so that a solver inventing a
# `latency_ms` key in its own JSON cannot become a measurement.
_HARNESS_KEYS = {
    "tool_calls_observed",
    "latency_ms",
    "duration_s",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "dispatched_at",
    "received_at",
    "model",
    "dispatch_role",
}

# Keys the SOLVER writes. Diagnostics only; never a cost figure.
_SELF_REPORT_KEYS = {"searches_used", "sources", "confidence", "abstained", "notes"}

# Recorded explicitly rather than left blank, so a reader can tell "we looked and
# it is not obtainable" from "nobody thought about it".
NOT_MEASURED = "NOT_MEASURED: harness returns an aggregate; per-tool split is not obtainable at this scale"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _as_int(v) -> int | None:
    """Ints only, and never a bool. `True` arriving where a count belongs is a
    bug upstream; silently storing it as 1 would hide the bug in a number."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return None


@dataclass(frozen=True)
class Telemetry:
    """What one dispatch cost, as measured. `None` means not measured."""

    dispatch_role: str
    model: str | None = None
    dispatched_at: str | None = None
    received_at: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    tool_calls_observed: int | None = None
    per_tool_split: str = NOT_MEASURED

    @property
    def tokens_measured(self) -> bool:
        return self.total_tokens is not None

    @property
    def cost_measured(self) -> bool:
        """True when this dispatch can enter a cost table at all.

        Observed tool calls are the lab's cost currency. A dispatch without them
        is excluded from cost aggregates rather than counted as zero — see the
        module docstring.
        """
        return self.tool_calls_observed is not None

    def as_dict(self) -> dict:
        return asdict(self)


def from_payload(payload: dict, role: str, received_at: str | None = None) -> Telemetry:
    """Build telemetry from a dispatch record, reading harness keys only.

    `total_tokens` is derived from the input/output pair when the harness gave
    the parts but not the sum. It is NOT derived the other way: a sum without
    parts stays a sum, because splitting it would be invention.
    """
    if role not in ROLES:
        raise ValueError(f"unknown dispatch role {role!r}; expected one of {ROLES}")

    latency = _as_int(payload.get("latency_ms"))
    if latency is None:
        secs = payload.get("duration_s")
        if isinstance(secs, (int, float)) and not isinstance(secs, bool):
            latency = int(round(float(secs) * 1000))

    inp = _as_int(payload.get("input_tokens"))
    out = _as_int(payload.get("output_tokens"))
    total = _as_int(payload.get("total_tokens"))
    if total is None and inp is not None and out is not None:
        total = inp + out

    return Telemetry(
        dispatch_role=role,
        model=payload.get("model"),
        dispatched_at=payload.get("dispatched_at"),
        received_at=received_at or payload.get("received_at") or _now(),
        latency_ms=latency,
        input_tokens=inp,
        output_tokens=out,
        total_tokens=total,
        tool_calls_observed=_as_int(payload.get("tool_calls_observed")),
    )


def self_report(payload: dict) -> dict:
    """The solver's own account of what it did. Diagnostics only.

    Deliberately a separate function returning a separate dict: there is no code
    path in the lab where a self-reported number can end up in a field that a
    reader would take for a measurement.
    """
    return {k: payload.get(k) for k in _SELF_REPORT_KEYS if k in payload}


def selfreport_gap(payload: dict) -> dict | None:
    """Observed tool calls minus self-reported searches, when both exist.

    Returns `None` when either side is missing — an absent measurement produces
    no gap, rather than a gap against zero.

    The two are not the same quantity (a tool call may be a fetch, not a search),
    so a non-zero gap is not automatically a false report. That is exactly why it
    is reported and not corrected: the interesting cases are the large ones.
    """
    observed = _as_int(payload.get("tool_calls_observed"))
    claimed = _as_int(payload.get("searches_used"))
    if observed is None or claimed is None:
        return None
    return {"observed": observed, "self_reported": claimed, "gap": observed - claimed}
