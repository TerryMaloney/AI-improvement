"""Per-item experimental specifications, and the tier wall between them.

Every diagnostic item carries a complete written specification, committed before
any solver dispatch. The plan's rule is blunt: *an item without a discriminator
that separates at least two explanations does not enter the battery, however
interesting it is.* This module is where that stops being a promise.

## Why a tier wall exists

The failure it prevents is subtle and common. You run a battery, one cell shows
movement, and the movement gets written up as evidence for the hypothesis — when
what the cell was actually built to detect was a property of the *instrument*.
"Search beats closed-book on current facts" says the retrieval channel works. It
says nothing whatever about whether the epistemic directive helps. Yet it lands
in the same results table, with the same kind of number, on the same day, and by
the time it reaches a summary the distinction is gone.

So each item declares an `evidence_tier`, and the tier caps what the item's
result may ever be cited for:

| Tier | May support | Never supports |
|---|---|---|
| `MEASUREMENT_VALIDITY` | that the instrument works, or does not | any explanation, any mechanism |
| `DIAGNOSTIC` | instrument validity; ruling a competing explanation in or out | the mechanism hypothesis itself |
| `PRIMARY` | all of the above, plus a mechanism effect | — |

`cite()` raises when a caller tries to use an item above its tier. That is the
whole mechanism: the wall is a function call that fails, not a paragraph in a
document that everyone agrees with and then forgets.

## Why PRIMARY implies deterministic

Decision D5: a judge may not determine a primary outcome where an objective
grader reasonably can. exp003c then measured a real judge length effect at rubric
boundaries (AMBER, Δ_length = −0.125). So `PRIMARY` items must grade
deterministically, and `validate_item` refuses a judged item at that tier. A
judged cell can be interesting, can eliminate an explanation, and still cannot
carry the headline — by construction, not by discipline.
"""

from __future__ import annotations

from enum import Enum

from lab.labels import validate as validate_labels
from lab.states import RetrievalState


class Tier(Enum):
    MEASUREMENT_VALIDITY = "MEASUREMENT_VALIDITY"
    DIAGNOSTIC = "DIAGNOSTIC"
    PRIMARY = "PRIMARY"

    @property
    def rank(self) -> int:
        return _TIER_ORDER.index(self)


_TIER_ORDER = [Tier.MEASUREMENT_VALIDITY, Tier.DIAGNOSTIC, Tier.PRIMARY]

# What a result can be used to say. Ordered by how strong the claim is.
CLAIM_KINDS = ("instrument_validity", "explanation_elimination", "mechanism_effect")

_MAX_CLAIM: dict[Tier, str] = {
    Tier.MEASUREMENT_VALIDITY: "instrument_validity",
    Tier.DIAGNOSTIC: "explanation_elimination",
    Tier.PRIMARY: "mechanism_effect",
}

# How a verdict is reached. `deterministic_with_judge_fallback` is its own
# category rather than a rounding of the other two: the trap grader decides
# most cases by string match but escalates the ones no marker covers, so SOME
# fraction of the item's trials are judged and the length caveat applies to
# exactly that fraction. Calling it "deterministic" would hide the judged tail.
OUTCOME_TYPES = (
    "deterministic",
    "deterministic_with_judge_fallback",
    "judged",
    "diagnostic_only",
)

# Outcome types with no judge anywhere in them. Only these may declare that
# response length cannot touch the result.
_NO_JUDGE = frozenset({"deterministic", "diagnostic_only"})

# The eight competing explanations from the design memo. An item must name which
# of them could also produce movement in it; "none" is not an available answer.
EXPLANATIONS = {
    "E1": "latent-knowledge access",
    "E2": "reasoning improvement",
    "E3": "stochastic variation",
    "E4": "prompt length / placebo",
    "E5": "format prescription",
    "E6": "retrieval benefit",
    "E7": "retrieval displacement",
    "E8": "judge phrasing sensitivity",
}

LENGTH_SENSITIVITY = ("NONE", "POSSIBLE", "LIKELY")

