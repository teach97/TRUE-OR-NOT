"""Direct answers reuse grounded judgments without a second provider request."""
import asyncio
from copy import deepcopy
import json

import httpx
from pydantic import SecretStr
import pytest

from contracts import FactCheckResponse
import runtime
from runtime import RuntimeAdapters, Settings, build_runtime_workflow, make_runtime_adapters
from streaming import stream_events
import runtime_adapters


QUESTION = "인류는 달에 갔나?"
QUOTE = "Apollo 11 landed humans on the Moon in July 1969."
SUMMARY = "미국은 1969년 아폴로 11호로 인간을 달에 보냈습니다."
CONFIRMED = "아폴로 11호의 유인 달 착륙 기록이 확인됩니다."
UNRESOLVED = "이 근거는 미국의 아폴로 임무 기록을 다룹니다."


def checked_state():
    return {
        "text": QUESTION, "focus": "달 방문 기록의 사실 여부", "consent": True,
        "modelPreference": "deepseek-v4.1-flash",
        "claims": [{
            "id": "c1", "quote": QUESTION, "kind": "fact", "start": 0, "end": len(QUESTION),
            "factScore": 90, "verdictCode": "mostly_supported", "verdict": "대체로 확인됨",
            "tone": "positive", "summary": SUMMARY, "confirmed": [CONFIRMED],
            "unresolved": [UNRESOLVED], "warnings": [], "evidenceIds": ["e1"],
        }],
        "sources": [{
            "id": "s1", "url": "https://example.org/apollo", "title": "Apollo 11 record",
            "publisher": "Example", "accessStatus": "verified", "sourceType": "기사",
            "retrievedAt": "2026-10-05T00:00:00+00:00", "originGroupId": "example.org",
        }],
        "sourceTexts": {"s1": QUOTE},
        "evidence": [{
            "id": "e1", "claimId": "c1", "sourceId": "s1", "quote": QUOTE,
            "quoteVerified": True, "relation": "supports",
            "quoteTranslation": "아폴로 11호는 1969년 7월 인간을 달에 착륙시켰습니다.",
        }],
        "llmModel": "deepseek-v4.1-flash", "llmReasoning": "max",
    }


def completion(value):
    return httpx.Response(200, json={"choices": [{
        "finish_reason": "stop", "message": {"content": json.dumps(value, ensure_ascii=False)},
    }]})


def generated_answer():
    citation = {"sourceId": "s1", "quote": QUOTE}
    return {
        "status": "grounded", "overview": {"text": "기존 합성 경로 응답입니다.", "citations": [citation]},
        "sections": [], "conclusion": {"text": "생성한 결론입니다.", "citations": [citation]},
    }


def provider_adapters(monkeypatch, handler):
    real_client = httpx.AsyncClient

    def client(*args, **kwargs):
        return real_client(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(runtime_adapters.httpx, "AsyncClient", client)
    return make_runtime_adapters(Settings(api_key=SecretStr(""), explabs_api_key=SecretStr("test-only")))


@pytest.mark.parametrize("code,relation", [("mostly_supported", "supports"), ("contradicted", "contradicts")])
def test_simple_grounded_fact_reuses_text_citations_and_skips_provider(monkeypatch, code, relation):
    state = checked_state()
    state["claims"][0]["verdictCode"] = code
    state["evidence"][0]["relation"] = relation
    requests = []

    def handler(request):
        requests.append(request)
        return completion(generated_answer())

    result = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))

    assert requests == []
    answer = result["answer"]
    assert answer["status"] == "grounded"
    assert answer["overview"]["text"] == SUMMARY
    assert answer["overview"]["citations"] == [{"sourceId": "s1", "quote": QUOTE}]
    items = [item for section in answer["sections"] for item in section["items"]]
    assert {item["text"] for item in items} == {CONFIRMED, UNRESOLVED}
    assert answer["model"] is None and answer["reasoning"] is None
    assert result["answerModel"] is None and result["answerReasoning"] is None
    assert state["evidence"][0]["quoteTranslation"] == "아폴로 11호는 1969년 7월 인간을 달에 착륙시켰습니다."


