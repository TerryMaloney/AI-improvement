"""Stage 0A-M candidate battery: structure, key quarantine, grading, schedule.

Nothing here dispatches. The grading tests exercise every authored key against
its own accepted phrasing and against the specific wrong answer the mechanism
predicts -- the current officeholder instead of the anchored one, the
alternative-definition quantity instead of the requested one. An item whose
displacing answer would grade as correct is a broken item, not a finding.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest
import yaml

from lab.anchored_grading import (NUMBER_WORDS, extract_numbers, grade,
                                  grade_numeric, normalise)

REPO = pathlib.Path(__file__).resolve().parent.parent
BATTERY = yaml.safe_load((REPO / "batteries" / "anchored_v1.yaml").read_text())
KEYS = yaml.safe_load((REPO / "batteries" / "answers.anchored_v1.yaml").read_text())["answers"]
MANIFEST = json.loads((REPO / "experiments" / "exp004_stage0am" / "manifest.json").read_text())
SCHEDULE = json.loads((REPO / "experiments" / "exp004_stage0am" / "schedule.json").read_text())
DIFF = json.loads((REPO / "experiments" / "exp004_stage0am" / "arm_packet_diff.json").read_text())
PROV = (REPO / "docs" / "EXP004_STAGE0A_M_KEY_PROVENANCE.md").read_text()
Q = BATTERY["questions"]


def by_class(c):
    return [q for q in Q if q["class"] == c]


class TestComposition:
    def test_exact_class_counts(self):
        assert len(by_class("date_anchored")) == 25
        assert len(by_class("definition_anchored")) == 25
        assert len(by_class("arithmetic_control")) == 15
        assert len(Q) == 65

    def test_manifest_counts_match_the_generated_battery(self):
        c = MANIFEST["counts"]
        assert c["date_anchored"] == len(by_class("date_anchored"))
        assert c["definition_anchored"] == len(by_class("definition_anchored"))
        assert c["arithmetic_control"] == len(by_class("arithmetic_control"))
        assert c["total_dispatches"] == len(Q) * 2 == 130

    def test_one_class_per_item_and_no_duplicate_ids_or_stems(self):
        assert len({q["id"] for q in Q}) == 65
        assert len({normalise(q["text"]) for q in Q}) == 65

    def test_control_is_outside_the_holm_family(self):
        assert MANIFEST["holm_family"] == ["date_anchored", "definition_anchored"]
        assert MANIFEST["outside_holm_family"] == ["arithmetic_control"]

    def test_every_item_declares_a_route_before_dispatch(self):
        assert all(q["grading_route"] in {"exact_entity", "numeric", "boolean"} for q in Q)


class TestKeyQuarantine:
    def test_no_item_stem_contains_its_own_answer(self):
        """Scoped per item, because a trial packet carries exactly one question.
        An answer appearing in a DIFFERENT item's stem is not a leak; an answer
        appearing in its own stem hands the solver the answer."""
        leaks = []
        for q in Q:
            stem = normalise(q["text"])
            for phrase in KEYS[q["id"]].get("accept", []):
                n = normalise(phrase)
                if len(n) >= 5 and n in stem:
                    leaks.append((q["id"], phrase))
        assert not leaks, f"stems containing their own answer: {leaks}"

    def test_no_stem_reveals_another_items_answer_within_the_same_class(self):
        """Weaker cross-item check, reported rather than fatal: two items in one
        class sharing an entity narrows the class's effective diversity."""
        overlaps = []
        for a in Q:
            for b in Q:
                if a["id"] >= b["id"] or a["class"] != b["class"]:
                    continue
                for phrase in KEYS[b["id"]].get("accept", []):
                    n = normalise(phrase)
                    if len(n) >= 5 and n in normalise(a["text"]):
                        overlaps.append((a["id"], b["id"], phrase))
        assert len(overlaps) <= 2, f"too many within-class entity overlaps: {overlaps}"

    def test_battery_file_carries_route_names_only(self):
        for q in Q:
            assert set(q) == {"id", "class", "subtype", "domain", "text", "grading_route"}

    def test_every_item_has_a_key(self):
        assert {q["id"] for q in Q} == set(KEYS)


