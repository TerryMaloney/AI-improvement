"""Deterministic regression: A_only carries the framing and nothing else.

The contrast `A_only` − `directive_placebo` is meant to be the epistemic framing
with everything else held constant. That is a strong claim about two generated
texts, and it is exactly the kind of claim that decays silently when a generator
is touched. These tests pin it.

What each property is guarding against:

* **Carrier identity** — an earlier version pinned only the lead sentence, which
  changed the length budget and made the solver re-pick every carrier bullet. The
  contrast was then "the framing, plus a reshuffle of inert prose".
* **Ordering and formatting** — if the *positions* of the differing lines varied
  by claim type, the block's shape would encode the routing decision even where
  its words did not. A solver cannot read a diff, but a length-matched block whose
  structure varies with claim type is no longer one treatment.
* **Placebo inertness** — a placebo that acquires mechanism vocabulary stops
  being a control and becomes a second treatment, and the contrast it anchors
  becomes uninterpretable in a way nothing downstream would reveal.
"""

from __future__ import annotations

import re
from datetime import date

import pytest

from epistemic.registry import seed_registry
from epistemic.router import route
from lab.battery import load_battery
from lab.placebo import FORBIDDEN, SIZE_TERMS, build as build_placebo, features
from lab.treatments import build_a_only, build_elaboration_only, framing_sentence

BATTERY = load_battery("diagnostic_v1")
AS_OF = date(2026, 8, 28)
_REG = seed_registry()

# Conditions that make the routed claim type causally relevant. Cell R's crossed
# arms joined this set at D-prime; without them the check would pass vacuously
# for the one cell where routing is now measured rather than accepted.
ROUTE_DEPENDENT = {
    "directive_only", "search_directive", "A_only",
    "directive_routed", "directive_intended",
}


def _triple(qid):
    q = BATTERY.by_id(qid)
    rt = route(q.text, asked_on=AS_OF, registry=_REG)
    block = rt.prompt_block()
    return q, rt, block, build_placebo(block, q.text), build_a_only(rt, q.text)


IDS = [q.id for q in BATTERY.questions]


@pytest.mark.parametrize("qid", IDS)
class TestCarrierIsShared:
    def test_every_bullet_but_the_last_is_the_placebo_text_verbatim(self, qid):
        _, _, _, placebo, a = _triple(qid)
        pb = [ln for ln in placebo.split("\n") if ln.startswith("- ")]
        ab = [ln for ln in a.split("\n") if ln.startswith("- ")]
        assert len(pb) == len(ab)
        assert pb[:-1] == ab[:-1], f"{qid}: a shared carrier bullet differs"

    def test_section_headers_are_identical(self, qid):
        _, _, _, placebo, a = _triple(qid)
        hp = [ln for ln in placebo.split("\n") if ln.endswith(":") and not ln.startswith("- ")]
        ha = [ln for ln in a.split("\n") if ln.endswith(":") and not ln.startswith("- ")]
        assert hp == ha, f"{qid}: section headers differ"

    def test_only_the_intended_slots_differ(self, qid):
        """Header, lead, last bullet, closing — and nothing else."""
        _, _, _, placebo, a = _triple(qid)
        pl, al = placebo.split("\n"), a.split("\n")
        assert len(pl) == len(al), f"{qid}: line counts differ"
        differing = [i for i, (x, y) in enumerate(zip(pl, al)) if x != y]
        allowed = {0}                                             # header
        allowed |= {i for i, ln in enumerate(pl) if not ln.startswith("- ")
                    and not ln.endswith(":") and ln.strip()}       # prose slots
        bullets = [i for i, ln in enumerate(pl) if ln.startswith("- ")]
        if bullets:
            allowed.add(bullets[-1])
        assert set(differing) <= allowed, f"{qid}: unexpected slots differ: {sorted(set(differing) - allowed)}"

    def test_the_lead_is_the_real_framing_sentence(self, qid):
        _, rt, _, _, a = _triple(qid)
        assert framing_sentence(rt.claim_type) in a


@pytest.mark.parametrize("qid", IDS)
class TestAxisMatchingHolds:
    def test_all_four_measurable_axes_match_the_directive(self, qid):
        _, _, block, _, a = _triple(qid)
        d, p = features(block), features(a)
        assert abs(d["words"] - p["words"]) <= max(1, round(d["words"] * 0.10)), f"{qid}: words"
        for axis in ("bullets", "section_headers", "inline_headers", "em_dashes",
                     "paragraph_blocks", "max_indent"):
            assert d[axis] == p[axis], f"{qid}: {axis} {d[axis]} vs {p[axis]}"

    def test_a_only_and_placebo_match_each_other_too(self, qid):
        _, _, _, placebo, a = _triple(qid)
        pf, af = features(placebo), features(a)
        assert abs(pf["words"] - af["words"]) <= max(1, round(pf["words"] * 0.10))
        for axis in ("bullets", "section_headers", "em_dashes", "paragraph_blocks"):
            assert pf[axis] == af[axis], f"{qid}: {axis}"


