"""Jev verdicts through AI Gateway; no live traffic (all transports mocked)."""
import asyncio
import json

import httpx
import pytest
from pydantic import SecretStr

from jev import JevError, evaluate_claims_jev


JEV_URL = "https://ai-gateway.vercel.sh/typesafe/v1/systemone"


def jev_response(verdict="mostly_supported", score=3.2, confidence=0.9):
    return httpx.Response(200, json={
        "model": "typesafe-ai/jev",
        "answers": {
            "verdict": {
                "type": "choice", "choice": verdict,
                "probabilities": {verdict: confidence},
                "confidence": confidence,
            },
            "strength": {
                "type": "score", "score": score,
                "legend": {str(index): f"level {index}" for index in range(5)},
                "probabilities": {str(index): 1.0 if index == round(score) else 0.0 for index in range(5)},
                "confidence": confidence,
            },
        },
        "usage": {"input_tokens": 100, "output_tokens": 10},
    })


def test_evaluate_maps_verdict_and_strength_to_fact_score():
    seen = {}

    def handler(request):
        assert str(request.url) == JEV_URL
        assert request.headers["authorization"] == "Bearer gw-test-key"
        body = json.loads(request.content)
        assert body["model"] == "typesafe-ai/jev"
        assert set(body["questions"]) == {"verdict", "strength"}
        assert body["questions"]["verdict"]["type"] == "choice"
        assert body["questions"]["strength"]["type"] == "score"
        seen["state"] = body["state"]
        return jev_response()

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await evaluate_claims_jev(
                [{"id": "c1", "quote": "Water boils at 100C.", "kind": "fact"}],
                {"c1": "[s1] Water boils at 100 degrees Celsius at sea level."},
                client=client, api_key="gw-test-key",
            )

    result = asyncio.run(run())
    assert result == [{"claimId": "c1", "verdictCode": "mostly_supported", "factScore": 80}]
    assert seen["state"]["claim"] == "Water boils at 100C."
    assert "Water boils at 100 degrees" in seen["state"]["evidence"]


def test_strength_score_scales_to_0_100():
    async def run(score):
        async def handler(request):
            return jev_response(score=score)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await evaluate_claims_jev(
                [{"id": "c1", "quote": "q", "kind": "fact"}],
                {"c1": "e"},
                client=client, api_key="k",
            )
            return result[0]["factScore"]

    assert asyncio.run(run(0.0)) == 0
    assert asyncio.run(run(4.0)) == 100
    assert asyncio.run(run(1.0)) == 25


@pytest.mark.parametrize("make_response", [
    lambda: httpx.Response(500, json={"error": "busy"}),
    lambda: httpx.Response(200, json={"model": "x"}),
    lambda: httpx.Response(200, json={
        "model": "x",
        "answers": {"verdict": {"type": "choice", "choice": "bogus", "confidence": 0.9},
                    "strength": {"type": "score", "score": 3.0, "confidence": 0.9}},
    }),
    lambda: httpx.Response(200, json={
        "model": "x",
        "answers": {"verdict": {"type": "choice", "choice": "contradicted", "confidence": 0.9},
                    "strength": {"type": "score", "score": 9.0, "confidence": 0.9}},
    }),
])
def test_transport_and_shape_failures_raise_jev_error(make_response):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: make_response())) as client:
            await evaluate_claims_jev(
                [{"id": "c1", "quote": "q", "kind": "fact"}],
                {"c1": "e"},
                client=client, api_key="k",
            )

    with pytest.raises(JevError):
        asyncio.run(run())


def test_low_confidence_escalates_and_missing_key_fails_fast():
    async def run(response):
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: response)
        ) as client:
            return await evaluate_claims_jev(
                [{"id": "c1", "quote": "q", "kind": "fact"}],
                {"c1": "e"},
                client=client, api_key="k",
            )

    with pytest.raises(JevError):
        asyncio.run(run(jev_response(confidence=0.2)))

    async def run_no_key():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: jev_response())
        ) as client:
            return await evaluate_claims_jev(
                [{"id": "c1", "quote": "q", "kind": "fact"}],
                {"c1": "e"},
                client=client, api_key="  ",
            )

    with pytest.raises(JevError):
        asyncio.run(run_no_key())


