"""Toss Securities adapter; all transports mocked, no live traffic."""
import asyncio


def _state():
    return {"token_calls": 0}


def _handler_factory(state, candles=None):
    import httpx

    async def _noop(_request):
        raise AssertionError("unexpected call")

    def handler(request):
        path = request.url.path
        if path == "/oauth2/token":
            state["token_calls"] += 1
            return httpx.Response(200, json={
                "access_token": "tok-%d" % state["token_calls"],
                "token_type": "Bearer",
                "expires_in": 3600,
            })
        if path == "/api/v1/prices":
            assert request.headers["Authorization"] == "Bearer tok-1"
            assert "005930" in request.url.params["symbols"]
            return httpx.Response(200, json={"result": [{
                "symbol": "005930",
                "timestamp": "2026-09-30T15:30:00+09:00",
                "lastPrice": "72500",
                "currency": "KRW",
            }]})
        if path == "/api/v1/candles":
            assert request.url.params["interval"] == "1d"
            items = candles if candles is not None else [
                {"timestamp": "2026-09-29T00:00:00+09:00", "openPrice": "1", "highPrice": "2",
                 "lowPrice": "0.5", "closePrice": "1.2", "volume": "10"},
                {"timestamp": "2026-09-30T00:00:00+09:00", "openPrice": "2", "highPrice": "3",
                 "lowPrice": "1.5", "closePrice": "2.2", "volume": "20"},
            ]
            return httpx.Response(200, json={"result": list(reversed(items))})
        return httpx.Response(404, json={})

    return handler


def _run(coro):
    return asyncio.run(coro)


def test_token_cached_across_calls(monkeypatch):
    import httpx

    import tossinvest

    tossinvest._token_cache.update({"token": None, "expires_at": 0.0})
    state = _state()

    async def run():
        transport = httpx.MockTransport(_handler_factory(state))
        async with httpx.AsyncClient(transport=transport) as client:
            first = await tossinvest.fetch_stock_quote(
                "005930", client_id="id", client_secret="secret", client=client)
            second = await tossinvest.fetch_stock_quote(
                "005930", client_id="id", client_secret="secret", client=client)
        return first, second

    first, second = _run(run())
    assert first["current"] == 72500.0
    assert second["current"] == 72500.0
    assert state["token_calls"] == 1


def test_candles_sorted_oldest_first_and_capped(monkeypatch):
    import httpx

    import tossinvest

    tossinvest._token_cache.update({"token": None, "expires_at": 0.0})
    state = _state()

    async def run():
        transport = httpx.MockTransport(_handler_factory(state))
        async with httpx.AsyncClient(transport=transport) as client:
            return await tossinvest.fetch_candles(
                "AAPL", client_id="id", client_secret="secret", client=client)

    result = _run(run())
    closes = [point["close"] for point in result["points"]]
    assert closes == [1.2, 2.2]
    assert result["points"][0]["time"] < result["points"][1]["time"]


def test_missing_credentials_and_bad_symbol():
    import asyncio

    import httpx

    import tossinvest

    async def run():
        transport = httpx.MockTransport(_handler_factory(_state()))
        async with httpx.AsyncClient(transport=transport) as client:
            no_creds = await tossinvest.fetch_stock_quote(
                "005930", client_id=" ", client_secret=" ", client=client)
            bad_symbol = await tossinvest.fetch_candles(
                "???", client_id="id", client_secret="secret", client=client)
            bad_interval = await tossinvest.fetch_candles(
                "005930", interval="1h", client_id="id", client_secret="secret", client=client)
        return no_creds, bad_symbol, bad_interval

    no_creds, bad_symbol, bad_interval = asyncio.run(run())
    assert no_creds["error"] == "not_configured"
    assert bad_symbol["error"] == "invalid_symbol"
    assert bad_interval["error"] == "invalid_resolution"


def test_401_refreshes_token_once(monkeypatch):
    import httpx

    import tossinvest

    tossinvest._token_cache.update({"token": None, "expires_at": 0.0})
    calls = {"token": 0, "prices": 0}

    def handler(request):
        if request.url.path == "/oauth2/token":
            calls["token"] += 1
            return httpx.Response(200, json={
                "access_token": "tok-%d" % calls["token"],
                "token_type": "Bearer", "expires_in": 3600})
        if request.url.path == "/api/v1/prices":
            calls["prices"] += 1
            if calls["prices"] == 1:
                return httpx.Response(401, json={})
            return httpx.Response(200, json={"result": [{
                "symbol": "AAPL", "lastPrice": "10",
                "timestamp": "2026-09-30T00:00:00+00:00", "currency": "USD"}]})
        return httpx.Response(404, json={})

    async def run():
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            return await tossinvest.fetch_stock_quote(
                "AAPL", client_id="id", client_secret="secret", client=client)

    result = asyncio.run(run())
    assert result["current"] == 10.0
    assert calls == {"token": 2, "prices": 2}
