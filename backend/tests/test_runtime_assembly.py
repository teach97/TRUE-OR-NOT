"""Runtime assembly tests; explicit adapters keep the five-node graph offline."""
import asyncio

from contracts import FactCheckResponse
from runtime import RuntimeAdapters, Settings, build_fact_check_result, build_runtime_workflow
from pydantic import SecretStr


def test_final_result_warns_when_llm_search_was_unavailable():
    result = build_fact_check_result(
        {
            "text": "Claim", "focus": "", "consent": True,
            "claims": [], "sources": [], "evidence": [],
            "searchNotice": "LLM_SEARCH_UNAVAILABLE",
        },
        {},
    )
    assert any("웹검색을 사용할 수 없어" in warning for warning in result.warnings)


def test_forecast_keywords_reach_search_through_graph_without_leaking_into_result():
    import json
    import httpx
    from extraction import extract_claims
    from search import search_sources
    from verification import verify_claims

    question = "AGI는 2030년 안에 오나?"
    # Distinct from the fallback query to detect a graph-state field being dropped.
    keywords = "AGI 2030년 전문가 전망"
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            return httpx.Response(200, json={"status": "completed", "output": [
                {"type": "message", "content": [{"type": "output_text", "text": json.dumps({
                    "claims": [{"quote": question, "kind": "prediction", "searchQuery": keywords}],
                })}]},
            ]})
        assert json.loads(body["input"])["primaryQueries"] == [keywords]
        return httpx.Response(200, json={"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed", "action": {"sources": []}},
        ]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            async def extract(state):
                return await extract_claims(state, api_key="test-only", client=client)

            async def search(state):
                return await search_sources(state, api_key="test-only", client=client)

            async def read(state):
                return {"sources": state["sources"], "sourceTexts": {}}

            async def verify(state):
                return await verify_claims(state, api_key="test-only", client=client)

            async def synthesize(state):
                raise AssertionError("No readable source text must skip answer synthesis")

            graph = build_runtime_workflow(
                Settings(api_key=SecretStr("test-only")),
                adapters=RuntimeAdapters(
                    extract=extract, search=search, read=read, verify=verify,
                    synthesize=synthesize,
                ),
            )
            return await graph.ainvoke({"text": question, "focus": "", "consent": True})

    state = asyncio.run(run())
    assert len(requests) == 2
    assert state["searchQueries"] == {"c1": keywords}
    result = FactCheckResponse.model_validate({"result": state["result"]}).result
    assert result.claims[0].kind == "prediction"
    assert result.claims[0].verdictCode == "not_checkable"
    assert result.answer.status == "insufficient_evidence"
    assert "searchQueries" not in result.model_dump()
    assert "searchQuery" not in result.claims[0].model_dump()


