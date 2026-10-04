"""External API routes require explicit boolean consent before client creation."""
import pytest


@pytest.mark.parametrize("consent_fields", [
    {},
    {"consent": False},
    {"consent": "true"},
    {"consent": 1},
    {"consent": None},
], ids=["missing", "false", "string", "integer", "null"])
@pytest.mark.parametrize("route, request_fields", [
    ("/api/intent", {"text": "claim"}),
    ("/api/fact-check", {"text": "claim", "focus": ""}),
    ("/api/fact-check/stream", {"text": "claim", "focus": ""}),
    ("/api/fact-check/jev", {"text": "claim", "focus": "", "jevMode": True}),
    ("/api/summarize", {"text": "claim", "focus": ""}),
])
def test_external_route_rejects_invalid_consent_before_clients(
    monkeypatch, route, request_fields, consent_fields,
):
    import main
    from fastapi.testclient import TestClient
    from pydantic import SecretStr
    from runtime import Settings

    def load_test_settings():
        if route == "/api/intent":
            raise AssertionError("Intent must reject invalid consent before loading settings")
        return Settings(api_key=SecretStr("test-only"))

    def unexpected_client(*args, **kwargs):
        raise AssertionError("Invalid consent must not create an external client")

    monkeypatch.delenv("BACKEND_SHARED_SECRET", raising=False)
    monkeypatch.setattr(main, "load_settings", load_test_settings)
    monkeypatch.setattr(main.httpx, "AsyncClient", unexpected_client)
    with TestClient(main.app) as client:
        response = client.post(route, json={**request_fields, **consent_fields})

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"
    assert response.headers["cache-control"] == "no-store"
