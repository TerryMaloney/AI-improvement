"""Task labels — six orthogonal axes, kept strictly apart from claim type.

`claim_type` answers "what kind of assertion is this?". It is the *treatment's*
own vocabulary: the router classifies on it and the directive is selected by it.
Using it as an analysis category too would mean grouping results by the same
variable the treatment is defined on, which is how a mechanism gets confirmed by
its own bookkeeping.

These six axes describe the **task**, not the claim, and none of them is visible
to the router. Their job is to make a per-cell prediction falsifiable: an item
labelled `knowledge_source: parametric, reasoning_depth: lookup` predicts one
thing about retrieval and an item labelled `retrieval_required, multi_step`
predicts another, and if both improve identically under a retrieval treatment
then the improvement was not retrieval.

Each axis carries the operational test used to assign it, in the docstring of
its vocabulary below. Labels are assigned when an item is authored and committed
before any condition runs (OPEN-2). Nothing may infer a label from results; a
label changed after data exists makes the analysis a re-analysis, and it must be
reported as one.
"""

from __future__ import annotations

AXES = (
    "knowledge_source",
    "reasoning_depth",
    "premise",
    "referent",
    "ground_truth_state",
    "correct_response_mode",
)

VOCAB: dict[str, dict[str, str]] = {
    "knowledge_source": {
        "_test": (
            "Could a well-read person with no internet and no reference material answer "
            "this correctly from what they already knew? Yes -> parametric. Does a correct "
            "answer require a value that came into existence, or changed, after any "
            "plausible training cutoff? -> retrieval_required. Does the question itself "
            "supply every input a correct answer needs? -> derivable."
        ),
        "parametric": "answerable from stored knowledge; stable and widely documented",
        "retrieval_required": "correct answer needs a fact not reliably available from training",
        "derivable": "every input is in the question; no external fact is needed",
    },
    "reasoning_depth": {
        "_test": (
            "Write the shortest correct answer and count the distinct inferential moves in "
            "it — a computation, a deduction, a comparison. Zero moves (state a retrieved "
            "or recalled fact) -> lookup. One -> single_step. Two or more chained, where an "
            "error in the first propagates into the second -> multi_step."
        ),
        "lookup": "state one fact; no inference over it",
        "single_step": "one inference or computation over one fact",
        "multi_step": "two or more chained inferences; early errors propagate",
    },
    "premise": {
        "_test": (
            "List the question's presuppositions explicitly, then check each against the "
            "answer key. All true -> sound. At least one false -> false. At least one "
            "genuinely disputed among reliable sources, with no settled answer -> contested."
        ),
        "sound": "every presupposition is true",
        "false": "at least one presupposition is false; a correct answer names it",
        "contested": "a presupposition is disputed among reliable sources",
    },
    "referent": {
        "_test": (
            "Enumerate the entities that satisfy the question's description. Exactly one -> "
            "unique. More than one plausible reading, such that answering requires picking "
            "or splitting -> ambiguous. None -> nonexistent."
        ),
        "unique": "exactly one entity or value satisfies the description",
        "ambiguous": "several plausible referents; a correct answer disambiguates",
        "nonexistent": "nothing satisfies the description",
    },
    "ground_truth_state": {
        "_test": (
            "If this were re-asked ninety days from now, could the correct answer differ? "
            "No -> stable. Yes, on a known calendar -> scheduled. Yes, at any moment -> "
            "volatile. Is there currently no established correct answer at all -> unknown."
        ),
        "stable": "will not change over the experiment's lifetime",
        "scheduled": "changes on a known calendar",
        "volatile": "can change at any time",
        "unknown": "no established answer exists; genuinely open",
    },
    "correct_response_mode": {
        "_test": (
            "Read the answer key's `correct_handling` and ask what a correct response DOES, "
            "independent of whether its content is right. Does it state a value -> assert. "
            "Does it have to name something false in the question before anything else -> "
            "reject_premise. Does it have to split into cases because the question does not "
            "pick one -> disambiguate. Does it have to decline, because no answer is "
            "established -> abstain. Does it have to give a range or probability because a "
            "point value would overclaim -> estimate. This axis is about the SHAPE of the "
            "response, which is what lets cell U be scored categorically against anchors "
            "rather than judged on a continuum (mitigation C3)."
        ),
        "assert": "state the answer directly",
        "reject_premise": "decline the frame and say what is wrong with it",
        "disambiguate": "split into cases and answer each",
        "abstain": "decline to answer, with the reason",
        "estimate": "give a range or probability rather than a point value",
    },
}


