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

    monkeypatch.setattr(runtime.httpx, "AsyncClient", client)
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
    (("claims", 0, "kind"), "prediction"),
    (("claims", 0, "kind"), "opinion"),
    (("claims", 0, "verdictCode"), "conflicting_sources"),
    (("claims", 0, "summary"), "가" * 1201),
    (("claims", 0, "summary"), "🌕" * 601),
    (("claims", 0, "confirmed"), ["가" * 1201]),
    (("evidence", 0, "quoteVerified"), False),
    (("evidence", 0, "quote"), "원문에는 없는 인용 문장입니다."),
    (("evidence", 0, "sourceId"), "unknown"),
    (("evidence", 0, "claimId"), "other-claim"),
    (("evidence", 0, "id"), "other-evidence"),
    (("evidence", 0, "relation"), "context"),
], ids=lambda value: str(value)[:30])
def test_unusable_fact_keeps_existing_provider_path(monkeypatch, path, value):
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


@pytest.mark.parametrize("path,value", [
    (("text",), "상세 설명 요청입니다. " * 15 + QUESTION),
    (("text",), "🌕" * 60 + "?"),
    (("text",), "인류는 달에 갔습니다."),
    (("text",), "인류는 달에 갔나? 화성에도 갔나?"),
    (("claims", 0, "kind"), "unclear"),
    (("claims", 0, "verdictCode"), "partially_supported"),
    (("claims", 0, "verdictCode"), "missing_context"),
    (("claims", 0, "warnings"), ["확인하지 못한 조건이 있습니다."]),
    (("claims", 0, "unresolved"), ["CONDITION_UNKNOWN"]),
    (("claims", 0, "confirmed"), ["확인 내용"] * 4),
    (("claims", 0, "unresolved"), ["미해결 내용"] * 4),
    (("linkUrl",), "https://example.org/input"),
    (("image",), {"mime": "image/png", "data": "test-only"}),
    (("recoveryRequested",), True),
], ids=lambda value: str(value)[:30])
def test_verified_general_fact_finishes_without_rewriting_or_losing_conditions(monkeypatch, path, value):
    state = checked_state()
    target = state
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    before = deepcopy(state)
    requests = []

    def handler(request):
        requests.append(request)
        return completion(generated_answer())

    result = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))
    assert requests == []
    answer = result["answer"]
    assert answer["status"] == "grounded"
    assert answer["overview"]["text"] == SUMMARY
    assert answer["model"] is None and answer["reasoning"] is None
    rendered = json.dumps(answer, ensure_ascii=False)
    for text in [*state["claims"][0]["confirmed"], *state["claims"][0]["unresolved"], *state["claims"][0]["warnings"]]:
        assert text in rendered
    assert state == before


def test_verified_multiple_claims_all_appear_without_provider_synthesis(monkeypatch):
    state = checked_state()
    state["sources"].append({**state["sources"][0], "id": "s2", "url": "https://example.net/apollo12"})
    state["sourceTexts"]["s2"] = "Apollo 12 landed humans on the Moon in November 1969."
    state["claims"].append({**state["claims"][0], "id": "c2", "summary": "아폴로 12호도 달에 착륙했습니다.",
                            "confirmed": ["1969년 11월 임무입니다."], "unresolved": ["다른 탐사선의 기록은 별도입니다."],
                            "warnings": ["이번 확인 범위는 두 임무입니다."], "evidenceIds": ["e2"]})
    state["evidence"].append({**state["evidence"][0], "id": "e2", "claimId": "c2", "sourceId": "s2",
                              "quote": "Apollo 12 landed humans on the Moon in November 1969."})
    requests = []

    def handler(request):
        requests.append(request)
        return completion(generated_answer())

    answer = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))["answer"]
    assert requests == []
    assert answer["status"] == "grounded"
    assert answer["overview"]["text"] == SUMMARY
    blocks = [answer["overview"], answer["conclusion"], *[item for section in answer["sections"] for item in section["items"]]]
    rendered = json.dumps(answer, ensure_ascii=False)
    for text in ["아폴로 12호도 달에 착륙했습니다.", "1969년 11월 임무입니다.", "다른 탐사선의 기록은 별도입니다.", "이번 확인 범위는 두 임무입니다."]:
        assert text in rendered
    assert {citation["sourceId"] for block in blocks for citation in block["citations"]} == {"s1", "s2"}


