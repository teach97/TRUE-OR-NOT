"""Offline provider transport fixtures, never real model responses."""
import asyncio
import importlib.util
import json

import httpx
import pytest


@pytest.mark.parametrize("case", ["missing_key", "http", "incomplete", "duplicate", "multiple", "refusal"])
def test_extractor_rejects_unsafe_outputs(case):
    from extraction import extract_claims

    def handler(request):
        assert case != "missing_key", "Missing key must not send a request"
        if case == "http":
            return httpx.Response(401, text="private diagnostic")
        quote = "invented" if case == "invented" else "claim"
        claims = [{"quote": quote, "kind": "fact"}]
        if case == "duplicate":
            claims *= 2
        content = [{"type": "output_text", "text": json.dumps({"claims": claims})}]
        if case == "multiple":
            content *= 2
        if case == "refusal":
            content = [{"type": "refusal", "refusal": "private diagnostic"}]
        return httpx.Response(200, json={"status": "incomplete" if case == "incomplete" else "completed",
            "output": [{"type": "message", "content": content}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await extract_claims({"text": "claim", "focus": "", "consent": True},
                api_key="" if case == "missing_key" else "test-only", client=client)

    with pytest.raises(ValueError, match="^(NOT_CONFIGURED|EXTRACTION_FAILED)$"):
        asyncio.run(run())



def test_extractor_sends_documented_options_and_preserves_utf16_offsets():
    assert importlib.util.find_spec("extraction") is not None, "Extraction adapter missing"
    from extraction import extract_claims

    def handler(request):
        assert str(request.url) == "https://api.openai.com/v1/responses"
        body = json.loads(request.content)
        assert body["model"] == "gpt-5.6-luna"
        assert body["reasoning"] == {"effort": "max"}
        assert body["store"] is False
        assert body["text"]["format"]["strict"] is True
        return httpx.Response(200, json={"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps({"claims": [{"quote": "claim", "kind": "fact"}]})}
        ]}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await extract_claims({"text": "😀 claim", "focus": "", "consent": True}, api_key="test-only", client=client)

    assert asyncio.run(run()) == {"claims": [{"id": "c1", "quote": "claim", "kind": "fact", "start": 3, "end": 8}]}


def test_extractor_uses_focus_to_prioritize_without_dropping_text_claims():
    from extraction import extract_claims

    def handler(request):
        body = json.loads(request.content)
        instructions = body["instructions"]
        assert "Use the focus to prioritize claims, not as a hard filter" in instructions
        assert "Do not discard a factual claim solely because the focus asks about details absent from the text" in instructions
        return httpx.Response(200, json={"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps({"claims": [{
                "quote": "구글, '제미나이 노트북'에 맞춤형 학습 기능 추가",
                "kind": "fact",
            }]})}
        ]}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await extract_claims(
                {
                    "text": "구글, '제미나이 노트북'에 맞춤형 학습 기능 추가…'듣고 말하며 공부한다'",
                    "focus": "행사 일정과 무료 참여 조건이 궁금해요.",
                    "consent": True,
                },
                api_key="test-only",
                client=client,
            )

    result = asyncio.run(run())
    assert result["claims"][0]["quote"].startswith("구글")


def test_extractor_keeps_valid_claims_when_one_model_quote_is_not_in_source():
    from extraction import extract_claims

    def handler(request):
        return httpx.Response(200, json={"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps({"claims": [
                {"quote": "valid claim", "kind": "fact"},
                {"quote": "model paraphrase not in source", "kind": "fact"},
            ]})}
        ]}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await extract_claims(
                {"text": "valid claim", "focus": "", "consent": True},
                api_key="test-only",
                client=client,
            )

    result = asyncio.run(run())
    assert [claim["quote"] for claim in result["claims"]] == ["valid claim"]


def test_extractor_drops_invented_claim_without_fabricating_source_text():
    from extraction import extract_claims

    def handler(request):
        return httpx.Response(200, json={"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps({"claims": [{
                "quote": "invented claim",
                "kind": "fact",
            }]})}
        ]}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await extract_claims(
                {"text": "source text", "focus": "", "consent": True},
                api_key="test-only",
                client=client,
            )

    assert asyncio.run(run()) == {"claims": []}
