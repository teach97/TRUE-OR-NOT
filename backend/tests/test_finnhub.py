"""Finnhub quote adapter; no live traffic (all transports mocked)."""
import asyncio

import httpx


def run(symbol, handler, api_key="fh-test"):
    from finnhub import fetch_stock_quote

    async def run_once():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await fetch_stock_quote(symbol, api_key=api_key, client=client)

    return asyncio.run(run_once())


def test_quote_returns_prices():
    def handler(request):
        assert request.url.host == "finnhub.io"
        assert request.url.params["symbol"] == "AAPL"
        assert request.url.params["token"] == "fh-test"
        return httpx.Response(200, json={
            "c": 232.5, "o": 230.0, "h": 233.0, "l": 229.5, "pc": 231.0, "t": 1790482517,
        })

    result = run("aapl", handler)
    assert result == {
        "symbol": "AAPL", "current": 232.5, "open": 230.0, "high": 233.0,
        "low": 229.5, "previousClose": 231.0, "timestamp": 1790482517,
    }


def test_quote_failure_modes():
    assert run("AAPL", lambda request: httpx.Response(429, json={}))["error"] == "upstream_unavailable"
    assert run("XXXX", lambda request: httpx.Response(200, json={"c": 0, "t": 0}))["error"] == "unknown_symbol"
    assert run("AAPL", lambda request: httpx.Response(200, json=[]))["error"] == "invalid_response"
    assert run("AAPL", lambda request: httpx.Response(200, json={"c": 1}), api_key="  ")["error"] == "not_configured"
    assert run("not a symbol!", lambda request: httpx.Response(200, json={"c": 1}))["error"] == "invalid_symbol"


def test_finnhub_key_is_server_only_and_redacted(monkeypatch):
    from pathlib import Path

    from runtime import load_settings

    monkeypatch.setenv("FINNHUB_API_KEY", "test-finnhub-secret")
    settings = load_settings(Path("missing-test-env-file"))
    assert settings.finnhub_api_key.get_secret_value() == "test-finnhub-secret"
    assert "test-finnhub-secret" not in repr(settings)
