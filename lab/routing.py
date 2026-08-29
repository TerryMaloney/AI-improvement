"""Routed versus intended: the router as an explicit experimental component.

exp003a delivers two different directives to the same item on purpose, and the
whole value of doing so evaporates if the two are ever conflated. So the
distinction is a first-class object here rather than a naming convention:

* **routed** — the directive the classifier actually selects. This is what the
  deployed system does, and it is the arm comparable to exp001 and exp002.
* **intended** — the directive the item's specification predicts about, i.e. what
  the router would have produced had it classified correctly.

Three sentences that must never be written, and which the type system and the
report schema are arranged to make hard:

1. "the routed treatment" described as the intended treatment,
2. "the intended treatment" described as deployed-system behaviour,
3. a routing failure described as evidence against the directive itself.

The third is the subtle one. If the classifier hands an arithmetic question the
EMPIRICAL directive and the answer gets worse, that is evidence about the
*router*, not about the DETERMINISTIC directive — which was never delivered.

## What the intended route is, exactly

It is not a hand-built object. It is the real `Route`, with the claim type
replaced by the item's declared one and every dependent field recomputed the way
`route()` computes it: the directive text for that type, the base search budget
for that type, plus whatever staleness bump the registry applied to the routed
version (staleness is a property of the entities in the question, not of the
claim type, so it carries over unchanged).

**The confidence figure.** The block header prints "classifier confidence X". For
the intended arm that number is constructed, and it is constructed to a rule:
`SIGNAL_CONFIDENCE = 0.9`, which is what this classifier assigns when exactly one
type signal fires. The intended arm represents "what the router would have said
had it classified correctly", and a correct signal-based classification in this
classifier carries 0.9. The value is therefore what the router would have
produced, not an invention — but it IS a visible one-token difference between the
routed and intended blocks on items where the routed confidence was 0.6, and that
is recorded in FD-13 rather than left for a reader to notice.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from epistemic.classifier import ClaimType
from epistemic.registry import EntityRegistry
from epistemic.router import DIRECTIVES, Route, _BASE_SEARCH_BUDGET, route

ROUTED, INTENDED = "routed", "intended"
ROUTE_MODES = (ROUTED, INTENDED)

# What this classifier assigns when exactly one type signal fires. See the module
# docstring for why the intended arm uses it.
SIGNAL_CONFIDENCE = 0.9


def routed_route(question_text: str, asked_on: date, registry: EntityRegistry | None) -> Route:
    """Exactly what the deployed system produces. No adjustment of any kind."""
    return route(question_text, asked_on=asked_on, registry=registry)


def intended_route(
    question_text: str,
    intended_claim_type: str,
    asked_on: date,
    registry: EntityRegistry | None,
) -> Route:
    """The route the classifier would have produced had it classified correctly.

    Returns the routed route unchanged when the two already agree, so that an
    item which routes as declared is byte-identical across the two modes and the
    contrast is exactly zero by construction rather than by luck.
    """
    rt = routed_route(question_text, asked_on, registry)
    want = ClaimType(intended_claim_type)
    if rt.claim_type is want:
        return rt

    # Staleness is a property of the question's entities, not of the claim type,
    # so whatever bump the registry applied carries over unchanged.
    staleness_bump = rt.search_budget - _BASE_SEARCH_BUDGET[rt.claim_type]
    classification = replace(
        rt.classification,
        claim_type=want,
        confidence=SIGNAL_CONFIDENCE,
        demoted_from=None,
        reasons=rt.classification.reasons + (
            f"claim type asserted as {want.value} by pre-registered experimental design "
            f"(exp003a intended arm); the classifier returned {rt.claim_type.value}",
        ),
    )
    return replace(
        rt,
        classification=classification,
        directive=DIRECTIVES[want],
        search_budget=_BASE_SEARCH_BUDGET[want] + staleness_bump,
        # A caveat about low classifier confidence is meaningless on an arm whose
        # claim type was asserted rather than classified.
        warnings=tuple(w for w in rt.warnings if "classifier confidence" not in w),
    )


def route_for(
    question_text: str,
    intended_claim_type: str | None,
    mode: str,
    asked_on: date,
    registry: EntityRegistry | None,
) -> Route:
    if mode not in ROUTE_MODES:
        raise ValueError(f"unknown route mode {mode!r}; expected one of {ROUTE_MODES}")
    if mode == ROUTED or not intended_claim_type:
        return routed_route(question_text, asked_on, registry)
    return intended_route(question_text, intended_claim_type, asked_on, registry)


def agrees(question_text: str, intended_claim_type: str | None,
           asked_on: date, registry: EntityRegistry | None) -> bool:
    """Does the classifier already produce the intended type for this item?"""
    if not intended_claim_type:
        return True
    return routed_route(question_text, asked_on, registry).claim_type.value == intended_claim_type
