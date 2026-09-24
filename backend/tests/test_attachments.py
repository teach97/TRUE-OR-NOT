"""Link and image attachment paths; no external traffic (all transports mocked)."""
import asyncio
import base64
import json

import httpx
import pytest
from pydantic import SecretStr, ValidationError


def test_request_accepts_blank_text_only_with_image():
    from schemas import FactCheckRequest

    payload = {
        "text": "", "focus": "", "consent": True,
        "image": {"mime": "image/jpeg", "data": base64.b64encode(b"x" * 100).decode()},
    }
    request = FactCheckRequest.model_validate(payload)
    assert request.text == "" and request.image is not None


def test_request_rejects_blank_text_without_image():
    from schemas import FactCheckRequest

    with pytest.raises(ValidationError):
        FactCheckRequest.model_validate({"text": "  ", "focus": "", "consent": True})


def test_request_rejects_bad_link_and_image():
    from schemas import FactCheckRequest

    with pytest.raises(ValidationError):
        FactCheckRequest.model_validate(
            {"text": "hi", "focus": "", "consent": True, "linkUrl": "ftp://x/y"})
    with pytest.raises(ValidationError):
        FactCheckRequest.model_validate(
            {"text": "hi", "focus": "", "consent": True,
             "image": {"mime": "image/gif", "data": "eA=="}})
    with pytest.raises(ValidationError):
        FactCheckRequest.model_validate(
            {"text": "hi", "focus": "", "consent": True,
             "image": {"mime": "image/png", "data": "!!!"}})


def test_structured_image_payload_shapes():
    from providers import LLMProvider, request_structured_image

    seen = {}

    def handler(request):
        seen[request.url.host] = json.loads(request.content)
        if "openai" in request.url.host:
            return httpx.Response(200, json={"status": "completed", "output": [
                {"type": "message", "content": [{"type": "output_text", "text": "{}"}]}]})
        return httpx.Response(200, json={"status": "completed", "output_text": "{}"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            gemini = LLMProvider("gemini", "gemini-3.8-flash", "high", "k")
            await request_structured_image(
                gemini, client, instructions="i", input_data={"caption": "c"},
                image={"mime": "image/jpeg", "data": "eA=="},
                schema={"type": "object"}, max_output_tokens=10)
            openai = LLMProvider("openai", "gpt-6-luna", "max", "k")
            await request_structured_image(
                openai, client, instructions="i", input_data={"caption": "c"},
                image={"mime": "image/png", "data": "eA=="},
                schema={"type": "object"}, max_output_tokens=10)

    asyncio.run(run())
    parts = seen["generativelanguage.googleapis.com"]["input"]
    assert parts[0] == {"type": "text", "text": '{"caption": "c"}'}
    assert parts[1] == {"type": "image", "data": "eA==", "mime_type": "image/jpeg"}
    content = seen["api.openai.com"]["input"]
    assert content[0]["role"] == "user"
    assert content[0]["content"][1] == {
        "type": "input_image", "image_url": "data:image/png;base64,eA=="}


def test_extract_image_claims_replaces_state_text(monkeypatch):
    import extraction
    from providers import LLMProvider

    async def fake_image(provider, client, **kwargs):
        assert kwargs["image"] == {"mime": "image/jpeg", "data": "eA=="}
        return json.dumps({"observedText": "Zucc is a lizard.", "claims": [
            {"quote": "Zucc is a lizard", "kind": "fact", "searchQuery": "Zucc lizard"}]})

    monkeypatch.setattr(extraction, "request_structured_image", fake_image)
    state = {"text": "", "focus": "", "consent": True,
             "image": {"mime": "image/jpeg", "data": "eA=="}}
    update = asyncio.run(extraction.extract_image_claims(
        state, state["image"], client=None,
        provider=LLMProvider("gemini", "gemini-3.8-flash", "high", "k")))
    assert update["text"] == "Zucc is a lizard."
    assert update["claims"][0]["start"] == 0
    assert update["searchQueries"] == {"c1": "Zucc lizard"}


def test_extract_page_claims_replaces_state_text(monkeypatch):
    import extraction
    from providers import LLMProvider

    async def fake_structured(provider, client, **kwargs):
        assert kwargs["input_data"] == {"text": "Page body text.", "focus": ""}
        return json.dumps({"claims": [
            {"quote": "Page body", "kind": "fact", "searchQuery": ""}]})

    monkeypatch.setattr(extraction, "request_structured", fake_structured)
    update = asyncio.run(extraction.extract_page_claims(
        "Page body text.", client=None,
        provider=LLMProvider("openai", "gpt-6-luna", "max", "k")))
    assert update["text"] == "Page body text."
    assert update["claims"][0]["quote"] == "Page body"
    assert "searchQueries" not in update


def test_read_prepends_link_seed_without_network(monkeypatch):
    import runtime
    from runtime import Settings, make_runtime_adapters

    async def fake_read(state, youtube_reader=None):
        return {"sources": state["sources"], "sourceTexts": {}, "sourceSections": {}}

    monkeypatch.setattr(runtime, "read_sources", fake_read)
    settings = Settings(api_key=SecretStr(""))
    adapters = make_runtime_adapters(settings)
    state = {"sources": [{"id": "s1", "url": "https://example.org/a"}],
             "linkUrl": "https://example.com/page"}
    update = asyncio.run(adapters.read(state))
    assert update["sources"][0]["id"] == "s0"
    assert update["sources"][0]["url"] == "https://example.com/page"
    assert update["sources"][0]["accessStatus"] == "pending"


def test_workflow_preserves_link_and_image_state_keys():
    from workflow import build_workflow

    seen = {}

    async def capture(state):
        seen.update({key: state.get(key) for key in ("text", "linkUrl", "image")})
        return {}

    graph = build_workflow(
        extract=capture, search=capture, read=capture, verify=capture, synthesize=capture)
    asyncio.run(graph.ainvoke({
        "text": "https://example.com/", "focus": "", "consent": True,
        "linkUrl": "https://example.com/",
        "image": {"mime": "image/jpeg", "data": "eA=="},
    }))
    assert seen == {
        "text": "https://example.com/",
        "linkUrl": "https://example.com/",
        "image": {"mime": "image/jpeg", "data": "eA=="},
    }


def test_extract_url_only_fetches_page(monkeypatch):
    import runtime
    from runtime import Settings, make_runtime_adapters

    async def fake_fetch(url):
        assert url == "https://example.com/page"
        return ("Fetched page body.", url)

    async def fake_page(page_text, **kwargs):
        assert page_text == "Fetched page body."
        return {"claims": [{"id": "c1", "quote": "Fetched page", "kind": "fact",
                            "start": 0, "end": 12}], "text": page_text}

    monkeypatch.setattr(runtime, "fetch_public_text", fake_fetch)
    monkeypatch.setattr(runtime, "extract_page_claims", fake_page)
    settings = Settings(api_key=SecretStr("test-only"))
    adapters = make_runtime_adapters(settings)
    state = {"text": "https://example.com/page", "focus": "", "consent": True,
             "linkUrl": "https://example.com/page"}
    update = asyncio.run(adapters.extract(state))
    assert update["text"] == "Fetched page body."
    assert update["llmModel"] == "gpt-6-luna"
