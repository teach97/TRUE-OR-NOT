"""Offline input-packet and original-citation regression tests."""
import asyncio
from copy import deepcopy
import json

import httpx
import pytest

from answer_synthesis import synthesize_answer
from providers import LLMProvider, ProviderCallError
from verification import verify_claims
from contracts import FactCheckResponse
from pydantic import SecretStr
import runtime
from runtime import RuntimeAdapters, Settings, build_runtime_workflow, make_runtime_adapters
from streaming import stream_events
import runtime_adapters


PROVIDER = LLMProvider("openai", "gpt-6-luna", "max", "test-only")
SUPPORT = "The Atlas river reached record levels in 2024."
COUNTER = "The Atlas river did not reach record levels in 2025."
CONDITION = "This record concerns Seoul, 2024, and metres, not another population or unit."
FILLER = "An unrelated cooking recipe discusses ingredients and kitchen equipment. "


def state_for(body, kind="fact"):
    return {
        "text": "Atlas river reached record levels?", "focus": "date and location",
        "claims": [{"id": "c1", "quote": "Atlas river reached record levels?", "kind": kind,
                    "start": 0, "end": 34, "verdictCode": "mostly_supported" if kind == "fact" else "not_checkable",
                    "summary": "출처가 해당 연도의 기록을 설명합니다.", "confirmed": ["지역·연도를 확인했습니다."],
                    "unresolved": ["다른 연도에는 적용하지 않습니다."], "warnings": [], "evidenceIds": ["e1"]}],
        "searchQueries": {"c1": "Atlas river 2024"},
        "sources": [{"id": "s1", "url": "https://example.org/record", "title": "Atlas record",
                     "publisher": "Example", "publishedAt": "2024-06-01", "accessStatus": "verified",
                     "sourceType": "기사", "snippet": "DO-NOT-SEND-SEARCH-SNIPPET"}],
        "sourceTexts": {"s1": body},
        "evidence": [{"id": "e1", "claimId": "c1", "sourceId": "s1", "quote": SUPPORT,
                      "quoteTranslation": "Atlas 강은 2024년에 기록적인 수위에 도달했습니다.",
                      "quoteVerified": True, "relation": "supports"}],
    }


def judgment(quote=SUPPORT):
    return {"claims": [{"claimId": "c1", "verdictCode": "mostly_supported", "factScore": 90,
                        "summary": "출처에서 해당 기록을 확인했습니다.", "confirmed": ["기록을 확인했습니다."],
                        "unresolved": [], "evidence": [{"sourceId": "s1", "quote": quote,
                        "relation": "supports", "comparison": "same"}]}]}


def answer(quote=SUPPORT):
    block = {"text": "제공된 출처의 기록입니다.", "citations": [{"sourceId": "s1", "quote": quote}]}
    return {"status": "grounded", "overview": block, "sections": [], "conclusion": block}


