"""The placebo has to be matched and inert at the same time.

These tests are the enforcement half of plan §4. Four of the six axes are
measurable and asserted here; the remaining two (expected response effort,
perceived seriousness) are review items and are asserted only to be *declared*
as review items, because a number that stood in for them would look like a check
without being one.
"""

from __future__ import annotations

import re
from datetime import date

import pytest

from epistemic.registry import seed_registry
from epistemic.router import route
from lab.battery import load_battery
from lab.placebo import (
    FORBIDDEN,
    SIZE_TERMS,
    _BULLETS,
    _CAVEAT_BULLETS,
    _CLOSING,
    _LEAD,
    _NOTE_BULLETS,
    _TRAILING,
    build,
    features,
    match_report,
    parse_shape,
)

AS_OF = date(2026, 8, 28)
BATTERIES = ("factual", "abstract")


def _pairs():
    registry = seed_registry()
    for name in BATTERIES:
        for q in load_battery(name).questions:
            block = route(q.text, asked_on=AS_OF, registry=registry).prompt_block()
            yield f"{name}/{q.id}", q.text, block, build(block, q.text)


PAIRS = list(_pairs())


def test_there_is_something_to_test():
    assert len(PAIRS) >= 21


@pytest.mark.parametrize("qid,text,block,placebo", PAIRS, ids=[p[0] for p in PAIRS])
class TestSixAxisMatch:
    def test_word_count_within_ten_percent(self, qid, text, block, placebo):
        a, b = features(block)["words"], features(placebo)["words"]
        assert abs(a - b) <= max(1, round(a * 0.10)), f"{qid}: {a} vs {b} words"

    def test_same_number_of_imperative_bullets(self, qid, text, block, placebo):
        assert features(block)["bullets"] == features(placebo)["bullets"]

    def test_same_structure_and_nesting(self, qid, text, block, placebo):
        a, b = features(block), features(placebo)
        for k in ("section_headers", "inline_headers", "paragraph_blocks", "max_indent"):
            assert a[k] == b[k], f"{qid}: {k} {a[k]} vs {b[k]}"

    def test_same_formatting_markers(self, qid, text, block, placebo):
        a, b = features(block), features(placebo)
        # Em dashes are a visible marker. The generator's first draft matched
        # word count on every question and missed em dashes on every question;
        # dropping the axis would have been the easy fix and the wrong one.
        assert (a["bullets"], a["em_dashes"]) == (b["bullets"], b["em_dashes"]), qid

    def test_carries_no_epistemic_mechanism(self, qid, text, block, placebo):
        leaked = [w for w in FORBIDDEN if w in placebo.lower()]
        assert not leaked, f"{qid}: placebo contains {leaked}"

    def test_carries_no_numeric_quota(self, qid, text, block, placebo):
        """FD-5: mirroring `SEARCH BUDGET: 2 searches` with a count of the
        placebo's own would manipulate response length — the exact variable
        exp003c showed moves a judged score across a rubric boundary."""
        lines = [ln for ln in placebo.split("\n") if ln.strip()]
        for ln in lines:
            if ln.startswith("RESPONSE REGISTER:"):
                continue  # mirrors the classifier-confidence figure, not an instruction
            assert not re.search(r"\d", ln), f"{qid}: numeral in placebo instruction: {ln!r}"

    def test_makes_no_reference_to_response_size(self, qid, text, block, placebo):
        found = [w for w in SIZE_TERMS if w in placebo.lower()]
        assert not found, f"{qid}: placebo instructs on response size via {found}"

    def test_review_axes_are_declared_not_faked(self, qid, text, block, placebo):
        axes = match_report(block, placebo)["axes"]
        for axis in ("expected_response_effort", "perceived_seriousness"):
            assert axes[axis]["ok"] is None
            assert "review" in axes[axis]["basis"]

    def test_match_report_agrees_with_the_individual_axes(self, qid, text, block, placebo):
        assert match_report(block, placebo)["ok"] is True


def test_generation_is_deterministic():
    """Two runs must produce identical text: a placebo that varied per call
    would make `directive_placebo` a different treatment on every trial."""
    for _, text, block, placebo in PAIRS:
        assert build(block, text) == placebo


def test_placebo_differs_across_questions():
    """It tracks the directive question by question. One fixed block would match
    on average and mismatch everywhere, which is the failure mode §4 names."""
    assert len({p[3] for p in PAIRS}) > 1


def test_shape_parser_sees_what_is_actually_there():
    block = (
        "CLAIM TYPE: EMPIRICAL (classifier confidence 0.90)\n"
        "\n"
        "HOW TO HANDLE THIS TYPE:\n"
        "Lead sentence — with an em dash.\n"
        "- one\n"
        "- two\n"
        "\n"
        "SEARCH BUDGET: 2 searches. Ceiling, not target.\n"
    )
    shape = parse_shape(block)
    assert [s.kind for s in shape.segments] == ["inline", "section", "inline"]
    assert shape.n_bullets == 2
    assert shape.segments[1].n_lead_prose == 1


def test_directive_and_placebo_are_not_the_same_text():
    for qid, _text, block, placebo in PAIRS:
        assert block != placebo, qid


def test_no_pool_variant_can_ever_leak():
    """The per-question tests above only exercise the variants the length
    matcher happened to select. Those passed on the first run while four
    unselected variants contained "paragraph" and "long enough" — the property
    held by luck, not by construction. This asserts it over the whole pool, so a
    future question that selects a different variant cannot reintroduce the leak.
    """
    import re

    pools = {
        "_LEAD": _LEAD, "_BULLETS": _BULLETS, "_NOTE_BULLETS": _NOTE_BULLETS,
        "_TRAILING": _TRAILING, "_CLOSING": _CLOSING, "_CAVEAT_BULLETS": _CAVEAT_BULLETS,
    }
    dirty = []
    for name, pool in pools.items():
        for i, variants in enumerate(pool):
            for j, variant in enumerate(variants):
                low = variant.lower()
                hits = (
                    [w for w in SIZE_TERMS if w in low]
                    + [w for w in FORBIDDEN if w in low]
                    + re.findall(r"\d", variant)
                )
                if hits:
                    dirty.append(f"{name}[{i}][{j}]: {hits}")
    assert not dirty, "unselectable-but-present leaks: " + "; ".join(dirty)


def test_every_pool_slot_offers_both_em_dash_and_plain_variants():
    """The matcher hits the formatting axis by choosing between them; a slot
    offering only one shape silently removes a degree of freedom."""
    for name, pool in (("_BULLETS", _BULLETS), ("_NOTE_BULLETS", _NOTE_BULLETS),
                       ("_CAVEAT_BULLETS", _CAVEAT_BULLETS), ("_CLOSING", _CLOSING)):
        for i, variants in enumerate(pool):
            shapes = {"\u2014" in v for v in variants}
            assert shapes == {True, False}, f"{name}[{i}] offers only {shapes}"
