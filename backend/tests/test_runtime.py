"""Isolated settings and extraction graph tests; no paid API calls."""
import asyncio
import importlib.util
from pathlib import Path

import httpx
from pydantic import SecretStr


def test_settings_load_file_without_exposing_key(tmp_path, monkeypatch):
    assert importlib.util.find_spec("runtime") is not None, "Runtime wiring missing"
    from runtime import load_settings
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    path = tmp_path / ".env"
    path.write_text(
        "OPENAI_API_KEY=test-file-value\nGEMINI_API_KEY=gemini-file-value\nYOUTUBE_API_KEY=youtube-file-value\n",
        encoding="utf-8",
    )
    settings = load_settings(path)
    assert settings.api_key.get_secret_value() == "test-file-value"
    assert settings.gemini_api_key.get_secret_value() == "gemini-file-value"
    assert settings.youtube_api_key.get_secret_value() == "youtube-file-value"
    assert "test-file-value" not in repr(settings)
    assert "gemini-file-value" not in repr(settings)
    assert "youtube-file-value" not in repr(settings)
    monkeypatch.setenv("OPENAI_API_KEY", "test-process-value")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-process-value")
    monkeypatch.setenv("YOUTUBE_API_KEY", "youtube-process-value")
    assert load_settings(path).api_key.get_secret_value() == "test-process-value"
    assert load_settings(path).gemini_api_key.get_secret_value() == "gemini-process-value"
    assert load_settings(path).youtube_api_key.get_secret_value() == "youtube-process-value"


def test_extraction_graph_ends_without_fabricating_verdict():
    assert importlib.util.find_spec("runtime") is not None, "Runtime wiring missing"
    from runtime import build_extraction_graph

    async def extract(state):
        return {"claims": [{"id": "c1", "quote": state["text"]}]}

    state = asyncio.run(build_extraction_graph(extract).ainvoke({"text": "claim", "focus": "", "consent": True}))
    assert state["claims"] == [{"id": "c1", "quote": "claim"}]
    assert "result" not in state


def test_youtube_api_key_is_loaded_from_server_environment_and_redacted(monkeypatch):
    assert importlib.util.find_spec("runtime") is not None, "Runtime wiring missing"
    from runtime import load_settings

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("YOUTUBE_API_KEY", "youtube-test-value")
    settings = load_settings(Path("missing-test-env-file"))

    assert settings.youtube_api_key.get_secret_value() == "youtube-test-value"
    assert "youtube-test-value" not in repr(settings)


def test_llm_search_is_used_directly_without_a_search_notice(monkeypatch):
    import runtime
    from runtime import Settings, make_runtime_adapters

    requested_paths = []

    def handler(request):
        requested_paths.append(request.url.path)
        assert request.url.path == "/v1/responses"
        return httpx.Response(200, json={"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed", "action": {"sources": [
                {"url": "https://example.org/report", "title": "Fallback report"},
            ]}},
        ]})

    real_async_client = httpx.AsyncClient

    def mock_async_client(**kwargs):
        return real_async_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(runtime.httpx, "AsyncClient", mock_async_client)
    adapters = make_runtime_adapters(Settings(
        api_key=SecretStr("test-openai-key"),
    ))
    update = asyncio.run(adapters.search({
        "consent": True,
        "modelPreference": "gpt-6-luna",
        "claims": [{"id": "c1", "kind": "fact", "quote": "Claim"}],
    }))
    assert requested_paths == ["/v1/responses"]
    assert update["sources"][0]["searchProvider"] == "openai_web_search"
    assert "searchNotice" not in update


def test_llm_runtime_ignores_environment_proxy_for_provider_connection(monkeypatch):
    import json
    import runtime
    from runtime import Settings, make_runtime_adapters

    real_async_client = httpx.AsyncClient

    def handler(request):
        assert request.url.host == "api.openai.com"
        return httpx.Response(200, json={"status": "completed", "output": [{
            "type": "message", "content": [{"type": "output_text", "text": json.dumps({
                "claims": [{"quote": "AGI는 2030년 안에 오나?", "kind": "prediction", "searchQuery": "AGI 2030년"}],
            }, ensure_ascii=False)}],
        }]})

    def mock_async_client(**kwargs):
        assert kwargs.get("trust_env") is False
        return real_async_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(runtime.httpx, "AsyncClient", mock_async_client)
    adapters = make_runtime_adapters(Settings(api_key=SecretStr("test-openai-key")))
    update = asyncio.run(adapters.extract({
        "text": "AGI는 2030년 안에 오나?", "focus": "", "consent": True,
        "modelPreference": "gpt-6-luna",
    }))
    assert update["claims"][0]["kind"] == "prediction"


def test_runtime_read_stage_uses_youtube_adapter_without_adding_comments_to_source_texts(monkeypatch):
    import runtime

    def handler(request):
        if request.url.path.endswith("/videos"):
            return httpx.Response(200, json={"items": [{
                "snippet": {
                    "title": "실제 영상 제목",
                    "channelTitle": "실제 채널",
                    "publishedAt": "2026-09-20T12:30:00Z",
                },
                "statistics": {"viewCount": "1234567"},
            }]})
        return httpx.Response(200, json={"items": [{"snippet": {
            "topLevelComment": {"snippet": {"textDisplay": "댓글 맥락"}}
        }}]})

    real_async_client = httpx.AsyncClient

    def mock_async_client(**kwargs):
        assert kwargs == {"timeout": 8.0, "trust_env": False}
        return real_async_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(runtime.httpx, "AsyncClient", mock_async_client)
    settings = runtime.Settings(
        api_key=SecretStr("llm-test-key"),
        youtube_api_key=SecretStr("youtube-test-key"),
    )
    state = asyncio.run(runtime.make_runtime_adapters(settings).read({"sources": [{
        "id": "s1",
        "url": "https://youtube.com/watch?v=aB_12345678",
        "title": "Search title",
        "sourceType": "유튜브",
        "accessStatus": "pending",
    }]}))

    assert state["sources"][0]["youtubeTitle"] == "실제 영상 제목"
    assert state["sources"][0]["youtubeChannelTitle"] == "실제 채널"
    assert state["sources"][0]["youtubePublishedAt"] == "2026-09-20T12:30:00Z"
    assert state["sources"][0]["youtubeViewCount"] == "1234567"
    assert state["sources"][0]["youtubeComments"] == ["댓글 맥락"]
    assert state["sourceTexts"] == {}
