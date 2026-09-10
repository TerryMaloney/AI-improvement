from lab.exp005_epi_worlds_b import generate_transfer_world


def test_transfer_world_is_reproducible():
    assert generate_transfer_world(123) == generate_transfer_world(123)


def test_transfer_world_has_temporal_changes_and_false_corrections():
    w = generate_transfer_world(456)
    assert len(w.temporal_changed) >= 2
    assert len(w.false_corrections) >= 1


def test_transfer_world_truth_matches_rules():
    w = generate_transfer_world(789)
    truth = dict(w.base_truth)
    for rule in w.rules:
        truth[rule.output] = all(truth[p] == expected for p, expected in rule.premises)
    assert truth == w.truth


def test_transfer_world_contains_shared_lineages():
    w = generate_transfer_world(999)
    counts = {}
    for e in w.initial_evidence:
        counts[e.lineage_id] = counts.get(e.lineage_id, 0) + 1
    assert max(counts.values()) >= 2


def test_transfer_world_impacts_are_not_just_descendant_counts():
    w = generate_transfer_world(321)
    hi = [w.impacts[p] for p in w.truth if p.startswith("I")]
    hub = [w.impacts[p] for p in w.truth if p.startswith("H")]
    assert min(hi) > max(hub)
