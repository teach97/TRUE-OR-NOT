"""Market assembly fallback order; transports mocked, no live traffic."""
import asyncio
from types import SimpleNamespace


def _settings(toss=True, finnhub=True):
    return SimpleNamespace(
        toss_client_id=SimpleNamespace(get_secret_value=lambda: "tid" if toss else " "),
        toss_client_secret=SimpleNamespace(get_secret_value=lambda: "tsec" if toss else " "),
        finnhub_api_key=SimpleNamespace(get_secret_value=lambda: "fkey" if finnhub else " "),
    )


def test_fetch_market_prefers_toss(monkeypatch):
    import finnhub
    import runtime
    import tossinvest

    async def fake_toss_quote(symbol, **kwargs):
        return {"symbol": symbol, "current": 100.0, "previousClose": 90.0}

    async def fake_toss_candles(symbol, **kwargs):
        return {"symbol": symbol, "points": [
            {"time": 1, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.0, "volume": 5.0}]}

    async def no_finnhub(*args, **kwargs):
        raise AssertionError("finnhub must not be called when toss succeeds")

    monkeypatch.setattr(tossinvest, "fetch_stock_quote", fake_toss_quote)
    monkeypatch.setattr(tossinvest, "fetch_candles", fake_toss_candles)
    monkeypatch.setattr(finnhub, "fetch_stock_quote", no_finnhub)
    result = asyncio.run(runtime._fetch_market(["005930"], _settings()))
    assert result["source"] == "tossinvest"
    assert result["symbol"] == "005930"
    assert result["changePercent"] == round((100.0 - 90.0) / 90.0 * 100, 2)


def test_fetch_market_falls_back_to_finnhub(monkeypatch):
    import finnhub
    import runtime
    import tossinvest

    async def failing_toss(*args, **kwargs):
        return {"symbol": "X", "error": "upstream_unavailable"}

    async def fake_finnhub_quote(symbol, **kwargs):
        return {"symbol": symbol, "current": 10.0, "previousClose": 10.0}

    async def fake_finnhub_candles(symbol, **kwargs):
        return {"symbol": symbol, "points": [
            {"time": 1, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0}]}

    monkeypatch.setattr(tossinvest, "fetch_stock_quote", failing_toss)
    monkeypatch.setattr(finnhub, "fetch_stock_quote", fake_finnhub_quote)
    monkeypatch.setattr(finnhub, "fetch_candles", fake_finnhub_candles)
    result = asyncio.run(runtime._fetch_market(["TSLA"], _settings()))
    assert result["source"] == "finnhub"
    assert result["changePercent"] == 0.0


def test_fetch_market_returns_none_without_keys_or_symbols():
    import asyncio

    import runtime

    assert asyncio.run(runtime._fetch_market([], _settings())) is None
    assert asyncio.run(runtime._fetch_market(["TSLA"], _settings(toss=False, finnhub=False))) is None
