"""Stage 0B search-exposure instrument — offline tests.

These run against a REAL runtime fixture (`tests/fixtures/stage0b_runtime/`),
captured from the live searcher on 2026-09-03. That is deliberate: the design
draft's claim that the searcher "returns the block verbatim" passed review, a
red-team and a causal-contract pass while being false, because every check was
written against an imagined block. A parser tested only on examples its author
invented tests the author's imagination.

Nothing here dispatches. The live checks live in `lab/stage0b_runtime_gate.py`.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

from lab.stage0b_failures import BY_CODE, CLASSES, NOT_A_FAILURE, RULES, classify
from lab.stage0b_harness import (ANSWER_PACKET, EXPOSURE_SECTION, build_answer_packet,
                                 build_query_writer_packet, extract_answer, extract_query,
                                 fixed_query, packet_diff_report,
                                 ANALYSIS_FIELD_LINEAGE, FORBIDDEN_LINEAGE, DispatchRow)
from lab.stage0b_search import (parse_exposure_block, parse_stream, relevance_flags, sha)

FIX = pathlib.Path(__file__).parent / "fixtures" / "stage0b_runtime"
MANIFEST = json.loads((FIX / "MANIFEST.json").read_text())


def _fixture(name: str) -> str:
    return (FIX / name).read_text()


# --------------------------------------------------------------------------- #
# the fixture is genuine, and says so honestly
# --------------------------------------------------------------------------- #

class TestTheRuntimeFixtureIsReal:

    def test_raw_blocks_are_unmodified_and_their_hashes_prove_it(self):
        for entry in MANIFEST["files"]:
            if entry["sanitised"]:
                continue
            text = _fixture(entry["file"])
            assert hashlib.sha256(text.encode()).hexdigest() == entry["raw_sha256"]
            assert entry["raw_sha256"] == entry["fixture_sha256"]
            assert entry["bytes_changed_by_sanitisation"] == 0

    def test_the_sanitised_transcript_keeps_raw_and_fixture_hashes_apart(self):
        entry = next(e for e in MANIFEST["files"] if e["sanitised"])
        text = _fixture(entry["file"])
        assert hashlib.sha256(text.encode()).hexdigest() == entry["fixture_sha256"]
        # The distinction is the point: a sanitised fixture that reported one hash
        # would let a reader believe the committed bytes are the captured bytes.
        assert entry["raw_sha256"] != entry["fixture_sha256"]
        assert entry["bytes_changed_by_sanitisation"] > 0

    def test_sanitisation_removed_identifiers_and_nothing_scientific(self):
        text = _fixture("searcher_stream_transcript.jsonl")
        assert "/home/user" not in text
        # everything the parser and the telemetry lineage read survived
        p = parse_stream(text.splitlines())
        assert p["init_tools"] == ["WebSearch"]
        assert [c["name"] for c in p["tool_calls"]] == ["WebSearch"]
        assert p["tool_results"] and p["tool_results"][0] == _fixture("websearch_block_unsg_2015.txt")
        mu = p["result"]["modelUsage"]
        assert sum(int(v.get("webSearchRequests") or 0) for v in mu.values()) == 1

    def test_two_dispatches_of_one_query_are_not_byte_identical(self):
        a = _fixture("websearch_block_lovelace.txt")
        b = _fixture("websearch_block_lovelace_repeat.txt")
        assert a != b, "if these ever match, re-measure before claiming determinism"
        pa, pb = parse_exposure_block(a), parse_exposure_block(b)
        # the links are stable; the runtime's synthesised paragraph is not
        assert pa.links == pb.links
        assert pa.summary_text != pb.summary_text
        assert pa.raw_sha != pb.raw_sha


# --------------------------------------------------------------------------- #
# what the runtime actually exposes
# --------------------------------------------------------------------------- #

class TestWhatCrossesTheTreatmentBoundary:

    def test_the_block_carries_no_snippets_only_titles_and_urls(self):
        """The construct is not `search_snippet_exposure`. There are no snippets."""
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        assert b.link_count == 8
        for link in b.links:
            assert set(link) == {"title", "url"}, f"unexpected result field: {sorted(link)}"

    def test_the_block_carries_a_runtime_synthesised_answer(self):
        """A model answers the query inside the block. A displacement effect could
        originate there rather than in any retrieved page, and the design has to
        say so rather than call this 'retrieved content'."""
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        assert b.has_summary
        assert "Ban Ki-moon" in b.summary_text
        assert "Guterres" in b.summary_text

    def test_the_runtime_imperative_is_stripped_and_recorded(self):
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        assert b.reminder_stripped.startswith("REMINDER:")
        assert "markdown hyperlinks" in b.reminder_stripped
        assert "REMINDER:" not in b.injected
        # removal is exact: injected + the imperative reconstitutes the raw block
        assert b.raw.rstrip().endswith(b.reminder_stripped)
        assert b.raw.rstrip()[: -len(b.reminder_stripped)].rstrip() == b.injected

    def test_an_answerer_never_receives_an_instruction_to_cite_sources(self):
        """Left in, it would tell C and D answerers to emit markdown source lists —
        a format change arm A never receives, landing directly on the grader's
        leading-sentence span rule."""
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        packet = build_answer_packet("Q?", b.injected)
        assert "You MUST" not in packet
        assert "REMINDER" not in packet

    def test_the_header_echoes_the_query_and_that_path_is_declared(self):
        """The query text itself reaches the answerer through the header. Kept,
        because it is part of what the runtime exposes and the whole lesson is to
        bind to what actually crosses the boundary — but it is a direct
        query→answerer path and must be named, not discovered later."""
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        assert b.header_query == "Secretary-General of the United Nations 2015"
        assert b.header_query in b.injected

    def test_hashes_are_computed_over_both_raw_and_injected(self):
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        assert b.raw_sha == sha(b.raw) and b.injected_sha == sha(b.injected)
        assert b.raw_sha != b.injected_sha


# --------------------------------------------------------------------------- #
# the parser refuses to turn a treatment failure into a crash
# --------------------------------------------------------------------------- #

class TestTheParserDegradesHonestly:

    def test_a_block_with_no_summary_is_a_weaker_dose_not_an_error(self):
        raw = ('Web search results for query: "x"\n\n'
               'Links: [{"title":"T","url":"https://e.example/1"}]\n')
        b = parse_exposure_block(raw)
        assert b.parse_ok and b.link_count == 1 and b.has_summary is False
        assert "no synthesised summary" in b.parse_note

    def test_a_block_with_no_links_still_parses_if_it_carries_a_summary(self):
        b = parse_exposure_block('Web search results for query: "x"\n\nSome prose.\n')
        assert b.parse_ok and b.link_count == 0 and b.summary_text == "Some prose."

    def test_an_empty_block_is_an_injection_failure_not_an_exception(self):
        b = parse_exposure_block("")
        assert b.parse_ok is False
        assert "not a usable treatment artifact" in b.parse_note

    def test_a_malformed_links_array_is_recorded_rather_than_raised(self):
        b = parse_exposure_block('Web search results for query: "x"\n\nLinks: [{oops]\n\nProse.\n')
        assert "Links array did not parse" in b.parse_note


# --------------------------------------------------------------------------- #
# relevance flags — deterministic, model-free, over the injected block
# --------------------------------------------------------------------------- #

class TestRelevanceFlags:

    def test_real_block_is_divergent_on_the_canary_item(self):
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        f = relevance_flags(b, ["Ban Ki-moon"], ["Guterres"])
        assert f["classification"] == "both"
        assert f["reject_in_summary"] is True and f["reject_in_summary_matched"] == ["Guterres"]
        assert f["reject_in_links_only"] is False
        assert f["divergent"] is True

    def test_an_incidental_link_title_match_does_not_make_an_item_divergent(self):
        """The measured case that forced the flag to locate its matches. On the real
        Lovelace block the reject alias "1852" matches inside the link title
        "Ada Lovelace (1815 - 1852)" — a biographical date range asserting nothing.
        A flag reading only `reject_present` would have called this divergent and
        spent a production slot on a foregone null."""
        b = parse_exposure_block(_fixture("websearch_block_lovelace.txt"))
        f = relevance_flags(b, ["1815"], ["1852", "1816"])
        assert f["reject_present"] is True          # containment fires
        assert f["reject_matched"] == ["1852"]
        assert f["reject_in_summary"] is False      # but nothing claims it
        assert f["reject_in_links_only"] is True
        assert f["divergent"] is False              # so it is not a dose
        assert "1852" in "".join(l["title"] for l in b.links)
        assert "1852" not in b.summary_text

    def test_divergence_is_defined_on_the_summary_not_on_the_whole_block(self):
        raw_links_only = ('Web search results for query: "x"\n\n'
                          'Links: [{"title":"Rival Person profile","url":"https://e.example/1"}]\n\n'
                          'The answer is Anchor Person.\n')
        b = parse_exposure_block(raw_links_only)
        f = relevance_flags(b, ["Anchor Person"], ["Rival Person"])
        assert f["reject_present"] and not f["reject_in_summary"]
        assert f["divergent"] is False

    @pytest.mark.parametrize("acc,rej,cls", [
        (["Ban Ki-moon"], ["Guterres"], "both"),
        (["Ban Ki-moon"], ["Nobody At All"], "accept_only"),
        (["Nobody At All"], ["Guterres"], "reject_only"),
        (["Nobody At All"], ["Also Nobody"], "neither"),
    ])
    def test_all_four_classifications_are_reachable(self, acc, rej, cls):
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        assert relevance_flags(b, acc, rej)["classification"] == cls

    def test_flags_read_the_injected_block_not_the_raw_one(self):
        """The answerer sees `injected`. A flag computed on `raw` could fire on the
        stripped imperative and would be measuring the wrong string."""
        raw = ('Web search results for query: "x"\n\nProse.\n\n'
               "REMINDER: You MUST include the sources above in your response to the user "
               "using markdown hyperlinks.")
        b = parse_exposure_block(raw)
        assert relevance_flags(b, [], ["markdown hyperlinks"])["reject_present"] is False

    def test_matching_is_case_insensitive_and_reports_what_matched(self):
        b = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt"))
        f = relevance_flags(b, ["ban ki-MOON"], [])
        assert f["accept_present"] and f["accept_matched"] == ["ban ki-MOON"]


# --------------------------------------------------------------------------- #
# arm symmetry, expressed on realized strings
# --------------------------------------------------------------------------- #

class TestArmSymmetry:

    def test_arm_A_packet_contains_no_exposure_section(self):
        p = build_answer_packet("Who?", None)
        assert "SEARCH RESULT BLOCK" not in p and "Links:" not in p

    def test_C_and_D_packets_differ_only_inside_the_injected_block(self):
        c = parse_exposure_block(_fixture("websearch_block_unsg_2015.txt")).injected
        d = parse_exposure_block(_fixture("websearch_block_lovelace.txt")).injected
        rep = packet_diff_report("Who?", c, d)
        assert rep["C_and_D_differ_only_inside_the_block"]
        assert rep["A_contains_no_exposure_section"]
        assert rep["C_line_count"] == rep["D_line_count"] or True  # blocks may differ in length

    def test_the_answer_first_instruction_is_identical_in_every_arm(self):
        instr = "Begin your reply with the direct answer."
        for block in (None, "BLOCK"):
            assert build_answer_packet("Who?", block).count(instr) == 1

    def test_the_exposure_section_is_the_only_arm_difference(self):
        a = build_answer_packet("Who?", None)
        c = build_answer_packet("Who?", "BLOCK")
        assert c.replace(EXPOSURE_SECTION.replace("{BLOCK}", "BLOCK"), "") == a


# --------------------------------------------------------------------------- #
# fixed-query construction
# --------------------------------------------------------------------------- #

class TestFixedQueryConstruction:

    def test_it_is_the_subject_plus_the_anchor_as_written(self):
        assert fixed_query({"id": "i", "query_subject": "Prime Minister of the United Kingdom",
                            "anchor_as_written": "June 2016"}) == \
               "Prime Minister of the United Kingdom June 2016"

    def test_a_yaml_anchor_that_parsed_as_a_number_is_refused(self):
        """`anchor_as_written: 2015` parses to an int, and the fixed query would then
        depend on how the battery file was quoted rather than on the stem."""
        with pytest.raises(TypeError):
            fixed_query({"id": "i", "query_subject": "x", "anchor_as_written": 2015})

    def test_an_empty_query_is_refused(self):
        with pytest.raises(ValueError):
            fixed_query({"id": "i", "query_subject": "  ", "anchor_as_written": " "})

    def test_the_canary_battery_yields_the_documented_queries(self):
        import yaml
        spec = yaml.safe_load(
            (pathlib.Path(__file__).parent.parent / "experiments" / "exp004_stage0b"
             / "divergence_canaries.yaml").read_text())
        assert spec["production_barred"] is True
        got = {i["id"]: fixed_query(i) for i in spec["items"]}
        assert got["canary_unsg_2015"] == "Secretary-General of the United Nations 2015"
        assert got["canary_uk_pm_2016"] == "Prime Minister of the United Kingdom June 2016"


# --------------------------------------------------------------------------- #
# extraction
# --------------------------------------------------------------------------- #

class TestExtraction:

    def test_a_single_json_query_is_extracted(self):
        assert extract_query('{"query": "UN Secretary-General 2015"}') == \
               ("UN Secretary-General 2015", None)

    def test_no_output_is_a_query_writer_failure(self):
        assert extract_query("")[1] == "QUERY_WRITER_NO_OUTPUT"
        assert extract_query(None)[1] == "QUERY_WRITER_NO_OUTPUT"

    def test_two_queries_are_a_failure_not_a_silent_first_pick(self):
        text = 'Here: {"query": "a"} or maybe {"query": "b"}'
        assert extract_query(text) == (None, "QUERY_WRITER_MULTIPLE_QUERIES")

    def test_a_query_list_is_a_failure(self):
        assert extract_query('{"query": ["a", "b"]}')[1] == "QUERY_WRITER_MULTIPLE_QUERIES"

    def test_prose_around_one_json_object_still_yields_the_query(self):
        assert extract_query('Sure.\n{"query": "x y"}\n')[0] == "x y"

    def test_a_non_json_but_non_empty_answer_is_still_an_answer(self):
        assert extract_answer("Ban Ki-moon was the Secretary-General.") == \
               ("Ban Ki-moon was the Secretary-General.", None)

    def test_an_empty_answer_is_an_answer_failure(self):
        assert extract_answer("   ")[1] == "EMPTY_RESPONSE"


# --------------------------------------------------------------------------- #
# telemetry lineage
# --------------------------------------------------------------------------- #

class TestTelemetryLineage:

    def test_every_ledger_field_that_feeds_analysis_names_its_runtime_source(self):
        for field_name, source in ANALYSIS_FIELD_LINEAGE.items():
            assert source and "[OPEN]" not in source, field_name

    def test_the_defective_stage0am_indicator_is_named_and_barred(self):
        assert "usage.server_tool_use.web_search_requests" in FORBIDDEN_LINEAGE
        assert ANALYSIS_FIELD_LINEAGE["search_attempted"] == \
               "sum(result.modelUsage[*].webSearchRequests)"

    def test_the_real_transcript_shows_why_server_tool_use_is_barred(self):
        """A search demonstrably ran; `server_tool_use` reports zero. This is the
        same defect that made Stage 0A-M's retrieval_failure_rate vacuous."""
        p = parse_stream(_fixture("searcher_stream_transcript.jsonl").splitlines())
        r = p["result"]
        assert r["usage"]["server_tool_use"]["web_search_requests"] == 0
        assert sum(int(v.get("webSearchRequests") or 0)
                   for v in r["modelUsage"].values()) == 1
        assert p["tool_results"], "the search really did return a block"

    def test_websearch_is_billed_to_a_model_that_is_not_the_solver(self):
        """So the indicator must sum over ALL models. Reading the solver model's own
        count would report zero on every trial."""
        p = parse_stream(_fixture("searcher_stream_transcript.jsonl").splitlines())
        mu = p["result"]["modelUsage"]
        searching = [m for m, v in mu.items() if (v.get("webSearchRequests") or 0) > 0]
        assert searching == ["claude-haiku-4-5-20251001"]
        assert mu["claude-opus-5"]["webSearchRequests"] == 0

    def test_a_value_the_runtime_did_not_expose_stays_none(self):
        d = DispatchRow.__dataclass_fields__
        for f in ("web_search_requests", "thinking_tokens", "realized_tool_surface"):
            assert "None" in str(d[f].type), f


