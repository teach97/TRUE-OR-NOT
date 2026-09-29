"""Safe diagnostics for failed provider fallbacks."""
import asyncio
import logging

import httpx
import pytest
from pydantic import SecretStr

import runtime
from providers import ProviderCallError


def test_provider_fallback_logs_model_stage_and_status_without_secrets(monkeypatch, caplog):
    attempted_models = []

    async def fail_extraction(state, *, client, provider):
        attempted_models.append(provider.model)
        request = httpx.Request("POST", "https://provider.invalid")
        response = httpx.Response(429, request=request)
        cause = httpx.HTTPStatusError("rate limited", request=request, response=response)
        raise ProviderCallError("Provider request failed") from cause

    monkeypatch.setattr(runtime, "extract_claims", fail_extraction)
    settings = runtime.Settings(
        api_key=SecretStr("openai-secret-must-not-be-logged"),
        gemini_api_key=SecretStr("gemini-secret-must-not-be-logged"),
    )
    adapters = runtime.make_runtime_adapters(settings)

    async def run():
        with pytest.raises(ValueError, match="EXTRACTION_FAILED"):
            await adapters.extract({"text": "private claim", "focus": "private focus"})

    with caplog.at_level(logging.WARNING, logger="runtime"):
        asyncio.run(run())

    logs = "\n".join(record.getMessage() for record in caplog.records)
    assert attempted_models == ["gemini-3.8-flash", "gemini-3.7-flash", "gpt-6-luna"]
    assert logs.count("provider attempt failed") == 3
    assert "stage=EXTRACTION_FAILED" in logs
    assert "provider=gemini-3.8-flash" in logs
    assert "provider=gemini-3.7-flash" in logs
    assert "provider=gpt-6-luna" in logs
    assert "http_status=429" in logs
    assert "must-not-be-logged" not in logs
    assert "private claim" not in logs