class TestGradingEveryAuthoredKey:
    """Each key must accept its own answer and reject the displacing one."""

    @pytest.mark.parametrize("qid", [q["id"] for q in Q])
    def test_route_is_implementable_and_deterministic(self, qid):
        g = KEYS[qid]
        item = {"grading": g}
        if g["route"] == "exact_entity":
            assert grade(item, g["accept"][0])
        elif g["route"] == "numeric":
            assert grade(item, f"The answer is {g['value']}.")
        else:
            assert grade(item, "Yes." if g["expected"] else "No.")

    @pytest.mark.parametrize("qid", [q["id"] for q in Q])
    def test_the_predicted_wrong_answer_fails(self, qid):
        g = KEYS[qid]
        item = {"grading": g}
        if g["route"] == "exact_entity":
            for r in g.get("rejects", []):
                assert not grade(item, f"The answer is {r}."), f"{qid}: reject {r!r} graded correct"
        elif g["route"] == "numeric":
            for r in g.get("rejects", []):
                assert not grade(item, f"The answer is {r}."), f"{qid}: reject {r} graded correct"
        else:
            assert not grade(item, "No." if g["expected"] else "Yes.")

    @pytest.mark.parametrize("qid", [q["id"] for q in Q if KEYS[q["id"]]["route"] == "exact_entity"])
    def test_capitalisation_and_punctuation_are_harmless(self, qid):
        g = KEYS[qid]
        a = g["accept"][0]
        assert grade({"grading": g}, f"  {a.upper()}!  ")
        assert grade({"grading": g}, f"It was {a.lower()}, I believe.")

    def test_lexical_exactness_does_not_masquerade_as_correctness(self):
        """A response naming the displacing state must fail even when it also
        mentions the accepted one -- 'X, not Y' and 'Y, not X' must differ."""
        g = KEYS["a01"]
        assert grade({"grading": g}, "Angela Merkel.")
        assert not grade({"grading": g}, "Olaf Scholz, who succeeded Angela Merkel.")

    def test_numeric_tolerance_separates_accept_from_reject(self):
        for qid, g in KEYS.items():
            if g["route"] != "numeric":
                continue
            for r in g.get("rejects", []):
                assert abs(g["value"] - r) > g["tolerance"], \
                    f"{qid}: tolerance {g['tolerance']} overlaps reject {r}"


class TestProvenance:
    @pytest.mark.parametrize("qid", [q["id"] for q in Q if q["class"] != "arithmetic_control"])
    def test_every_primary_item_has_a_provenance_record(self, qid):
        assert f"### {qid} —" in PROV

    def test_verification_status_is_recorded_per_item(self):
        allowed = {"VERIFIED_SOURCE_2026-08-30T00:00:00Z", "COMPUTED_IN_SESSION"}
        assert {i["verification"] for i in MANIFEST["items"]} <= allowed

    def test_no_primary_key_remains_pending(self):
        pending = [i["id"] for i in MANIFEST["items"] if "PENDING" in i["verification"]]
        assert pending == [], f"unverified keys remain: {pending}"

    def test_every_item_is_production_eligible(self):
        ineligible = [i["id"] for i in MANIFEST["items"] if not i["production_eligible"]]
        assert ineligible == [], f"not production eligible: {ineligible}"

    def test_every_primary_item_records_a_verification_timestamp_and_pass(self):
        for qid in [q["id"] for q in Q if q["class"] != "arithmetic_control"]:
            block = PROV.split(f"### {qid} —")[1].split("### ")[0]
            flat = block.replace("**", "")
            assert "Verified at: 2026-08-30T00:00:00Z" in flat, f"{qid}: no verification timestamp"
            assert re.search(r"pass-\d", flat), f"{qid}: no verifier pass recorded"


class TestDispatchSchedule:
    def test_every_item_appears_exactly_once(self):
        assert sorted(s["item_id"] for s in SCHEDULE["schedule"]) == sorted(q["id"] for q in Q)

    def test_no_class_is_dispatched_as_a_contiguous_block(self):
        cls = {q["id"]: q["class"] for q in Q}
        seq = [cls[s["item_id"]] for s in SCHEDULE["schedule"]]
        longest, run = 1, 1
        for a, b in zip(seq, seq[1:]):
            run = run + 1 if a == b else 1
            longest = max(longest, run)
        assert longest <= 4, f"a class ran {longest} positions contiguously"

    def test_the_control_is_spread_across_the_run_not_dumped_at_one_end(self):
        cls = {q["id"]: q["class"] for q in Q}
        pos = [s["position"] for s in SCHEDULE["schedule"] if cls[s["item_id"]] == "arithmetic_control"]
        assert min(pos) < 15 and max(pos) > 50

    def test_arm_order_is_randomised_not_fixed(self):
        firsts = [s["arm_first"] for s in SCHEDULE["schedule"]]
        assert 0.25 < firsts.count("closed") / len(firsts) < 0.75
        assert len(set(firsts)) == 2

    def test_both_arms_are_present_and_adjacent_for_every_item(self):
        for s in SCHEDULE["schedule"]:
            assert {s["arm_first"], s["arm_second"]} == {"closed", "retrieval_enabled"}

    def test_seeds_are_recorded_so_the_schedule_is_reproducible(self):
        assert isinstance(SCHEDULE["item_order_seed"], int)
        assert isinstance(SCHEDULE["arm_order_seed"], int)
        assert SCHEDULE["generated_before_any_outcome"] is True


