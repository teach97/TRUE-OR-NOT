"""Runtime assembly tests; fake adapters keep the four-node graph offline."""
import asyncio

from contracts import FactCheckResponse
from runtime import RuntimeAdapters, Settings, build_fact_check_result, build_runtime_workflow
from pydantic import SecretStr


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

            graph = build_runtime_workflow(
                Settings(api_key=SecretStr("test-only")),
                adapters=RuntimeAdapters(extract=extract, search=search, read=read, verify=verify),
            )
            return await graph.ainvoke({"text": question, "focus": "", "consent": True})

    state = asyncio.run(run())
    assert len(requests) == 2
    assert state["searchQueries"] == {"c1": keywords}
    result = FactCheckResponse.model_validate({"result": state["result"]}).result
    assert result.claims[0].kind == "prediction"
    assert result.claims[0].verdictCode == "not_checkable"
    assert "searchQueries" not in result.model_dump()
    assert "searchQuery" not in result.claims[0].model_dump()


def test_runtime_graph_assembles_valid_final_result_after_four_stages():
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
        }]}

    graph = build_runtime_workflow(
        Settings(api_key=SecretStr("test-only")),
        adapters=RuntimeAdapters(extract=extract, search=search, read=read, verify=verify),
    )
    state = asyncio.run(graph.ainvoke({
        "text": "Claim", "focus": "", "consent": True,
    }))

    assert seen == ["extracting", "searching", "reading", "verifying"]
    parsed = FactCheckResponse.model_validate({"result": state["result"]})
    assert parsed.result.sources[0].url == "https://example.org/source"
    assert parsed.result.claims[0].evidenceIds == ["e1"]
    assert "sourceTexts" in state


def test_result_reports_provider_used_by_the_final_stage():
    result = build_fact_check_result(
        {"text": "Claim", "focus": "", "consent": True, "sources": []},
        {
            "claims": [],
            "evidence": [],
            "llmModel": "gemini-3.8-flash",
            "llmReasoning": "high",
        },
    )

    assert result.model == "gemini-3.8-flash"
    assert result.reasoning == "high"


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
                "youtubeComments": ["Raw public comment"],
                "youtubeDataStatus": "collected",
                "publisher": "www.youtube.com",
                "accessStatus": "unavailable",
                "sourceType": "유튜브",
                "originGroupId": "youtube",
            }],
        },
        {"claims": [], "evidence": []},
    )

    parsed = FactCheckResponse.model_validate({"result": result.model_dump(mode="json")}).result
    assert parsed.sources[0].youtubeTitle == "API video title"
    assert parsed.sources[0].youtubeComments == ["Raw public comment"]
    assert parsed.sources[0].accessStatus == "unavailable"
    assert any("유튜브 공개 댓글" in warning for warning in parsed.warnings)