def test_runtime_graph_assembles_valid_final_result_after_five_stages():
    seen = []

    async def extract(state):
        seen.append("extracting")
        return {"claims": [{
            "id": "c1", "quote": state["text"], "start": 0, "end": 5,
            "end": 5, "kind": "fact",
        }]}

    async def search(state):
        seen.append("searching")
        return {"sources": [{
            "id": "s1", "url": "https://example.org/source", "title": "Example source",
            "publisher": "example.org", "accessStatus": "pending",
        }]}

    async def read(state):
        seen.append("reading")
        return {"sources": [{
            "id": "s1", "url": "https://example.org/source", "title": "Example source",
            "publisher": "example.org", "accessStatus": "verified",
            "retrievedAt": "2026-09-20T00:00:00+00:00",
        }], "sourceTexts": {"s1": "Claim is supported."}}

    async def verify(state):
        seen.append("verifying")
        return {"claims": [{
            "id": "c1", "quote": "Claim", "start": 0, "end": 5, "kind": "fact",
            "verdictCode": "mostly_supported", "verdict": "대체로 확인됨",
            "tone": "positive", "summary": "원문이 주장을 뒷받침합니다.",
            "confirmed": ["Claim"], "unresolved": [], "warnings": [], "evidenceIds": ["e1"],
        }], "evidence": [{
            "id": "e1", "claimId": "c1", "sourceId": "s1",
            "quote": "Claim is supported.", "quoteVerified": True, "relation": "supports",
        }], "llmModel": "gpt-6-luna", "llmReasoning": "max"}

    async def synthesize(state):
        seen.append("synthesizing")
        assert state["llmModel"] == "gpt-6-luna"
        citation = {"sourceId": "s1", "quote": "Claim is supported."}
        return {
            "answer": {
                "status": "grounded",
                "overview": {"text": "원문은 주장을 뒷받침합니다.", "citations": [citation]},
                "sections": [],
                "conclusion": {"text": "제한된 근거에 따른 결론입니다.", "citations": [citation]},
                "model": "gemini-3.8-flash", "reasoning": "high",
            },
            "answerModel": "gemini-3.8-flash",
            "answerReasoning": "high",
        }

    graph = build_runtime_workflow(
        Settings(api_key=SecretStr("test-only")),
        adapters=RuntimeAdapters(
            extract=extract, search=search, read=read, verify=verify, synthesize=synthesize,
        ),
    )
    state = asyncio.run(graph.ainvoke({
        "text": "Claim", "focus": "", "consent": True,
    }))

    assert seen == ["extracting", "searching", "reading", "verifying", "synthesizing"]
    parsed = FactCheckResponse.model_validate({"result": state["result"]})
    assert parsed.result.sources[0].url == "https://example.org/source"
    assert parsed.result.claims[0].evidenceIds == ["e1"]
    assert parsed.result.model == "gpt-6-luna"
    assert parsed.result.reasoning == "max"
    assert parsed.result.answer.model == "gemini-3.8-flash"
    assert parsed.result.answer.reasoning == "high"
    assert "sourceTexts" in state


