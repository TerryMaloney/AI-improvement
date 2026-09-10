from lab.exp005a_procedures import (
    COMMON_SYSTEM,
    a0,
    b3,
    c3_critique,
    c3_initial,
    c3_repair,
    d3_initial,
    d3_repair,
    d3_verifier,
    majority_vote,
    static_fingerprints,
)


def test_a0_and_b3_direct_packet_is_identical():
    task = "Question? FINAL format."
    assert a0(task)[0] == b3(task)[0] == b3(task)[1] == b3(task)[2]
    assert a0(task)[0].system == COMMON_SYSTEM


def test_c3_context_policy_is_intentional():
    task = "Q"
    assert c3_initial(task).context_policy == "fresh"
    assert c3_critique().context_policy == "continue"
    assert c3_repair().context_policy == "continue"


def test_d3_verifier_and_repair_are_fresh():
    v = d3_verifier("Q", "A")
    r = d3_repair("Q", "A", "report")
    assert d3_initial("Q").context_policy == "fresh"
    assert v.context_policy == "fresh"
    assert r.context_policy == "fresh"
    assert "CANDIDATE FINAL" in v.user
    assert "VERIFIER REPORT" in r.user


def test_d3_verifier_does_not_receive_solver_reasoning_field():
    v = d3_verifier("Q", "A")
    assert "candidate reasoning" not in v.user.casefold()
    assert "CANDIDATE FINAL:\nA" in v.user


def test_majority_vote_basic_and_tie_break():
    assert majority_vote(["A", "a", "B"]) == "A"
    assert majority_vote(["A", "B", "C"]) == "A"
    assert majority_vote([None, "B", "b"]) == "B"
    assert majority_vote([None, None, None]) is None


def test_majority_vote_rejects_wrong_sample_count():
    try:
        majority_vote(["A", "B"])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_static_fingerprints_are_stable_shape():
    fp = static_fingerprints()
    assert len(fp) == 8
    assert all(len(v) == 16 for v in fp.values())
