from lab.exp005a_tasks import (
    FAMILIES,
    arithmetic_task,
    bank_fingerprint,
    extract_final,
    generate_bank,
    generate_task,
    grade,
    multihop_task,
    ordering_task,
    state_machine_task,
)


def test_all_families_generate_and_grade_known_key():
    for family in FAMILIES:
        t = generate_task(family, 12345)
        assert t.family == family
        assert t.answer
        assert grade(t, f"work\nFINAL: {t.answer}")
        assert not grade(t, "FINAL: definitely-wrong")


def test_generation_is_deterministic():
    for family in FAMILIES:
        assert generate_task(family, 7) == generate_task(family, 7)
        assert generate_task(family, 7).fingerprint() == generate_task(family, 7).fingerprint()


def test_seeds_change_instances():
    for family in FAMILIES:
        assert generate_task(family, 7).prompt != generate_task(family, 8).prompt


def test_bank_has_expected_size_balance_and_uniqueness():
    bank = generate_bank(20260909, per_family=12)
    assert len(bank) == 48
    assert {f: sum(t.family == f for t in bank) for f in FAMILIES} == {f: 12 for f in FAMILIES}
    assert len({t.task_id for t in bank}) == 48
    assert len({t.prompt for t in bank}) == 48


def test_bank_fingerprint_reconstructs_and_changes_with_seed():
    a = generate_bank(10, 3)
    b = generate_bank(10, 3)
    c = generate_bank(11, 3)
    assert bank_fingerprint(a) == bank_fingerprint(b)
    assert bank_fingerprint(a) != bank_fingerprint(c)


def test_ordering_key_is_position_in_hidden_total_order():
    for seed in range(50):
        t = ordering_task(seed)
        order = t.metadata["order"]
        pos = t.metadata["position"]
        assert t.answer == order[pos - 1]
        pairs = set()
        for clue in t.metadata["clues"]:
            parts = clue.rstrip('.').split()
            pairs.add((parts[0], parts[-1]))
        assert pairs == set(zip(order, order[1:]))


def test_state_machine_key_is_recomputed_from_transitions():
    for seed in range(50):
        t = state_machine_task(seed)
        cur = t.metadata["start"]
        tr = t.metadata["transitions"]
        for sym in t.metadata["sequence"]:
            cur = tr[f"{cur}|{sym}"]
        assert cur == t.answer


def test_multihop_key_is_chain_endpoint():
    for seed in range(50):
        t = multihop_task(seed)
        assert t.answer == t.metadata["chain"][t.metadata["hops"]]


def test_arithmetic_key_recomputes():
    for seed in range(50):
        t = arithmetic_task(seed)
        m = t.metadata
        expected = (
            m["start"] + m["crates"] * m["per_crate"] - m["sold"] - m["damaged"]
            + m["bonus_groups"] * m["bonus_each"]
        )
        assert int(t.answer) == expected


def test_extract_final_uses_last_final_line():
    assert extract_final("FINAL: A\ntext\nFINAL: B") == "B"
    assert extract_final("no final marker") is None


def test_arithmetic_grade_accepts_commas():
    t = arithmetic_task(999)
    n = int(t.answer)
    assert grade(t, f"FINAL: {n:,}")