# The fifteen fields the operator required locked before dispatch, plus the
# three the plan requires (§5) and the tier field. Order is the order they are
# rendered in the frozen specification document.
REQUIRED_FIELDS = (
    "id",                       # 1  item id
    "conditions",               # which arms this item runs under
    "cell",                     # 2  task family
    "family",                   # 2  task family, in words
    "task_labels",              # 3  six axes
    "intended_mechanism",       # 4  target capability / mechanism
    "expected_retrieval_state", # 5  per condition class
    "gold_criterion",           # 6  how correctness is decided (NOT the answer)
    "response_mode",            # 7  classification
    "mode_anchors",             # 7  anchors
    "outcome_type",             # 8  deterministic / judged / diagnostic-only
    "known_confounds",          # 9
    "why_in_battery",           # 10
    "verdict_rules",            # 11 PASS / PARTIAL / FAIL / NOT ESTABLISHED
    "length_sensitivity",       # 12
    "matching",                 # 13 placebo / matched-item relationship
    "exclusion_criteria",       # 14
    "failure_consequences",     # 15
    "competing_explanations",   # plan §5
    "predictions",              # plan §5
    "discriminator",            # plan §5
    "evidence_tier",            # the tier wall
    "estimand",                 # which causal quantities this item can inform
    "routing_disposition",      # how this item's routing is handled, explicitly
)

# The causal quantities an item may contribute to. Declared per item so a result
# can never be attributed to an estimand the item was not built to inform.
ESTIMANDS = (
    "theta_system",       # the deployed layer, classifier included — comparable to exp001/exp002
    "theta_directive",    # the intended directive, correctly delivered
    "theta_routing",      # theta_system minus theta_directive, as a difference in differences
    "theta_framing",      # the claim-type framing sentence alone
    "theta_instruction",  # the placebo effect: being instructed at all
    "delta_displacement", # retrieval making an answer worse
    "mode_shift",         # categorical response-mode change
    "gate",               # instrument validity only
)

# How each item's routing is handled. Every misroute must carry a declared
# disposition; "nobody noticed" is not one of the options.
ROUTING_DISPOSITIONS = (
    "agrees",                  # the classifier already produces the declared type
    "crossed",                 # both directives are delivered, as separate arms
    "accepted_as_system",      # the routed directive is used; the estimand is theta_system
    "inert_no_directive_arm",  # no condition injects a directive, so routing cannot matter
)

VERDICTS = ("PASS", "PARTIAL", "FAIL", "NOT_ESTABLISHED")

# Which conditions hand the solver a search tool. `directive_placebo` and
# `A_only` are closed-book variants of the directive contrast; the four cell-D
# conditions are the search ladder.
CLOSED_CONDITIONS = frozenset({
    "baseline", "directive_placebo", "A_only", "directive_only", "closed_book",
    # D-prime (decision packet §1.3). Cell R crosses the routed directive against
    # the intended one, each with its OWN length-matched placebo — because the
    # intended block is 68 words shorter than the routed one, so a single placebo
    # would leave one arm uncontrolled and put E4/E5 back into the contrast.
    "placebo_routed", "placebo_intended", "directive_routed", "directive_intended",
})
SEARCH_CONDITIONS = frozenset(
    {"search_only", "search_directive", "search_selfcheck", "search_independent"}
)
KNOWN_CONDITIONS = CLOSED_CONDITIONS | SEARCH_CONDITIONS


def _reachable() -> frozenset[RetrievalState] | None:
    """The states this environment can actually produce, from the committed probe.

    Returns None when no probe exists, so that item validation still works in a
    checkout that has not probed — the ingest path is where a missing probe
    becomes a refusal (FD-4). Where a probe DOES exist, an item may not be
    specified to reach a state the environment cannot produce, which is how a
    cell-D specification stays honest at authoring time rather than at analysis
    time.
    """
    from lab.states import load_egress

    try:
        return load_egress().reachable
    except (FileNotFoundError, KeyError, ValueError):
        return None


def _need(item: dict, field: str, where: str):
    if field not in item or item[field] in (None, "", [], {}):
        raise ValueError(f"{where}: specification field {field!r} is missing or empty")
    return item[field]


