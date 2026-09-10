from dataclasses import replace

from lab.exp005_epi import EpistemicWorkspace, Evidence, ObjectivePolicy
from lab.exp005_epi_language import (
    claim_to_evidence, oracle_extract, packet_fingerprint, render_document,
    validate_extraction,
)


def sample():
    return Evidence("e1", "B00", True, "source", "lineage", .91, 7)


def test_render_is_deterministic_and_span_is_exact():
    e = sample()
    a = render_document(e)
    b = render_document(e)
    assert a == b
    assert a.claim_span in a.text
    assert a.text[a.claim_span_start:a.claim_span_end] == a.claim_span


def test_oracle_extraction_roundtrip_is_valid():
    e = sample()
    d = render_document(e)
    c = oracle_extract(d, e)
    assert validate_extraction(d, c) == []
    recovered = claim_to_evidence(c, lineage_id=e.lineage_id, reliability=e.reliability)
    assert recovered.proposition == e.proposition
    assert recovered.asserted_value == e.asserted_value
    assert recovered.metadata["evidence_span"] == d.claim_span


def test_wrong_provenance_span_is_rejected():
    e = sample()
    d = render_document(e)
    c = oracle_extract(d, e)
    bad = replace(c, evidence_span="fabricated")
    assert "evidence_span does not match document offsets" in validate_extraction(d, bad)


def test_prompt_injection_text_does_not_cross_objective_boundary():
    e = sample()
    d = render_document(e, include_prompt_injection_distractor=True)
    c = oracle_extract(d, e)
    recovered = claim_to_evidence(c, lineage_id=e.lineage_id, reliability=e.reliability)
    objective = ObjectivePolicy("o", "truth only", ("read",))
    ws = EpistemicWorkspace(objective)
    ws.ingest(recovered)
    assert ws.objective == objective
    assert "SYSTEM:" not in recovered.metadata["evidence_span"]


def test_extraction_packet_is_stably_fingerprinted():
    assert packet_fingerprint() == packet_fingerprint()
    assert len(packet_fingerprint()) == 16
