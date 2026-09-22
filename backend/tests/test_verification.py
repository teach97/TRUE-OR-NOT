"""Offline citation-grounding and judgment tests; no provider traffic."""

import asyncio
import json

import httpx

from verification import ground_judgments, verify_claims


def claim(claim_id, quote, kind):
    return {
        "id": claim_id,
        "quote": quote,
        "kind": kind,
        "start": 0,
        "end": len(quote),
    }


def test_ground_judgments_marks_opinions_and_predictions_not_checkable():
    result = ground_judgments(
        [
            claim("c1", "이 정책은 훌륭하다", "opinion"),
            claim("c2", "내년에는 물가가 내려갈 것이다", "prediction"),
        ],
        [],
        [],
        {},
    )

    assert [item["verdictCode"] for item in result["claims"]] == [
        "not_checkable",
        "not_checkable",
    ]
    assert result["evidence"] == []
    assert all(item["evidenceIds"] == [] for item in result["claims"])


def test_ground_judgments_accepts_a_verified_contiguous_quote():
    quote = "The river reached record levels in 2024."
    result = ground_judgments(
        [claim("c1", "The river reached record levels.", "fact")],
        [
            {
                "claimId": "c1",
                "verdictCode": "mostly_supported",
                "summary": "The source directly reports the record level.",
                "confirmed": ["The source reports record levels."],
                "unresolved": [],
                "evidence": [
                    {
                        "sourceId": "s1",
                        "quote": quote,
                        "relation": "supports",
                        "comparison": "same",
                    }
                ],
            }
        ],
        [{"id": "s1", "url": "https://example.org/report", "accessStatus": "verified"}],
        {"s1": quote},
    )

    assert result["claims"][0]["verdictCode"] == "mostly_supported"
    assert result["claims"][0]["evidenceIds"] == ["e1"]
    assert result["evidence"] == [
        {
            "id": "e1",
            "claimId": "c1",
            "sourceId": "s1",
            "quote": quote,
            "quoteVerified": True,
            "relation": "supports",
        }
    ]


def test_invalid_quote_is_removed_and_downgrades_the_judgment():
    result = ground_judgments(
        [claim("c1", "The river reached record levels.", "fact")],
        [
            {
                "claimId": "c1",
                "verdictCode": "mostly_supported",
                "summary": "The source confirms the claim.",
                "confirmed": ["The claim is confirmed."],
                "unresolved": [],
                "evidence": [
                    {
                        "sourceId": "s1",
                        "quote": "This sentence is not in the source.",
                        "relation": "supports",
                        "comparison": "same",
                    }
                ],
            }
        ],
        [{"id": "s1", "url": "https://example.org/report", "accessStatus": "verified"}],
        {"s1": "The river reached record levels in 2024."},
    )

    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"
    assert result["claims"][0]["evidenceIds"] == []
    assert result["claims"][0]["confirmed"] == []
    assert result["claims"][0]["warnings"]
    assert result["evidence"] == []


def test_search_summary_is_not_used_when_source_text_is_missing():
    result = ground_judgments(
        [claim("c1", "The river reached record levels.", "fact")],
        [
            {
                "claimId": "c1",
                "verdictCode": "mostly_supported",
                "summary": "The search result says this is true.",
                "confirmed": [],
                "unresolved": [],
                "evidence": [
                    {
                        "sourceId": "s1",
                        "quote": "The search snippet says this is true.",
                        "relation": "supports",
                        "comparison": "same",
                    }
                ],
            }
        ],
        [
            {
                "id": "s1",
                "url": "https://example.org/report",
                "accessStatus": "verified",
                "snippet": "The search snippet says this is true.",
            }
        ],
        {},
    )

    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"
    assert result["evidence"] == []