def allowed(axis: str) -> tuple[str, ...]:
    return tuple(k for k in VOCAB[axis] if not k.startswith("_"))


# Coherence rules. Each is a definitional consequence of the labels involved,
# not a stylistic preference — which is why violating one means a label is wrong
# rather than an item being unusual.
def _coherence(labels: dict[str, str]) -> list[str]:
    errs: list[str] = []
    mode = labels.get("correct_response_mode")
    if labels.get("premise") == "false" and mode != "reject_premise":
        errs.append(
            "premise=false requires correct_response_mode=reject_premise: an answer that "
            "does not name the false presupposition is not a correct answer to the item"
        )
    if labels.get("referent") == "nonexistent" and mode != "reject_premise":
        errs.append(
            "referent=nonexistent requires correct_response_mode=reject_premise: there is "
            "nothing to assert about"
        )
    if labels.get("referent") == "ambiguous" and mode == "assert":
        errs.append(
            "referent=ambiguous is incompatible with correct_response_mode=assert: picking "
            "one referent silently is the failure the item is built to detect"
        )
    if labels.get("ground_truth_state") == "unknown" and mode not in {"abstain", "estimate"}:
        errs.append(
            "ground_truth_state=unknown requires correct_response_mode of abstain or "
            "estimate: there is no established value to assert"
        )
    if labels.get("knowledge_source") == "derivable" and labels.get("reasoning_depth") == "lookup":
        errs.append(
            "knowledge_source=derivable is incompatible with reasoning_depth=lookup: if the "
            "answer must be derived, at least one inferential move exists"
        )
    if labels.get("knowledge_source") == "derivable" and \
            labels.get("ground_truth_state") in {"volatile", "scheduled"}:
        errs.append(
            "knowledge_source=derivable is incompatible with a changing ground truth: a "
            "value computed from the question cannot drift with the calendar"
        )
    return errs


def validate(labels: dict | None, where: str = "item") -> dict[str, str]:
    """Check a label set and return it normalised. Raises on anything wrong.

    Strict on purpose. A partially-labelled item cannot be assigned to a cell,
    and an item silently defaulted into `parametric/lookup/sound/unique/stable/
    assert` would be assigned to the wrong cell while looking deliberate.
    """
    if not labels:
        raise ValueError(
            f"{where}: task_labels missing. Every diagnostic item declares all six axes "
            f"before it runs (OPEN-2); there is no default."
        )
    unknown_axes = sorted(set(labels) - set(AXES))
    if unknown_axes:
        raise ValueError(f"{where}: unknown task-label axes {unknown_axes}; expected {list(AXES)}")
    missing = [a for a in AXES if a not in labels]
    if missing:
        raise ValueError(f"{where}: task_labels missing axes {missing}")

    out: dict[str, str] = {}
    for axis in AXES:
        value = str(labels[axis]).strip()
        if value not in allowed(axis):
            raise ValueError(
                f"{where}: {axis}={value!r} is not in the vocabulary {list(allowed(axis))}. "
                f"Operational test: {VOCAB[axis]['_test']}"
            )
        out[axis] = value

    errs = _coherence(out)
    if errs:
        raise ValueError(f"{where}: incoherent task labels — " + "; ".join(errs))
    return out


def collinearity(items: list[tuple[str, dict, str | None]]) -> dict:
    """Is any axis just `claim_type` wearing a different name?

    `items` is (id, labels, expected_claim_type). For each axis this reports
    whether the mapping claim_type -> axis value is one-to-one across the
    battery. If it is, that axis carries no information the router does not
    already have, and grouping results by it is grouping by the treatment.

    Reported rather than enforced here: on a small battery a coincidental
    one-to-one mapping is possible, and the fix is to add a discriminating item,
    which is a step-4 authoring decision rather than something this function can
    make. The step-4 test asserts on the result.
    """
    report: dict[str, dict] = {}
    for axis in AXES:
        seen: dict[str, set[str]] = {}
        for _id, labels, ct in items:
            if not labels or ct is None:
                continue
            seen.setdefault(ct, set()).add(labels.get(axis, "?"))
        determined = bool(seen) and all(len(v) == 1 for v in seen.values())
        report[axis] = {
            "values_per_claim_type": {k: sorted(v) for k, v in seen.items()},
            "determined_by_claim_type": determined,
            "distinct_values": len({v for vs in seen.values() for v in vs}),
        }
    return report