def test_verify_claims_jev_builds_score_only_results():
    from verification import verify_claims_jev

    async def handler(request):
        return jev_response(verdict="contradicted", score=0.5, confidence=0.8)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await verify_claims_jev(
                {
                    "claims": [
                        {"id": "c1", "quote": "Water boils at 50C.", "kind": "fact", "start": 0, "end": 20},
                        {"id": "c2", "quote": "I love this policy.", "kind": "opinion", "start": 0, "end": 20},
                    ],
                    "sources": [{"id": "s1", "url": "https://example.org/r", "accessStatus": "verified"}],
                    "sourceTexts": {"s1": "Water boils at 100 degrees Celsius at sea level."},
                },
                client=client, api_key="k",
            )

    result = asyncio.run(run())
    fact, opinion = result["claims"]
    assert fact["verdictCode"] == "contradicted"
    assert fact["factScore"] == 12
    assert fact["evidenceIds"] == []
    assert fact["warnings"] == ["Jev 고속 판정: 직접 인용을 표시하지 않습니다."]
    assert result["evidence"] == []
    assert opinion["verdictCode"] == "not_checkable"


def test_verify_claims_jev_without_sources_never_calls_gateway():
    from verification import verify_claims_jev

    def handler(request):
        raise AssertionError("no verified sources means no Jev call")

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await verify_claims_jev(
                {
                    "claims": [{"id": "c1", "quote": "q", "kind": "fact", "start": 0, "end": 1}],
                    "sources": [],
                    "sourceTexts": {},
                },
                client=client, api_key="k",
            )

    result = asyncio.run(run())
    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"


def test_fast_check_searches_with_llm_and_sends_read_source_text_to_jev(monkeypatch):
    import runtime
    from runtime import Settings

    claim = "AGI\uB294 2030\uB144 \uC548\uC5D0 \uC624\uB098?"
    seen = {"search_hosts": [], "jev_state": None}

    def handler(request):
        if request.url.host == "api.openai.com":
            seen["search_hosts"].append(request.url.host)
            return httpx.Response(200, json={"status": "completed", "output": [
                {"type": "web_search_call", "status": "completed", "action": {"sources": [
                    {"url": "https://www.aitimes.com/news/agi-outlook", "title": "AGI timeline outlook"},
                ]}},
            ]})

        assert request.url.host == "ai-gateway.vercel.sh"
        seen["jev_state"] = json.loads(request.content)["state"]
        return jev_response(verdict="mostly_supported", score=3.0, confidence=0.9)

    async def fake_fetch(url):
        assert url == "https://www.aitimes.com/news/agi-outlook"
        return (
            "Expert forecasts disagree on AGI arrival timelines.",
            url,
        )

    monkeypatch.setattr(runtime, "fetch_public_text", fake_fetch)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await runtime.run_jev_fast_check(
                text=claim, focus="",
                client=client, api_key="k",
                settings=Settings(api_key=SecretStr("test-openai-key")),
                consent=True,
            )

    result = asyncio.run(run())
    assert result.model == "typesafe-ai/jev"
    assert result.text == claim
    assert [(c.id, c.verdictCode, c.factScore) for c in result.claims] == [
        ("c1", "mostly_supported", 75),
    ]
    assert seen["search_hosts"] == ["api.openai.com"]
    assert seen["jev_state"]["claim"] == claim
    assert "Expert forecasts disagree" in seen["jev_state"]["evidence"]
    assert result.claims[0].evidenceIds == []
    assert result.evidence == []
    assert [source.url for source in result.sources] == [
        "https://www.aitimes.com/news/agi-outlook",
    ]


def test_fast_check_uses_linked_source_as_evidence_without_replacing_claim(monkeypatch):
    import runtime
    from runtime import Settings

    async def fake_fetch(url):
        assert url == "https://example.org/article"
        return ("Fetched page body text here.", "https://example.org/article")

    async def handler(request):
        assert "Fetched page body text here." in json.loads(request.content)["state"]["evidence"]
        return jev_response(verdict="partially_supported", score=2.0, confidence=0.8)

    monkeypatch.setattr(runtime, "fetch_public_text", fake_fetch)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await runtime.run_jev_fast_check(
                text="Water boils at 50C.", focus="",
                link_url="https://example.org/article",
                client=client, api_key="k",
                settings=Settings(api_key=SecretStr("")),
            )

    result = asyncio.run(run())
    assert result.text == "Water boils at 50C."
    assert [s.id for s in result.sources] == ["s0"]
    assert result.sources[0].accessStatus == "verified"
    assert result.claims[0].factScore == 50


