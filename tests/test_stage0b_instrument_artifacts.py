"""The persisted Stage 0B instrument artifacts say what the repo claims they say.

These read committed evidence files. They do not dispatch. Their job is to stop
a claim in a document from drifting away from the artifact that earns it — the
failure mode that put "returns the block verbatim" into a reviewed design.
"""
from __future__ import annotations

import json
import pathlib

import yaml

from lab.causal_contract import load, validate
from lab.stage0b_fingerprint import COMPONENTS, audit

REPO = pathlib.Path(__file__).resolve().parent.parent
GATE = REPO / "experiments" / "exp004_stage0b" / "runtime_correspondence.json"
PROBE = REPO / "runs" / "exp004_stage0b_instrument" / "divergence_probe.json"
CONTRACT = REPO / "experiments" / "exp004_stage0b" / "causal_contract.yaml"
FINGERPRINTS = REPO / "experiments" / "exp004_stage0b" / "instrument_fingerprints.json"


class TestTheLiveGateEvidence:

    def test_the_gate_ran_and_recorded_fourteen_checks(self):
        d = json.loads(GATE.read_text())
        assert d["counts"]["total"] == 14
        assert d["counts"]["pass"] + d["counts"]["fail"] + d["counts"]["unobservable"] == 14

    def test_every_check_carries_a_status_from_the_declared_set(self):
        d = json.loads(GATE.read_text())
        for c in d["checks"]:
            assert c["status"] in {"PASS", "FAIL", "UNOBSERVABLE"}, c
            assert c["detail"], c["id"]

    def test_unobservable_is_never_counted_as_a_pass(self):
        d = json.loads(GATE.read_text())
        unobs = [c for c in d["checks"] if c["status"] == "UNOBSERVABLE"]
        assert d["counts"]["unobservable"] == len(unobs)
        assert d["counts"]["pass"] == 14 - len(unobs) - d["counts"]["fail"]

    def test_the_gate_recorded_real_dispatches_not_a_config_read(self):
        d = json.loads(GATE.read_text())
        live = d["live_records"]
        for role in ("query_writer", "search_C", "search_D", "answerer_C"):
            assert role in live
        # a real dispatch has a session id, a served model and a token count
        assert live["query_writer"]["session_id"]
        assert live["query_writer"]["models_used"]
        assert live["answerer_C"]["output_tokens"]

    def test_the_search_indicator_came_from_the_authoritative_field(self):
        d = json.loads(GATE.read_text())
        for role in ("search_C", "search_D"):
            r = d["live_records"][role]
            assert r["web_search_requests"] >= 1
            # the defective field is recorded, and it disagrees — which is the point
            assert r["server_tool_use"]["web_search_requests"] == 0

    def test_both_arms_used_the_same_searcher_and_the_same_realized_surface(self):
        d = json.loads(GATE.read_text())
        c, dd = d["live_records"]["search_C"], d["live_records"]["search_D"]
        assert c["agent"] == dd["agent"] == "stage0b-searcher"
        assert c["realized_tool_surface"] == dd["realized_tool_surface"] == ["WebSearch"]
        assert c["query_text"] != dd["query_text"], "C and D must differ in the query"

    def test_no_stage0b_role_has_file_access(self):
        d = json.loads(GATE.read_text())
        for probe in ("query_writer_probe", "answerer_probe"):
            assert d["live_records"][probe]["report"]["can_read_files"] is False
            assert d["live_records"][probe]["report"]["tools"] == []

    def test_the_construct_is_not_called_web_retrieval_or_snippets(self):
        text = GATE.read_text()
        assert "runtime_exposed_search_result_block" in text
        assert "unrestricted web retrieval" in text   # only ever as a disclaimer
        for c in json.loads(text)["checks"]:
            assert "snippet" not in c["check"].lower()


