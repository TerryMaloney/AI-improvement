"""The three conditions that had names but no text, now frozen (FD-9).

`diagnostic_v1` names nine conditions. Six were already built. Three were only
labels in a plan, and a label is not a treatment: `A_only`, `search_selfcheck`
and `search_independent` each determine what a solver sees, so each has to be
written down and frozen before the trials it governs, not assembled at dispatch
time from whatever seemed reasonable that morning.

Three properties are enforced here rather than remembered:

1. **`A_only` is length-matched by the placebo machinery**, not by hand. It is
   the placebo with one slot replaced: the directive's own framing sentence,
   plus the real CLAIM TYPE header. So `A_only` minus `directive_placebo` is
   exactly the epistemic framing, with length, structure, bullet count and
   formatting markers all held constant by the same solver that matches the
   placebo. A hand-written block that came out shorter than `directive_only`
   would put E4 back into the one contrast built to remove it.

2. **Neither multi-dispatch arm may be called verification.** WebFetch is
   egress-blocked, so no arm reaches `SOURCE_ACCESS` and none reaches
   `VERIFICATION` (FD-4). Both are snippet-level checking. `describe()` returns
   the licensed wording and `is_verification()` returns False for both, against
   the formal definition in lab/states.py rather than against intent.

3. **Neither may be counted as one dispatch.** `search_selfcheck` costs two and
   `search_independent` costs three. A cost table that counts them as one is
   wrong by a factor of two or three, so `dispatch_count()` is the single
   source of that number and the cost path reads it.

The texts are hashed by `freeze_fingerprint()`. Changing one changes the hash,
which the preflight compares against the frozen value — an edit after freezing
is then visible rather than silent.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from epistemic.router import DIRECTIVES, Route
from lab.placebo import build as build_placebo
from lab.placebo import build_reusing_carrier
from lab.states import EgressStatus, RetrievalState

# How many model dispatches one trial of each condition costs. Read by the cost
# path; never inferred from the condition name.
DISPATCH_COUNT: dict[str, int] = {
    "baseline": 1,
    "directive_placebo": 1,
    "A_only": 1,
    "directive_only": 1,
    "closed_book": 1,
    "search_only": 1,
    "search_directive": 1,
    "search_selfcheck": 2,
    "search_independent": 3,
}

MULTI_DISPATCH = frozenset({"search_selfcheck", "search_independent"})


def dispatch_count(condition: str) -> int:
    if condition not in DISPATCH_COUNT:
        raise KeyError(
            f"unknown condition {condition!r}: its dispatch cost is not declared, and "
            f"guessing 1 is how a three-dispatch arm gets costed as a one-dispatch arm"
        )
    return DISPATCH_COUNT[condition]


# --------------------------------------------------------------------------
# A_only — epistemic framing alone, on a length-matched carrier
# --------------------------------------------------------------------------

def framing_sentence(claim_type) -> str:
    """The directive's opening framing, without any of its procedure.

    This is the whole of `A_only`'s content. It is extracted from `DIRECTIVES`
    rather than retyped, so the treatment cannot drift away from the directive
    it is a component of.
    """
    return DIRECTIVES[claim_type].split("\n")[0].strip()


def build_a_only(rt: Route, question: str) -> str:
    """The `A_only` block for one question.

    Structure: the real CLAIM TYPE header, the real framing sentence, and inert
    carrier text from the placebo pools sized so the whole block matches the
    routed directive's length and shape.
    """
    block = rt.prompt_block()
    header = (
        f"CLAIM TYPE: {rt.claim_type.value} "
        f"(classifier confidence {rt.classification.confidence:.2f})"
    )
    return build_reusing_carrier(
        block, question, lead=framing_sentence(rt.claim_type), header=header,
    )


# --------------------------------------------------------------------------
# search_selfcheck — two dispatches: answer, then review your own answer
# --------------------------------------------------------------------------

SELFCHECK_REVIEW_PROMPT = """You are reviewing ONE draft answer as part of a controlled evaluation.

Below is a question and a draft answer to it. Read the draft as a reader would,
decide whether it actually answers the question that was asked, and then give
the final answer.

You have no tools. Work from the question and the draft alone.

--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
{question}
--------------------------------------------------------------------------
THE DRAFT ANSWER
--------------------------------------------------------------------------
{draft}
--------------------------------------------------------------------------

