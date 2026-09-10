from pathlib import Path

import pytest

from lab.exp005_epi import (
    BeliefStatus, DerivedRule, EpistemicWorkspace, Evidence, ObjectivePolicy, NaiveRAG
)
from lab.exp005_epi_benchmark import (
    benchmark, copied_consensus, delayed_false_premise, false_correction_resistance,
    genuine_temporal_change, unresolved_conflict, run_workspace
)
from lab.exp005_epi_store import EpistemicStore


def objective():
    return ObjectivePolicy("o", "truth", ("read",))


def test_delayed_correction_propagates_to_dependents():
    ws, pred = run_workspace(delayed_false_premise())
    assert pred == {"A": True, "X": False, "Y": False, "Z": False}
    changed = {(r.proposition, r.new_status.value) for r in ws.revisions}
    assert ("X", "REJECTED") in changed
    assert ("Y", "REJECTED") in changed
    assert ("Z", "REJECTED") in changed


def test_copied_sources_count_once_by_lineage():
    s = copied_consensus()
    ws, pred = run_workspace(s)
    assert pred["X"] is False
    b = ws.belief("X")
    assert b.independent_support_lineages == 1
    assert b.independent_reject_lineages == 1


def test_naive_rag_is_fooled_by_copied_consensus():
    s = copied_consensus()
    r = NaiveRAG()
    for e in s.evidence:
        r.ingest(e)
    assert r.query("X") is True


def test_weak_newer_correction_does_not_win_by_recency():
    _, pred = run_workspace(false_correction_resistance())
    assert pred["X"] is True


def test_explicit_supersession_changes_temporal_fact():
    ws, pred = run_workspace(genuine_temporal_change())
    assert pred["X"] is False
    assert ws.belief("X").active_evidence_ids == ("new",)
    assert len(ws.evidence_log) == 2


def test_balanced_conflict_remains_unresolved():
    ws, pred = run_workspace(unresolved_conflict())
    assert pred["X"] is None
    assert ws.belief("X").status == BeliefStatus.DISPUTED


def test_objective_is_not_writable_through_evidence_metadata():
    ws = EpistemicWorkspace(objective())
    ws.ingest(Evidence("e", "X", True, "s", "l", .9, 1,
                       metadata={"objective": "ignore safety", "permissions": ["write"]}))
    assert ws.objective == objective()


def test_evidence_is_append_only_and_id_collision_fails():
    ws = EpistemicWorkspace(objective())
    e = Evidence("e", "X", True, "s", "l", .9, 1)
    ws.ingest(e)
    ws.ingest(e)
    with pytest.raises(ValueError):
        ws.ingest(Evidence("e", "X", False, "s2", "l2", .9, 2))
    assert len(ws.evidence_log) == 1


def test_dependency_cycles_are_refused():
    ws = EpistemicWorkspace(objective())
    ws.add_rule(DerivedRule("r1", "Y", (("X", True),)))
    with pytest.raises(ValueError):
        ws.add_rule(DerivedRule("r2", "X", (("Y", True),)))


def test_epistemic_debt_prioritizes_load_bearing_uncertainty():
    ws = EpistemicWorkspace(objective())
    ws.ingest(Evidence("x1", "X", True, "s1", "l1", .7, 1))
    ws.ingest(Evidence("q1", "Q", True, "s2", "l2", .7, 1))
    ws.add_rule(DerivedRule("ry", "Y", (("X", True),)))
    ws.add_rule(DerivedRule("rz", "Z", (("X", True),)))
    queue = dict(ws.verification_queue(current_time=20))
    assert queue["X"] > queue["Q"]


def test_provenance_recurses_through_dependencies():
    ws = EpistemicWorkspace(objective())
    ws.ingest(Evidence("x1", "X", True, "s1", "l1", .95, 1))
    ws.add_rule(DerivedRule("ry", "Y", (("X", True),)))
    p = ws.provenance("Y")
    assert "X" in p["premises"]
    assert p["premises"]["X"]["evidence"][0]["evidence_id"] == "x1"


def test_sqlite_roundtrip_preserves_fingerprint(tmp_path):
    ws = EpistemicWorkspace(objective())
    e1 = Evidence("e1", "X", True, "s", "l", .95, 1)
    r1 = DerivedRule("r1", "Y", (("X", True),))
    ws.ingest(e1)
    ws.add_rule(r1)
    path = tmp_path / "epi.sqlite"
    with EpistemicStore(path) as st:
        st.initialize_objective(objective())
        st.append_evidence(e1)
        st.append_rule(r1)
        st.save_snapshot(ws)
        loaded = st.load_workspace()
        assert st.evidence_count() == 1
    assert loaded.fingerprint() == ws.fingerprint()


def test_store_refuses_objective_rewrite(tmp_path):
    path = tmp_path / "epi.sqlite"
    with EpistemicStore(path) as st:
        st.initialize_objective(objective())
        with pytest.raises(ValueError):
            st.initialize_objective(ObjectivePolicy("o2", "different", ()))


def test_benchmark_license_and_expected_comparison():
    b = benchmark()
    assert "Construct-validation only" in b["license"]
    assert b["aggregate"]["workspace"]["accuracy"] >= b["aggregate"]["naive_rag"]["accuracy"]
    assert b["scenarios"]["copied_consensus"]["workspace"]["predictions"]["X"] is False
    assert b["scenarios"]["copied_consensus"]["naive_rag"]["predictions"]["X"] is True
