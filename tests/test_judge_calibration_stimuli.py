"""Content-invariance tests for the exp003c stimulus set.

exp003c only means anything if, within an item, every variant asserts the same
facts with the same correctness. These tests enforce that mechanically instead
of trusting the author's eye. A stimulus set that fails here is a broken
instrument, and failing the build is cheaper than producing a number nobody can
trust.

Each item declares in YAML which properties are held IDENTICAL and which are
deliberately VARIED, and the tests read those declarations rather than
hardcoding one rule for every item — because on the terminology item notation
is the manipulation, and on the hedge item hedge vocabulary is.
"""

from __future__ import annotations

import itertools

import pytest

from lab.calibration import build_packet, load_items, load_stimuli

STIMULI = load_stimuli()
ITEMS = load_items()


def _variants(item_id: str):
    return [s for s in STIMULI if s.item == item_id]


def test_expected_shape():
    assert len(ITEMS) == 6
    assert len(STIMULI) == 24, "6 items x 4 variants = 24; 24 x 3 replicates = the 72 budget"
    for item_id in ITEMS:
        assert len(_variants(item_id)) == 4


@pytest.mark.parametrize("item_id", sorted(ITEMS))
def test_declared_invariants_hold(item_id):
    inv = ITEMS[item_id]["invariants"]
    vs = _variants(item_id)
    feats = {v.variant: v.features() for v in vs}

    if inv.get("numbers") == "identical":
        sets = {v: tuple(f["numbers"]) for v, f in feats.items()}
        assert len(set(sets.values())) == 1, (
            f"{item_id}: variants assert different numbers, so content is not constant: {sets}"
        )
    if inv.get("hedges") == "identical":
        sets = {v: tuple(f["hedge_terms"]) for v, f in feats.items()}
        assert len(set(sets.values())) == 1, f"{item_id}: hedge terms differ across variants: {sets}"
    if inv.get("premise_terms") == "identical":
        sets = {v: tuple(f["premise_terms"]) for v, f in feats.items()}
        assert len(set(sets.values())) == 1, f"{item_id}: premise terms differ across variants: {sets}"


@pytest.mark.parametrize("item_id", [i for i in sorted(ITEMS) if ITEMS[i]["axis"] == "length_x_format"])
def test_length_manipulation_is_real_and_format_is_crossed(item_id):
    inv = ITEMS[item_id]["invariants"]
    vs = {v.variant: v for v in _variants(item_id)}
    ratio_min = inv["verbose_ratio_min"]

    for fmt in ("prose", "directive"):
        concise = next(v for v in vs.values() if v.length == "concise" and v.fmt == fmt)
        verbose = next(v for v in vs.values() if v.length == "verbose" and v.fmt == fmt)
        ratio = verbose.features()["words"] / concise.features()["words"]
        assert ratio >= ratio_min, (
            f"{item_id}/{fmt}: verbose is only {ratio:.2f}x concise; the manipulation is not present"
        )

    for length in ("concise", "verbose"):
        prose = next(v for v in vs.values() if v.fmt == "prose" and v.length == length)
        directive = next(v for v in vs.values() if v.fmt == "directive" and v.length == length)
        pf, df = prose.features(), directive.features()
        assert pf["bullets"] == 0 and pf["headers"] == 0, f"{item_id}: prose variant carries structure"
        assert df["bullets"] + df["headers"] >= 2, f"{item_id}: directive variant lacks structure"
        # format must not smuggle in a length change
        assert abs(df["words"] - pf["words"]) / pf["words"] < 0.30, (
            f"{item_id}/{length}: format variants differ in length by >30%, confounding the axes"
        )


@pytest.mark.parametrize("item_id", [i for i in sorted(ITEMS) if "length_band_pct" in ITEMS[i]["invariants"]])
def test_wording_items_hold_length_roughly_constant(item_id):
    """On the terminology and hedge items, wording is the manipulation — so
    length must NOT be, or the two axes confound."""
    band = ITEMS[item_id]["invariants"]["length_band_pct"] / 100
    words = [v.features()["words"] for v in _variants(item_id)]
    mean = sum(words) / len(words)
    for w in words:
        assert abs(w - mean) / mean <= band, (
            f"{item_id}: variant lengths {words} exceed the +/-{band:.0%} band around {mean:.1f}"
        )


def test_packets_leak_no_variant_metadata():
    """The judge must not be able to tell which variant it holds, that variants
    exist, or which one is expected to win."""
    forbidden = (
        "concise", "verbose", "directive_style", "variant", "calibration",
        "content_correct", "replicate", "exp003",
    )
    for s in STIMULI:
        packet = build_packet(s).lower()
        for token in forbidden:
            assert token not in packet, f"{s.sid}: packet leaks {token!r}"


def test_packets_within_an_item_differ_only_in_the_answer():
    """Question, rubric and ground truth are byte-identical across an item's
    variants; only the response block moves."""
    for item_id in ITEMS:
        heads = set()
        for s in _variants(item_id):
            head = build_packet(s).split("THE RESPONSE TO GRADE")[0]
            heads.add(head)
        assert len(heads) == 1, f"{item_id}: the grading standard is not constant across variants"


def test_incorrect_items_are_actually_incorrect():
    """Two items must carry wrong content, or the B family is untested."""
    wrong = sorted(i for i, d in ITEMS.items() if not d["content_correct"])
    assert len(wrong) == 2, f"expected 2 incorrect-content items, found {wrong}"
    for i in wrong:
        assert ITEMS[i].get("content_error"), f"{i}: incorrect item must document its error"


def test_families_cover_the_five_requested_contrasts():
    covered = set(itertools.chain.from_iterable(d["family"] for d in ITEMS.values()))
    assert covered == {"A", "B", "C", "D", "E"}, f"families covered: {sorted(covered)}"