def run_stage(stage, state, response, seen):
    def handler(request):
        body = json.loads(request.content)
        seen.update(json.loads(body["input"]))
        assert body["model"] == "gpt-6-luna" and body["reasoning"]["effort"] == "max"
        return httpx.Response(200, json={"status": "completed", "output": [{"type": "message",
            "content": [{"type": "output_text", "text": json.dumps(response, ensure_ascii=False)}]}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await stage(state, client=client, provider=PROVIDER)
    return asyncio.run(run())


def test_verification_selects_late_support_counter_and_nearby_conditions():
    body = "DO-NOT-SEND-LEAD " + FILLER * 180 + CONDITION + " " + SUPPORT + " " + FILLER * 30 + COUNTER
    state = state_for(body)
    before = deepcopy(state)
    seen = {}
    result = run_stage(verify_claims, state, judgment(), seen)
    packet = json.dumps(seen["sources"], ensure_ascii=False)
    assert SUPPORT in packet and COUNTER in packet and CONDITION in packet
    assert "DO-NOT-SEND-LEAD" not in packet and "DO-NOT-SEND-SEARCH-SNIPPET" not in packet
    assert sum(len(p["text"]) for p in seen["sources"][0]["passages"]) < 6_000
    for passage in seen["sources"][0]["passages"]:
        assert body[passage["start"]:passage["end"]] == passage["text"]
    assert result["claims"][0]["verdictCode"] == "mostly_supported"
    assert result["evidence"][0]["quote"] == SUPPORT
    assert state == before


def test_synthesis_reuses_validated_quote_translation_and_context_not_bulk():
    body = "DO-NOT-SEND-LEAD " + FILLER * 75 + CONDITION + " " + SUPPORT + " " + FILLER * 180
    state = state_for(body)
    seen = {}
    result = run_stage(synthesize_answer, state, answer(), seen)
    packet = json.dumps(seen, ensure_ascii=False)
    assert "DO-NOT-SEND-LEAD" not in packet and "DO-NOT-SEND-SEARCH-SNIPPET" not in packet
    assert CONDITION in packet and SUPPORT in packet
    assert seen["evidence"][0]["quoteTranslation"] == "Atlas 강은 2024년에 기록적인 수위에 도달했습니다."
    assert seen["sources"][0]["contextOnly"] is False
    assert result["overview"]["citations"][0]["quote"] == SUPPORT
    assert len(packet) < 4_000


def test_forecast_context_preserves_speaker_date_negation_and_conditions():
    forecast = "In 2025 Demis forecast AGI around 2030."
    caveat = "This is not a guaranteed date and depends on reasoning progress."
    body = "DO-NOT-SEND-LEAD " + FILLER * 180 + forecast + " " + caveat
    state = state_for(body, "prediction")
    state["text"] = "AGI는 2030년 안에 오나?"
    state["claims"][0]["quote"] = state["text"]
    state["claims"][0]["evidenceIds"] = []
    state["searchQueries"] = {"c1": "AGI 2030년"}
    state["evidence"] = []
    seen = {}
    result = run_stage(synthesize_answer, state, answer(forecast), seen)
    packet = json.dumps(seen["sources"], ensure_ascii=False)
    assert forecast in packet and caveat in packet
    assert "DO-NOT-SEND-LEAD" not in packet
    assert seen["sources"][0]["contextOnly"] is True
    assert seen["claims"][0]["verdictCode"] == "not_checkable"
    assert seen["evidence"] == []
    assert result["status"] == "grounded"


def test_verification_rejects_a_real_quote_outside_the_supplied_passages():
    outside = "The bakery opened a branch in another city."
    body = outside + " " + FILLER * 180 + SUPPORT
    result = run_stage(verify_claims, state_for(body), judgment(outside), {})
    assert result["evidence"] == []
    assert result["claims"][0]["verdictCode"] == "insufficient_evidence"
    assert result["claims"][0]["warnings"]


def test_synthesis_rejects_a_real_quote_outside_the_supplied_packet():
    outside = "The bakery opened a branch in another city."
    body = outside + " " + FILLER * 60 + SUPPORT + " " + FILLER * 120
    with pytest.raises(ProviderCallError):
        run_stage(synthesize_answer, state_for(body), answer(outside), {})


def test_forecast_keywords_do_not_match_inside_unrelated_english_words():
    forecast = "AGI is forecast for 2030, not a confirmed schedule."
    body = "MAGIC TRICKS ARE UNRELATED. " * 600 + forecast
    state = state_for(body, "prediction")
    state["claims"][0]["quote"] = "AGI 2030"
    state["claims"][0]["evidenceIds"] = []
    state["searchQueries"] = {"c1": "AGI 2030"}
    state["evidence"] = []
    seen = {}
    result = run_stage(synthesize_answer, state, answer(forecast), seen)
    assert forecast in json.dumps(seen["sources"])
    assert sum(len(p["text"]) for p in seen["sources"][0]["passages"]) < 1_000
    assert result["status"] == "grounded"


def test_no_keyword_match_has_explicit_prefix_fallback():
    body = "A different topic has no matching entity. " + FILLER * 180
    state = state_for(body, "prediction")
    state["claims"][0]["evidenceIds"] = []
    state["evidence"] = []
    seen = {}
    run_stage(synthesize_answer, state, answer("A different topic has no matching entity."), seen)
    assert seen["sources"][0]["selection"] == "fallback"
    assert seen["sources"][0]["contextOnly"] is True
    assert seen["sources"][0]["passages"] == [{"start": 0, "end": 6_000, "text": body[:6_000]}]


def test_overbroad_match_keeps_bounded_fallback_instead_of_silently_dropping_windows():
    body = SUPPORT + (" Atlas river data. " + FILLER * 3) * 100
    state = state_for(body)
    seen = {}
    run_stage(verify_claims, state, judgment(), seen)
    assert seen["sources"][0]["selection"] == "fallback"
    assert seen["sources"][0]["passages"] == [{"start": 0, "end": 6_000, "text": body[:6_000]}]


@pytest.mark.parametrize("field,value", [("quoteVerified", False), ("id", "not-linked"), ("claimId", "other")])
def test_unverified_or_unlinked_evidence_is_not_promoted_to_a_verified_packet(field, value):
    state = state_for(FILLER * 100 + SUPPORT)
    state["evidence"][0][field] = value
    seen = {}
    run_stage(synthesize_answer, state, answer(), seen)
    assert seen["evidence"] == []
    assert seen["sources"][0]["contextOnly"] is True


def test_all_validated_support_and_counter_quotes_survive_a_large_packet():
    first = "Atlas observation supports the finding: " + "a" * 1_800
    second = "Atlas observation contradicts another year: " + "b" * 1_800
    third = "Atlas observation supplies a material condition: " + "c" * 1_800
    body = FILLER * 40 + first + " " + FILLER * 40 + second + " " + FILLER * 40 + third
    state = state_for(body)
    state["claims"][0]["evidenceIds"] = ["e1", "e2", "e3"]
    state["evidence"] = [{"id": f"e{index}", "claimId": "c1", "sourceId": "s1", "quote": quote,
                          "quoteVerified": True, "relation": relation}
                         for index, (quote, relation) in enumerate([(first, "supports"), (second, "contradicts"),
                                                                   (third, "context")], 1)]
    reply = answer(first)
    reply["overview"]["citations"] = [{"sourceId": "s1", "quote": q} for q in (first, second, third)]
    seen = {}
    run_stage(synthesize_answer, state, reply, seen)
    assert [item["relation"] for item in seen["evidence"]] == ["supports", "contradicts", "context"]
    assert len(seen["sources"][0]["passages"]) == 3
    assert sum(len(p["text"]) for p in seen["sources"][0]["passages"]) > 6_000
    packet = json.dumps(seen, ensure_ascii=False)
    assert all(quote in packet for quote in (first, second, third))


def test_whitespace_normalized_evidence_keeps_exact_original_passage_offsets():
    original = "The Atlas river reached\nrecord levels in 2024."
    body = FILLER * 100 + original
    state = state_for(body)
    seen = {}
    run_stage(synthesize_answer, state, answer(original), seen)
    assert seen["evidence"][0]["quote"] == SUPPORT
    passage = seen["sources"][0]["passages"][0]
    assert body[passage["start"]:passage["end"]] == passage["text"]
    assert original in passage["text"]


def test_source_excerpt_offsets_are_original_character_indices_not_utf16_units():
    body = "🍀" * 1_000 + SUPPORT
    seen = {}
    run_stage(synthesize_answer, state_for(body), answer(), seen)
    assert seen["sources"][0]["passages"] == [{"start": 550, "end": 1_046,
                                               "text": "🍀" * 450 + SUPPORT}]


def test_repeated_verified_quote_keeps_each_distinct_date_and_place_context():
    repeated = "The Atlas river reached record levels."
    first_context = "This report concerns Seoul in 1990."
    second_context = "This report concerns Busan in 2024."
    body = first_context + " " + repeated + " " + FILLER * 180 + second_context + " " + repeated
    state = state_for(body)
    state["evidence"][0]["quote"] = repeated
    seen = {}
    run_stage(synthesize_answer, state, answer(repeated), seen)
    packet = json.dumps(seen["sources"], ensure_ascii=False)
    assert first_context in packet and second_context in packet
    assert len(seen["sources"][0]["passages"]) == 2


@pytest.mark.parametrize("kind,expected_calls", [("fact", 3), ("prediction", 2)])
def test_real_runtime_stream_finishes_with_late_grounded_passages(monkeypatch, kind, expected_calls):
    quote = SUPPORT if kind == "fact" else "In 2025 Demis forecast AGI around 2030."
    state = state_for("DO-NOT-SEND-LEAD " + FILLER * 180 + quote + " This is not a guaranteed schedule.", kind)
    extracted_quote = "Atlas river reached record levels?" if kind == "fact" else "AGI는 2030년 안에 오나?"
    query = "Atlas river 2024" if kind == "fact" else "AGI 2030년"
    question = extracted_quote + " 지역·시점·조건을 구분하여 자세히 설명해 주세요." * 6
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert body["model"] == "deepseek-v4.1-flash" and body["reasoning_effort"] == "max"
        if len(requests) == 1:
            value = {"claims": [{"quote": extracted_quote, "kind": kind, "searchQuery": query}]}
        elif kind == "fact" and len(requests) == 2:
            value = judgment(quote)
        else:
            value = answer(quote)
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop",
            "message": {"content": json.dumps(value, ensure_ascii=False)}}]})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(runtime_adapters.httpx, "AsyncClient", lambda *a, **kw:
                        real_client(*a, transport=httpx.MockTransport(handler), **kw))
    settings = Settings(api_key=SecretStr(""), explabs_api_key=SecretStr("test-only"))
    adapters = make_runtime_adapters(settings)

    async def search(current):
        return {"sources": deepcopy(state["sources"])}

    async def read(current):
        return {"sources": deepcopy(state["sources"]), "sourceTexts": dict(state["sourceTexts"])}

    graph = build_runtime_workflow(settings, adapters=RuntimeAdapters(extract=adapters.extract, search=search,
        read=read, verify=adapters.verify, synthesize=adapters.synthesize))

    async def run():
        return [json.loads(event) async for event in stream_events(graph, {"text": question, "focus": "",
            "consent": True, "modelPreference": "deepseek-v4.1-flash"})]

    events = asyncio.run(run())
    assert len(requests) == expected_calls
    assert events[-1]["type"] == "result"
    assert [event["type"] for event in events].count("preview") == 1
    result = FactCheckResponse.model_validate({"result": events[-1]["result"]}).result
    assert result.answer.status == "grounded"
    assert result.answer.overview.citations[0].quote == quote
    assert result.answer.model == "deepseek-v4.1-flash" and result.answer.reasoning == "max"
    assert result.sources[0].url == "https://example.org/record"
    assert result.claims[0].verdictCode == ("mostly_supported" if kind == "fact" else "not_checkable")
    assert all("DO-NOT-SEND" not in json.dumps(json.loads(r["messages"][1]["content"]), ensure_ascii=False)
               for r in requests[1:])
