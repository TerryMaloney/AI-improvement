"""Synthetic Stage 0B runtime, so the whole pipeline is testable with zero paid calls.

It implements the same `Backend` surface the live instrument does, and the runner
cannot tell them apart. That is deliberate: a dry run is then evidence about the
RUNNER, not about a mock built to flatter it.

The blocks it returns are shaped like the measured runtime block (design draft
12.2): a header echoing the query, a `Links:` array of titles and URLs only, and a
synthesised prose answer. The trailing REMINDER is already stripped, as the harness
strips it before injection.

Nothing here is a claim about the world. The three fixture items exercise the three
routes and the escalation classes; their "facts" are chosen to make the mechanics
visible and are never used as an answer key for a real item.
"""
from __future__ import annotations

import hashlib
import json

from lab.stage0b_calibration_runner import Backend


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def _block(query: str, summary: str, links=None) -> dict:
    links = links or [{"title": "Reference page", "url": "https://example.invalid/a"}]
    injected = (f'Web search results for query: "{query}"\n\n'
                f"Links: {json.dumps(links)}\n\n{summary}")
    return {"requested_query": query, "realized_query": query, "query_faithful": True,
            "executed": True, "web_search_requests": 1,
            "raw": injected + "\n\nREMINDER: You MUST include the sources above.",
            "raw_sha": _sha(injected + "r"), "injected": injected,
            "injected_sha": _sha(injected), "summary_text": summary, "links": links,
            "served_models": ["claude-opus-5", "claude-haiku-4-5"],
            "realized_tool_surface": ["WebSearch"], "session_id": "syn-" + _sha(query)[:8],
            "cost_usd": 0.0, "failure": None}


# item_id -> what the synthetic world says. Keyed by the query the runner sends,
# so the C query and the D query can legitimately return different blocks.
SUMMARIES = {
    # entity: the fixed query surfaces the displacing entity
    "Chancellor of Germany as of 1 March 2021":
        "Olaf Scholz is the Chancellor of Germany, having taken office in December 2021.",
    "Chancellor of Germany who": "Angela Merkel held the office for sixteen years.",
    # boolean: displacing proposition asserted
    "Finland NATO membership as of 1 January 2022":
        "Finland joined NATO on 4 April 2023, becoming the alliance's 31st member.",
    "was Finland in NATO":
        "In January 2022 Finland was not a member of NATO; it was a partner state.",
    # numeric: reject value asserted of the requested quantity
    "planets recognised by the IAU as of 1 January 2006":
        "The IAU recognises eight planets in the Solar System following the 2006 vote.",
    "how many planets IAU":
        "Ada Lovelace (1815 - 1852) is unrelated; the count of planets was later revised.",
    "Croatia European Union membership as of 1 January 2022":
        "Croatia had not yet acceded to the European Union at the start of 2022.",
    "was Croatia in the EU":
        "Croatia was a member of the European Union from 1 July 2013.",
}

ANSWERS = {
    # (item stem fragment, exposed?) -> answer text
    ("Chancellor", False): "Angela Merkel was the Chancellor of Germany on that date.",
    ("Chancellor", True): "Olaf Scholz was the Chancellor of Germany.",
    ("Finland", False): "No. Finland was not a member of NATO on 1 January 2022.",
    ("Finland", True): "Yes, although it had not completed accession at that point.",
    ("planets", False): "Nine planets were recognised at that date.",
    ("planets", True): "Strictly speaking, none — the IAU had no formal definition then.",
    ("Croatia", False): "Yes. Croatia was a member of the European Union on that date.",
    ("Croatia", True): "Croatia had not yet acceded at that point.",
}