def validate_item(item: dict, where: str | None = None) -> dict:
    """Check one item's specification. Raises on anything incomplete.

    Strict everywhere, because the whole value of a pre-registered specification
    is that it was complete *before* the data existed. A field left blank now is
    a field that gets filled in after the results are in, and one filled in then
    is not a prediction.
    """
    where = where or f"item {item.get('id', '?')}"

    for field in REQUIRED_FIELDS:
        _need(item, field, where)

    validate_labels(item["task_labels"], where=where)

    tier = Tier(item["evidence_tier"])
    outcome = item["outcome_type"]
    if outcome not in OUTCOME_TYPES:
        raise ValueError(f"{where}: outcome_type {outcome!r} not in {OUTCOME_TYPES}")

    # D5, enforced rather than remembered.
    if tier is Tier.PRIMARY and outcome != "deterministic":
        raise ValueError(
            f"{where}: evidence_tier PRIMARY requires outcome_type 'deterministic', got "
            f"{outcome!r}. A judge may not determine a primary outcome (D5), and exp003c "
            f"measured a real judge length effect at rubric boundaries."
        )

    if item["length_sensitivity"] not in LENGTH_SENSITIVITY:
        raise ValueError(
            f"{where}: length_sensitivity must be one of {LENGTH_SENSITIVITY}"
        )
    # exp003c measured Delta_length = -0.125 at rubric boundaries. Length can
    # only act through a judge, so the two fields have to agree about whether
    # there is one.
    if outcome in _NO_JUDGE and item["length_sensitivity"] != "NONE":
        raise ValueError(
            f"{where}: outcome_type {outcome!r} has no judge in it, so length_sensitivity "
            f"cannot be {item['length_sensitivity']!r} — there is nothing for length to act "
            f"through. Either the grading is not judge-free or the sensitivity is misdeclared."
        )
    if outcome not in _NO_JUDGE and item["length_sensitivity"] == "NONE":
        raise ValueError(
            f"{where}: outcome_type {outcome!r} puts a judge on at least some trials, so "
            f"length_sensitivity NONE is not an available answer. exp003c measured "
            f"Delta_length = -0.125 at rubric boundaries; declare POSSIBLE or LIKELY with a "
            f"stated reason."
        )

    codes = list(item["competing_explanations"])
    unknown = [c for c in codes if c not in EXPLANATIONS]
    if unknown:
        raise ValueError(f"{where}: unknown explanation codes {unknown}; expected {sorted(EXPLANATIONS)}")
    if len(set(codes)) < 2:
        raise ValueError(
            f"{where}: an item must name at least two competing explanations it could be "
            f"confused between, otherwise its discriminator separates nothing and the item "
            f"does not belong in the battery (plan §5)."
        )

    conditions = list(item["conditions"])
    unknown_conditions = [c for c in conditions if c not in KNOWN_CONDITIONS]
    if unknown_conditions:
        raise ValueError(f"{where}: unknown conditions {unknown_conditions}")
    if len(conditions) < 2:
        raise ValueError(f"{where}: an item needs at least two conditions to contrast")

    states = item["expected_retrieval_state"]
    if set(states) != set(conditions):
        raise ValueError(
            f"{where}: expected_retrieval_state must name exactly the conditions this item "
            f"runs under. Declared {sorted(states)}, conditions {sorted(conditions)}. Stating "
            f"it per condition rather than per class is what makes the cell-D ladder "
            f"falsifiable."
        )
    reachable = _reachable()
    for cond, value in states.items():
        try:
            state = RetrievalState(value)
        except ValueError:
            raise ValueError(
                f"{where}: expected_retrieval_state[{cond}] = {value!r} is not a retrieval state"
            ) from None
        if cond in CLOSED_CONDITIONS and state is not RetrievalState.NONE:
            raise ValueError(
                f"{where}: {cond} is closed-book, so its retrieval state is NONE. Declaring "
                f"{value!r} claims something impossible."
            )
        if cond in SEARCH_CONDITIONS and state is RetrievalState.NONE:
            raise ValueError(
                f"{where}: {cond} has a search tool; expecting NONE says the item predicts "
                f"the solver never searches, which belongs in `predictions`, not here."
            )
        if reachable is not None and state not in reachable:
            raise ValueError(
                f"{where}: expected_retrieval_state[{cond}] = {value!r} is UNREACHABLE in "
                f"this environment (probed reachable set: "
                f"{sorted(s.value for s in reachable)}). An item may not be specified to "
                f"reach a state the egress probe says cannot occur — see FD-4."
            )

    if set(item["predictions"]) != set(conditions):
        raise ValueError(
            f"{where}: predictions must cover exactly the conditions this item runs under. "
            f"Declared {sorted(item['predictions'])}, conditions {sorted(conditions)}."
        )

    rules = item["verdict_rules"]
    missing = [v for v in VERDICTS if v not in rules]
    if missing:
        raise ValueError(
            f"{where}: verdict_rules missing {missing}. NOT_ESTABLISHED is required and is "
            f"not a synonym for FAIL — it is what a contrast returns when the instrument "
            f"cannot decide, and conflating the two turns an absent measurement into a "
            f"negative result."
        )

    if not str(item["discriminator"]).strip():
        raise ValueError(f"{where}: discriminator is empty")

    estimands = list(item["estimand"])
    unknown_estimands = [e for e in estimands if e not in ESTIMANDS]
    if unknown_estimands:
        raise ValueError(f"{where}: unknown estimands {unknown_estimands}; expected {list(ESTIMANDS)}")

    disposition = item["routing_disposition"]
    if disposition not in ROUTING_DISPOSITIONS:
        raise ValueError(
            f"{where}: routing_disposition {disposition!r} not in {list(ROUTING_DISPOSITIONS)}"
        )
    route_dependent = bool(set(conditions) & {"directive_only", "search_directive", "A_only",
                                              "directive_routed", "directive_intended"})
    if disposition == "inert_no_directive_arm" and route_dependent:
        raise ValueError(
            f"{where}: declared inert, but its conditions inject a routed directive or framing. "
            f"A misroute here would reach the solver."
        )
    if disposition == "crossed" and not {"directive_routed", "directive_intended"} <= set(conditions):
        raise ValueError(
            f"{where}: declared crossed, but does not run both directive_routed and "
            f"directive_intended. A crossed disposition without both arms measures nothing."
        )
    if disposition == "crossed" and "theta_routing" not in estimands:
        raise ValueError(
            f"{where}: a crossed item must declare theta_routing, or the contrast it pays for "
            f"is not attributed to any estimand"
        )
    if disposition == "accepted_as_system" and "theta_directive" in estimands:
        raise ValueError(
            f"{where}: accepted_as_system means the ROUTED directive is delivered, so the item "
            f"informs theta_system and cannot inform theta_directive — that directive is never "
            f"delivered to it"
        )

    metric = item.get("primary_metric")
    if metric is not None and metric not in ("verdict", "tool_calls_observed", "response_mode"):
        raise ValueError(
            f"{where}: primary_metric {metric!r} is not one the lab measures. A cell whose "
            f"headline is a counter rather than a verdict must say so, or its result gets "
            f"read as an accuracy number."
        )

    consequences = item["failure_consequences"]
    if not isinstance(consequences, dict) or not consequences:
        raise ValueError(
            f"{where}: failure_consequences must map each named failure to what it forces. "
            f"'We would look into it' is not a consequence."
        )
    return item