class TestArmPackets:
    def test_arms_differ_only_by_the_retrieval_permission(self):
        assert DIFF["identical_apart_from_treatment"] is True
        assert DIFF["differing_line_count"] <= 4

    def test_closed_arm_has_no_phantom_search_budget(self):
        assert DIFF["closed_arm_phantom_budget_terms_found"] == []

    def test_no_arm_label_cues_the_solver(self):
        assert DIFF["no_arm_label_visible_to_solver"] is True

    def test_stem_placeholder_is_identical_in_both_arms(self):
        assert DIFF["stem_placeholder_identical"] is True


class TestNoTreatmentExposure:
    def test_manifest_asserts_zero_exposure(self):
        assert "NONE" in MANIFEST["treatment_exposure"]
        assert "NOT FROZEN" in MANIFEST["status"]

    def test_no_run_directory_exists_for_this_experiment(self):
        assert not (REPO / "runs" / "exp004_stage0am").exists(), \
            "a run directory implies dispatch; none may exist before execution authorisation"


class TestPostVerificationAudit:
    """Invariants added by the post-verification audit.

    These exist because the audit found two things the earlier tests could not
    see: fingerprints that nothing in the repository could regenerate, and a
    numeric key whose acceptance interval, not whose stem, was doing the work of
    disambiguating the question.
    """

    def test_manifest_fingerprints_are_reproducible_from_the_committed_files(self):
        """A hand-edited key must not be able to keep its recorded fingerprint."""
        from lab.stage0am_fingerprint import audit

        result = audit()
        assert result["drifted_keys"] == []
        assert result["battery_fingerprint_matches"]
        assert result["items_in_manifest"] == result["items_in_battery"] == 65

    def test_fingerprint_lineage_records_every_stage(self):
        lineage = MANIFEST["fingerprint_lineage"]
        assert [s["stage"] for s in lineage] == ["authoring", "verification", "final_audited"]
        assert lineage[-1]["fingerprint"] == MANIFEST["battery_fingerprint"]
        assert len({s["fingerprint"] for s in lineage}) == 3, "a stage that changed nothing is not a stage"

    def test_no_accept_band_reaches_halfway_to_the_value_it_must_reject(self):
        """The frozen principle: ambiguity is removed in the question, not repaired
        by a broad acceptance interval.

        Operationalised without an invented threshold. A tolerance is a statement
        that answers within +/-t are the same answer. If the displacing value sat
        in a band of the same width, the two bands must still not touch --
        otherwise the tolerance is adjudicating the definitional distinction the
        stem is supposed to settle. That requires t < gap/2, and nothing weaker
        follows from the principle.

        This is the rule that caught b03, whose band came within 0.36 m of the
        pre-2020 Everest elevation it exists to reject.
        """
        offenders = []
        for q in Q:
            key = KEYS[q["id"]]
            if key["route"] != "numeric" or not key.get("rejects"):
                continue
            gap = min(abs(r - key["value"]) for r in key["rejects"])
            if key["tolerance"] >= gap / 2:
                offenders.append((q["id"], key["tolerance"], gap))
        assert not offenders, f"accept band adjudicating the definitional gap: {offenders}"

    def test_every_numeric_reject_is_outside_its_accept_band(self):
        collisions = []
        for q in Q:
            key = KEYS[q["id"]]
            if key["route"] != "numeric":
                continue
            lo, hi = key["value"] - key["tolerance"], key["value"] + key["tolerance"]
            collisions += [(q["id"], r) for r in key.get("rejects", []) if lo <= r <= hi]
        assert not collisions, f"rejected values falling inside the accept band: {collisions}"

    def test_retrieval_packet_names_the_tools_the_agent_is_actually_granted(self):
        """The arm's instruction and its actual affordances must agree: the
        estimand is intent-to-treat over the granted surface. Checked against
        the DEDICATED Stage 0A-M agent, by tool name, not by paraphrase."""
        fm = (REPO / ".claude" / "agents" / "stage0am-solver-web.md").read_text().split("---\n", 2)[1]
        granted = {t.strip() for t in yaml.safe_load(fm)["tools"].split(",")}
        packet = (REPO / "experiments" / "exp004_stage0am"
                  / "packet_retrieval_enabled.template.md").read_text()
        for tool in granted - {"TodoWrite"}:
            assert tool in packet, f"granted tool {tool} not named in the retrieval packet"

    def test_arms_still_differ_only_in_the_treatment(self):
        assert DIFF["differing_line_count"] == 3
        assert DIFF["identical_apart_from_treatment"]
        assert DIFF["closed_arm_phantom_budget_terms_found"] == []
        assert DIFF["no_arm_label_visible_to_solver"]


