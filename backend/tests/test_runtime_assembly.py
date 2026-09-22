"""Runtime assembly tests; fake adapters keep the four-node graph offline."""
import asyncio

from contracts import FactCheckResponse
from runtime import RuntimeAdapters, Settings, build_fact_check_result, build_runtime_workflow
from pydantic import SecretStr


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
