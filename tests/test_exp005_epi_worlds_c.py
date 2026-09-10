from dataclasses import fields

from lab.exp005_epi_crv import (
    build_workspace_c, counterfactual_affected_utility_fraction,
    realized_verification_evidence, structural_utility_fraction,
)
from lab.exp005_epi_worlds_c import (
    ControllerView, VerifierOffer, generate_adversarial_world,
)


def test_generator_c_is_reproducible():
    assert generate_adversarial_world(123456) == generate_adversarial_world(123456)


def test_generator_c_rules_match_hidden_truth():
    w = generate_adversarial_world(223344)
    truth = dict(w.base_truth)
    for rule in w.rules:
        truth[rule.output] = all(truth[p] == required for p, required in rule.premises)
    assert truth == w.truth


def test_controller_view_excludes_hidden_simulation_fields():
    w = generate_adversarial_world(334455)
    view = w.controller_view()
    view_fields = {f.name for f in fields(ControllerView)}
    offer_fields = {f.name for f in fields(VerifierOffer)}
    assert view_fields == {"reported_impacts", "verifier_offers"}
    assert offer_fields == {"tool_id", "proposition", "reported_accuracy", "cost"}
    assert not hasattr(view, "truth")
    assert not hasattr(view, "base_truth")
    assert not hasattr(view, "evaluation_impacts")
    assert not hasattr(view, "actual_verifier_accuracy")
    assert not hasattr(view, "actual_source_accuracy")
    assert not hasattr(view, "actual_lineage")


def test_blocked_gate_condition_is_false_and_currently_resolved():
    w = generate_adversarial_world(445566)
    ws = build_workspace_c(w)
    for i, gate in enumerate(w.gate_props):
        rule = next(r for r in w.rules if r.rule_id == f"C-BLK-{i}-A")
        gate_required = next(required for p, required in rule.premises if p == gate)
        assert w.base_truth[gate] != gate_required
        assert ws.belief(gate).resolved_value == w.base_truth[gate]


def test_counterfactual_revision_value_does_not_count_blocked_descendants_blindly():
    w = generate_adversarial_world(556677)
    ws = build_workspace_c(w)
    view = w.controller_view()
    for i in range(4):
        p = f"C{i:02d}"
        offer = next(o for o in view.verifier_offers
                     if o.proposition == p and o.tool_id.startswith("verify-deep-"))
        crv_fraction = counterfactual_affected_utility_fraction(ws, view, offer)
        structural_fraction = structural_utility_fraction(ws, view, p)
        assert crv_fraction < structural_fraction


def test_verifier_potential_outcome_is_policy_and_step_independent_in_value():
    w = generate_adversarial_world(667788)
    offer = w.verifier_offers[0]
    a = realized_verification_evidence(w, offer, 0)
    b = realized_verification_evidence(w, offer, 3)
    assert a.asserted_value == b.asserted_value
    assert a.reliability == b.reliability == offer.reported_accuracy


def test_reported_and_actual_verifier_quality_are_not_the_same_surface():
    w = generate_adversarial_world(778899)
    mismatches = [
        o for o in w.verifier_offers
        if abs(o.reported_accuracy - w.actual_verifier_accuracy[o.tool_id]) > 1e-9
    ]
    assert mismatches
