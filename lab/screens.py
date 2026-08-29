"""Screens: the checks that decide which items may enter exp003a, and at what power.

Two screens, and they differ in an important way.

**The routing screen is deterministic and runs now.** It compares the claim type
each item declares against the one `epistemic.router.route()` actually produces.
No solver is involved, so it can be run, frozen and reported before any dispatch
— and it decides which DIRECTIVE each item's treatment arm will contain, which
is the treatment itself.

**The knowledge screen needs solver dispatches and therefore does not run here.**
Its thresholds are frozen anyway. That is the entire point: a ceiling/floor rule
chosen after seeing which items looked interesting is not a screen, it is a
selection effect with a screen's name. `knowledge_screen()` refuses to run
without probe results and reports every item as NOT_SCREENED — fail closed, so a
missing screen blocks the experiment rather than silently passing it.

**Power is recomputed, never inherited.** When an item drops, the plan's §6
statement for that cell no longer holds. `power_statement()` recomputes it and
`cell_power()` says plainly when a cell has fallen below the point where its
consistency claim means anything. The original numbers are not preserved for
tidiness.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCREEN_DIR = REPO_ROOT / "runs" / "screens"

# ---------------------------------------------------------------- thresholds
# Frozen before any solver result exists. Changing one after dispatch is a
# protocol amendment and must be recorded as one.
CEILING = 0.90   # baseline correctness at or above this: nothing can move up
FLOOR = 0.10     # at or below this: the knowledge is not there to surface
PROBE_REPLICATES = 5

KEEP, EXCLUDE, NOT_SCREENED = "KEEP", "EXCLUDE", "NOT_SCREENED"

# Per-cell power from plan §6, as authored. Held here so a recomputation can be
# compared against what was originally claimed rather than replacing it quietly.
PLANNED = {
    "L": {"items": 6, "k": 5, "mde": 0.4, "consistency": 3},
    "R": {"items": 4, "k": 5, "mde": 0.4, "consistency": 2},
    "D": {"items": 5, "k": 5, "mde": 0.4, "consistency": 2},
    "U": {"items": 4, "k": 3, "mde": None, "consistency": 2},
    "N": {"items": 4, "k": 3, "mde": None, "consistency": 2},
    "C": {"items": 2, "k": 3, "mde": None, "consistency": 1},
}


@dataclass
class ScreenResult:
    item_id: str
    screen: str
    decision: str
    reason: str
    detail: dict


# --------------------------------------------------------------------------
# Routing screen — deterministic, runs before any dispatch
# --------------------------------------------------------------------------

def routing_screen(battery, registry=None, asked_on: date | None = None) -> list[ScreenResult]:
    """Does each item route to the claim type its specification declares?

    This is not bookkeeping. The routed claim type selects the directive text
    that `directive_only` and `search_directive` inject, so a misroute means the
    arm delivers a different treatment from the one the item's specification
    predicts about. An item whose spec says it tests the DETERMINISTIC
    directive, and which routes EMPIRICAL, is not testing what it says.
    """
    from epistemic.registry import seed_registry
    from epistemic.router import route

    registry = registry if registry is not None else seed_registry()
    asked_on = asked_on or date.fromisoformat(battery.asked_as_of or "2026-08-28")
    out: list[ScreenResult] = []
    for q in battery.questions:
        rt = route(q.text, asked_on=asked_on, registry=registry)
        routed = rt.claim_type.value
        declared = q.expected_claim_type
        agrees = routed == declared
        out.append(
            ScreenResult(
                item_id=q.id,
                screen="routing",
                decision=KEEP if agrees else EXCLUDE,
                reason=(
                    f"routes {routed} as declared"
                    if agrees
                    else f"declared {declared}, routes {routed} at confidence "
                    f"{rt.classification.confidence:.2f} — the injected directive would be "
                    f"the {routed} one, not the {declared} one the specification predicts about"
                ),
                detail={
                    "declared": declared,
                    "routed": routed,
                    "confidence": round(rt.classification.confidence, 2),
                    "search_budget": rt.search_budget,
                    "signals": {
                        k: v for k, v in rt.classification.as_dict().get("signals", {}).items() if v
                    },
                    "cell": q.cell,
                },
            )
        )
    return out


# --------------------------------------------------------------------------
# Knowledge screen — frozen thresholds, deferred execution
# --------------------------------------------------------------------------

def knowledge_screen(battery, probe: dict | None = None) -> list[ScreenResult]:
    """Ceiling/floor screen on baseline correctness.

    `probe` maps item id to the fraction correct under `baseline` across
    PROBE_REPLICATES replicates. When it is absent — as it is until the probe is
    dispatched — every item comes back NOT_SCREENED rather than KEEP. A screen
    that passes when it has not run is worse than no screen: it produces the
    reassurance without the check.
    """
    out: list[ScreenResult] = []
    for q in battery.questions:
        if probe is None or q.id not in probe:
            out.append(
                ScreenResult(
                    q.id, "knowledge", NOT_SCREENED,
                    "no probe result: the ceiling/floor screen has not been run for this item",
                    {"required_replicates": PROBE_REPLICATES},
                )
            )
            continue
        rate = float(probe[q.id])
        if rate >= CEILING:
            decision, reason = EXCLUDE, f"baseline {rate:.2f} at or above ceiling {CEILING}: no headroom for any condition to move into"
        elif rate <= FLOOR:
            decision, reason = EXCLUDE, f"baseline {rate:.2f} at or below floor {FLOOR}: the knowledge is not present to surface"
        else:
            decision, reason = KEEP, f"baseline {rate:.2f} inside the measurable band ({FLOOR}, {CEILING})"
        out.append(ScreenResult(q.id, "knowledge", decision, reason,
                                {"baseline_rate": rate, "ceiling": CEILING, "floor": FLOOR}))
    return out


# --------------------------------------------------------------------------
# Power, recomputed rather than inherited
# --------------------------------------------------------------------------

def consistency_threshold(n_items: int) -> int | None:
    """How many items must move in the same direction for a cell to claim one.

    Majority of surviving items, minimum two. Below two items there is no
    consistency claim available at all, and `None` says so rather than quietly
    returning 1 — one item moving is an item, not a direction.
    """
    if n_items < 2:
        return None
    return max(2, (n_items + 1) // 2)


@dataclass
class CellPower:
    cell: str
    planned_items: int
    surviving_items: int
    k: int
    per_item_mde: float | None
    consistency_required: int | None
    trials: int
    verdict: str
    note: str


def cell_power(cell: str, surviving: int, conditions: int) -> CellPower:
    planned = PLANNED[cell]
    threshold = consistency_threshold(surviving)
    trials = surviving * conditions * planned["k"]

    if surviving == 0:
        verdict = "DEAD"
        note = "no items survive; the cell reports nothing and its hypothesis is untested, not refuted"
    elif threshold is None:
        verdict = "SINGLE-ITEM"
        note = (
            "one surviving item. A per-item result is still reportable, but no consistency "
            "claim is available: one item moving is a fact about that item."
        )
    elif surviving < planned["items"]:
        verdict = "REDUCED"
        note = (
            f"reduced from {planned['items']} items to {surviving}. The per-item detectable "
            f"shift is unchanged at {planned['mde']} because k is unchanged, but the "
            f"consistency requirement is now {threshold} of {surviving} rather than "
            f"{planned['consistency']} of {planned['items']}, which is a weaker claim on a "
            f"smaller base and must be stated as such."
        )
    else:
        verdict = "AS PLANNED"
        note = f"all {planned['items']} items survive; plan §6 stands unchanged for this cell"

    return CellPower(
        cell=cell,
        planned_items=planned["items"],
        surviving_items=surviving,
        k=planned["k"],
        per_item_mde=planned["mde"],
        consistency_required=threshold,
        trials=trials,
        verdict=verdict,
        note=note,
    )


def power_statement(battery, excluded: set[str], conditions_per_cell: dict[str, int]) -> dict:
    """Recompute §6 for the surviving battery. Never reuses the original numbers."""
    cells: dict[str, CellPower] = {}
    for cell in PLANNED:
        members = [q for q in battery.questions if q.cell == cell]
        surviving = [q for q in members if q.id not in excluded]
        cells[cell] = cell_power(cell, len(surviving), conditions_per_cell.get(cell, 1))
    total = sum(c.trials for c in cells.values())
    return {
        "cells": {k: asdict(v) for k, v in cells.items()},
        "total_solver_trials": total,
        "excluded": sorted(excluded),
        "warning": (
            "Recomputed from the surviving items. The plan §6 figures describe a battery "
            "that no longer exists where a cell reads REDUCED or DEAD; they are kept for "
            "comparison and are not the operative numbers."
            if excluded else
            "No exclusions: plan §6 stands as written."
        ),
    }


def write_screen_report(name: str, payload: dict) -> Path:
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREEN_DIR / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    return path


def load_screen_report(name: str) -> dict | None:
    path = SCREEN_DIR / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else None