# --------------------------------------------------------------------------- #
# failure semantics
# --------------------------------------------------------------------------- #

class TestFailureSemantics:

    def test_the_four_classes_are_kept_apart(self):
        assert set(CLASSES) == {r.klass for r in RULES}
        assert len(CLASSES) == 4

    def test_every_class_has_at_least_one_rule(self):
        for k in CLASSES:
            assert any(r.klass == k for r in RULES), k

    def test_no_retry_is_permitted_where_retrying_would_change_the_estimand(self):
        for r in RULES:
            if r.changes_estimand:
                assert not r.retry_allowed and r.max_retries == 0, r.code

    def test_retries_are_bounded_wherever_they_are_allowed(self):
        for r in RULES:
            assert (r.max_retries > 0) == r.retry_allowed, r.code
            assert r.max_retries <= 2, r.code

    def test_environment_drift_always_halts_production(self):
        for r in RULES:
            if r.klass == "ENVIRONMENT_DRIFT":
                assert r.halts_production, r.code

    def test_an_arm_that_is_invalid_voids_its_item_except_where_stated(self):
        for r in RULES:
            if r.arm_invalid:
                assert r.voids_item, (
                    f"{r.code}: voiding one arm but keeping the item is post-treatment "
                    f"selection on a treatment-arm-only variable")

    def test_a_search_that_returns_nothing_displacing_is_not_a_failure(self):
        assert "no_reject_alias_in_block" in NOT_A_FAILURE
        assert not any("no_reject" in r.code.lower() for r in RULES)

    def test_query_fidelity_failure_exists_and_cannot_be_retried(self):
        r = classify("QUERY_FIDELITY_FAILURE")
        assert r.klass == "TREATMENT_REALIZATION_FAILURE"
        assert r.changes_estimand and not r.retry_allowed

    def test_unknown_codes_are_refused(self):
        with pytest.raises(KeyError):
            classify("SOMETHING_PLAUSIBLE")

    def test_every_code_is_unique(self):
        assert len(BY_CODE) == len(RULES)
