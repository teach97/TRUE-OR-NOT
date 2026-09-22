"""Isolated settings and extraction graph tests; no paid API calls."""
import asyncio
import importlib.util


def test_settings_load_file_without_exposing_key(tmp_path, monkeypatch):
    assert importlib.util.find_spec("runtime") is not None, "Runtime wiring missing"
    from runtime import load_settings
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    path = tmp_path / ".env"
    path.write_text(
        "OPENAI_API_KEY=test-file-value\nGEMINI_API_KEY=gemini-file-value\n",
        encoding="utf-8",
    )
    settings = load_settings(path)
    assert settings.api_key.get_secret_value() == "test-file-value"
    assert settings.gemini_api_key.get_secret_value() == "gemini-file-value"
    assert "test-file-value" not in repr(settings)
    assert "gemini-file-value" not in repr(settings)
    monkeypatch.setenv("OPENAI_API_KEY", "test-process-value")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-process-value")
    assert load_settings(path).api_key.get_secret_value() == "test-process-value"
    assert load_settings(path).gemini_api_key.get_secret_value() == "gemini-process-value"


def test_extraction_graph_ends_without_fabricating_verdict():
    assert importlib.util.find_spec("runtime") is not None, "Runtime wiring missing"
    from runtime import build_extraction_graph

    async def extract(state):
        return {"claims": [{"id": "c1", "quote": state["text"]}]}

    state = asyncio.run(build_extraction_graph(extract).ainvoke({"text": "claim", "focus": "", "consent": True}))
    assert state["claims"] == [{"id": "c1", "quote": "claim"}]
    assert "result" not in state