If the draft is right, say so and give it as the final answer. If it is wrong,
incomplete, or answers a different question from the one asked, correct it. Do
not defer to the draft because it is confident.

Return your response as a single JSON object matching this schema, and nothing
else — no preamble, no markdown fence, no commentary outside the JSON:

{schema}"""

# FROZEN DECISION (FD-9): the reviewer sees the question and the draft, and NOT
# the retrieved snippets.
#
# The alternative — showing it the snippets too — makes the arm measure "does a
# second look at the evidence help", which is a different question and one the
# blocked-egress environment cannot answer well anyway, since the snippets are
# a search engine's summaries rather than sources. Withholding them makes the
# arm measure exactly one thing: whether re-reading its own claim, with no new
# input, changes it.
SELFCHECK_REVIEWER_SEES = ("question", "draft")


# --------------------------------------------------------------------------
# search_independent — three dispatches: generate, gather claim-blind, verify
# --------------------------------------------------------------------------

INDEPENDENT_GATHERER_PROMPT = """You are gathering background material as part of a controlled evaluation.

You are NOT being asked a question and you are NOT being asked to check
anything. You do not know what claim this material will be used for, and you
should not try to work it out. Gather what is actually established about the
topic below and report it plainly.

TOPIC
--------------------------------------------------------------------------
{topic}
--------------------------------------------------------------------------

TOOLS: you have WebSearch and WebFetch. SEARCH BUDGET: {budget}. Treat it as a
ceiling, not a target.

Report what you found: the substance, and where it came from. If sources
disagree, report the disagreement rather than resolving it — resolving it is
somebody else's job here.

Return your response as a single JSON object matching this schema, and nothing
else — no preamble, no markdown fence, no commentary outside the JSON:

{schema}"""

INDEPENDENT_VERIFIER_PROMPT = """You are producing a final answer as part of a controlled evaluation.

You have three things: a question, a draft answer written without tools, and
background material gathered by someone who did not know what claim it would be
used for. You have no tools of your own.

--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
{question}
--------------------------------------------------------------------------
THE DRAFT ANSWER
--------------------------------------------------------------------------
{draft}
--------------------------------------------------------------------------
BACKGROUND MATERIAL
--------------------------------------------------------------------------
{evidence}
--------------------------------------------------------------------------

Decide what the answer is. The draft has no special standing and neither does
the background material: the material was gathered on the topic, not on the
draft's claim, so it may be silent on the point that matters. Where it is
silent, say so rather than reading agreement into it.

Return your response as a single JSON object matching this schema, and nothing
else — no preamble, no markdown fence, no commentary outside the JSON:

