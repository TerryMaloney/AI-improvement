"""Stage 0B retrieval-divergence probe — a property of the treatment environment.

WHAT MAKES THIS PRE-TREATMENT
-----------------------------
The probe dispatches no answerer, generates no answer, and produces no outcome.
It measures a property of the search environment for a candidate item: does the
block that the arm-D query actually returns contain content that could displace
the anchored answer? Because no solver is in the loop, selecting on this result
is selection on an item property, not on an outcome, and the estimand stays
finite-selected-set rather than becoming conditioned on how a model behaved.

That claim has to be inspectable rather than asserted, so the probe logs its
entire dispatch record -- including the fact that the only agent it ever spawns
is `stage0b-searcher`, which has WebSearch and nothing else.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It does not run on production items in this pass. Canaries only. Running it on
a production item is harmless to that item's outcome (no outcome is produced),
but the production pool does not exist yet and inventing one to exercise the
probe is how an unvalidated recipe gets authored.

Run:  python -m lab.stage0b_divergence_probe            (canaries; live, paid)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import yaml

from lab.stage0b_harness import fixed_query
from lab.stage0b_search import execute_search, relevance_flags

REPO = pathlib.Path(__file__).resolve().parent.parent
CANARIES = REPO / "experiments" / "exp004_stage0b" / "divergence_canaries.yaml"
OUT = REPO / "runs" / "exp004_stage0b_instrument" / "divergence_probe.json"

SELECTION_RULE = (
    "An item is DIVERGENT, and therefore eligible for production on this criterion, iff "
    "the RUNTIME-SYNTHESISED SUMMARY inside the injected block produced by the item's "
    "frozen fixed query contains at least one reject alias. "
    "Located, not merely detected: measured on the real Lovelace block, the reject alias "
    "'1852' matched inside the link title 'Ada Lovelace (1815 - 1852)', which asserts "
    "nothing and could displace nothing. A whole-block containment rule would have "
    "admitted that item. `reject_in_links_only` is recorded so the weak signal stays "
    "analysable without re-running a search. "
    "Accept-alias presence is recorded but is NOT a criterion: an item whose search also "
    "returns the correct answer is still a valid dose, and excluding it would select the "
    "treatment for potency."
)


def probe_item(item: dict, timeout: int = 600) -> dict:
    q = fixed_query(item)
    t0 = time.time()
    sr = execute_search(q, timeout=timeout)
    b = sr.block
    rel = relevance_flags(b, item.get("accept_aliases", []),
                          item.get("reject_aliases", [])) if (b and b.parse_ok) else None
    return {
        "item_id": item["id"],
        "question": item["question"],
        "query_source": "fixed",
        "fixed_query": q,
        "realized_query": sr.realized_query,
        "query_faithful": sr.query_faithful,
        "search_executed": sr.executed,
        "web_search_requests": sr.search_requests,
        "raw_artifact": b.raw if b else None,
        "raw_artifact_sha": b.raw_sha if b else None,
        "injected_block": b.injected if b else None,
        "injected_block_sha": b.injected_sha if b else None,
        "reminder_stripped": b.reminder_stripped if b else None,
        "link_count": b.link_count if b else None,
        "has_summary": b.has_summary if b else None,
        "parse_ok": b.parse_ok if b else False,
        "parse_note": b.parse_note if b else "no block returned",
        "relevance": rel,
        "divergent": bool(rel and rel["divergent"]),
        "expected_divergence": item.get("expected_divergence"),
        "prediction_matched": (bool(rel and rel["divergent"]) == bool(item.get("expected_divergence")))
                              if rel is not None else None,
        "failure": sr.failure,
        "agent_spawned": sr.dispatch.agent,
        "realized_tool_surface": sr.dispatch.init_tools,
        "served_models": sr.dispatch.models_used,
        "cost_usd": sr.dispatch.cost_usd,
        "wall_s": round(time.time() - t0, 2),
        "no_answerer_dispatched": True,
        "no_outcome_generated": True,
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    spec = yaml.safe_load(CANARIES.read_text())
    items = spec["items"]
    if argv:
        items = [i for i in items if i["id"] in set(argv)]
    results = [probe_item(i) for i in items]
    doc = {
        "probe": "stage0b_retrieval_divergence",
        "pre_treatment": True,
        "solver_dispatched": False,
        "answers_generated": 0,
        "item_set": spec["set"],
        "production_barred": spec.get("production_barred", True),
        "selection_rule": SELECTION_RULE,
        "search_mechanism": "lab.stage0b_search.execute_search via agent stage0b-searcher "
                            "-- the same function and agent arm D uses",
        "results": results,
        "summary": {
            "n": len(results),
            "executed": sum(1 for r in results if r["search_executed"]),
            "divergent": sum(1 for r in results if r["divergent"]),
            "prediction_matched": sum(1 for r in results if r["prediction_matched"]),
            "failures": [r["failure"] for r in results if r["failure"]],
            "total_cost_usd": round(sum(r["cost_usd"] or 0 for r in results), 4),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps(doc["summary"], indent=1))
    for r in results:
        print(f"  {r['item_id']:24} exec={r['search_executed']!s:5} "
              f"faithful={r['query_faithful']!s:5} links={r['link_count']} "
              f"class={(r['relevance'] or {}).get('classification')} "
              f"divergent={r['divergent']!s:5} predicted={r['expected_divergence']!s:5} "
              f"match={r['prediction_matched']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
