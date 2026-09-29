"""Intent gate tests; no external traffic (all transports mocked)."""
import asyncio
import json

import httpx
import pytest


def decision_response(decision):
    return httpx.Response(200, json={
        "status": "completed",
        "steps": [{
            "type": "model_output",
            "content": [{"type": "text", "text": json.dumps(decision, ensure_ascii=False)}],
        }],
    })


def test_intent_verify_passes_focus_through(monkeypatch):
    import intent
    from providers import LLMProvider

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: decision_response(
                    {"action": "verify", "reply": "", "focus": "그럼 검색해서 찾아"}))
        ) as client:
            return await intent.classify_intent(
                "그럼 검색해서 찾아", {"previousText": "기사 원문"},
                client=client,
                provider=LLMProvider("gemini", "gemini-3.8-flash", "high", "k"),
            )

    assert asyncio.run(run()) == {
        "action": "verify", "reply": None, "focus": "그럼 검색해서 찾아"}


def test_intent_reply_requires_text():
    import intent
    from providers import LLMProvider, ProviderCallError

    async def run_empty():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: decision_response({"action": "reply", "reply": "  ", "focus": ""}))
        ) as client:
            return await intent.classify_intent(
                "하이", {}, client=client,
                provider=LLMProvider("gemini", "gemini-3.8-flash", "high", "k"))

    with pytest.raises(ProviderCallError):
        asyncio.run(run_empty())

    async def run_reply():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={
                    "status": "completed",
                    "output": [{
                        "type": "message",
                        "content": [{
                            "type": "output_text",
                            "text": json.dumps(
                                {"action": "reply", "reply": "안녕!", "focus": ""},
                                ensure_ascii=False),
                        }],
                    }],
                }))
        ) as client:
            return await intent.classify_intent(
                "하이", {}, client=client,
                provider=LLMProvider("openai", "gpt-6-luna", "max", "k"))

    assert asyncio.run(run_reply()) == {"action": "reply", "reply": "안녕!", "focus": None}


def test_intent_endpoint_rejects_bad_payloads_and_reports_unconfigured(monkeypatch):
    from fastapi.testclient import TestClient
    from pydantic import SecretStr
    from runtime import Settings
    import main
    from main import app

    monkeypatch.setattr(
        main, "load_settings",
        lambda: Settings(api_key=SecretStr(""), gemini_api_key=SecretStr("")),
    )
    with TestClient(app) as client:
        assert client.post("/api/intent", json={}).status_code == 422
        assert client.post("/api/intent", json={"text": ""}).status_code == 422
        assert client.post(
            "/api/intent", json={"text": "하이", "context": {"previousText": 1}}).status_code == 422
        assert client.post(
            "/api/intent", json={"text": "하이", "modelPreference": "nope"}).status_code == 422
        unconfigured = client.post("/api/intent", json={"text": "하이"})
        assert unconfigured.status_code == 503


def test_intent_endpoint_uses_selected_model(monkeypatch):
    import main
    from fastapi.testclient import TestClient
    from main import app
    from pydantic import SecretStr
    from runtime import Settings
    import runtime

    real_async_client = httpx.AsyncClient
    hits: list[str] = []

    def handler(request):
        hits.append(request.url.host + request.url.path)
        if request.url.host == "api.openai.com":
            return httpx.Response(200, json={
                "status": "completed",
                "output": [{
                    "type": "message",
                    "content": [{
                        "type": "output_text",
                        "text": json.dumps(
                            {"action": "reply", "reply": "hi", "focus": ""},
                            ensure_ascii=False),
                    }],
                }],
            })
        return decision_response({"action": "reply", "reply": "hi", "focus": ""})

    def mock_client(*args, **kwargs):
        return real_async_client(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(main.httpx, "AsyncClient", mock_client)
    monkeypatch.setattr(
        main, "load_settings",
        lambda: Settings(api_key=SecretStr("openai-test-only"), gemini_api_key=SecretStr("gemini-test-only")),
    )
    with TestClient(app) as client:
        response = client.post("/api/intent", json={"text": "하이", "modelPreference": "gpt-6-luna"})
        assert response.status_code == 200
        assert hits == ["api.openai.com/v1/responses"]
        picked = client.post("/api/intent", json={"text": "하이", "modelPreference": "gemini-3.7-flash"})
        assert picked.status_code == 200
        assert hits[-1] == "generativelanguage.googleapis.com/v1beta/interactions"


def test_intent_endpoint_reports_missing_selected_model(monkeypatch):
    import main
    from fastapi.testclient import TestClient
    from main import app
    from pydantic import SecretStr
    from runtime import Settings

    monkeypatch.setattr(
        main, "load_settings",
        lambda: Settings(api_key=SecretStr("openai-test-only"), gemini_api_key=SecretStr("")),
    )
    with TestClient(app) as client:
        missing = client.post("/api/intent", json={"text": "하이", "modelPreference": "gemini-3.7-flash"})
        assert missing.status_code == 503
