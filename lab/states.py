"""The retrieval-state machine — four things that are not the same thing.

exp001's reports used "verified" to mean "the condition that was allowed to
search". That is four distinct claims collapsed into one word, and the collapse
is what makes a retrieval result unreadable:

| State | What it actually asserts |
|---|---|
| `RETRIEVAL` | a query ran and returned something |
| `SOURCE_ACCESS` | a source document was actually opened and read |
| `CLAIM_EVIDENCE_MATCH` | the specific claim at issue was located in evidence |
| `VERIFICATION` | that match was corroborated by independent evidence |

**These are not four rungs of one ladder.** The first draft of this module made
them one, and it immediately produced a false alarm: a solver that matches a
claim against a search snippet has attained `CLAIM_EVIDENCE_MATCH` while never
attaining `SOURCE_ACCESS`, which a linear ladder has to call either impossible or
a sandbox breach. It is neither — it is the ordinary case in a search-only
environment, and it is precisely the weak-evidence situation worth naming.

So each state is an independent **predicate** with its own preconditions, and a
trial attains a *set* of them. An ordering exists, but only to choose a headline;
the attained set travels with it, so "matched the claim but never opened a
source" stays visible instead of being flattened into one word.

Two rules are enforced in code rather than left to discipline:

1. **A state is reported only where its preconditions were met.** In particular a
   search-result snippet is `RETRIEVAL`, never `SOURCE_ACCESS`: a snippet is a
   search engine's summary of a document, selected for relevance to the query,
   which is the exact selection effect verification is supposed to be robust
   against. Matching a claim in one is `CLAIM_EVIDENCE_MATCH` **at snippet
   depth**, a genuinely weaker thing, so the depth travels with the state.

2. **No conclusion may be drawn about a state the environment made unreachable.**
   WebFetch egress is blocked here (FD-4), so `SOURCE_ACCESS` and `VERIFICATION`
   cannot occur. "Verification did not help" is not a licensed reading of an
   environment in which verification could not happen; the licensed claim is
   "retrieval, at snippet depth, did not help". `negative_conclusion_licensed()`
   exists so a report cannot make the first claim by accident — the trap is easy
   to fall into because the *condition* was called "verified" while the *state*
   never got past retrieval.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EGRESS_PROBE_PATH = REPO_ROOT / "runs" / "egress_probe" / "latest.json"


class RetrievalState(Enum):
    NONE = "NONE"
    RETRIEVAL = "RETRIEVAL"
    SOURCE_ACCESS = "SOURCE_ACCESS"
    CLAIM_EVIDENCE_MATCH = "CLAIM_EVIDENCE_MATCH"
    VERIFICATION = "VERIFICATION"

    @property
    def strength(self) -> int:
        """Headline ordering only. Says nothing about implication: a higher
        strength does NOT mean the lower states were attained."""
        return _STRENGTH.index(self)


_STRENGTH = [
    RetrievalState.NONE,
    RetrievalState.RETRIEVAL,
    RetrievalState.SOURCE_ACCESS,
    RetrievalState.CLAIM_EVIDENCE_MATCH,
    RetrievalState.VERIFICATION,
]


class EvidenceDepth(Enum):
    """How close to the source the text actually was.

    `SNIPPET` is what a search API returns. `DOCUMENT` is what a fetch returns.
    """

    SNIPPET = "SNIPPET"
    DOCUMENT = "DOCUMENT"


# Corroboration required before a match may be called VERIFICATION. Two
# *independent* origins, per the router's own directive: "Two sources that trace
# to the same original report are ONE source."
INDEPENDENCE_REQUIRED = 2


@dataclass(frozen=True)
class Evidence:
    """One retrieval event and what it produced.

    Authored by the orchestrator from what it observed, not by the solver about
    itself. A ledger shorter than the observed tool-call count is an audit flag,
    never a correction to the count.
    """

    query: str = ""
    returned: bool = False
    depth: EvidenceDepth = EvidenceDepth.SNIPPET
    addressed_claim: bool = False
    source_kind: str = "unknown"
    origin: str | None = None
    note: str = ""

    def as_dict(self) -> dict:
        d = asdict(self)
        d["depth"] = self.depth.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Evidence":
        depth = d.get("depth", EvidenceDepth.SNIPPET.value)
        return cls(
            query=d.get("query", ""),
            returned=bool(d.get("returned", False)),
            depth=depth if isinstance(depth, EvidenceDepth) else EvidenceDepth(depth),
            addressed_claim=bool(d.get("addressed_claim", False)),
            source_kind=d.get("source_kind", "unknown"),
            origin=d.get("origin"),
            note=d.get("note", ""),
        )


@dataclass(frozen=True)
class EgressStatus:
    """What the environment permitted, as probed — not as assumed."""

    web_search: bool
    web_fetch: bool
    probed_at: str = ""
    detail: str = ""

    @property
    def reachable(self) -> frozenset[RetrievalState]:
        """Which states could occur at all here.

        Note the shape: with search but no fetch, `CLAIM_EVIDENCE_MATCH` is
        reachable while `SOURCE_ACCESS` is not. That gap is not a bug in the
        model, it is the environment — you can read a claim off a snippet without
        ever opening the document the snippet came from.
        """
        states = {RetrievalState.NONE}
        if self.web_search or self.web_fetch:
            states |= {RetrievalState.RETRIEVAL, RetrievalState.CLAIM_EVIDENCE_MATCH}
        if self.web_fetch:
            states |= {RetrievalState.SOURCE_ACCESS, RetrievalState.VERIFICATION}
        return frozenset(states)

    @property
    def unreachable(self) -> frozenset[RetrievalState]:
        return frozenset(set(_STRENGTH) - self.reachable)

    @property
    def ceiling(self) -> RetrievalState:
        """Strongest reachable state. A headline, not a summary of the set —
        callers deciding what may be *concluded* must use `reachable`."""
        return max(self.reachable, key=lambda s: s.strength)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["reachable"] = sorted(s.value for s in self.reachable)
        d["unreachable"] = sorted(s.value for s in self.unreachable)
        d["ceiling"] = self.ceiling.value
        return d


def load_egress(path: str | Path = EGRESS_PROBE_PATH) -> EgressStatus:
    """Read the committed probe result.

    Deliberately raises when the artefact is missing. Defaulting to "blocked"
    would silently license the weaker reading and defaulting to "open" the
    stronger one; the right behaviour is to refuse until somebody has probed.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"no egress probe at {p}. Run `python -m lab egress-probe` and commit the "
            f"result before reporting any retrieval state — the ceiling is an "
            f"observation, not an assumption (FD-4)."
        )
    raw = json.loads(p.read_text())
    return EgressStatus(
        web_search=bool(raw["web_search"]),
        web_fetch=bool(raw["web_fetch"]),
        probed_at=raw.get("probed_at", ""),
        detail=raw.get("detail", ""),
    )


