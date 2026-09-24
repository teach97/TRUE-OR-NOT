"""Offline API boundary checks; no provider calls."""
import importlib.util

import pytest
from pydantic import ValidationError


def test_health_and_status_do_not_claim_provider_readiness(monkeypatch):
    assert importlib.util.find_spec("main") is not None, "FastAPI application is missing"
    from fastapi.testclient import TestClient
    import main
    from main import app
    from pydantic import SecretStr
    from runtime import Settings

    monkeypatch.setattr(main, "load_settings", lambda: Settings(api_key=SecretStr("")))
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        body = health.json()
        assert body["status"] == "ok" and body["service"] == "factlens-backend"
        assert isinstance(body.get("revision"), str) and body["revision"]
        status = client.get("/api/fact-check")
        assert status.status_code == 200
        assert status.headers["cache-control"] == "no-store"
        assert status.json() == {
            "configured": False, "workflowReady": False,
            "engine": "langgraph", "model": None, "reasoning": None,
            "webSearch": False, "phase": "api-foundation",
            "modelOptions": [
                {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash", "configured": False},
                {"id": "gemini-3.7-flash", "label": "Gemini 3.7 Flash", "configured": False},
                {"id": "gpt-6-luna", "label": "GPT-6 Luna Max", "configured": False},
            ],
        }
        assert client.post("/api/fact-check", json={
            "text": "claim", "focus": "", "consent": True,
        }).status_code == 503
        assert client.get("/openapi.json").status_code == 200


def test_status_reports_ready_for_configured_runtime(monkeypatch):
    from fastapi.testclient import TestClient
    from pydantic import SecretStr
    from runtime import Settings
    import main
    from main import app

    monkeypatch.setattr(
        main,
        "load_settings",
        lambda: Settings(
            api_key=SecretStr("test-only"),
            gemini_api_key=SecretStr("gemini-test-only"),
        ),
    )
    with TestClient(app) as client:
        assert client.get("/api/fact-check").json() == {
            "configured": True, "workflowReady": True,
            "engine": "langgraph", "model": "gemini-3.8-flash", "reasoning": "high",
            "webSearch": True, "phase": "workflow-ready",
            "modelOptions": [
                {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash", "configured": True},
                {"id": "gemini-3.7-flash", "label": "Gemini 3.7 Flash", "configured": True},
                {"id": "gpt-6-luna", "label": "GPT-6 Luna Max", "configured": True},
            ],
        }


def test_status_reports_gpt6_luna_when_only_openai_is_configured(monkeypatch):
    from fastapi.testclient import TestClient
    from pydantic import SecretStr
    from runtime import Settings
    import main
    from main import app

    monkeypatch.setattr(main, "load_settings", lambda: Settings(api_key=SecretStr("test-only")))
    with TestClient(app) as client:
        assert client.get("/api/fact-check").json()["model"] == "gpt-6-luna"


def test_status_reports_gemini_fallback_when_openai_is_missing(monkeypatch):
    from fastapi.testclient import TestClient
    from pydantic import SecretStr
    from runtime import Settings
    import main
    from main import app

    monkeypatch.setattr(
        main,
        "load_settings",
        lambda: Settings(
            api_key=SecretStr(""),
            gemini_api_key=SecretStr("gemini-test-only"),
        ),
    )
    with TestClient(app) as client:
        assert client.get("/api/fact-check").json() == {
            "configured": True, "workflowReady": True,
            "engine": "langgraph", "model": "gemini-3.8-flash", "reasoning": "high",
            "webSearch": True, "phase": "workflow-ready",
            "modelOptions": [
                {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash", "configured": True},
                {"id": "gemini-3.7-flash", "label": "Gemini 3.7 Flash", "configured": True},
                {"id": "gpt-6-luna", "label": "GPT-6 Luna Max", "configured": False},
            ],
        }



def test_request_preserves_original_text():
    assert importlib.util.find_spec("schemas") is not None, "Request schema is missing"
    from schemas import FactCheckRequest
    request = FactCheckRequest(text="  검증할 주장  ", focus="", consent=True)
    assert request.model_dump() == {
        "text": "  검증할 주장  ", "focus": "", "consent": True,
        "modelPreference": "auto",
    }
    selected = FactCheckRequest(
        text="claim", focus="", consent=True, modelPreference="gpt-6-luna"
    )
    assert selected.modelPreference == "gpt-6-luna"


@pytest.mark.parametrize("change", [
    {"text": " \n\t"}, {"text": "a" * 12001}, {"text": 123},
    {"text": "😀" * 6001}, {"focus": "a" * 501},
    {"focus": None}, {"consent": False}, {"consent": 1},
    {"consent": "true"}, {"extra": "not allowed"},
])
def test_request_rejects_invalid_input(change):
    assert importlib.util.find_spec("schemas") is not None, "Request schema is missing"
    from schemas import FactCheckRequest
    with pytest.raises(ValidationError):
        FactCheckRequest.model_validate({"text": "claim", "focus": "", "consent": True, **change})


def test_request_rejects_unknown_model_preference():
    assert importlib.util.find_spec("schemas") is not None, "Request schema is missing"
    from schemas import FactCheckRequest
    with pytest.raises(ValidationError):
        FactCheckRequest.model_validate({
            "text": "claim", "focus": "", "consent": True,
            "modelPreference": "unknown-model",
        })


@pytest.mark.parametrize("missing", ["text", "focus", "consent"])
def test_request_requires_all_contract_fields(missing):
    assert importlib.util.find_spec("schemas") is not None, "Request schema is missing"
    from schemas import FactCheckRequest
    payload = {"text": "claim", "focus": "", "consent": True}
    del payload[missing]
    with pytest.raises(ValidationError):
        FactCheckRequest.model_validate(payload)
