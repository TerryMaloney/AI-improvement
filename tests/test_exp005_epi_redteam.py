from lab.exp005_epi_redteam import (
    noisy_verification_evidence, paired_summary, run_custom,
)
from lab.exp005_epi_worlds import generate_world, run_policy


def test_redteam_frozen_debt_runner_matches_original_runner():
    w = generate_world(900123)
    original = run_policy(w, "debt", budget=3)
    audit = run_custom(w, "debt", budget=3)
    assert audit["chosen"] == original["chosen"]
    assert audit["gain"] == original["gain"]


def test_posthoc_strong_baseline_is_deterministic():
    w = generate_world(900456)
    a = run_custom(w, "uncertainty_total_utility", budget=3)
    b = run_custom(w, "uncertainty_total_utility", budget=3)
    assert a == b


def test_noisy_verifier_separates_actual_accuracy_from_reported_reliability():
    w = generate_world(900789)
    p = sorted(w.base_truth)[0]
    wrong = noisy_verification_evidence(
        w, p, 0, actual_accuracy=.9, reported_reliability=.99, draw=.95
    )
    assert wrong.asserted_value is not w.base_truth[p]
    assert wrong.reliability == .99


def test_paired_summary_preserves_direction():
    out = paired_summary([.3, .2, .5], [.1, .2, .2])
    assert out["mean_difference"] > 0
    assert out["wins"] == 2
    assert out["ties"] == 1
    assert out["losses"] == 0
