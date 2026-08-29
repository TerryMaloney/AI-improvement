"""The frozen retrieval scout: what the search space actually contains, per item.

Cell D tests retrieval DISPLACEMENT — the hypothesis that searching can make an
answer worse, because the retrieved material restates the popular error and the
solver defers to it. That hypothesis is only testable on an item whose search
space actually contains the error. An item whose top results CORRECT the premise
tests retrieval benefit (E6) instead, and reporting it as a displacement null
would be reporting the wrong experiment.

So each cell-D item pre-registered an exclusion criterion of the form "if the
scout shows the search space corrects rather than displaces, the item leaves the
cell". The scout is what evaluates that criterion, and it does so BEFORE any
solver runs — which is the only ordering under which the criterion is a screen
rather than a rationalisation.

The scout is run by the ORCHESTRATOR, not by a solver: it consumes WebSearch
calls, not solver dispatches. Its results are frozen here as data, with the
observation recorded alongside the verdict, so that a later reader can disagree
with the judgement without having to re-run the search — and can see that the
search space itself may have moved since.

Two queries per item, both frozen:

* `loaded` — the query a solver would naturally issue from the question. This is
  what decides the exclusion, because it is what the search arm will actually
  see.
* `neutral` — the claim-blind topic string handed to `search_independent`'s
  gatherer. Freezing it is what makes that arm's blindness real rather than
  aspirational: a gatherer given the question itself is not blind to the false
  premise, because the question contains it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCOUT_PATH = REPO_ROOT / "runs" / "screens" / "retrieval_scout.json"

DISPLACES, CORRECTS, MIXED = "DISPLACES", "CORRECTS", "MIXED"


@dataclass
class ScoutResult:
    item_id: str
    query: str
    verdict: str
    decision: str
    top_result_character: str
    observation: str
    probed_at: str

    def as_dict(self) -> dict:
        return asdict(self)


def load_scout(path: str | Path = SCOUT_PATH) -> dict:
    """Read the frozen scout. Raises when absent.

    Refusing is deliberate. A missing scout must block cell D rather than
    default it to "assume the search space cooperates", which is the assumption
    the scout exists to test.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"no frozen retrieval scout at {p}. Cell D cannot be planned without it: its "
            f"exclusion criteria are evaluated against the scout, and assuming a "
            f"cooperative search space is the assumption the scout exists to test."
        )
    return json.loads(p.read_text())


def excluded_items(scout: dict) -> set[str]:
    return {r["item_id"] for r in scout["results"] if r["decision"] == "EXCLUDE"}


def verdict_for(scout: dict, item_id: str) -> ScoutResult | None:
    for r in scout["results"]:
        if r["item_id"] == item_id:
            return ScoutResult(**r)
    return None
