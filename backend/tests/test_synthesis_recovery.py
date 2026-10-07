"""Recover token-limited synthesis without exposing reasoning or unchecked text."""

import asyncio
import json

import httpx
import pytest

from answer_synthesis import synthesize_answer
from contracts import FactCheckAnswer
from providers import LLMProvider, ProviderCallError, request_structured


QUOTE = "The evidence supports only part of this claim."


def verified_state():
    return {
        "text": "이 주장을 확인해 주세요.", "focus": "",
        "claims": [{
            "id": "c1", "kind": "fact", "quote": "이 주장",
            "verdictCode": "partially_supported", "summary": "주장은 일부만 확인됩니다.",
            "confirmed": ["확인된 조건이 있습니다."],
            "unresolved": ["나머지 조건은 확인되지 않았습니다."],
            "warnings": ["자료의 범위에 유의해야 합니다."], "evidenceIds": ["e1"],
        }],
        "sources": [{"id": "s1", "url": "https://example.org/a", "title": "원문",
                     "accessStatus": "verified", "sourceType": "기사"}],
        "sourceTexts": {"s1": QUOTE},
        "evidence": [{"id": "e1", "claimId": "c1", "sourceId": "s1", "quote": QUOTE,
                      "quoteVerified": True, "relation": "supports"}],
    }


def answer_draft():
    block = {"text": "확인된 조건에서만 성립합니다.",
             "citations": [{"sourceId": "s1", "quote": QUOTE}]}
    return {"status": "grounded", "overview": block, "sections": [], "conclusion": block}