@pytest.mark.parametrize("same_source_counter_first", [False, True])
def test_conflicting_judgment_preserves_both_directions_without_new_generation(monkeypatch, same_source_counter_first):
    state = checked_state()
    state["claims"][0].update(verdictCode="conflicting_sources", summary="같은 조건에서 자료들이 서로 다른 내용을 전합니다.")
    state["sources"].append({**state["sources"][0], "id": "s2", "url": "https://example.net/counter"})
    state["sourceTexts"]["s2"] = "This source contradicts the supplied claim under the same conditions."
    state["evidence"].append({**state["evidence"][0], "id": "e2", "sourceId": "s2", "relation": "contradicts",
                              "quote": state["sourceTexts"]["s2"]})
    state["claims"][0]["evidenceIds"].append("e2")
    if same_source_counter_first:
        quote = "This article also reports an opposing view under the same conditions."
        state["sourceTexts"]["s1"] += " " + quote
        state["evidence"].insert(1, {**state["evidence"][0], "id": "e0", "quote": quote, "relation": "contradicts"})
        state["claims"][0]["evidenceIds"].insert(1, "e0")
    requests = []

    def handler(request):
        requests.append(request)
        return completion(generated_answer())

    answer = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))["answer"]
    assert requests == []
    assert answer["overview"]["text"] == "같은 조건에서 자료들이 서로 다른 내용을 전합니다."
    assert {citation["sourceId"] for citation in answer["overview"]["citations"]} == {"s1", "s2"}


def test_fact_judgments_with_no_evidence_finish_as_insufficient_without_another_call(monkeypatch):
    state = checked_state()
    state["claims"][0].update(verdictCode="insufficient_evidence", summary="직접 근거가 없어 확인하지 못했습니다.", evidenceIds=[])
    state["evidence"] = []
    requests = []

    def handler(request):
        requests.append(request)
        return completion(generated_answer())

    result = asyncio.run(provider_adapters(monkeypatch, handler).synthesize(state))
    assert requests == []
    assert result["answer"]["status"] == "insufficient_evidence"
    assert state["claims"][0]["summary"] == "직접 근거가 없어 확인하지 못했습니다."


def test_research_finishes_before_composing_only_the_latest_verified_judgment(monkeypatch):
    state = checked_state()
    requests, searches = [], []
    final_source = {**state["sources"][0], "id": "s2", "url": "https://example.net/verified-apollo"}

    def handler(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            return completion({"claims": [{"quote": QUESTION, "kind": "fact", "searchQuery": "달 착륙 기록"}]})
        retry = len(requests) == 3
        return completion({"claims": [{
            "claimId": "c1", "verdictCode": "partially_supported", "factScore": 65,
            "summary": SUMMARY if retry else "검증 전 임시 요약입니다.",
            "confirmed": [CONFIRMED], "unresolved": [UNRESOLVED],
            "evidence": [{"sourceId": "s2" if retry else "s1", "quote": QUOTE if retry else "Fabricated quotation that is not in this source.",
                          "quoteTranslation": "달 착륙 기록입니다.", "relation": "supports", "comparison": "same"}],
        }]})

    adapters = provider_adapters(monkeypatch, handler)

    async def search(current):
        searches.append(current.get("recoveryCount", 0))
        return {"sources": [deepcopy(final_source if len(searches) == 2 else state["sources"][0])]}

    async def read(current):
        return {"sources": current["sources"], "sourceTexts": {current["sources"][0]["id"]: QUOTE}}

    graph = build_runtime_workflow(Settings(api_key=SecretStr(""), explabs_api_key=SecretStr("test-only")), adapters=RuntimeAdapters(
        extract=adapters.extract, search=search, read=read, verify=adapters.verify, synthesize=adapters.synthesize,
    ))

    async def run():
        return [json.loads(event) async for event in stream_events(graph, {
            "text": QUESTION, "focus": "", "consent": True, "modelPreference": "deepseek-v4.1-flash",
        })]

    events = asyncio.run(run())
    result = FactCheckResponse.model_validate({"result": events[-1]["result"]}).result
    assert searches == [0, 1]
    assert len(requests) == 3  # Extraction plus two verifications, no synthesis request.
    assert result.answer.status == "grounded"
    assert result.answer.overview.text == SUMMARY
    assert result.answer.overview.citations[0].sourceId == "s2"
    assert result.claims[0].factScore == 65
    assert "검증 전 임시 요약" not in json.dumps(result.model_dump(mode="json"), ensure_ascii=False)
    assert [event["type"] for event in events].count("preview") == 1
    assert any("재탐색" in warning for warning in result.warnings)


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

    monkeypatch.setattr(runtime.httpx, "AsyncClient", unexpected_client)
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


@pytest.mark.parametrize("code,score", [("mostly_supported", 90), ("partially_supported", 65)])
def test_runtime_stream_finishes_with_two_llm_requests_and_preserves_verification(monkeypatch, code, score):
    state = checked_state()
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            return completion({"claims": [{"quote": QUESTION, "kind": "fact", "searchQuery": "아폴로 11 달 착륙"}]})
        if len(requests) == 2:
            return completion({"claims": [{
                "claimId": "c1", "verdictCode": code, "factScore": score,
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
    assert result.claims[0].verdictCode == code
    assert result.claims[0].factScore == score
    assert result.evidence[0].quote == QUOTE and result.evidence[0].quoteVerified is True
    assert result.evidence[0].quoteTranslation == "아폴로 11호는 1969년 7월 인간을 달에 착륙시켰습니다."
    assert result.sources[0].url == "https://example.org/apollo"
