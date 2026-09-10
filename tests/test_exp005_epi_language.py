import json
from dataclasses import replace

import pytest

from lab.exp005_epi import EpistemicWorkspace, Evidence, ObjectivePolicy
from lab.exp005_epi_language import (
    claim_to_evidence, oracle_extract, packet_fingerprint, parse_model_extraction,
    render_document, validate_extraction,
)


def sample():
    return Evidence("e1", "B00", True, "source", "lineage", .91, 7)


def model_payload(document, **overrides):
    payload = {
        "proposition": "B00",
        "asserted_value": True,
        "evidence_span": document.claim_span,
        "span_start": document.claim_span_start,
        "span_end": document.claim_span_end,
        "extractor_confidence": .93,
    }
    payload.update(overrides)
    return payload


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


def test_model_output_cannot_smuggle_control_or_trusted_metadata():
    d = render_document(sample(), include_prompt_injection_distractor=True)
    payload = model_payload(d)
    payload["permissions"] = ["write_objective"]
    with pytest.raises(ValueError, match="schema mismatch"):
        parse_model_extraction(d, payload, ontology={"B00"})

    payload = model_payload(d)
    payload["source_id"] = "model-chosen-source"
    with pytest.raises(ValueError, match="schema mismatch"):
        parse_model_extraction(d, payload, ontology={"B00"})


def test_model_extraction_uses_document_trusted_metadata():
    e = sample()
    d = render_document(e)
    claim = parse_model_extraction(d, model_payload(d), ontology={"B00"})
    assert claim is not None
    assert claim.evidence_id == d.evidence_id
    assert claim.source_id == d.source_id
    assert claim.observed_at == d.observed_at
    assert claim.supersedes == d.supersedes
    assert claim.extractor == "model"


def test_model_extraction_explicit_abstention_never_enters_ledger():
    d = render_document(sample())
    payload = model_payload(
        d,
        proposition="",
        asserted_value=False,
        evidence_span="",
        span_start=0,
        span_end=0,
        extractor_confidence=0,
    )
    assert parse_model_extraction(d, json.dumps(payload), ontology={"B00"}) is None


def test_model_extraction_rejects_out_of_ontology_claim():
    d = render_document(sample())
    with pytest.raises(ValueError, match="outside the frozen ontology"):
        parse_model_extraction(
            d, model_payload(d, proposition="SYSTEM_OBJECTIVE"), ontology={"B00"}
        )