def test_forecast_synthesis_preserves_prediction_and_citations(monkeypatch):
    import json
    import re

    import httpx
    import runtime
    from runtime import make_runtime_adapters

    question = "AGI는 2030년 안에 오나?"
    early_text = "Several researchers expect AGI-capable systems before 2030 if current scaling continues."
    uncertainty_text = "The field has no agreed definition of AGI, and experts cannot provide a reliable timeline."
    source_texts = {"s1": early_text, "s2": uncertainty_text}
    sources = [
        {
            "id": "s1", "url": "https://example.org/early-forecast", "title": "Early timeline forecast",
            "publisher": "Example Lab", "publishedAt": None,
            "retrievedAt": "2026-09-23T00:00:00+00:00", "accessStatus": "verified",
            "sourceType": "기사", "originGroupId": None,
        },
        {
            "id": "s2", "url": "https://example.org/agi-uncertainty", "title": "AGI timeline uncertainty",
            "publisher": "Example Institute", "publishedAt": None,
            "retrievedAt": "2026-09-23T00:00:00+00:00", "accessStatus": "verified",
            "sourceType": "기사", "originGroupId": None,
        },
    ]
    early_quote = "expect AGI-capable systems before 2030 if current scaling continues"
    uncertainty_quote = "no agreed definition of AGI, and experts cannot provide a reliable timeline"
    answer_draft = {
        "status": "grounded",
        "overview": {
            "text": "일부 전망은 현재 추세가 이어지면 2030년 이전에 AGI 역량이 나타날 수 있다고 봅니다.",
            "citations": [{"sourceId": "s1", "quote": early_quote}],
        },
        "sections": [
            {
                "kind": "supporting",
                "title": "조기 도래 전망",
                "items": [{
                    "text": "한 연구자 그룹은 현재 추세가 이어지는 경우를 전제로 전망합니다.",
                    "citations": [{"sourceId": "s1", "quote": early_quote}],
                }],
            },
            {
                "kind": "uncertainty",
                "title": "남은 불확실성",
                "items": [{
                    "text": "AGI 정의에 합의가 없고 신뢰할 수 있는 일정도 제시되지 않았습니다.",
                    "citations": [{"sourceId": "s2", "quote": uncertainty_quote}],
                }],
            },
        ],
        "conclusion": {
            "text": "따라서 2030년 안에 도래할지는 확정된 사실이 아니라 불확실한 예측입니다.",
            "citations": [{"sourceId": "s2", "quote": uncertainty_quote}],
        },
    }
    attempted_models = []

    def provider_response(request):
        body = json.loads(request.content)
        attempted_models.append(body["model"])
        assert body["model"] == "gemini-3.8-flash"
        synthesis_input = json.loads(body["input"])
        assert synthesis_input["question"] == question
        assert {item["id"]: item["text"] for item in synthesis_input["sources"]} == source_texts
        return httpx.Response(200, json={
            "status": "completed",
            "steps": [{
                "type": "model_output",
                "content": [{"type": "text", "text": json.dumps(answer_draft, ensure_ascii=False)}],
            }],
        })

    real_async_client = httpx.AsyncClient

    def mock_client(*args, **kwargs):
        return real_async_client(*args, transport=httpx.MockTransport(provider_response), **kwargs)

    monkeypatch.setattr(runtime.httpx, "AsyncClient", mock_client)
    settings = Settings(
        api_key=SecretStr("openai-test-only"),
        gemini_api_key=SecretStr("gemini-test-only"),
    )
    provider_adapters = make_runtime_adapters(settings)

    async def extract(state):
        return {"claims": [{
            "id": "c1", "quote": question, "start": 0, "end": len(question),
            "kind": "prediction",
        }]}

    async def search(state):
        return {"sources": sources}

    async def read(state):
        return {"sources": sources, "sourceTexts": source_texts}

    async def verify(state):
        claim = state["claims"][0]
        return {
            "claims": [{
                **claim, "verdictCode": "not_checkable", "verdict": "검증 대상 아님",
                "tone": "neutral", "summary": "미래 예측은 현재 사실처럼 확정할 수 없습니다.",
                "confirmed": [], "unresolved": ["실현 시기는 불확실합니다."],
                "warnings": ["예측은 사실 판정과 구분합니다."], "evidenceIds": [],
            }],
            "evidence": [], "llmModel": "gpt-6-luna", "llmReasoning": "max",
        }

    graph = build_runtime_workflow(
        settings,
        adapters=RuntimeAdapters(
            extract=extract, search=search, read=read, verify=verify,
            synthesize=provider_adapters.synthesize,
        ),
    )
    state = asyncio.run(graph.ainvoke({"text": question, "focus": "", "consent": True}))
    result = FactCheckResponse.model_validate({"result": state["result"]}).result

    assert attempted_models == ["gemini-3.8-flash"]
    assert result.claims[0].kind == "prediction"
    assert result.claims[0].verdictCode == "not_checkable"
    assert result.claims[0].summary == "미래 예측은 현재 사실처럼 확정할 수 없습니다."
    assert result.evidence == []
    assert result.model == "gpt-6-luna"
    assert result.answer.model == "gemini-3.8-flash"
    assert result.answer.status == "grounded"
    assert [section.kind for section in result.answer.sections] == ["supporting", "uncertainty"]

    blocks = [result.answer.overview, result.answer.conclusion]
    blocks.extend(item for section in result.answer.sections for item in section.items)
    citations = [citation for block in blocks for citation in block.citations]
    assert citations
    assert {citation.sourceId for citation in citations} == {"s1", "s2"}
    assert all(citation.quote in source_texts[citation.sourceId] for citation in citations)
    answer_text = " ".join(block.text for block in blocks)
    assert re.search(r"\b\d+(?:\.\d+)?\s?%", answer_text) is None
    assert "확률" not in answer_text
    assert "전문가들의 의견이 일치합니다" not in answer_text