@dataclass(frozen=True)
class RetrievalAssessment:
    attained: frozenset[RetrievalState]
    reachable: frozenset[RetrievalState]
    depth: EvidenceDepth | None
    evidence_count: int
    returned_count: int
    matched_count: int
    document_count: int
    independent_origins: int
    reasons: tuple[str, ...] = field(default_factory=tuple)
    flags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def headline(self) -> RetrievalState:
        return max(self.attained, key=lambda s: s.strength)

    @property
    def label(self) -> str:
        """How the state must appear in any report: never bare above RETRIEVAL.

        Printing `CLAIM_EVIDENCE_MATCH` without its depth is the exact conflation
        this module exists to prevent, so the depth is part of the label rather
        than an adjacent column somebody might drop.
        """
        h = self.headline
        if h is RetrievalState.NONE or self.depth is None:
            return h.value
        return f"{h.value}@{self.depth.value}"

    def attained_without(self) -> list[RetrievalState]:
        """States NOT attained that are weaker than the headline.

        The interesting case is `SOURCE_ACCESS` missing under a
        `CLAIM_EVIDENCE_MATCH` headline: the claim was matched against text
        nobody opened the source for.
        """
        h = self.headline
        return [s for s in _STRENGTH if s.strength < h.strength and s not in self.attained
                and s is not RetrievalState.NONE]

    def as_dict(self) -> dict:
        return {
            "headline": self.headline.value,
            "label": self.label,
            "attained": sorted(s.value for s in self.attained),
            "not_attained_below_headline": [s.value for s in self.attained_without()],
            "reachable": sorted(s.value for s in self.reachable),
            "depth": self.depth.value if self.depth else None,
            "evidence_count": self.evidence_count,
            "returned_count": self.returned_count,
            "matched_count": self.matched_count,
            "document_count": self.document_count,
            "independent_origins": self.independent_origins,
            "reasons": list(self.reasons),
            "flags": list(self.flags),
        }


def _independent_origins(ledger: list[Evidence]) -> int:
    """Distinct declared origins among claim-addressing evidence.

    Undeclared origin counts for nothing. Two sources whose provenance nobody
    recorded cannot be *shown* independent, and "we did not check" must never
    read as "they were different".
    """
    return len({
        e.origin.strip().lower()
        for e in ledger
        if e.returned and e.addressed_claim and e.origin and e.origin.strip()
    })


