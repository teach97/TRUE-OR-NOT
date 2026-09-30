"""Small, read-only adapter for Finnhub stock quotes."""
import re

import httpx


API_ROOT = "https://finnhub.io/api/v1"
MAX_RESPONSE_BYTES = 64_000
MAX_CANDLES = 90
_SYMBOL = re.compile(r"^[A-Za-z0-9.\-]{1,16}$")


async def fetch_stock_quote(
    symbol: str,
    *,
    api_key: str,
    client: httpx.AsyncClient,
) -> dict:
    """Fetch the current quote for a ticker symbol.

    Returns {"symbol", "current", "open", "high", "low", "previousClose",
    "timestamp"} with None for missing numeric fields, or
    {"symbol", "error"} when the lookup fails.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        return {"symbol": symbol, "error": "not_configured"}
    if not isinstance(symbol, str) or not _SYMBOL.fullmatch(symbol.strip().upper()):
        return {"symbol": symbol, "error": "invalid_symbol"}
    try:
        body = bytearray()
        async with client.stream(
            "GET", f"{API_ROOT}/quote",
            params={"symbol": symbol.strip().upper(), "token": api_key.strip()},
            timeout=20.0,
        ) as response:
            if response.status_code != 200:
                return {"symbol": symbol, "error": "upstream_unavailable"}
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > MAX_RESPONSE_BYTES:
                    return {"symbol": symbol, "error": "response_too_large"}
        import json

        data = json.loads(body)
    except (httpx.HTTPError, TimeoutError, ValueError):
        return {"symbol": symbol, "error": "upstream_unavailable"}
    if not isinstance(data, dict):
        return {"symbol": symbol, "error": "invalid_response"}

    def number(value):
        return value if isinstance(value, (int, float)) else None

    current = number(data.get("c"))
    if current in (None, 0):
        return {"symbol": symbol, "error": "unknown_symbol"}
    return {
        "symbol": symbol.strip().upper(),
        "current": current,
        "open": number(data.get("o")),
        "high": number(data.get("h")),
        "low": number(data.get("l")),
        "previousClose": number(data.get("pc")),
        "timestamp": data.get("t") if isinstance(data.get("t"), int) else None,
    }


async def fetch_candles(
    symbol: str,
    *,
    resolution: str = "D",
    count: int = 60,
    api_key: str,
    client: httpx.AsyncClient,
) -> dict:
    """Fetch recent daily candles for charting (at most MAX_CANDLES points).

    Returns {"symbol", "points": [{time, open, high, low, close, volume}]}
    or {"symbol", "error"}. Timestamps are Unix seconds.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        return {"symbol": symbol, "error": "not_configured"}
    if not isinstance(symbol, str) or not _SYMBOL.fullmatch(symbol.strip().upper()):
        return {"symbol": symbol, "error": "invalid_symbol"}
    if resolution not in {"D", "W", "M"}:
        return {"symbol": symbol, "error": "invalid_resolution"}
    count = max(1, min(int(count), MAX_CANDLES))
    import time as _time

    now = int(_time.time())
    span = {"D": 86_400, "W": 604_800, "M": 2_592_000}[resolution]
    try:
        body = bytearray()
        async with client.stream(
            "GET",
            f"{API_ROOT}/stock/candle",
            params={
                "symbol": symbol.strip().upper(),
                "resolution": resolution,
                "from": now - span * (count + 5),
                "to": now,
                "token": api_key.strip(),
            },
            timeout=20.0,
        ) as response:
            if response.status_code != 200:
                return {"symbol": symbol, "error": "upstream_unavailable"}
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > MAX_RESPONSE_BYTES:
                    return {"symbol": symbol, "error": "response_too_large"}
        import json

        data = json.loads(body)
    except (httpx.HTTPError, TimeoutError, ValueError):
        return {"symbol": symbol, "error": "upstream_unavailable"}
    if not isinstance(data, dict) or data.get("s") != "ok":
        return {"symbol": symbol, "error": "unknown_symbol"}
    try:
        points = [
            {
                "time": int(timestamp),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(v) if v is not None else 0.0,
            }
            for timestamp, o, h, l, c, v in zip(
                data.get("t", []),
                data.get("o", []),
                data.get("h", []),
                data.get("l", []),
                data.get("c", []),
                data.get("v", []),
            )
        ][-count:]
    except (TypeError, ValueError):
        return {"symbol": symbol, "error": "invalid_response"}
    if not points:
        return {"symbol": symbol, "error": "unknown_symbol"}
    return {"symbol": symbol.strip().upper(), "points": points}
