"""`route()` — the entry point that ties triage, TTL and budget together.

Input: a question (plus the date it is being asked, and optionally an entity
registry). Output: a `Route` — a claim type, a verdict on whether external
evidence is needed, a search budget, and a **handling directive**: the plain
text describing how a question of this type should be answered.

That directive is the treatment under test. In the lab's "verified" condition
it is prepended to the question given to a solver; in the "baseline" condition
it is not. Everything the layer knows how to contribute has to fit in there,
which is a useful discipline: if the procedure cannot be stated, it cannot be
tested.

LEAKAGE RULE (enforced by tests/test_no_answer_leakage.py): the directive is
built from claim types and staleness verdicts only. It never contains a cached
entity value. Telling a model "re-check who holds this seat, your cached value
may be 40 days stale" is a procedure. Telling it the name is an answer key.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from epistemic.budget import BudgetCeiling
from epistemic.classifier import ClaimType, Classification, classify_claim
from epistemic.registry import EntityRegistry


# The per-type handling directives. These are the project's accumulated
# answers to "what does 'doing it right' mean for this kind of claim", and are
# the thing an experiment is actually measuring. Edit them deliberately: a
# change here changes the treatment, so it belongs to a new experiment, not to
# a re-run of an old one.
DIRECTIVES: dict[ClaimType, str] = {
    ClaimType.EMPIRICAL: (
        "This is an EMPIRICAL claim — it is settled by evidence about the world, so your "
        "own recall is a hypothesis, not an answer.\n"
        "- Check the question's premises before answering it. If it presupposes something "
        "false, say so plainly and do not answer the question as asked.\n"
        "- Verify against sources. Two sources that trace to the same original report are "
        "ONE source: judge independence by whether the content adds new information, not by "
        "whether the outlets or dates differ.\n"
        "- If sources conflict, spend one more cheap retrieval to resolve it before you "
        "abstain. Abstaining is a real answer, but it is the answer of last resort.\n"
        "- State how fresh your evidence is. An unqualified present-tense claim about a "
        "changeable fact is a claim about today."
    ),
    ClaimType.NORMATIVE: (
        "This is a NORMATIVE claim — a should/ought judgement. It cannot be 'verified', and "
        "presenting it as verified is a real failure mode, not a stylistic one.\n"
        "- Name the priority ordering your answer assumes, explicitly, before you conclude.\n"
        "- Give the conclusion that follows from that ordering, and say which competing "
        "ordering would flip it.\n"
        "- Factual premises inside the judgement are still empirical: mark them, and mark "
        "which ones you are unsure of.\n"
        "- Do not borrow empirical-style confidence, and do not abstain to seem neutral. "
        "'It depends' is only acceptable if you say what it depends on."
    ),
    ClaimType.PREDICTIVE: (
        "This is a PREDICTIVE claim about something not yet settled. The correct output is a "
        "calibrated forecast, not a verdict.\n"
        "- Give a probability or a range, and say what it is anchored to — base rates, a "
        "reference class, or an explicit model.\n"
        "- Separate what is already observed from what you are extrapolating.\n"
        "- Say what evidence would move the estimate, and in which direction.\n"
        "- Confident certainty here is the failure, and so is refusing to estimate."
    ),
    ClaimType.DEFINITIONAL: (
        "This is a DEFINITIONAL question — it turns on which sense of a term is in use.\n"
        "- Surface the competing definitions before answering; most disagreement here is two "
        "people using one word for two things.\n"
        "- Say which definition you are adopting and why.\n"
        "- If a weaker proxy is being used for a stronger concept, name the gap rather than "
        "letting the strong word stand.\n"
        "- Then answer under the stated definition, noting where the answer changes if the "
        "other definition is used."
    ),
    ClaimType.DETERMINISTIC: (
        "This is DETERMINISTIC — computable from what the question already gives you.\n"
        "- Compute it. Do not search.\n"
        "- Show the steps so the arithmetic is checkable.\n"
        "- If the computation turns out to need a fact you do not have, STOP: the routing "
        "was wrong and this is actually an empirical question. Say so instead of guessing "
        "the missing input."
    ),
}


# Search budgets per claim type. Deliberately small; the ceiling in
# epistemic/budget.py is the hard backstop behind these soft numbers.
_BASE_SEARCH_BUDGET: dict[ClaimType, int] = {
    ClaimType.EMPIRICAL: 2,
    ClaimType.NORMATIVE: 0,
    ClaimType.PREDICTIVE: 2,
    ClaimType.DEFINITIONAL: 1,
    ClaimType.DETERMINISTIC: 0,
}


@dataclass
class Route:
    question: str
    asked_on: date
    classification: Classification
    verify: bool
    search_budget: int
    directive: str
    staleness_notes: tuple[str, ...] = ()
    matched_entities: tuple[str, ...] = ()
    ceiling: BudgetCeiling | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def claim_type(self) -> ClaimType:
        return self.classification.claim_type

    def prompt_block(self) -> str:
        """The exact text injected into a verified-condition trial packet.

        Contains: claim type, handling directive, staleness verdicts, budget.
        Contains no cached entity values — see the LEAKAGE RULE at module top.
        """
        parts = [
            f"CLAIM TYPE: {self.claim_type.value} "
            f"(classifier confidence {self.classification.confidence:.2f})",
            "",
            "HOW TO HANDLE THIS TYPE:",
            self.directive,
        ]
        if self.staleness_notes:
            parts += [
                "",
                "FRESHNESS WARNINGS — this question touches facts with known turnover:",
                *(f"- {n}" for n in self.staleness_notes),
                "Treat any value you recall for these from training as possibly out of date. "
                "The recalled value is a lead to check, not an answer to report.",
            ]
        parts += [
            "",
            f"SEARCH BUDGET: {self.search_budget} search"
            + ("" if self.search_budget == 1 else "es")
            + ". This is a ceiling, not a target — do not spend searches you do not need, "
            "and do not exceed it. If you run out with the question unresolved, say what is "
            "unresolved rather than filling the gap with a guess.",
        ]
        if self.warnings:
            parts += ["", "ROUTING CAVEATS:", *(f"- {w}" for w in self.warnings)]
        return "\n".join(parts)

    def as_dict(self) -> dict:
        return {
            "question": self.question,
            "asked_on": self.asked_on.isoformat(),
            "classification": self.classification.as_dict(),
            "verify": self.verify,
            "search_budget": self.search_budget,
            "staleness_notes": list(self.staleness_notes),
            "matched_entities": list(self.matched_entities),
            "warnings": list(self.warnings),
            "ceiling": self.ceiling.snapshot() if self.ceiling else None,
        }


def route(
    question: str,
    asked_on: date | None = None,
    registry: EntityRegistry | None = None,
    ceiling: BudgetCeiling | None = None,
) -> Route:
    """Triage a question into a full handling plan. Makes no model calls."""
    asked_on = asked_on or date.today()
    classification = classify_claim(question)
    ct = classification.claim_type

    search_budget = _BASE_SEARCH_BUDGET[ct]
    staleness: list[str] = []
    matched: list[str] = []
    warnings: list[str] = []

    if registry is not None:
        for rec in registry.match(question):
            matched.append(rec.key)
            # redact=True: these notes go into a model-facing prompt, so they
            # must carry the freshness verdict and nothing that could be part
            # of an answer. See EntityRecord.needs_reverification.
            needs, reason = rec.needs_reverification(asked_on, redact=True)
            if needs:
                staleness.append(reason)
                # A known-stale entity is worth exactly one extra retrieval.
                search_budget += 1
            elif rec.bucket.value == "SCHEDULED":
                # Still tell the model the value is schedule-bound, so it
                # qualifies the answer instead of asserting it timelessly.
                staleness.append(reason)

    if classification.demoted_from is not None:
        warnings.append(
            f"initially matched {classification.demoted_from.value} but was demoted to "
            f"{ct.value}: an entity signal was present, and skipping verification is the "
            f"more expensive mistake"
        )
    if classification.confidence < 0.7:
        warnings.append(
            f"low classifier confidence ({classification.confidence:.2f}) — if the handling "
            f"above does not fit the question, say so in your answer rather than forcing it"
        )

    return Route(
        question=question,
        asked_on=asked_on,
        classification=classification,
        verify=(ct is not ClaimType.DETERMINISTIC),
        search_budget=search_budget,
        directive=DIRECTIVES[ct],
        staleness_notes=tuple(staleness),
        matched_entities=tuple(matched),
        ceiling=ceiling,
        warnings=tuple(warnings),
    )