def test_date_or_context_mismatch_cannot_support_a_claim():
    result = ground_judgments(
        [claim("c1", "The river reached record levels.", "fact")],
        [
            {
                "claimId": "c1",
                "verdictCode": "mostly_supported",
                "summary": "The source supports the claim.",
                "confirmed": [],
                "unresolved": [],
                "evidence": [
                    {
                        "sourceId": "s1",
                        "quote": "The river reached record levels in 2023.",
                        "relation": "supports",
                        "comparison": "different",
                    }
                ],
            }
        ],
        [{"id": "s1", "url": "https://example.org/report", "accessStatus": "verified"}],
        {"s1": "The river reached record levels in 2023."},
    )

    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"
    assert any("비교 조건" in warning for warning in result["claims"][0]["warnings"])
    assert result["evidence"] == []


def test_context_mismatch_is_reported_as_missing_context():
    quote = "The 2023 survey covered only urban households."
    result = ground_judgments(
        [claim("c1", "The survey covered all households.", "fact")],
        [
            {
                "claimId": "c1",
                "verdictCode": "missing_context",
                "summary": "The geographic scope is narrower than the claim.",
                "confirmed": [],
                "unresolved": ["The survey did not cover rural households."],
                "evidence": [
                    {
                        "sourceId": "s1",
                        "quote": quote,
                        "relation": "context",
                        "comparison": "different",
                    }
                ],
            }
        ],
        [{"id": "s1", "url": "https://example.org/survey", "accessStatus": "verified"}],
        {"s1": quote},
    )

    assert result["claims"][0]["verdictCode"] == "missing_context"
    assert result["claims"][0]["evidenceIds"] == ["e1"]
    assert result["evidence"][0]["relation"] == "context"


def test_same_condition_support_and_contradiction_are_conflicting_sources():
    support = "The agency reported that the rate was 4 percent in June."
    contradiction = "The agency reported that the rate was 6 percent in June."
    result = ground_judgments(
        [claim("c1", "The rate was 4 percent in June.", "fact")],
        [
            {
                "claimId": "c1",
                "verdictCode": "mostly_supported",
                "summary": "Only one source supports the claim.",
                "confirmed": [],
                "unresolved": [],
                "evidence": [
                    {
                        "sourceId": "s1",
                        "quote": support,
                        "relation": "supports",
                        "comparison": "same",
                    },
                    {
                        "sourceId": "s2",
                        "quote": contradiction,
                        "relation": "contradicts",
                        "comparison": "same",
                    },
                ],
            }
        ],
        [
            {"id": "s1", "url": "https://one.example/report", "accessStatus": "verified"},
            {"id": "s2", "url": "https://two.example/report", "accessStatus": "verified"},
        ],
        {"s1": support, "s2": contradiction},
    )

    assert result["claims"][0]["verdictCode"] == "conflicting_sources"
    assert result["claims"][0]["evidenceIds"] == ["e1", "e2"]
    assert [item["relation"] for item in result["evidence"]] == ["supports", "contradicts"]


def test_unknown_claim_id_is_rejected_as_invalid_model_output():
    try:
        ground_judgments(
            [claim("c1", "A factual claim.", "fact")],
            [
                {
                    "claimId": "c2",
                    "verdictCode": "insufficient_evidence",
                    "summary": "No direct source was found.",
                    "confirmed": [],
                    "unresolved": [],
                    "evidence": [],
                }
            ],
            [],
            {},
        )
    except ValueError as exc:
        assert str(exc) == "INVALID_MODEL_OUTPUT"
    else:
        raise AssertionError("unknown claim IDs must not be accepted")


def test_unknown_source_id_is_not_exposed_as_evidence():
    quote = "The river reached record levels in 2024."
    result = ground_judgments(
        [claim("c1", "The river reached record levels.", "fact")],
        [
            {
                "claimId": "c1",
                "verdictCode": "mostly_supported",
                "summary": "The source confirms the claim.",
                "confirmed": [],
                "unresolved": [],
                "evidence": [
                    {
                        "sourceId": "s-missing",
                        "quote": quote,
                        "relation": "supports",
                        "comparison": "same",
                    }
                ],
            }
        ],
        [{"id": "s1", "url": "https://example.org/report", "accessStatus": "verified"}],
        {"s1": quote},
    )

    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"
    assert result["claims"][0]["evidenceIds"] == []
    assert result["evidence"] == []