def run_response(text, *, kind="openai", state=None, reason="max_output_tokens", completed=False,
                 strict=False, refusal=False):
    calls = []

    def handle(request):
        calls.append(json.loads(request.content))
        if kind == "experiential":
            message = {"content": text, "reasoning_content": "PRIVATE REASONING"}
            if refusal:
                message["refusal"] = "refused"
            return httpx.Response(200, json={"choices": [{
                "finish_reason": "stop" if completed else "length", "message": message,
            }]})
        output = [{"type": "reasoning", "content": [{"text": "PRIVATE REASONING"}]}]
        if refusal:
            output.append({"type": "message", "content": [{"type": "refusal", "refusal": "refused"}]})
        elif text is not None:
            output.append({"type": "message", "content": [{"type": "output_text", "text": text}]})
        return httpx.Response(200, json={
            "status": "completed" if completed else "incomplete",
            "incomplete_details": {"reason": reason}, "output": output,
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            provider = LLMProvider(kind, "test-model", "max", "test-key")
            if strict:
                return await request_structured(provider, client, instructions="test", input_data={},
                                                schema={}, max_output_tokens=4000)
            return await synthesize_answer(state or verified_state(), client=client, provider=provider)

    return asyncio.run(run()), calls


@pytest.mark.parametrize("kind", ["openai", "experiential"])
def test_complete_capped_answer_is_accepted_without_another_call(kind):
    answer, calls = run_response(json.dumps(answer_draft()), kind=kind)
    assert answer["status"] == "grounded"
    assert answer["overview"] == answer_draft()["overview"]
    assert len(calls) == 1


def test_only_complete_grounded_blocks_survive_truncated_json():
    text = '{"status":"grounded","overview":' + json.dumps(answer_draft()["overview"])
    text += ',"sections":[{"kind":"context","title":"CUT OFF'
    answer, calls = run_response(text)
    assert answer["status"] == "partial"
    assert answer["overview"] == answer_draft()["overview"]
    assert answer["sections"] == []
    assert "CUT OFF" not in json.dumps(answer)
    assert len(calls) == 1


@pytest.mark.parametrize("kind", ["openai", "experiential"])
def test_reasoning_only_cap_reuses_verified_summary_and_preserves_caveats(kind):
    answer, calls = run_response(None, kind=kind)
    assert answer["status"] == "partial"
    assert answer["overview"]["text"] == "주장은 일부만 확인됩니다."
    assert answer["overview"]["citations"][0]["quote"] == QUOTE
    rendered = json.dumps(answer, ensure_ascii=False)
    assert "나머지 조건은 확인되지 않았습니다." in rendered
    assert "자료의 범위에 유의해야 합니다." in rendered
    assert "PRIVATE REASONING" not in rendered
    assert answer["model"] is None
    assert len(calls) == 1


@pytest.mark.parametrize("invalid", ["unverified", "unlinked", "wrong_claim", "fabricated", "prediction"])
def test_no_fallback_from_unchecked_or_unlinked_evidence(invalid):
    state = verified_state()
    if invalid == "unverified":
        state["sources"][0]["accessStatus"] = "unavailable"
        # Keep an eligible source so synthesis still runs, but not the evidence source.
        state["sources"].append({**state["sources"][0], "id": "s2", "accessStatus": "verified"})
        state["sourceTexts"]["s2"] = QUOTE
    elif invalid == "unlinked":
        state["claims"][0]["evidenceIds"] = []
    elif invalid == "wrong_claim":
        state["evidence"][0]["claimId"] = "other"
    elif invalid == "fabricated":
        state["evidence"][0]["quote"] = "This fabricated quotation is not in the source."
    else:
        state["claims"][0]["kind"] = "prediction"
        state["claims"][0]["verdictCode"] = "not_checkable"
    with pytest.raises(ProviderCallError):
        run_response(None, state=state)


def test_bad_citation_in_complete_prefix_uses_checked_claim_instead():
    block = {"text": "Invented answer", "citations": [{"sourceId": "s1", "quote": "Invented quotation"}]}
    text = '{"status":"grounded","overview":' + json.dumps(block) + ',"sections":['
    answer, _ = run_response(text)
    assert answer["status"] == "partial"
    assert "Invented" not in json.dumps(answer)
    assert answer["overview"]["citations"][0]["quote"] == QUOTE


def test_unfinished_string_is_not_scanned_for_embedded_json():
    text = '{"status":"grounded","overview":{"text":"unfinished ' + json.dumps(answer_draft())
    answer, _ = run_response(text)
    assert answer["overview"]["text"] == "주장은 일부만 확인됩니다."
    assert answer["model"] is None


def test_complete_section_survives_but_unfinished_next_section_does_not():
    section = {"kind": "uncertainty", "title": "남은 조건", "items": [answer_draft()["overview"]]}
    text = '{"status":"grounded","overview":' + json.dumps(answer_draft()["overview"])
    text += ',"sections":[' + json.dumps(section) + ',{"kind":"context","title":"unfinished'
    answer, _ = run_response(text)
    assert answer["status"] == "partial"
    assert answer["sections"] == [section]


@pytest.mark.parametrize("sections", [None, "bad", {"bad": True}])
def test_malformed_complete_sections_cannot_crash_recovery(sections):
    value = {**answer_draft(), "sections": sections}
    answer, _ = run_response(json.dumps(value))
    assert answer["status"] == "partial"
    assert answer["sections"] == []


def test_oversized_qualifications_are_not_silently_dropped():
    state = verified_state()
    state["claims"][0]["unresolved"] = ["조건" * 1201]
    with pytest.raises(ProviderCallError):
        run_response(None, state=state)


def test_recovered_blocks_respect_browser_utf16_limits():
    draft = answer_draft()
    draft["overview"]["text"] = "😀" * 601
    text = '{"status":"grounded","overview":' + json.dumps(draft["overview"]) + ',"sections":['
    answer, _ = run_response(text)
    assert answer["overview"]["text"] == "주장은 일부만 확인됩니다."


def test_partial_contract_still_requires_cited_overview_and_conclusion():
    from pydantic import ValidationError

    answer, _ = run_response(None)
    assert FactCheckAnswer.model_validate(answer).status == "partial"
    answer["overview"]["citations"] = []
    with pytest.raises(ValidationError):
        FactCheckAnswer.model_validate(answer)


def test_runtime_uses_capped_recovery_without_smaller_retry_or_next_provider(monkeypatch):
    import runtime
    from pydantic import SecretStr

    calls = []
    real_client = httpx.AsyncClient

    def handle(request):
        calls.append(json.loads(request.content)["max_output_tokens"])
        return httpx.Response(200, json={
            "status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"},
            "output": [{"type": "reasoning", "content": [{"text": "PRIVATE REASONING"}]}],
        })

    monkeypatch.setattr(runtime.httpx, "AsyncClient", lambda *args, **kwargs:
                        real_client(*args, transport=httpx.MockTransport(handle), **kwargs))
    adapters = runtime.make_runtime_adapters(runtime.Settings(
        api_key=SecretStr("test-only"), gemini_api_key=SecretStr("next-test-only"),
    ))
    # Mixed fact/forecast answers still use synthesis; only the fact is recoverable.
    state = verified_state()
    state["claims"].append({"id": "c2", "kind": "prediction", "verdictCode": "not_checkable",
                            "summary": "미래 전망은 확정하지 않았습니다.", "evidenceIds": []})
    result = asyncio.run(adapters.synthesize(state))
    assert result["answer"]["status"] == "partial"
    assert result["answerModel"] is None
    assert calls == [4000]


@pytest.mark.parametrize("kind", ["openai", "experiential"])
def test_non_synthesis_requests_still_reject_capped_output(kind):
    with pytest.raises(ProviderCallError):
        run_response(json.dumps(answer_draft()), kind=kind, strict=True)


@pytest.mark.parametrize("reason", ["content_filter", "unknown"])
def test_other_incomplete_reasons_are_not_salvaged(reason):
    with pytest.raises(ProviderCallError):
        run_response(None, reason=reason)


@pytest.mark.parametrize("kind", ["openai", "experiential"])
def test_refusals_are_not_salvaged(kind):
    with pytest.raises(ProviderCallError):
        run_response(None, kind=kind, refusal=True)


def test_completed_malformed_output_still_fails_validation():
    with pytest.raises(ProviderCallError):
        run_response('{"status":"grounded",', completed=True)