@pytest.mark.parametrize("path,value", [
    (("text",), "상세 설명 요청입니다. " * 15 + QUESTION),
    (("text",), "🌕" * 60 + "?"),
    (("text",), "인류는 달에 갔습니다."),
    (("text",), "인류는 달에 갔나? 화성에도 갔나?"),
    (("claims", 0, "kind"), "prediction"),
    (("claims", 0, "kind"), "opinion"),
    (("claims", 0, "kind"), "unclear"),
    (("claims", 0, "verdictCode"), "partially_supported"),
    (("claims", 0, "verdictCode"), "conflicting_sources"),
    (("claims", 0, "verdictCode"), "missing_context"),
    (("claims", 0, "verdictCode"), "insufficient_evidence"),
    (("claims", 0, "warnings"), ["확인하지 못한 조건이 있습니다."]),
    (("claims", 0, "unresolved"), ["CONDITION_UNKNOWN"]),
    (("claims", 0, "summary"), "가" * 1201),
    (("claims", 0, "summary"), "🌕" * 601),
    (("claims", 0, "confirmed"), ["확인 내용"] * 4),
    (("claims", 0, "unresolved"), ["미해결 내용"] * 4),
    (("claims", 0, "confirmed"), ["가" * 1201]),
    (("linkUrl",), "https://example.org/input"),
    (("image",), {"mime": "image/png", "data": "test-only"}),
    (("recoveryRequested",), True),
    (("evidence", 0, "quoteVerified"), False),
    (("evidence", 0, "quote"), "원문에는 없는 인용 문장입니다."),
    (("evidence", 0, "sourceId"), "unknown"),
    (("evidence", 0, "claimId"), "other-claim"),
    (("evidence", 0, "id"), "other-evidence"),
    (("evidence", 0, "relation"), "context"),
], ids=lambda value: str(value)[:30])
def test_complex_or_unusable_fact_keeps_existing_provider_path(monkeypatch, path, value):
    state = checked_state()
    target = state
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        return completion(generated_answer())

    result = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))

    assert len(requests) == 1
    assert requests[0]["model"] == "deepseek-v4.1-flash"
    assert requests[0]["reasoning_effort"] == "max"
    assert result["answer"]["overview"]["text"] == "기존 합성 경로 응답입니다."
    assert result["answer"]["model"] == "deepseek-v4.1-flash"


@pytest.mark.parametrize("changes", [
    {"jevMode": True},
    {"sourceTexts": {}},
    {"sources": []},
])
def test_direct_answer_never_promotes_missing_evidence_or_jev(monkeypatch, changes):
    state = {**checked_state(), **changes}

    def handler(request):
        raise AssertionError("This case must neither compose a grounded answer nor open a provider request")

    result = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))
    assert result["answer"]["status"] == "insufficient_evidence"


def test_multiple_claims_keep_provider_synthesis(monkeypatch):
    state = checked_state()
    state["claims"].append({**state["claims"][0], "id": "c2", "evidenceIds": []})
    requests = []

    def handler(request):
        requests.append(request)
        return completion(generated_answer())

    result = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))
    assert len(requests) == 1
    assert result["answer"]["model"] == "deepseek-v4.1-flash"


def test_direct_answer_uses_grounded_result_even_without_another_provider_key(monkeypatch):
    def unexpected_client(*args, **kwargs):
        raise AssertionError("Composing an already grounded answer must not open another provider client")

    monkeypatch.setattr(runtime_adapters.httpx, "AsyncClient", unexpected_client)
    result = asyncio.run(make_runtime_adapters(Settings(api_key=SecretStr(""))).synthesize(checked_state()))
    assert result["answer"]["overview"]["text"] == SUMMARY
    assert result["answer"]["model"] is None