class TestTheDivergenceProbeEvidence:

    def test_the_probe_dispatched_no_solver_and_produced_no_outcome(self):
        d = json.loads(PROBE.read_text())
        assert d["pre_treatment"] is True
        assert d["solver_dispatched"] is False
        assert d["answers_generated"] == 0
        for r in d["results"]:
            assert r["no_answerer_dispatched"] is True
            assert r["no_outcome_generated"] is True
            assert r["agent_spawned"] == "stage0b-searcher"

    def test_it_ran_only_on_items_barred_from_production(self):
        d = json.loads(PROBE.read_text())
        assert d["production_barred"] is True
        spec = yaml.safe_load(
            (REPO / "experiments" / "exp004_stage0b" / "divergence_canaries.yaml").read_text())
        canary_ids = {i["id"] for i in spec["items"]}
        assert {r["item_id"] for r in d["results"]} <= canary_ids

    def test_every_result_persists_both_hashes_and_the_realized_query(self):
        d = json.loads(PROBE.read_text())
        for r in d["results"]:
            assert r["raw_artifact_sha"] and r["injected_block_sha"]
            assert r["raw_artifact_sha"] != r["injected_block_sha"]
            assert r["realized_query"] == r["fixed_query"], "query fidelity"

    def test_it_used_the_same_search_mechanism_arm_D_will_use(self):
        d = json.loads(PROBE.read_text())
        assert "the same function and agent arm D uses" in d["search_mechanism"]

    def test_the_probe_can_return_non_divergent_and_did(self):
        """A probe that always says yes measures nothing."""
        d = json.loads(PROBE.read_text())
        assert any(not r["divergent"] for r in d["results"])
        assert any(r["divergent"] for r in d["results"])

    def test_its_predictions_were_recorded_before_it_ran_and_are_scored(self):
        d = json.loads(PROBE.read_text())
        for r in d["results"]:
            assert r["expected_divergence"] is not None
            assert r["prediction_matched"] is not None

    def test_the_selection_rule_is_on_the_summary_not_the_whole_block(self):
        d = json.loads(PROBE.read_text())
        assert "RUNTIME-SYNTHESISED SUMMARY" in d["selection_rule"]
        assert "Ada Lovelace (1815 - 1852)" in d["selection_rule"]


class TestTheContract:

    def test_the_stage0b_contract_is_valid(self):
        assert validate(load(CONTRACT), REPO) == []

    def test_it_is_still_a_draft_and_not_freeze_ready(self):
        c = load(CONTRACT)
        assert c["status"] == "draft"
        assert c["open_fields"], "a draft with nothing open is a freeze_ready in disguise"

    def test_the_things_that_are_genuinely_unbuilt_are_still_open(self):
        text = CONTRACT.read_text()
        for unbuilt in ("calibration bank", "grader freeze", "power re-derived",
                        "production items"):
            assert unbuilt in text

    def test_the_query_writer_edge_to_outcome_is_declared_absent_and_checked(self):
        c = load(CONTRACT)
        edges = {tuple(e["edge"]): e for e in c["assumed_absent_edges"]}
        e = edges[("query_writer", "outcome")]
        assert e["check"]["type"] == "live_probe"
        assert "runtime_correspondence.json" in e["check"]["artifact"]

    def test_the_header_query_path_is_declared_rather_than_left_to_be_found(self):
        c = load(CONTRACT)
        edges = {tuple(e["edge"]): e for e in c["assumed_absent_edges"]}
        note = edges[("query_writer", "outcome")]["check"]["note"]
        assert "echoes the query in" in note

    def test_the_retired_verbatim_construct_is_gone(self):
        c = load(CONTRACT)
        names = {b["construct"] for b in c["bindings"]}
        assert "searcher_verbatim_return" not in names
        assert "searcher_c_d_symmetry" in names
        assert "runtime_exposed_search_result_block_exposure" in names
        assert "search_snippet_exposure_treatment" not in names

    def test_the_cvd_binding_records_that_it_currently_fails(self):
        text = CONTRACT.read_text()
        assert "c_vs_d_inferential_requirement" in text
        assert "CURRENTLY FAILS ON THE ASSUMED DESIGN POINT" in text


class TestTheInstrumentFingerprints:

    def test_every_declared_component_exists_and_is_hashed(self):
        d = audit()
        assert d["missing"] == []
        assert set(d["components"]) == set(COMPONENTS)
        for rel, v in d["components"].items():
            assert len(v["sha16"]) == 16 and v["bytes"] > 0
            assert v["load_bearing_for"], rel

    def test_the_committed_file_matches_a_fresh_recomputation(self):
        committed = json.loads(FINGERPRINTS.read_text())
        fresh = audit()
        assert committed["combined_sha16"] == fresh["combined_sha16"], (
            "regenerate with `python -m lab.stage0b_fingerprint` after touching the "
            "instrument")

    def test_the_set_does_not_claim_to_be_frozen(self):
        d = json.loads(FINGERPRINTS.read_text())
        assert d["frozen"] is False
        assert "calibration bank" in d["why_not_frozen"]
