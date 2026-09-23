"""Real LangGraph via HTTP boundary; adapters contain offline fixtures only."""
from fastapi.testclient import TestClient
import main
import pytest
from workflow import build_workflow


@pytest.mark.parametrize("mode", ["exception", "missing", "null"])
def test_graph_failure_returns_safe_error(mode):
    async def stage(state):
        if mode == "exception":
            raise RuntimeError("PRIVATE_PROVIDER_DIAGNOSTIC")
        return {"result": None} if mode == "null" else {"sources": []}

    graph = build_workflow(extract=stage, search=stage, read=stage, verify=stage)
    main.app.dependency_overrides[main.get_workflow] = lambda: graph
    try:
        with TestClient(main.app, raise_server_exceptions=False) as client:
            response = client.post("/api/fact-check", json={"text": "claim", "focus": "", "consent": True})
        assert response.status_code == 502
        assert response.json()["code"] == "AGENT_FAILED"
        assert "PRIVATE_PROVIDER_DIAGNOSTIC" not in response.text
        assert "result" not in response.json()
    finally:
        main.app.dependency_overrides.clear()


@pytest.mark.parametrize("body", [
    '{"text":"PRIVATE_INPUT","focus":"","consent":false}',
    '{"text":"PRIVATE_INPUT","focus":"","consent":1}',
    '{"text":"   ","focus":"","consent":true}',
    '{"text":"PRIVATE_INPUT",',
])
def test_invalid_http_input_is_safe_and_never_runs_graph(body):
    calls = []

    async def stage(state):
        calls.append(state)
        return {}

    graph = build_workflow(extract=stage, search=stage, read=stage, verify=stage)
    main.app.dependency_overrides[main.get_workflow] = lambda: graph
    try:
        with TestClient(main.app) as client:
            response = client.post("/api/fact-check", content=body, headers={"Content-Type": "application/json"})
        assert response.status_code == 422
        assert response.json()["code"] == "INVALID_REQUEST"
        assert "PRIVATE_INPUT" not in response.text
        assert calls == []
    finally:
        main.app.dependency_overrides.clear()


def test_post_rejects_malformed_result_contract():
    async def stage(state):
        return {"result": {"fixture": True}}

    graph = build_workflow(extract=stage, search=stage, read=stage, verify=stage)
    main.app.dependency_overrides[main.get_workflow] = lambda: graph
    try:
        with TestClient(main.app, raise_server_exceptions=False) as client:
            response = client.post("/api/fact-check", json={
                "text": "claim", "focus": "", "consent": True,
            })
        assert response.status_code == 502
        assert response.json() == {
            "code": "AGENT_FAILED", "message": "검증을 완료하지 못했습니다."
        }
    finally:
        main.app.dependency_overrides.clear()


def test_post_runs_graph_and_returns_only_result():
    assert hasattr(main, "get_workflow"), "Workflow injection boundary is missing"
    seen = []
    fixture_result = {
        "text": "  claim  ", "focus": "", "demo": False,
        "model": "gpt-6-luna", "reasoning": "max",
        "checkedAt": "2026-09-20T00:00:00+00:00",
        "claims": [], "sources": [], "evidence": [], "warnings": [],
    }

    async def extract(state):
        seen.append("extracting")
        assert state == {"text": "  claim  ", "focus": "", "consent": True}
        return {"claims": [{"id": "c1"}]}

    async def search(state):
        seen.append("searching")
        assert state["claims"] == [{"id": "c1"}]
        return {"sources": []}

    async def read(state):
        seen.append("reading")
        return {"evidence": []}

    async def verify(state):
        seen.append("verifying")
        return {"result": fixture_result}

    graph = build_workflow(extract=extract, search=search, read=read, verify=verify)
    main.app.dependency_overrides[main.get_workflow] = lambda: graph
    try:
        with TestClient(main.app) as client:
            response = client.post("/api/fact-check", json={"text": "  claim  ", "focus": "", "consent": True})
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-store"
        assert response.json() == {"result": fixture_result}
        assert seen == ["extracting", "searching", "reading", "verifying"]
    finally:
        main.app.dependency_overrides.clear()