def test_fast_check_truncates_long_text_to_contract_limit():
    import runtime
    from runtime import Settings

    seen = {}

    async def handler(request):
        body = json.loads(request.content)
        seen["quote_len"] = len(body["state"]["claim"] if isinstance(body.get("state"), dict) else "")
        return jev_response()

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await runtime.run_jev_fast_check(
                text="가" * 15000, focus="",
                client=client, api_key="k",
                settings=Settings(api_key=SecretStr("")),
            )

    result = asyncio.run(run())
    assert len(result.text) <= 12000
    assert result.claims[0].end <= 12000


def test_fast_check_propagates_jev_failure_without_llm_fallback(monkeypatch):
    import runtime
    from runtime import Settings

    async def fake_fetch(url):
        return "Relevant source text.", url

    async def handler(request):
        return httpx.Response(500, json={"error": "busy"})

    monkeypatch.setattr(runtime, "fetch_public_text", fake_fetch)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await runtime.run_jev_fast_check(
                text="Some claim text here.", focus="",
                link_url="https://example.org/source",
                client=client, api_key="k",
                settings=Settings(api_key=SecretStr("")),
            )

    with pytest.raises(JevError):
        asyncio.run(run())


def _jev_runtime_state():
    quote = "Water boils at 100C."
    return {
        "text": quote,
        "focus": "",
        "consent": True,
        "jevMode": True,
        "claims": [{"id": "c1", "quote": quote, "kind": "fact", "start": 0, "end": len(quote)}],
        "sources": [{"id": "s1", "url": "https://example.org/report", "accessStatus": "verified"}],
        "sourceTexts": {"s1": "Water boils at 100 degrees Celsius at sea level."},
    }


def test_runtime_verify_uses_jev_when_mode_on(monkeypatch):
    import runtime
    from runtime import Settings, make_runtime_adapters

    real_async_client = httpx.AsyncClient

    def handler(request):
        assert request.url.host == "ai-gateway.vercel.sh"
        return jev_response(verdict="mostly_supported", score=3.6, confidence=0.9)

    def mock_client(*args, **kwargs):
        return real_async_client(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(runtime.httpx, "AsyncClient", mock_client)
    settings = Settings(
        api_key=SecretStr(""),
        gemini_api_key=SecretStr(""),
        ai_gateway_api_key=SecretStr("gw-test-only"),
    )
    adapters = make_runtime_adapters(settings)
    update = asyncio.run(adapters.verify(_jev_runtime_state()))
    assert update["claims"][0]["verdictCode"] == "mostly_supported"
    assert update["claims"][0]["factScore"] == 90
    assert update["llmModel"] == "typesafe-ai/jev"


def test_runtime_verify_escales_to_llm_when_jev_fails(monkeypatch):
    import runtime
    from runtime import Settings, make_runtime_adapters

    real_async_client = httpx.AsyncClient

    def handler(request):
        if request.url.host == "ai-gateway.vercel.sh":
            return httpx.Response(500, json={"error": "busy"})
        body = json.loads(request.content)
        assert body["model"] == "gemini-3.8-flash"
        quote = "Water boils at 100 degrees Celsius at sea level."
        return httpx.Response(200, json={
            "status": "completed",
            "steps": [{
                "type": "model_output",
                "content": [{
                    "type": "text",
                    "text": json.dumps({"claims": [{
                        "claimId": "c1",
                        "verdictCode": "mostly_supported",
                        "factScore": 85,
                        "summary": "The source reports the level.",
                        "confirmed": ["The source reports record levels."],
                        "unresolved": [],
                        "evidence": [{
                            "sourceId": "s1",
                            "quote": quote,
                            "relation": "supports",
                            "comparison": "same",
                        }],
                    }]}),
                }],
            }],
        })

    def mock_client(*args, **kwargs):
        return real_async_client(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(runtime.httpx, "AsyncClient", mock_client)
    settings = Settings(
        api_key=SecretStr(""),
        gemini_api_key=SecretStr("gemini-test-only"),
        ai_gateway_api_key=SecretStr("gw-test-only"),
    )
    adapters = make_runtime_adapters(settings)
    update = asyncio.run(adapters.verify(_jev_runtime_state()))
    assert update["claims"][0]["verdictCode"] == "mostly_supported"
    assert update["llmModel"] == "gemini-3.8-flash"
