"""Four retrieval states that must never be reported as each other.

The tests that matter here are the negative ones: a snippet must not become
SOURCE_ACCESS, corroboration must not be counted from undeclared origins, and no
conclusion may be drawn about a state the environment made impossible.
"""

from __future__ import annotations

import json

import pytest

from lab.states import (
    EGRESS_PROBE_PATH,
    INDEPENDENCE_REQUIRED,
    EgressStatus,
    Evidence,
    EvidenceDepth,
    RetrievalState,
    assess,
    licensed_claim,
    load_egress,
    negative_conclusion_licensed,
)

SEARCH_ONLY = EgressStatus(web_search=True, web_fetch=False)
FULL = EgressStatus(web_search=True, web_fetch=True)
CLOSED = EgressStatus(web_search=False, web_fetch=False)


def _snip(**kw):
    return Evidence(query="q", returned=True, depth=EvidenceDepth.SNIPPET, **kw)


def _doc(**kw):
    return Evidence(query="q", returned=True, depth=EvidenceDepth.DOCUMENT, **kw)


class TestStatesAreNotOneLadder:
    def test_a_snippet_match_attains_claim_evidence_match_without_source_access(self):
        """The case that broke the first draft. A linear ladder had to call this
        either impossible or a sandbox breach; it is neither, it is the ordinary
        search-only case, and it is the weak-evidence situation worth naming."""
        a = assess([_snip(addressed_claim=True, origin="bbc")], SEARCH_ONLY)
        assert RetrievalState.CLAIM_EVIDENCE_MATCH in a.attained
        assert RetrievalState.SOURCE_ACCESS not in a.attained
        assert a.attained_without() == [RetrievalState.SOURCE_ACCESS]
        assert not a.flags

    def test_the_label_always_carries_its_depth(self):
        assert assess([_snip(addressed_claim=True)], SEARCH_ONLY).label == \
            "CLAIM_EVIDENCE_MATCH@SNIPPET"
        assert assess([_doc(addressed_claim=True)], FULL).label == \
            "CLAIM_EVIDENCE_MATCH@DOCUMENT"

    def test_a_snippet_is_never_source_access(self):
        a = assess([_snip(), _snip(), _snip()], SEARCH_ONLY)
        assert a.attained == frozenset({RetrievalState.NONE, RetrievalState.RETRIEVAL})
        assert "no SOURCE_ACCESS" in " ".join(a.reasons)


class TestVerification:
    def test_two_independent_documents_reach_verification(self):
        a = assess(
            [_doc(addressed_claim=True, origin="reuters"), _doc(addressed_claim=True, origin="ap")],
            FULL,
        )
        assert RetrievalState.VERIFICATION in a.attained
        assert a.independent_origins == INDEPENDENCE_REQUIRED

    def test_two_snippets_do_not(self):
        """Two snippets off one ranked result page are two views of a ranking,
        not two witnesses."""
        a = assess(
            [_snip(addressed_claim=True, origin="reuters"), _snip(addressed_claim=True, origin="ap")],
            FULL,
        )
        assert RetrievalState.VERIFICATION not in a.attained
        assert "no claim match at document depth" in " ".join(a.reasons)

    def test_the_same_origin_twice_is_one_source(self):
        a = assess(
            [_doc(addressed_claim=True, origin="Reuters"), _doc(addressed_claim=True, origin="reuters")],
            FULL,
        )
        assert a.independent_origins == 1
        assert RetrievalState.VERIFICATION not in a.attained

    def test_undeclared_origins_count_for_nothing(self):
        """"We did not record provenance" must never read as "they were
        different sources"."""
        a = assess([_doc(addressed_claim=True), _doc(addressed_claim=True)], FULL)
        assert a.independent_origins == 0
        assert RetrievalState.VERIFICATION not in a.attained


class TestReachability:
    def test_search_only_cannot_reach_source_access_or_verification(self):
        assert SEARCH_ONLY.unreachable == frozenset(
            {RetrievalState.SOURCE_ACCESS, RetrievalState.VERIFICATION}
        )

    def test_no_tools_reaches_nothing(self):
        assert CLOSED.reachable == frozenset({RetrievalState.NONE})

    def test_a_state_above_the_environment_is_flagged_not_accepted(self):
        a = assess([_doc(addressed_claim=True, origin="a")], SEARCH_ONLY)
        assert any("UNREACHABLE-STATE" in f for f in a.flags)

    def test_no_negative_conclusion_about_an_unreachable_state(self):
        assert negative_conclusion_licensed(RetrievalState.RETRIEVAL, SEARCH_ONLY)
        assert not negative_conclusion_licensed(RetrievalState.VERIFICATION, SEARCH_ONLY)
        claim = licensed_claim(RetrievalState.VERIFICATION, SEARCH_ONLY)
        assert claim.startswith("NOT LICENSED")
        assert "positive or negative" in claim

    def test_licensed_claim_names_what_may_be_said_instead(self):
        claim = licensed_claim(RetrievalState.VERIFICATION, SEARCH_ONLY)
        assert "RETRIEVAL" in claim


class TestAudit:
    def test_a_ledger_shorter_than_the_observed_count_is_flagged(self):
        a = assess([_snip()], SEARCH_ONLY, tool_calls_observed=4)
        assert any("LEDGER-SHORT" in f for f in a.flags)
        assert "1 evidence entries against 4" in " ".join(a.flags)

    def test_the_observed_count_is_not_corrected_by_the_ledger(self):
        a = assess([_snip()], SEARCH_ONLY, tool_calls_observed=4)
        assert "The observed count stands" in " ".join(a.flags)

    def test_nothing_returned_is_state_none(self):
        a = assess([Evidence(query="q", returned=False)], SEARCH_ONLY)
        assert a.attained == frozenset({RetrievalState.NONE})
        assert a.label == "NONE"


class TestEgressArtefact:
    def test_a_missing_probe_refuses_rather_than_defaults(self, tmp_path):
        """Defaulting to blocked silently licenses the weaker reading and
        defaulting to open the stronger one. Refuse until somebody has probed."""
        with pytest.raises(FileNotFoundError, match="egress probe"):
            load_egress(tmp_path / "nope.json")

    def test_the_committed_probe_is_present_and_readable(self):
        status = load_egress()
        assert status.probed_at
        assert len(status.detail) > 200, "a probe artefact must carry its evidence"

    def test_the_committed_probe_matches_what_this_environment_does(self):
        """Recorded from three EGRESS_BLOCKED responses on three unrelated hosts
        plus one successful search. If this ever flips, cell D's reachable set
        changes and the probe must be re-run before anything is concluded."""
        raw = json.loads(EGRESS_PROBE_PATH.read_text())
        assert raw["web_search"] is True
        assert raw["web_fetch"] is False
        assert raw["ceiling"] == "CLAIM_EVIDENCE_MATCH"
        assert sorted(raw["unreachable"]) == ["SOURCE_ACCESS", "VERIFICATION"]

    def test_round_trip_through_the_artefact(self):
        assert load_egress().reachable == SEARCH_ONLY.reachable
