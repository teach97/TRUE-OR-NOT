"""Final Python contract tests; no provider calls."""
import pytest
from pydantic import ValidationError

from contracts import FactCheckResponse, FactCheckResult


def result_payload():
    return {
        "text": "Claim",
        "focus": "",
        "demo": False,
        "model": "gpt-5.6-luna",
        "reasoning": "max",
        "checkedAt": "2026-09-20T00:00:00+00:00",
        "claims": [{
            "id": "c1",
            "quote": "Claim",
            "start": 0,
            "end": 5,
            "kind": "fact",
            "verdictCode": "mostly_supported",
            "verdict": "대체로 확인됨",
            "tone": "positive",
            "summary": "원문이 주장을 뒷받침합니다.",
            "confirmed": ["Claim"],
            "unresolved": [],
            "warnings": [],
            "evidenceIds": ["e1"],
        }],
        "sources": [{
            "id": "s1",
            "url": "https://example.org/source",
            "title": "Example source",
            "publisher": "example.org",
            "publishedAt": None,
            "retrievedAt": "2026-09-20T00:00:00+00:00",
            "accessStatus": "verified",
            "sourceType": "유형 미확인",
            "originGroupId": None,
        }],
        "evidence": [{
            "id": "e1",
            "claimId": "c1",
            "sourceId": "s1",
            "quote": "Claim is supported.",
            "quoteVerified": True,
            "relation": "supports",
        }],
        "warnings": [],
    }


def test_final_contract_accepts_frontend_shape_and_wrapper():
    parsed = FactCheckResponse.model_validate({"result": result_payload()})
    assert parsed.result.demo is False
    assert parsed.result.claims[0].evidenceIds == ["e1"]
    assert parsed.model_dump(mode="json")["result"]["sources"][0]["publishedAt"] is None


@pytest.mark.parametrize("change", [
    {"evidence": [{
        "id": "e1", "claimId": "c1", "sourceId": "unknown",
        "quote": "Claim is supported.", "quoteVerified": True, "relation": "supports",
    }]},
    {"claims": [{**result_payload()["claims"][0], "evidenceIds": ["missing"]}]},
    {"claims": [{**result_payload()["claims"][0], "start": 1}]},
    {"claims": [{**result_payload()["claims"][0], "kind": "opinion"}]},
    {"sources": [{**result_payload()["sources"][0], "accessStatus": "unavailable"}]},
    {"evidence": [{
        "id": "e1", "claimId": "c1", "sourceId": "s1",
        "quote": "Claim is supported.", "quoteVerified": False, "relation": "supports",
    }]},
    {"extra": "not allowed"},
])
def test_final_contract_rejects_broken_links_or_unverified_evidence(change):
    payload = {**result_payload(), **change}
    with pytest.raises(ValidationError):
        FactCheckResult.model_validate(payload)


def test_response_contract_does_not_accept_internal_source_fields():
    payload = result_payload()
    payload["sources"] = [{**payload["sources"][0], "resolvedUrl": "https://example.org/final"}]
    with pytest.raises(ValidationError):
        FactCheckResult.model_validate(payload)