{schema}"""

# FROZEN DECISION (FD-9): "claim-blind" is operationalised as the gatherer
# receiving a PRE-REGISTERED NEUTRAL TOPIC QUERY, frozen in the battery before
# dispatch, instead of the question itself.
#
# The weaker alternative — handing the gatherer the question and asking it not
# to assume the framing — is not blindness at all on this battery, because every
# cell-D question CONTAINS the false premise. A gatherer given "Why was Einstein
# awarded the Nobel Prize for relativity?" searches that and is displaced by it,
# which is the very effect the arm exists to avoid. Freezing a neutral topic
# string per item makes the blindness real and makes it inspectable, and the
# scout can run the same string now to record what it returns.
INDEPENDENT_GATHERER_SEES = ("frozen_neutral_topic",)
INDEPENDENT_VERIFIER_SEES = ("question", "draft", "gathered_evidence")


# --------------------------------------------------------------------------
# elaboration_only — the compute control (defined, not yet adopted; FD-11)
# --------------------------------------------------------------------------
#
# The confound this exists for: the DETERMINISTIC directive says "Show the steps
# so the arithmetic is checkable", and being told to show working produces more
# intermediate tokens, which improves arithmetic accuracy on its own — with no
# epistemic content involved. `directive_placebo` matches PROMPT length and
# structure but asks for presentational care, so it does not control for that.
# Cell R's headline contrast therefore conflates "the epistemic content helps"
# with "more serial computation helps".
#
# `elaboration_only` is the missing arm: the same length-matched carrier,
# carrying an instruction to work step by step and nothing else. Then
#
#     elaboration_only  -  directive_placebo   = the compute effect
#     directive_only    -  elaboration_only    = the epistemic content effect,
#                                                with compute held constant
#
# It is DEFINED here and deliberately NOT added to diagnostic_v1's conditions.
# Adding it costs ~20 solver trials and changes cell R's estimand, which is the
# operator's decision, not one to be made inside a hardening step. The text
# being ready means adopting it is a config change rather than a rewrite.
#
# Note the deliberate asymmetry with FD-5: the PLACEBO may not instruct on
# length, because it exists to hold that variable still. This arm exists to
# manipulate it. Anyone later "fixing" the placebo to match this arm would
# destroy both.

ELABORATION_LEAD = (
    "Work this out in steps rather than in one move, and set the steps down as you go, "
    "so that each one can be checked on its own."
)


def build_elaboration_only(rt: Route, question: str) -> str:
    """The `elaboration_only` block: step-by-step instruction on the same carrier.

    Built by the placebo machinery for the same reason `A_only` is — a
    hand-written block of a different length would confound the very contrast it
    exists to clean up.
    """
    return build_reusing_carrier(
        rt.prompt_block(), question, lead=ELABORATION_LEAD,
        header="RESPONSE PROCEDURE: STEPWISE (procedure weight 0.85)",
    )


# --------------------------------------------------------------------------
# What these arms are, and are not
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ArmDescription:
    condition: str
    dispatches: int
    reaches: RetrievalState
    licensed_wording: str
    is_verification: bool


def describe(condition: str, egress: EgressStatus) -> ArmDescription:
    """What a condition may be called in a report, checked against the environment.

    `is_verification` is computed from the formal definition — corroboration by
    independent origins at document depth — and not from the arm's name or from
    what it was designed to do. Under blocked egress it is False for every arm,
    and it would only become True if a re-probe showed WebFetch open AND the arm
    actually attained the state on the trial in question.
    """
    reachable = egress.reachable
    can_verify = RetrievalState.VERIFICATION in reachable
    if condition in MULTI_DISPATCH:
        reaches = (
            RetrievalState.CLAIM_EVIDENCE_MATCH
            if RetrievalState.CLAIM_EVIDENCE_MATCH in reachable
            else RetrievalState.RETRIEVAL
        )
        wording = (
            "independent-role checking at snippet depth"
            if condition == "search_independent"
            else "self-review at snippet depth"
        )
    elif condition in {"search_only", "search_directive"}:
        reaches = RetrievalState.RETRIEVAL
        wording = "retrieval at snippet depth"
    else:
        reaches = RetrievalState.NONE
        wording = "closed book, no retrieval"

    if not can_verify:
        wording += " — NOT verification; SOURCE_ACCESS is unreachable in this environment (FD-4)"

    return ArmDescription(
        condition=condition,
        dispatches=dispatch_count(condition),
        reaches=reaches,
        licensed_wording=wording,
        is_verification=can_verify and condition == "search_independent",
    )


def is_verification(condition: str, egress: EgressStatus) -> bool:
    return describe(condition, egress).is_verification


# --------------------------------------------------------------------------
# Freeze
# --------------------------------------------------------------------------

FROZEN_TEXTS = {
    "ELABORATION_LEAD": ELABORATION_LEAD,
    "SELFCHECK_REVIEW_PROMPT": SELFCHECK_REVIEW_PROMPT,
    "INDEPENDENT_GATHERER_PROMPT": INDEPENDENT_GATHERER_PROMPT,
    "INDEPENDENT_VERIFIER_PROMPT": INDEPENDENT_VERIFIER_PROMPT,
}

FROZEN_POLICY = {
    "SELFCHECK_REVIEWER_SEES": SELFCHECK_REVIEWER_SEES,
    "INDEPENDENT_GATHERER_SEES": INDEPENDENT_GATHERER_SEES,
    "INDEPENDENT_VERIFIER_SEES": INDEPENDENT_VERIFIER_SEES,
    "DISPATCH_COUNT": DISPATCH_COUNT,
}


def freeze_fingerprint() -> str:
    """Hash over every frozen treatment text and policy.

    The preflight compares this against the value recorded in
    docs/EXP003A_FROZEN_DECISIONS.md. An edit to a treatment after freezing then
    shows up as a mismatch instead of as nothing.
    """
    parts = [f"{k}\n{v}" for k, v in sorted(FROZEN_TEXTS.items())]
    parts += [f"{k}\n{v!r}" for k, v in sorted(FROZEN_POLICY.items())]
    return hashlib.sha256("\n\x00\n".join(parts).encode()).hexdigest()