def cite(item: dict, claim_kind: str) -> None:
    """Assert that this item's result may be used to support `claim_kind`.

    Raises otherwise. This is the tier wall, and it is a function precisely so
    that promoting a diagnostic result to a mechanism claim requires editing the
    item's declared tier — a visible, reviewable change — rather than writing a
    confident sentence.
    """
    if claim_kind not in CLAIM_KINDS:
        raise ValueError(f"unknown claim kind {claim_kind!r}; expected {CLAIM_KINDS}")
    tier = Tier(item["evidence_tier"])
    allowed = CLAIM_KINDS[: CLAIM_KINDS.index(_MAX_CLAIM[tier]) + 1]
    if claim_kind not in allowed:
        raise ValueError(
            f"{item['id']}: tier {tier.value} may support {list(allowed)}, not "
            f"{claim_kind!r}. {_WHY[tier]}"
        )


_WHY = {
    Tier.MEASUREMENT_VALIDITY: (
        "A measurement-validity item tells you whether the instrument works. A working "
        "instrument is a precondition for reading any result, never itself a result about "
        "the hypothesis."
    ),
    Tier.DIAGNOSTIC: (
        "A diagnostic item can rule a competing explanation in or out. Eliminating one "
        "alternative is not the same as establishing the mechanism, and treating it that "
        "way is how a battery confirms whatever it was built around."
    ),
    Tier.PRIMARY: "",
}


