"""Stock detection and market-context assembly; no network calls."""
import asyncio


def test_detects_curated_korean_and_us_names():
    from stocks import detect_stock_symbols

    assert detect_stock_symbols("테슬라 실적이 좋아졌다") == ["TSLA"]
    assert detect_stock_symbols("삼성전자 주가는?", "반도체 확인") == ["005930"]
    assert detect_stock_symbols("엔비디아와 애플 비교", "") == ["NVDA"]


def test_detects_bare_tickers_with_particles():
    from stocks import detect_stock_symbols

    assert detect_stock_symbols("TSLA는 오늘 어때", "") == ["TSLA"]
    assert detect_stock_symbols("NVDA가 신고가래", "") == ["NVDA"]


def test_ignores_common_false_positives():
    from stocks import detect_stock_symbols

    assert detect_stock_symbols("AI 시대의 TV 이야기", "") == []
    assert detect_stock_symbols("오늘 날씨가 좋다", "") == []


def test_finance_hint_without_symbol_still_counts():
    from stocks import is_finance_question

    assert is_finance_question("코스피가 급등했다", "") is True
    assert is_finance_question("오늘 점심 뭐 먹지", "") is False


def test_build_market_context_combines_quote_and_candles():
    from stocks import build_market_context

    quote = {"symbol": "TSLA", "current": 250.0, "previousClose": 200.0}
    candles = {"symbol": "TSLA", "points": [
        {"time": 1, "open": 1.0, "high": 2.0, "low": 0.5, "close": 200.0, "volume": 10.0},
        {"time": 2, "open": 2.0, "high": 3.0, "low": 1.5, "close": 250.0, "volume": 20.0},
    ]}
    context = build_market_context("TSLA", "테슬라", quote, candles, data_as_of="2026-09-30T00:00:00+00:00")
    assert context["symbol"] == "TSLA"
    assert context["changePercent"] == 25.0
    assert len(context["candles"]) == 2


def test_build_market_context_returns_none_on_leg_failure():
    from stocks import build_market_context

    quote = {"symbol": "TSLA", "current": 250.0, "previousClose": 200.0}
    assert build_market_context("X", None, {"symbol": "X", "error": "nope"}, {"symbol": "X", "points": []}, data_as_of=None) is None
    assert build_market_context("X", None, quote, {"symbol": "X", "error": "nope"}, data_as_of=None) is None
    assert build_market_context("X", None, quote, {"symbol": "X", "points": []}, data_as_of=None) is None


def test_fetch_candles_parses_ok_response(monkeypatch):
    import json

    import httpx

    import finnhub

    payload = {"s": "ok", "t": [10, 20], "o": [1.0, 2.0], "h": [1.5, 2.5],
               "l": [0.5, 1.5], "c": [1.2, 2.2], "v": [100, 200]}

    def handler(request):
        assert request.url.params["symbol"] == "TSLA"
        return httpx.Response(200, json=payload)

    async def run():
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await finnhub.fetch_candles("TSLA", api_key="k", client=client)

    result = asyncio.run(run())
    assert [p["close"] for p in result["points"]] == [1.2, 2.2]
    assert result["points"][0]["time"] == 10


def test_fetch_candles_rejects_bad_status_and_key():
    import asyncio

    import httpx

    import finnhub

    async def run():
        transport = httpx.MockTransport(lambda request: httpx.Response(401, json={}))
        async with httpx.AsyncClient(transport=transport) as client:
            bad_key = await finnhub.fetch_candles("TSLA", api_key="  ", client=client)
            bad_symbol = await finnhub.fetch_candles("TSLA", api_key="k", client=client)
        return bad_key, bad_symbol

    bad_key, bad_symbol = asyncio.run(run())
    assert bad_key["error"] == "not_configured"
    assert bad_symbol["error"] == "upstream_unavailable"