class TestEgressProbeIsScreenClassAndUncontaminating:
    PROBE = json.loads((REPO / "experiments" / "exp004_stage0am"
                        / "egress_probe.frozen.json").read_text())
    RESULTS = json.loads((REPO / "experiments" / "exp004_stage0am"
                          / "egress_probe.results.json").read_text())

    def test_probe_is_screen_class_and_spends_no_production_dispatch(self):
        assert self.PROBE["dispatch_class"] == "screen"
        assert self.PROBE["counts_against_production_dispatches"] is False
        assert self.RESULTS["production_dispatches_consumed"] == 0

    def test_no_probe_target_or_query_is_a_production_stem(self):
        stems = {normalise(q["text"]) for q in Q}
        for entry in self.PROBE["search_queries"]:
            assert normalise(entry["q"]) not in stems
        probe_text = json.dumps(self.PROBE).lower()
        for q in Q:
            assert normalise(q["text"]) not in normalise(probe_text)

    def test_the_design_was_frozen_before_results_were_observed(self):
        assert self.PROBE["frozen_before_observation"]
        assert self.RESULTS["design_frozen_in_commit"]
        targets = [t["url"] for t in self.PROBE["fetch_targets"]]
        observed = [f["url"] for f in self.RESULTS["arm_orchestrator"]["fetch"]]
        assert observed == targets, "results may not add, drop or reorder frozen targets"

    def test_an_arm_that_returned_no_data_claims_no_finding(self):
        """A probe arm that died before issuing a call is not evidence either way."""
        arm = self.RESULTS["arm_solver_web_subagent"]
        if arm["status"].startswith("INCONCLUSIVE"):
            assert arm["fetch"] == [] and arm["search"] == []
            assert arm["finding"].startswith("NONE")

    def test_the_probe_declares_no_pass_fail_gate(self):
        assert "not_a_gate" in self.PROBE
        assert "threshold" in self.PROBE["not_a_gate"]

    def test_analysis_is_never_conditioned_on_reachability(self):
        assert "no_analysis_conditioning" in self.RESULTS
        spec = (REPO / "docs" / "EXP004_STAGE0A_M_SPECIFICATION.md").read_text()
        assert "No reachability-conditioned analysis" in spec
        assert all(i["production_eligible"] for i in MANIFEST["items"])