def test_direct_answer_deduplicates_identical_grounded_citations(monkeypatch):
    state = checked_state()
    state["evidence"].append({**state["evidence"][0], "id": "e2"})
    state["claims"][0]["evidenceIds"].append("e2")
    result = asyncio.run(make_runtime_adapters(Settings(api_key=SecretStr(""))).synthesize(state))
    assert result["answer"]["overview"]["citations"] == [{"sourceId": "s1", "quote": QUOTE}]


def test_direct_answer_keeps_multiple_supporting_sources(monkeypatch):
    state = checked_state()
    state["sources"].append({**state["sources"][0], "id": "s2", "url": "https://example.net/apollo"})
    state["sourceTexts"]["s2"] = "The Moon landing by Apollo 11 took place in 1969."
    state["evidence"].append({**state["evidence"][0], "id": "e2", "sourceId": "s2", "quote": state["sourceTexts"]["s2"]})
    state["claims"][0]["evidenceIds"].append("e2")
    result = asyncio.run(make_runtime_adapters(Settings(api_key=SecretStr(""))).synthesize(state))
    assert result["answer"]["overview"]["citations"] == [
        {"sourceId": "s1", "quote": QUOTE},
        {"sourceId": "s2", "quote": "The Moon landing by Apollo 11 took place in 1969."},
    ]
    assert "하나의 출처" not in result["answer"]["conclusion"]["text"]


def test_runtime_stream_finishes_with_two_llm_requests_and_preserves_verification(monkeypatch):
    state = checked_state()
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            return completion({"claims": [{"quote": QUESTION, "kind": "fact", "searchQuery": "아폴로 11 달 착륙"}]})
        if len(requests) == 2:
            return completion({"claims": [{
                "claimId": "c1", "verdictCode": "mostly_supported", "factScore": 90,
                "summary": SUMMARY, "confirmed": [CONFIRMED], "unresolved": [UNRESOLVED],
                "evidence": [{"sourceId": "s1", "quote": QUOTE, "quoteTranslation": state["evidence"][0]["quoteTranslation"],
                              "relation": "supports", "comparison": "same"}],
            }]})
        return completion(generated_answer())

    adapters = provider_adapters(monkeypatch, handler)

    async def search(current):
        return {"sources": deepcopy(state["sources"])}

    async def read(current):
        return {"sources": deepcopy(state["sources"]), "sourceTexts": dict(state["sourceTexts"])}

    graph = build_runtime_workflow(
        Settings(api_key=SecretStr(""), explabs_api_key=SecretStr("test-only")),
        adapters=RuntimeAdapters(extract=adapters.extract, search=search, read=read,
                                 verify=adapters.verify, synthesize=adapters.synthesize),
    )

    async def run():
        return [json.loads(event) async for event in stream_events(graph, {
            "text": QUESTION, "focus": state["focus"], "consent": True,
            "modelPreference": "deepseek-v4.1-flash",
        })]

    events = asyncio.run(run())
    assert len(requests) == 2
    assert all(request["model"] == "deepseek-v4.1-flash" and request["reasoning_effort"] == "max" for request in requests)
    assert events[-1]["type"] == "result"
    assert [event["type"] for event in events].count("preview") == 1
    result = FactCheckResponse.model_validate({"result": events[-1]["result"]}).result
    assert result.answer.overview.text == SUMMARY
    assert result.answer.model is None and result.answer.reasoning is None
    assert result.model == "deepseek-v4.1-flash" and result.reasoning == "max"
    assert result.claims[0].verdictCode == "mostly_supported"
    assert result.evidence[0].quote == QUOTE and result.evidence[0].quoteVerified is True
    assert result.evidence[0].quoteTranslation == "아폴로 11호는 1969년 7월 인간을 달에 착륙시켰습니다."
    assert result.sources[0].url == "https://example.org/apollo"
