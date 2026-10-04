"""Finnhub-only market assembly; external transports are mocked."""
import asyncio
from types import SimpleNamespace

import pytest


def _settings(configured=True):
    return SimpleNamespace(
        finnhub_api_key=SimpleNamespace(
            get_secret_value=lambda: "test-only" if configured else " ",
        ),
    )


def test_fetch_market_needs_only_finnhub_settings(monkeypatch):
    import finnhub
    import runtime

    calls = []

    async def quote(symbol, **kwargs):
        calls.append(("quote", symbol))
        assert kwargs["api_key"] == "test-only"
        return {"symbol": symbol, "current": 100.0, "previousClose": 90.0}

    async def candles(symbol, **kwargs):
        calls.append(("candles", symbol))
        return {"symbol": symbol, "points": [{
            "time": 1, "open": 1.0, "high": 2.0,
            "low": 0.5, "close": 1.0, "volume": 5.0,
        }]}

    monkeypatch.setattr(finnhub, "fetch_stock_quote", quote)
    monkeypatch.setattr(finnhub, "fetch_candles", candles)
    result = asyncio.run(runtime._fetch_market(["TSLA", "AAPL"], _settings()))
    assert result["source"] == "finnhub"
    assert result["symbol"] == "TSLA"
    assert result["changePercent"] == 11.11
    assert len(result["candles"]) == 1
    assert calls == [("quote", "TSLA"), ("candles", "TSLA")]


def test_quote_failure_omits_market_without_requesting_candles(monkeypatch):
    import finnhub
    import runtime

    async def unavailable(*args, **kwargs):
        return {"error": "upstream_unavailable"}

    async def unexpected(*args, **kwargs):
        pytest.fail("Candles must not be fetched after a failed quote")

    monkeypatch.setattr(finnhub, "fetch_stock_quote", unavailable)
    monkeypatch.setattr(finnhub, "fetch_candles", unexpected)
    assert asyncio.run(runtime._fetch_market(["TSLA"], _settings())) is None


def test_candle_failure_omits_market(monkeypatch):
    import finnhub
    import runtime

    async def quote(*args, **kwargs):
        return {"current": 10.0, "previousClose": 10.0}

    async def unavailable(*args, **kwargs):
        return {"error": "upstream_unavailable"}

    monkeypatch.setattr(finnhub, "fetch_stock_quote", quote)
    monkeypatch.setattr(finnhub, "fetch_candles", unavailable)
    assert asyncio.run(runtime._fetch_market(["TSLA"], _settings())) is None


def test_fetch_market_skips_missing_key_or_symbols(monkeypatch):
    import finnhub
    import runtime

    async def unexpected(*args, **kwargs):
        pytest.fail("No market request is allowed without a key or symbol")

    monkeypatch.setattr(finnhub, "fetch_stock_quote", unexpected)
    assert asyncio.run(runtime._fetch_market([], _settings())) is None
    assert asyncio.run(runtime._fetch_market(["TSLA"], _settings(False))) is None


def test_provider_exception_omits_market_without_failing_verification(monkeypatch):
    import finnhub
    import runtime

    async def unavailable(*args, **kwargs):
        raise TimeoutError("test-only failure")

    monkeypatch.setattr(finnhub, "fetch_stock_quote", unavailable)
    assert asyncio.run(runtime._fetch_market(["TSLA"], _settings())) is None