def test_result_reports_provider_used_by_the_final_stage():
    result = build_fact_check_result(
        {
            "text": "Claim", "focus": "", "consent": True,
            "sources": [{
                "id": "s1", "url": "https://example.org/source", "title": "Example",
                "publisher": "example.org", "publishedAt": None,
                "retrievedAt": "2026-09-20T00:00:00+00:00", "accessStatus": "verified",
                "sourceType": "기사", "originGroupId": None,
            }],
            "claims": [], "evidence": [],
            "llmModel": "gpt-6-luna", "llmReasoning": "max",
        },
        {
            "answer": {
                "status": "grounded",
                "overview": {"text": "개요입니다.", "citations": [{
                    "sourceId": "s1", "quote": "Verified source text.",
                }]},
                "sections": [],
                "conclusion": {"text": "결론입니다.", "citations": [{
                    "sourceId": "s1", "quote": "Verified source text.",
                }]},
                "model": "gemini-3.8-flash", "reasoning": "high",
            },
            "answerModel": "gemini-3.8-flash",
            "answerReasoning": "high",
        },
    )

    assert result.model == "gpt-6-luna"
    assert result.reasoning == "max"
    assert result.answer.model == "gemini-3.8-flash"
    assert result.answer.reasoning == "high"


def test_runtime_synthesis_skips_provider_without_verified_source_text(monkeypatch):
    import httpx
    import runtime
    from runtime import make_runtime_adapters

    def unexpected_client(*args, **kwargs):
        raise AssertionError("No readable source text must not open a provider client")

    monkeypatch.setattr(runtime.httpx, "AsyncClient", unexpected_client)
    adapters = make_runtime_adapters(Settings(
        api_key=SecretStr("openai-test-only"),
        gemini_api_key=SecretStr("gemini-test-only"),
    ))

    result = asyncio.run(adapters.synthesize({
        "sources": [{
            "id": "s1", "url": "https://example.org/source", "accessStatus": "verified",
            "sourceType": "기사",
        }],
        "sourceTexts": {"s1": "  "},
    }))

    assert result["answer"]["status"] == "insufficient_evidence"
    assert result["answerModel"] is None
    assert result["answerReasoning"] is None


def test_all_synthesis_providers_failing_preserves_verified_result(monkeypatch):
    import json
    import httpx
    import runtime
    from runtime import make_runtime_adapters

    attempted_models = []
    real_async_client = httpx.AsyncClient

    def failing_provider(request):
        attempted_models.append(json.loads(request.content)["model"])
        return httpx.Response(503, json={"error": "TEST_ONLY provider unavailable"})

    def mock_client(*args, **kwargs):
        return real_async_client(
            *args, transport=httpx.MockTransport(failing_provider), **kwargs,
        )

    monkeypatch.setattr(runtime.httpx, "AsyncClient", mock_client)
    settings = Settings(
        api_key=SecretStr("openai-test-only"),
        gemini_api_key=SecretStr("gemini-test-only"),
    )
    provider_adapters = make_runtime_adapters(settings)
    source = {
        "id": "s1", "url": "https://example.org/source", "title": "Example source",
        "publisher": "example.org", "publishedAt": None,
        "retrievedAt": "2026-09-20T00:00:00+00:00", "accessStatus": "verified",
        "sourceType": "기사", "originGroupId": None,
    }

    async def extract(state):
        return {}

    async def search(state):
        return {"sources": [source]}

    async def read(state):
        return {"sources": [source], "sourceTexts": {"s1": "The source supports this claim."}}

    async def verify(state):
        return {
            "claims": [{
                "id": "c1", "quote": "Claim", "start": 0, "end": 5, "kind": "fact",
                "verdictCode": "mostly_supported", "verdict": "대체로 확인됨",
                "tone": "positive", "summary": "원문이 주장을 뒷받침합니다.",
                "confirmed": ["Claim"], "unresolved": [], "warnings": [],
                "evidenceIds": ["e1"],
            }],
            "evidence": [{
                "id": "e1", "claimId": "c1", "sourceId": "s1",
                "quote": "The source supports this claim.",
                "quoteVerified": True, "relation": "supports",
            }],
            "llmModel": "gpt-6-luna", "llmReasoning": "max",
        }

    graph = build_runtime_workflow(
        settings,
        adapters=RuntimeAdapters(
            extract=extract, search=search, read=read, verify=verify,
            synthesize=provider_adapters.synthesize,
        ),
    )
    state = asyncio.run(graph.ainvoke({"text": "Claim", "focus": "", "consent": True}))
    result = FactCheckResponse.model_validate({"result": state["result"]}).result

    assert attempted_models == ["gemini-3.8-flash", "gemini-3.7-flash", "gpt-6-luna"]
    assert [claim.id for claim in result.claims] == ["c1"]
    assert [evidence.id for evidence in result.evidence] == ["e1"]
    assert result.model == "gpt-6-luna"
    assert result.reasoning == "max"
    assert result.answer.status == "insufficient_evidence"
    assert result.answer.model is None
    assert result.answer.reasoning is None