class TestSpelledNumbersAreGradedLikeDigits:
    """A solver writing "four" must be graded as one writing "4".

    The concern is not politeness to prose. Answer format plausibly correlates
    with arm, so a format-sensitive grader can manufacture discordant pairs out
    of formatting rather than correctness -- and discordant pairs are exactly
    what the primary test counts.
    """
    SMALL_INT_ITEMS = [q["id"] for q in Q
                       if KEYS[q["id"]]["route"] == "numeric"
                       and float(KEYS[q["id"]]["value"]).is_integer()
                       and 0 <= KEYS[q["id"]]["value"] <= 20]

    def test_the_battery_still_has_items_this_protects(self):
        assert self.SMALL_INT_ITEMS, "if this empties, re-justify the mapping"

    def test_each_small_integer_item_accepts_its_key_spelled_out(self):
        inverse = {v: k for k, v in NUMBER_WORDS.items()}
        for qid in self.SMALL_INT_ITEMS:
            key = KEYS[qid]
            word = inverse[int(key["value"])]
            assert grade_numeric(word, key["value"], key["tolerance"], key["rejects"]), \
                f"{qid}: spelled key {word!r} graded incorrect"
            assert grade_numeric(word.capitalize(), key["value"],
                                      key["tolerance"], key["rejects"])

    def test_each_small_integer_item_still_rejects_its_rejects_spelled_out(self):
        inverse = {v: k for k, v in NUMBER_WORDS.items()}
        for qid in self.SMALL_INT_ITEMS:
            key = KEYS[qid]
            for reject in key["rejects"]:
                if float(reject).is_integer() and int(reject) in inverse:
                    assert not grade_numeric(inverse[int(reject)], key["value"],
                                                  key["tolerance"], key["rejects"]), \
                        f"{qid}: spelled reject {reject} graded correct"

    def test_no_key_or_reject_collides_with_a_frequent_prose_number(self):
        """0, 1 and 2 carry heavy non-numeric prose senses. The mapping is only
        safe while no key depends on them."""
        for q in Q:
            key = KEYS[q["id"]]
            if key["route"] != "numeric":
                continue
            # Only ACCEPTED values matter: a reject cannot change a numeric
            # verdict (see grade_numeric), and only an integer can be produced by
            # a number word, so b06's 0.0086 cannot collide either way.
            if float(key["value"]).is_integer():
                assert not (0 <= key["value"] <= 2), \
                    f"{q['id']}: value {key['value']} collides with a frequent prose word"

    def test_number_words_are_matched_only_as_whole_words(self):
        for text in ("money", "none", "atone", "sixteenth-century", "someone"):
            assert extract_numbers(text) == [], f"{text!r} produced a number"

    def test_digits_still_work_exactly_as_before(self):
        assert extract_numbers("8,848.86 m") == [8848.86]
        assert extract_numbers("57573") == [57573.0]


class TestRejectsDoNotOverrideACorrectNumericAnswer:
    """A correct answer that also names the contrasting figure must be correct.

    Under the earlier rule it was not, and the false negatives were arm-correlated:
    a solver that has just retrieved a source is likelier to state both figures,
    so they concentrated in the retrieval-enabled arm and manufactured n10 -- a
    false harm signal pointing the way the hypothesis predicts.
    """

    CONTRAST_ANSWERS = {
        "b05": "8 planets; there were 9 before the 2006 definition",
        "b08": "13 individual golds, out of 23 in total",
        "b09": "20 of the 27 EU member states had adopted it",
        "b15": "193 member states, excluding the 2 permanent observer states",
        "b17": "381 m to the architectural top; 443 m including the antenna",
        "b25": "3 of the contiguous 48; 5 counting Alaska and Hawaii",
    }

    def test_a_correct_answer_naming_the_contrast_is_graded_correct(self):
        for qid, answer in self.CONTRAST_ANSWERS.items():
            key = KEYS[qid]
            assert grade_numeric(answer, key["value"], key["tolerance"], key["rejects"]), \
                f"{qid}: correct answer naming the contrast graded incorrect: {answer!r}"

    def test_a_bare_displacing_answer_is_still_graded_incorrect(self):
        """The fix must not have made the items ungradeable."""
        for q in Q:
            key = KEYS[q["id"]]
            if key["route"] != "numeric":
                continue
            for reject in key.get("rejects", []):
                assert not grade_numeric(str(reject), key["value"],
                                         key["tolerance"], key["rejects"]), \
                    f"{q['id']}: bare displacing answer {reject} graded correct"

    def test_rejects_are_redundant_for_numeric_grading_by_construction(self):
        """Why dropping reject-precedence is safe rather than merely convenient:
        the separation invariant puts every reject outside its accept band, so a
        bare reject already fails on the accept test alone."""
        for q in Q:
            key = KEYS[q["id"]]
            if key["route"] != "numeric":
                continue
            for reject in key.get("rejects", []):
                assert abs(reject - key["value"]) > key["tolerance"], \
                    f"{q['id']}: reject {reject} sits inside the accept band"

    def test_entity_route_keeps_reject_precedence(self):
        """The asymmetry is deliberate. An entity answer naming the displacing
        entity has not answered; a numeric one that names both has."""
        from lab.anchored_grading import grade_exact_entity
        assert not grade_exact_entity("Scholz, who succeeded Merkel",
                                      ["Angela Merkel", "Merkel"], ["Olaf Scholz", "Scholz"])
        assert grade_exact_entity("Angela Merkel", ["Angela Merkel", "Merkel"], ["Olaf Scholz"])
