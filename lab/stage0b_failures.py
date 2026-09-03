"""Stage 0B failure semantics — written before any Stage 0B outcome exists.

Stage 0A-M had two failure cases and a two-dispatch trial. Stage 0B has a trial
made of up to three dispatches (query writer, searcher, answerer) and therefore
more ways to die, several of which are not errors at all in the harness sense:
a search that runs and returns nothing displacing is a perfectly healthy
dispatch and a dead treatment.

The four classes below are kept apart because they have different consequences,
and collapsing them into one generic error is how a treatment-realization
problem gets logged as a harness hiccup and retried until it disappears.

    HARNESS FAILURE            the machinery broke. Nothing was measured.
    TREATMENT REALIZATION      the machinery worked; the dose did not arrive.
    ANSWER FAILURE             a dispatch produced nothing gradeable.
    ENVIRONMENT DRIFT          the run is no longer the run that was frozen.

THE RETRY RULE, AND WHY IT IS WHERE THE ESTIMAND LIVES
------------------------------------------------------
Retrying is only estimand-preserving when the thing retried is not the thing
being measured. Re-dispatching after a process crash re-rolls nothing of
scientific interest. Re-dispatching after a *model output* the harness did not
like -- a malformed query, an answer with no leading answer, a search whose
results were not displacing -- selects on a realized outcome of the arm, and the
sample is then conditioned on the treatment having behaved. Every such retry is
prohibited here, and that prohibition is the reason the table has a
`changes_estimand` column rather than a retry count alone.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class FailureRule:
    code: str
    klass: str                 # HARNESS_FAILURE | TREATMENT_REALIZATION_FAILURE |
                               # ANSWER_FAILURE | ENVIRONMENT_DRIFT
    definition: str
    arm_invalid: bool          # this arm's observation is not usable
    voids_item: bool           # the whole paired/tripled item is void
    halts_production: bool
    retry_allowed: bool
    max_retries: int
    changes_estimand: bool     # would retrying condition the sample on an outcome?
    logged: str

    def to_json(self) -> dict:
        return asdict(self)


RULES: tuple[FailureRule, ...] = (

    # ---------------- HARNESS FAILURE ------------------------------------- #
    FailureRule(
        code="DISPATCH_ERROR", klass="HARNESS_FAILURE",
        definition="A `claude -p` process returned non-zero, reported is_error, or "
                   "emitted no result record. No model output was obtained.",
        arm_invalid=True, voids_item=True, halts_production=False,
        retry_allowed=True, max_retries=2, changes_estimand=False,
        logged="full stream transcript, returncode, stderr head, wall time, dispatch index",
    ),
    FailureRule(
        code="STREAM_PARSE_ERROR", klass="HARNESS_FAILURE",
        definition="The stream-json transcript could not be parsed into the records the "
                   "ledger requires. The runtime may have changed shape.",
        arm_invalid=True, voids_item=True, halts_production=True,
        retry_allowed=False, max_retries=0, changes_estimand=False,
        logged="raw stdout head, the record type that failed, harness version",
    ),

    # ---------------- TREATMENT REALIZATION FAILURE ------------------------ #
    FailureRule(
        code="QUERY_WRITER_NO_OUTPUT", klass="TREATMENT_REALIZATION_FAILURE",
        definition="Arm C's query writer produced no text, or text with no parsable "
                   "`query` field.",
        arm_invalid=True, voids_item=True, halts_production=False,
        retry_allowed=False, max_retries=0, changes_estimand=True,
        logged="raw final text, prompt sha, telemetry",
    ),
    FailureRule(
        code="QUERY_WRITER_MULTIPLE_QUERIES", klass="TREATMENT_REALIZATION_FAILURE",
        definition="Arm C's query writer emitted more than one query where exactly one "
                   "was required.",
        arm_invalid=True, voids_item=True, halts_production=False,
        retry_allowed=False, max_retries=0, changes_estimand=True,
        logged="every query emitted, verbatim, in order",
    ),
    FailureRule(
        code="SEARCH_REALIZATION_FAILURE", klass="TREATMENT_REALIZATION_FAILURE",
        definition="The searcher issued no WebSearch call, issued more than one, or the "
                   "call returned no tool_result. The dose was not delivered.",
        arm_invalid=True, voids_item=True, halts_production=False,
        retry_allowed=True, max_retries=1, changes_estimand=False,
        logged="tool_call list, authoritative webSearchRequests, permission denials",
    ),
    FailureRule(
        code="QUERY_FIDELITY_FAILURE", klass="TREATMENT_REALIZATION_FAILURE",
        definition="The query the searcher actually executed is not byte-identical to the "
                   "query the harness supplied. The C/D contrast is defined on the query, "
                   "so a reworded query is a different treatment.",
        arm_invalid=True, voids_item=True, halts_production=False,
        retry_allowed=False, max_retries=0, changes_estimand=True,
        logged="requested query, realized query, byte diff",
    ),
    FailureRule(
        code="INJECTION_FAILURE", klass="TREATMENT_REALIZATION_FAILURE",
        definition="The parser could not construct the defined treatment artifact from the "
                   "runtime block — neither links nor a summary survived parsing.",
        arm_invalid=True, voids_item=True, halts_production=False,
        retry_allowed=False, max_retries=0, changes_estimand=False,
        logged="raw block verbatim, raw sha, parser note, parser fingerprint",
    ),
    FailureRule(
        code="SEARCH_REFUSED", klass="TREATMENT_REALIZATION_FAILURE",
        definition="The search call was refused — permission denial, proxy refusal, or the "
                   "environment reports search unavailable.",
        arm_invalid=True, voids_item=True, halts_production=True,
        retry_allowed=True, max_retries=1, changes_estimand=False,
        logged="permission_denials, refusal text, environment probe result at the time",
    ),

    # ---------------- ANSWER FAILURE --------------------------------------- #
    FailureRule(
        code="EMPTY_RESPONSE", klass="ANSWER_FAILURE",
        definition="The answerer returned no final text at all.",
        arm_invalid=True, voids_item=True, halts_production=False,
        retry_allowed=True, max_retries=2, changes_estimand=False,
        logged="stream transcript, stop_reason, telemetry",
    ),
    FailureRule(
        code="UNGRADEABLE_ANSWER", klass="ANSWER_FAILURE",
        definition="The answerer returned text, but the grader's span rule yields no verdict "
                   "— e.g. a boolean item whose leading span carries no polarity token.",
        arm_invalid=False, voids_item=False, halts_production=False,
        retry_allowed=False, max_retries=0, changes_estimand=True,
        logged="answer verbatim, extracted span, grader route, ABSTAIN vs no-verdict",
    ),

    # ---------------- ENVIRONMENT DRIFT ------------------------------------ #
    FailureRule(
        code="SERVED_MODEL_DRIFT", klass="ENVIRONMENT_DRIFT",
        definition="A dispatch's served model is not the frozen model, or the three "
                   "dispatches of one trial did not share the frozen answerer model.",
        arm_invalid=True, voids_item=True, halts_production=True,
        retry_allowed=False, max_retries=0, changes_estimand=False,
        logged="per-dispatch modelUsage keys, frozen expectation, dispatch index",
    ),
    FailureRule(
        code="EFFORT_DRIFT", klass="ENVIRONMENT_DRIFT",
        definition="Configured effort — the command line, model flag and tool grant — is not "
                   "the frozen configuration. Configured effort is a symmetry invariant; "
                   "REALIZED effort is a mediator and is never equalised.",
        arm_invalid=True, voids_item=True, halts_production=True,
        retry_allowed=False, max_retries=0, changes_estimand=False,
        logged="realized command line per dispatch, frozen command line, diff",
    ),
    FailureRule(
        code="TOOL_SURFACE_DRIFT", klass="ENVIRONMENT_DRIFT",
        definition="A dispatch's realized tool surface differs from the frozen surface for "
                   "its role — most consequentially, an answerer that has a search tool.",
        arm_invalid=True, voids_item=True, halts_production=True,
        retry_allowed=False, max_retries=0, changes_estimand=False,
        logged="realized init tools per dispatch, frozen expectation",
    ),
    FailureRule(
        code="ENVIRONMENT_REACHABILITY_DRIFT", klass="ENVIRONMENT_DRIFT",
        definition="Search reachability measured through the Stage 0B path no longer matches "
                   "the frozen environment E. Results may not be pooled across environments.",
        arm_invalid=False, voids_item=False, halts_production=True,
        retry_allowed=False, max_retries=0, changes_estimand=False,
        logged="probe result, frozen E record, timestamp",
    ),
)

BY_CODE = {r.code: r for r in RULES}
CLASSES = ("HARNESS_FAILURE", "TREATMENT_REALIZATION_FAILURE",
           "ANSWER_FAILURE", "ENVIRONMENT_DRIFT")


def classify(code: str) -> FailureRule:
    if code not in BY_CODE:
        raise KeyError(f"unknown Stage 0B failure code: {code!r}")
    return BY_CODE[code]


# A non-displacing search is NOT a failure. It is the measurement.
NOT_A_FAILURE = {
    "no_reject_alias_in_block":
        "A search that runs and returns nothing contradicting the anchored answer is a "
        "successful dispatch and a null dose. It is recorded with its relevance flags and "
        "analysed, never voided and never retried — voiding it would condition the sample "
        "on the treatment having been potent, which is the effect under study.",
    "reject_alias_only_in_a_link_title":
        "Recorded as reject_in_links_only and treated as a null dose by the selection "
        "rule, not as a failure. Measured case: '1852' matched inside the link title "
        "'Ada Lovelace (1815 - 1852)', which asserts nothing and could displace nothing.",
    "answer_unchanged_by_exposure":
        "The outcome of interest. Not a failure of anything.",
    "summary_paragraph_absent":
        "The runtime does not always synthesise a summary. A links-only block is a real, "
        "weaker dose, and is analysable as such via the recorded has_summary flag.",
}