def test_synthesis_stage_failure_does_not_return_intermediate_result():
    import pytest

    source = {
        "id": "s1", "url": "https://example.org/source", "title": "Example source",
        "publisher": "example.org", "publishedAt": None,
        "retrievedAt": "2026-09-20T00:00:00+00:00", "accessStatus": "verified",
        "sourceType": "기사", "originGroupId": None,
    }

    async def extract(state):
        return {}

    async def search(state):
        return {"sources": [source]}

    async def read(state):
        return {"sources": [source], "sourceTexts": {"s1": "Verified source text."}}

    async def verify(state):
        return {"claims": [], "evidence": [], "llmModel": "gpt-6-luna", "llmReasoning": "max"}

    async def synthesize(state):
        raise RuntimeError("TEST_ONLY synthesis stage failure")

    graph = build_runtime_workflow(
        Settings(api_key=SecretStr("test-only")),
        adapters=RuntimeAdapters(
            extract=extract, search=search, read=read, verify=verify, synthesize=synthesize,
        ),
    )

    with pytest.raises(RuntimeError, match="TEST_ONLY synthesis stage failure"):
        asyncio.run(graph.ainvoke({"text": "Claim", "focus": "", "consent": True}))


def test_result_exposes_youtube_comments_only_as_context_not_verified_content():
    result = build_fact_check_result(
        {
            "text": "Claim",
            "focus": "",
            "consent": True,
            "sources": [{
                "id": "s1",
                "url": "https://www.youtube.com/watch?v=aB_12345678",
                "title": "Search title",
                "youtubeTitle": "API video title",
                "youtubeChannelTitle": "API channel",
                "youtubePublishedAt": "2026-09-20T12:30:00Z",
                "youtubeViewCount": "1234567",
                "youtubeComments": ["Raw public comment"],
                "youtubeDataStatus": "collected",
                "publisher": "www.youtube.com",
                "accessStatus": "unavailable",
                "sourceType": "유튜브",
                "originGroupId": "youtube",
            }],
            "claims": [],
            "evidence": [],
        },
        {
            "answer": {
                "status": "insufficient_evidence", "overview": None, "sections": [],
                "conclusion": None, "model": None, "reasoning": None,
            },
            "answerModel": None,
            "answerReasoning": None,
        },
    )

    parsed = FactCheckResponse.model_validate({"result": result.model_dump(mode="json")}).result
    assert parsed.sources[0].youtubeTitle == "API video title"
    assert parsed.sources[0].youtubeChannelTitle == "API channel"
    assert parsed.sources[0].youtubePublishedAt == "2026-09-20T12:30:00Z"
    assert parsed.sources[0].youtubeViewCount == "1234567"
    assert parsed.sources[0].youtubeComments == ["Raw public comment"]
    assert parsed.sources[0].accessStatus == "unavailable"
    assert any("유튜브 공개 댓글" in warning for warning in parsed.warnings)
