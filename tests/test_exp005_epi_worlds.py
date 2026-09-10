from lab.exp005_epi_worlds import (
    generate_world, policy_benchmark, run_policy, verification_evidence,
)


def test_world_generation_is_reproducible():
    a = generate_world(12345)
    b = generate_world(12345)
    assert a == b


def test_world_rules_match_hidden_truth():
    w = generate_world(22222)
    truth = dict(w.base_truth)
    for rule in w.rules:
        truth[rule.output] = all(truth[p] == expected for p, expected in rule.premises)
    assert truth == w.truth


def test_verification_evidence_reports_hidden_truth():
    w = generate_world(33333)
    for p in w.base_props:
        e = verification_evidence(w, p, 0)
        assert e.asserted_value == w.base_truth[p]
        assert e.reliability == .995


def test_policy_run_respects_budget_and_unique_actions():
    w = generate_world(44444)
    r = run_policy(w, "debt", budget=3)
    assert len(r["chosen"]) == 3
    assert len(set(r["chosen"])) == 3
    assert len(r["trajectory"]) == 4


def test_debt_beats_random_on_fixed_development_worlds():
    # Development/construct regression only, not a confirmation test.
    b = policy_benchmark(n_worlds=40, budget=3, root_seed=50000)
    assert b["summary"]["debt"]["mean_gain"] > b["summary"]["random"]["mean_gain"]


def test_benchmark_labels_same_pass_design_as_development_only():
    b = policy_benchmark(n_worlds=4, budget=1, root_seed=70000)
    assert "same research pass" in b["license"]
    assert "oracle" not in b["summary"]