def max_claim(item: dict) -> str:
    return _MAX_CLAIM[Tier(item["evidence_tier"])]


def gates(item: dict) -> bool:
    """Does a failure here block interpretation of everything else?

    True only for measurement-validity items that declare it. A gate is the one
    way a low-tier item legitimately affects a high-tier reading: by preventing
    it, never by supporting it.
    """
    return bool(item.get("gate", False))


# --------------------------------------------------------------------------
# The frozen specification document
# --------------------------------------------------------------------------

def battery_fingerprint(items: list[dict]) -> str:
    """A content hash over the specifications, in canonical form.

    Printed in the rendered document so that a specification edited after
    dispatch is visible as a changed fingerprint rather than as nothing at all.
    It is not a security measure — anyone can regenerate it — it is a way for a
    reader to tell at a glance whether the document in front of them describes
    the battery that ran.
    """
    import hashlib
    import json

    canonical = json.dumps(
        [{k: v for k, v in sorted(i.items())} for i in sorted(items, key=lambda i: i["id"])],
        sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


_FIELD_TITLES = [
    ("intended_mechanism", "Target capability / mechanism"),
    ("why_in_battery", "Why this item is in the battery"),
    ("discriminator", "Discriminating observation"),
    ("gold_criterion", "Gold criterion (how correctness is decided)"),
    ("matching", "Placebo / matched-item relationship"),
]


def _para(text) -> str:
    return " ".join(str(text).split())


def render_specification(battery, answers: dict | None = None) -> str:
    """Render the battery as an inspectable frozen specification.

    Generated from the YAML rather than written alongside it, so the document
    and the thing that will actually run cannot disagree. A test asserts the
    committed file matches what this produces.

    Contains no ground-truth VALUE. Where an item's answer key matters, the
    document reports its STATUS — verified, rubric_only — which is what a
    reader needs to judge whether the item is scorable.
    """
    items = [q.spec for q in battery.questions]
    out: list[str] = []
    A = out.append

    A(f"# {battery.id} — frozen battery specification")
    A("")
    A(f"**Fingerprint:** `{battery_fingerprint(items)}`")
    A("")
    A("Generated from `batteries/diagnostic_v1.yaml` by `python -m lab spec diagnostic_v1 "
      "--write`. Do not edit this file directly: edit the battery and regenerate, so the "
      "document and the thing that runs cannot disagree. A test asserts they match.")
    A("")
    A(_para(battery.description))
    A("")
    A("**No solver dispatch has occurred.** This specification is committed before any, "
      "which is the only thing that makes its predictions predictions.")
    A("")

    A("## The tier wall")
    A("")
    A("Each item declares an evidence tier, and the tier caps what its result may ever be "
      "cited for. Results travel from measurement validity to diagnostic to primary in one "
      "direction only: a diagnostic finding that the instrument is sensitive to some feature "
      "is a fact about the instrument, and does not become evidence for the hypothesis "
      "because it appeared in the same table. `lab.spec.cite()` raises rather than relying "
      "on anyone remembering this.")
    A("")
    A("| Tier | May support | Items |")
    A("|---|---|---|")
    for tier in _TIER_ORDER:
        ids = [i["id"] for i in items if i["evidence_tier"] == tier.value]
        allowed = CLAIM_KINDS[: CLAIM_KINDS.index(_MAX_CLAIM[tier]) + 1]
        A(f"| `{tier.value}` | {', '.join(allowed)} | {', '.join(ids) or '—'} |")
    A("")
    gated = [i["id"] for i in items if gates(i)]
    if gated:
        A(f"**Gate:** {', '.join(gated)}. A failure there halts interpretation of the run "
          f"rather than lowering a number in it.")
        A("")

    A("## Cells")
    A("")
    A("| Cell | Items | Tier | Outcome | Conditions | Primary metric |")
    A("|---|---|---|---|---|---|")
    seen: list[str] = []
    for item in items:
        if item["cell"] in seen:
            continue
        seen.append(item["cell"])
        members = [i for i in items if i["cell"] == item["cell"]]
        tiers = sorted({i["evidence_tier"] for i in members})
        outcomes = sorted({i["outcome_type"] for i in members})
        metrics = sorted({i.get("primary_metric", "verdict") for i in members})
        A(f"| **{item['cell']}** | {len(members)} | {', '.join(tiers)} | "
          f"{', '.join(outcomes)} | `{'`, `'.join(item['conditions'])}` | "
          f"{', '.join(metrics)} |")
    A("")

    A("## Task-label coverage")
    A("")
    A("Six axes, kept apart from `claim_type` so that results are not grouped by the "
      "variable the treatment is defined on. Every axis varies across the battery, and none "
      "is a one-to-one relabelling of claim type — both asserted by test.")
    A("")
    from lab.labels import AXES

    A("| Axis | Values used |")
    A("|---|---|")
    for axis in AXES:
        counts = {}
        for q in battery.questions:
            counts[q.task_labels[axis]] = counts.get(q.task_labels[axis], 0) + 1
        A(f"| `{axis}` | " + ", ".join(f"{k} ({v})" for k, v in sorted(counts.items())) + " |")
    A("")

    A("---")
    A("")
    A("## Items")
    A("")

    for q in battery.questions:
        item = q.spec
        entry = (answers or {}).get(q.id) or {}
        A(f"### {q.id} — {item['family']} (cell {item['cell']})")
        A("")
        A(f"> {_para(q.text)}")
        A("")
        A(f"| | |")
        A(f"|---|---|")
        A(f"| Evidence tier | `{item['evidence_tier']}`"
          + (" · **GATE**" if gates(item) else "") + " |")
        A(f"| Max claim | `{max_claim(item)}` |")
        A(f"| Outcome type | `{item['outcome_type']}` |")
        A(f"| Primary metric | `{item.get('primary_metric', 'verdict')}` |")
        A(f"| Grading method | `{q.grading_method}` |")
        A(f"| Ground truth | status `{entry.get('status', 'MISSING')}`"
          f"{' — no value exists by construction' if entry.get('status') == 'rubric_only' else ''} |")
        A(f"| Response mode | `{item['response_mode']}` |")
        A(f"| Length sensitivity | `{item['length_sensitivity']}` |")
        A(f"| Competing explanations | "
          + ", ".join(f"{c} ({EXPLANATIONS[c]})" for c in item["competing_explanations"]) + " |")
        A("")
        A("**Task labels** — "
          + ", ".join(f"`{k}`: {v}" for k, v in item["task_labels"].items()))
        A("")
        for field, title in _FIELD_TITLES:
            A(f"**{title}.** {_para(item[field])}")
            A("")
        A("**Conditions, expected retrieval state, and prediction**")
        A("")
        A("| Condition | Expected retrieval state | Prediction |")
        A("|---|---|---|")
        for cond in item["conditions"]:
            A(f"| `{cond}` | `{item['expected_retrieval_state'][cond]}` | "
              f"{_para(item['predictions'][cond])} |")
        A("")
        A("**Response-mode anchors**")
        A("")
        for mode, anchor in item["mode_anchors"].items():
            A(f"- `{mode}` — {_para(anchor)}")
        A("")
        A("**Verdict rules**")
        A("")
        for verdict in VERDICTS:
            A(f"- **{verdict}** — {_para(item['verdict_rules'][verdict])}")
        A("")
        A("**Known confounds**")
        A("")
        for c in item["known_confounds"]:
            A(f"- {_para(c)}")
        A("")
        A("**Exclusion criteria**")
        A("")
        for c in item["exclusion_criteria"]:
            A(f"- {_para(c)}")
        A("")
        A("**Consequence of each failure**")
        A("")
        for name, consequence in item["failure_consequences"].items():
            A(f"- `{name}` → {_para(consequence)}")
        A("")
        A("---")
        A("")

    return "\n".join(out)
