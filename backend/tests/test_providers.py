"""Provider priority and fallback policy tests; no network traffic."""

import asyncio

from pydantic import SecretStr


def test_configured_provider_chain_is_ordered_and_skips_missing_keys():
    from providers import configured_providers
    from runtime import Settings

    providers = configured_providers(
        Settings(
            api_key=SecretStr("openai-test-only"),
            gemini_api_key=SecretStr("gemini-test-only"),
        )
    )

    assert [(provider.kind, provider.model, provider.reasoning) for provider in providers] == [
        ("openai", "gpt-5.6-luna", "max"),
        ("gemini", "gemini-3.8-flash", "high"),
        ("gemini", "gemini-3.7-flash", "high"),
    ]

    only_gemini = configured_providers(
        Settings(api_key=SecretStr(""), gemini_api_key=SecretStr("gemini-test-only"))
    )
    assert [provider.model for provider in only_gemini] == [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
    ]


def test_run_with_fallback_tries_next_provider_after_failure():
    from providers import LLMProvider, ProviderCallError, run_with_fallback

    providers = (
        LLMProvider("openai", "gpt-5.6-luna", "max", "test-openai"),
        LLMProvider("gemini", "gemini-3.8-flash", "high", "test-gemini"),
    )
    attempts = []

    async def operation(provider):
        attempts.append(provider.model)
        if provider.kind == "openai":
            raise ProviderCallError("provider failed")
        return {"ok": True}

    result = asyncio.run(run_with_fallback(providers, operation))

    assert result == ({"ok": True}, providers[1])
    assert attempts == ["gpt-5.6-luna", "gemini-3.8-flash"]


def test_run_with_fallback_reaches_third_provider_when_first_two_fail():
    from providers import LLMProvider, ProviderCallError, run_with_fallback

    providers = (
        LLMProvider("openai", "gpt-5.6-luna", "max", "test-openai"),
        LLMProvider("gemini", "gemini-3.8-flash", "high", "test-gemini"),
        LLMProvider("gemini", "gemini-3.7-flash", "high", "test-gemini"),
    )
    attempts = []

    async def operation(provider):
        attempts.append(provider.model)
        if provider.model != "gemini-3.7-flash":
            raise ProviderCallError("provider failed")
        return {"ok": True}

    result = asyncio.run(run_with_fallback(providers, operation))

    assert result == ({"ok": True}, providers[2])
    assert attempts == [
        "gpt-5.6-luna",
        "gemini-3.8-flash",
        "gemini-3.7-flash",
    ]


def test_runtime_stage_retries_next_provider_after_adapter_failure(monkeypatch):
    import runtime
    from runtime import Settings, make_runtime_adapters

    attempts = []

    async def fake_extract(state, *, client, provider):
        attempts.append(provider.model)
        if provider.kind == "openai":
            raise ValueError("EXTRACTION_FAILED")
        return {"claims": [], "llmModel": provider.model}

    monkeypatch.setattr(runtime, "extract_claims", fake_extract)
    adapters = make_runtime_adapters(
        Settings(
            api_key=SecretStr("openai-test-only"),
            gemini_api_key=SecretStr("gemini-test-only"),
        )
    )

    result = asyncio.run(
        adapters.extract({"text": "claim", "focus": "", "consent": True})
    )

    assert attempts == ["gpt-5.6-luna", "gemini-3.8-flash"]
    assert result["llmModel"] == "gemini-3.8-flash"