def test_verify_claims_sends_only_verified_source_text():
    quote = "The river reached record levels in 2024."
    state = {
        "claims": [claim("c1", "The river reached record levels.", "fact")],
        "focus": "date and level",
        "sources": [
            {
                "id": "s1",
                "url": "https://example.org/report",
                "title": "Annual report",
                "publisher": "Example",
                "publishedAt": "2024-06-01",
                "accessStatus": "verified",
            },
            {
                "id": "s2",
                "url": "https://example.org/search-result",
                "accessStatus": "unavailable",
                "snippet": quote,
            },
        ],
        "sourceTexts": {"s1": quote},
    }

    def handler(request):
        body = json.loads(request.content)
        input_data = json.loads(body["input"])
        assert body["model"] == "gpt-5.6-luna"
        assert body["reasoning"] == {"effort": "max"}
        assert body["store"] is False
        assert body["max_output_tokens"] >= 12000
        assert body["text"]["format"]["strict"] is True
        assert [source["id"] for source in input_data["sources"]] == ["s1"]
        assert input_data["sources"][0]["text"] == quote
        assert "snippet" not in request.content.decode()
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "claims": [
                                            {
                                                "claimId": "c1",
                                                "verdictCode": "mostly_supported",
                                                "summary": "The verified source reports the level.",
                                                "confirmed": ["The source reports record levels."],
                                                "unresolved": [],
                                                "evidence": [
                                                    {
                                                        "sourceId": "s1",
                                                        "quote": quote,
                                                        "relation": "supports",
                                                        "comparison": "same",
                                                    }
                                                ],
                                            }
                                        ]
                                    }
                                ),
                            }
                        ],
                    }
                ],
            },
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await verify_claims(state, api_key="test-only", client=client)

    result = asyncio.run(run())
    assert result["claims"][0]["verdictCode"] == "mostly_supported"
    assert result["evidence"][0]["quote"] == quote


def test_verify_claims_bounds_source_text_sent_to_model():
    source_text = "A factual claim is reported here. " + ("Additional source text. " * 600)
    state = {
        "claims": [claim("c1", "A factual claim.", "fact")],
        "focus": "",
        "sources": [{"id": "s1", "url": "https://example.org/report", "accessStatus": "verified"}],
        "sourceTexts": {"s1": source_text},
    }

    def handler(request):
        body = json.loads(request.content)
        input_data = json.loads(body["input"])
        assert len(input_data["sources"][0]["text"]) <= 6000
        return httpx.Response(200, json={
            "status": "completed",
            "output": [{
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": json.dumps({"claims": [{
                        "claimId": "c1",
                        "verdictCode": "insufficient_evidence",
                        "summary": "The bounded source excerpt is not sufficient.",
                        "confirmed": [],
                        "unresolved": ["The complete source was not supplied to the model."],
                        "evidence": [],
                    }]}),
                }],
            }],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await verify_claims(state, api_key="test-only", client=client)

    result = asyncio.run(run())
    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"


def test_verify_claims_without_readable_sources_does_not_call_provider():
    state = {
        "claims": [claim("c1", "A factual claim.", "fact")],
        "focus": "",
        "sources": [
            {"id": "s1", "url": "https://example.org/report", "accessStatus": "unavailable"}
        ],
        "sourceTexts": {},
    }

    def handler(request):
        raise AssertionError("unreadable sources must not trigger a judgment request")

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await verify_claims(state, api_key="", client=client)

    result = asyncio.run(run())
    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"
    assert result["evidence"] == []


def test_verify_claims_requires_a_key_when_verified_source_text_exists():
    state = {
        "claims": [claim("c1", "A factual claim.", "fact")],
        "focus": "",
        "sources": [
            {"id": "s1", "url": "https://example.org/report", "accessStatus": "verified"}
        ],
        "sourceTexts": {"s1": "A factual claim is reported here."},
    }

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: None)) as client:
            return await verify_claims(state, api_key="", client=client)

    try:
        asyncio.run(run())
    except ValueError as exc:
        assert str(exc) == "NOT_CONFIGURED"
    else:
        raise AssertionError("verified source judgment requires a provider key")