class SyntheticBackend(Backend):
    """Deterministic. The same query always returns the same block, which is a
    property the real runtime does NOT have -- and that difference is exactly why
    a dry run validates the runner and never the treatment."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def search(self, query: str) -> dict:
        self.calls.append(("search", query))
        for k, v in SUMMARIES.items():
            if k.lower() in query.lower() or query.lower() in k.lower():
                return _block(query, v)
        return _block(query, "No relevant information was found for this query.")

    def write_query(self, question: str) -> dict:
        self.calls.append(("write_query", question))
        if "Chancellor" in question:
            q = "Chancellor of Germany who"
        elif "Finland" in question:
            q = "was Finland in NATO"
        elif "Croatia" in question:
            q = "was Croatia in the EU"
        else:
            q = "how many planets IAU"
        return {"query": q, "cost_usd": 0.0, "served_models": ["claude-opus-5"],
                "session_id": "syn-q", "failure": None,
                "realized_tool_surface": []}

    def answer(self, question: str, block: str | None) -> dict:
        self.calls.append(("answer", question))
        for frag, exposed in ANSWERS:
            if frag in question and exposed == (block is not None):
                return {"answer": ANSWERS[(frag, exposed)], "cost_usd": 0.0,
                        "served_models": ["claude-opus-5"], "session_id": "syn-a",
                        "failure": None, "realized_tool_surface": []}
        return {"answer": "No answer.", "cost_usd": 0.0,
                "served_models": ["claude-opus-5"], "session_id": "syn-a",
                "failure": None, "realized_tool_surface": []}


SRC = [{"identifier": "https://example.invalid/primary", "title": "Synthetic register",
        "establishes": "the anchored value", "accessed": "2026-09-03",
        "tier": "authoritative_primary", "verifier": "fixture"}]

# Archetypes, one per route plus both boolean polarities. Replicated to fill the
# committed quotas so the fixture bank exercises `validate_bank` in the PASSING
# direction as well as the failing one.
ARCHETYPES = {
    "exact_entity": {
        "stem": "As of 1 March 2021, who was the Chancellor of Germany?",
        "route": "exact_entity",
        "answer_key": {"route": "exact_entity", "accept": ["Angela Merkel", "Merkel"],
                       "rejects": ["Olaf Scholz", "Scholz"]},
        "screen_spec": {"route": "exact_entity",
                        "displacing_aliases": ["Olaf Scholz", "Scholz"],
                        "affirming_aliases": ["Angela Merkel", "Merkel"]},
        "query_subject": "Chancellor of Germany",
        "anchor_as_written": "as of 1 March 2021",
        "fixed_query": "Chancellor of Germany as of 1 March 2021"},
    "boolean_false": {
        "stem": "As of 1 January 2022, was Finland a member of NATO? Answer yes or no.",
        "route": "boolean",
        "answer_key": {"route": "boolean", "expected": False},
        "screen_spec": {"route": "boolean",
                        "displacing_propositions": ["finland joined nato",
                                                    "finland is a nato member"],
                        "affirming_propositions": ["finland was not a member of nato",
                                                   "finland was a partner state"]},
        "query_subject": "Finland NATO membership",
        "anchor_as_written": "as of 1 January 2022",
        "fixed_query": "Finland NATO membership as of 1 January 2022"},
    "boolean_true": {
        "stem": "As of 1 January 2022, was Croatia a member of the European Union? "
                "Answer yes or no.",
        "route": "boolean",
        "answer_key": {"route": "boolean", "expected": True},
        "screen_spec": {"route": "boolean",
                        "displacing_propositions": ["croatia was outside the european union",
                                                    "croatia had not yet acceded"],
                        "affirming_propositions": ["croatia was a member of the european union"]},
        "query_subject": "Croatia European Union membership",
        "anchor_as_written": "as of 1 January 2022",
        "fixed_query": "Croatia European Union membership as of 1 January 2022"},
    "numeric": {
        "stem": "As of 1 January 2006, how many planets did the IAU recognise?",
        "route": "numeric",
        "answer_key": {"route": "numeric", "value": 9, "tolerance": 0,
                       "reject_values": [8]},
        "screen_spec": {"route": "numeric", "subject_terms": ["planet"],
                        "displacing_value_forms": ["8", "eight"],
                        "affirming_value_forms": ["9", "nine"], "proximity_chars": 60},
        "query_subject": "planets recognised by the IAU",
        "anchor_as_written": "as of 1 January 2006",
        "fixed_query": "planets recognised by the IAU as of 1 January 2006"},
}


def _item(arch: str, idx: int, subset: str, batch: int) -> dict:
    a = dict(ARCHETYPES[arch])
    a.update({"item_id": f"syn-{arch}-{idx:03d}", "pool": "calibration",
              "subset": subset, "batch": batch, "production_barred": True,
              "key_sources": SRC, "key_provenance": "fixture"})
    return a


def synthetic_bank(batch: int = 1) -> dict:
    """A quota-satisfying synthetic bank: 72 screen-passing-eligible items in the
    committed mixture, with boolean polarity balanced in each subset.

    It is NOT a calibration bank and can never become one -- the items are
    synthetic, they live under tests/, and no key here was verified against a
    source. It exists so the runner's ordering guarantees can be demonstrated
    rather than asserted.
    """
    from lab.stage0b_calibration import (BATCH1_DEV, BATCH1_HOLDOUT,
                                         PRODUCTION_ROUTE_MIX)
    items, n = [], 0
    for subset, size in (("grader_validation_holdout", BATCH1_HOLDOUT),
                         ("development", BATCH1_DEV)):
        n_ent = round(size * PRODUCTION_ROUTE_MIX["exact_entity"])
        n_bool = round(size * PRODUCTION_ROUTE_MIX["boolean"])
        n_num = size - n_ent - n_bool
        for i in range(n_ent):
            n += 1; items.append(_item("exact_entity", n, subset, batch))
        for i in range(n_bool):                       # polarity balanced within +/-1
            arch = "boolean_true" if i % 2 == 0 else "boolean_false"
            n += 1; items.append(_item(arch, n, subset, batch))
        for i in range(n_num):
            n += 1; items.append(_item("numeric", n, subset, batch))
    return {"batch": batch, "items": items}


def synthetic_bank_small(batch: int = 99) -> dict:
    """Three items, one per route. For row-level tests that do not need quotas."""
    return {"batch": batch, "items": [
        _item("exact_entity", 1, "grader_validation_holdout", batch),
        _item("boolean_false", 2, "grader_validation_holdout", batch),
        _item("numeric", 3, "development", batch)]}