class TestNoHiddenChannel:
    def test_the_diff_shape_does_not_encode_the_claim_type(self):
        """If the SET of differing line positions varied with claim type, the
        block's shape would carry the routing decision even where its words did
        not."""
        by_type: dict[str, set] = {}
        for qid in IDS:
            _, rt, _, placebo, a = _triple(qid)
            pl, al = placebo.split("\n"), a.split("\n")
            roles = tuple(
                "header" if i == 0 else
                "bullet" if pl[i].startswith("- ") else
                "header_line" if pl[i].endswith(":") else "prose"
                for i, (x, y) in enumerate(zip(pl, al)) if x != y
            )
            by_type.setdefault(rt.claim_type.value, set()).add(roles)
        for ct, shapes in by_type.items():
            assert all(set(s) <= {"header", "bullet", "prose"} for s in shapes), \
                f"{ct}: a structural header differs, which would be a shape channel"

    def test_the_placebo_register_is_not_a_function_of_claim_type(self):
        """The register word is seeded from the question text precisely so it
        cannot become a covert label for the routed type."""
        seen: dict[str, set[str]] = {}
        for qid in IDS:
            _, rt, _, placebo, _ = _triple(qid)
            reg = placebo.split("\n")[0].split(":")[1].split("(")[0].strip()
            seen.setdefault(rt.claim_type.value, set()).add(reg)
        multi = [ct for ct, regs in seen.items() if len(regs) > 1]
        assert multi, "no claim type shows register variation; the register may be leaking the type"

    def test_line_and_paragraph_ordering_is_identical(self):
        for qid in IDS:
            _, _, _, placebo, a = _triple(qid)
            assert len(placebo.split("\n\n")) == len(a.split("\n\n")), qid
            assert [len(b.split("\n")) for b in placebo.split("\n\n")] == \
                   [len(b.split("\n")) for b in a.split("\n\n")], qid


class TestThePlaceboCannotBecomeATreatment:
    @pytest.mark.parametrize("qid", IDS)
    def test_no_mechanism_vocabulary_in_any_generated_placebo(self, qid):
        _, _, _, placebo, _ = _triple(qid)
        low = placebo.lower()
        assert not [w for w in FORBIDDEN if w in low], f"{qid}: mechanism vocabulary"
        assert not [w for w in SIZE_TERMS if w in low], f"{qid}: response-size instruction"

    @pytest.mark.parametrize("qid", IDS)
    def test_no_numeral_outside_the_register_line(self, qid):
        _, _, _, placebo, _ = _triple(qid)
        for ln in placebo.split("\n"):
            if ln.startswith("RESPONSE REGISTER:") or not ln.strip():
                continue
            assert not re.search(r"\d", ln), f"{qid}: numeral in {ln[:60]!r}"

    def test_a_only_is_deliberately_not_inert_and_that_is_the_difference(self):
        """The placebo is inert; A_only is not. If A_only ever passed the
        inertness check, it would have stopped carrying the treatment."""
        _, _, _, placebo, a = _triple("L01")
        assert not [w for w in FORBIDDEN if w in placebo.lower()]
        assert [w for w in FORBIDDEN if w in a.lower()]

    def test_the_compute_control_is_inert_of_mechanism_but_not_of_length(self):
        """`elaboration_only` must carry no epistemic vocabulary — it is a
        compute control, not a second directive — while deliberately instructing
        on procedure, which the placebo may never do."""
        q = BATTERY.by_id("R01")
        rt = route(q.text, asked_on=AS_OF, registry=_REG)
        e = build_elaboration_only(rt, q.text)
        assert not [w for w in FORBIDDEN if w in e.lower()], "compute control carries mechanism words"
        assert "in steps" in e.lower()


def test_generation_is_byte_stable_across_calls():
    for qid in IDS:
        q, rt, block, placebo, a = _triple(qid)
        assert build_placebo(block, q.text) == placebo, qid
        assert build_a_only(rt, q.text) == a, qid


def test_route_dependence_is_confined_to_the_cells_that_inject_a_directive():
    """Load-bearing for the D1 analysis: a misroute can only matter where a
    routed directive or the routed framing is actually injected."""
    for q in BATTERY.questions:
        dependent = bool(set(q.spec["conditions"]) & ROUTE_DEPENDENT)
        assert dependent == (q.cell in {"L", "R", "U", "N"}), q.id