def assess(
    ledger: list[Evidence] | list[dict],
    egress: EgressStatus,
    tool_calls_observed: int | None = None,
) -> RetrievalAssessment:
    """Which states the evidence actually supports, checked against reachability."""
    items = [e if isinstance(e, Evidence) else Evidence.from_dict(e) for e in ledger]
    returned = [e for e in items if e.returned]
    matched = [e for e in returned if e.addressed_claim]
    documents = [e for e in returned if e.depth is EvidenceDepth.DOCUMENT]
    matched_docs = [e for e in matched if e.depth is EvidenceDepth.DOCUMENT]
    independent = _independent_origins(items)

    attained: set[RetrievalState] = {RetrievalState.NONE}
    reasons: list[str] = []
    depth: EvidenceDepth | None = None

    if not returned:
        reasons.append("no retrieval returned anything")
    else:
        attained.add(RetrievalState.RETRIEVAL)
        depth = EvidenceDepth.DOCUMENT if documents else EvidenceDepth.SNIPPET
        reasons.append(f"RETRIEVAL: {len(returned)} retrieval(s) returned results")

        if documents:
            attained.add(RetrievalState.SOURCE_ACCESS)
            reasons.append(f"SOURCE_ACCESS: {len(documents)} source document(s) fetched")
        else:
            reasons.append("no SOURCE_ACCESS: every result was a snippet, no document opened")

        if matched:
            attained.add(RetrievalState.CLAIM_EVIDENCE_MATCH)
            depth = EvidenceDepth.DOCUMENT if matched_docs else EvidenceDepth.SNIPPET
            reasons.append(
                f"CLAIM_EVIDENCE_MATCH: {len(matched)} item(s) addressed the specific "
                f"claim (deepest match: {depth.value})"
            )
        else:
            reasons.append("no CLAIM_EVIDENCE_MATCH: nothing returned addressed the specific claim")

        # Corroboration counts only at document depth. Two snippets off one
        # ranked result page are two views of a ranking, not two witnesses, and
        # independent witnesses are the entire content of VERIFICATION.
        if matched_docs and independent >= INDEPENDENCE_REQUIRED:
            attained.add(RetrievalState.VERIFICATION)
            reasons.append(
                f"VERIFICATION: {independent} independent declared origins at document "
                f"depth (threshold {INDEPENDENCE_REQUIRED})"
            )
        elif not matched_docs:
            reasons.append("no VERIFICATION: no claim match at document depth")
        else:
            reasons.append(
                f"no VERIFICATION: {independent} independent declared origin(s), "
                f"need {INDEPENDENCE_REQUIRED}"
            )

    flags: list[str] = []
    impossible = sorted(s.value for s in attained if s not in egress.reachable)
    if impossible:
        # Either the probe is stale or something bypassed the sandbox. Both are
        # serious; neither is resolved in favour of the nicer number.
        flags.append(
            f"UNREACHABLE-STATE: attained {', '.join(impossible)} which the probed "
            f"environment cannot produce. Either the egress probe is stale or the "
            f"sandbox leaked. Do not report this trial until resolved."
        )
    if tool_calls_observed is not None and len(items) < tool_calls_observed:
        flags.append(
            f"LEDGER-SHORT: {len(items)} evidence entries against {tool_calls_observed} "
            f"observed tool calls. The observed count stands; the ledger is incomplete."
        )

    return RetrievalAssessment(
        attained=frozenset(attained),
        reachable=egress.reachable,
        depth=depth,
        evidence_count=len(items),
        returned_count=len(returned),
        matched_count=len(matched),
        document_count=len(documents),
        independent_origins=independent,
        reasons=tuple(reasons),
        flags=tuple(flags),
    )


def negative_conclusion_licensed(about: RetrievalState, egress: EgressStatus) -> bool:
    """May a report conclude anything about `about` in this environment?

    Only if `about` was reachable. Concluding "verification does not help" from
    trials in which verification was impossible is the error this guards.
    """
    return about in egress.reachable


def licensed_claim(about: RetrievalState, egress: EgressStatus) -> str:
    """The strongest sentence a report is allowed to write about `about`."""
    if negative_conclusion_licensed(about, egress):
        return (
            f"Conclusions about {about.value} are licensed: it was reachable in this "
            f"environment (web_search={egress.web_search}, web_fetch={egress.web_fetch})."
        )
    return (
        f"NOT LICENSED: {about.value} was unreachable here "
        f"(web_search={egress.web_search}, web_fetch={egress.web_fetch}). No claim — "
        f"positive or negative — may be made about {about.value}. A null result may be "
        f"reported only about the states that were reachable: "
        f"{', '.join(sorted(s.value for s in egress.reachable if s is not RetrievalState.NONE))}."
    )
