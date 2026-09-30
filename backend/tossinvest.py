"""Toss Securities Open API adapter (market data only, read-only).

Covers KR (6-digit codes, e.g. 005930) and US (tickers, e.g. AAPL) symbols.
Auth is OAuth2 client credentials; exactly one access token stays valid per
client, so tokens are cached in-process and refreshed only near expiry.
See https://developers.tossinvest.com/docs (llms.txt).
"""
import time

import httpx


API_ROOT = "https://openapi.tossinvest.com"
MAX_RESPONSE_BYTES = 256_000
MAX_CANDLES = 90
_EXPIRY_SKEW_SECONDS = 120

_token_cache: dict[str, object] = {"token": None, "expires_at": 0.0}


async def _access_token(
    client_id: str,
    client_secret: str,
    client: httpx.AsyncClient,
    *,
    force_refresh: bool = False,
) -> str | None:
    """Return a cached bearer token, issuing a fresh one when needed."""
    if (
        not force_refresh
        and isinstance(_token_cache.get("token"), str)
        and _token_cache["token"]
        and time.time() < float(_token_cache.get("expires_at", 0.0))
    ):
        return _token_cache["token"]  # type: ignore[return-value]
    try:
        response = await client.post(
            f"{API_ROOT}/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id.strip(),
                "client_secret": client_secret.strip(),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20.0,
        )
    except (httpx.HTTPError, TimeoutError):
        return None
    if response.status_code != 200:
        return None
    try:
        data = response.json()
    except ValueError:
        return None
    token = data.get("access_token") if isinstance(data, dict) else None
    expires_in = data.get("expires_in") if isinstance(data, dict) else 0
    if not isinstance(token, str) or not token:
        return None
    _token_cache["token"] = token
    _token_cache["expires_at"] = time.time() + max(0, int(expires_in or 0)) - _EXPIRY_SKEW_SECONDS
    return token


async def _authorized_get(
    path: str,
    params: dict,
    *,
    client_id: str,
    client_secret: str,
    client: httpx.AsyncClient,
) -> dict | None:
    """GET with bearer auth; retries once with a fresh token on 401."""
    token = await _access_token(client_id, client_secret, client)
    if token is None:
        return None
    for attempt in (False, True):
        try:
            response = await client.get(
                f"{API_ROOT}{path}",
                params=params,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                timeout=20.0,
            )
        except (httpx.HTTPError, TimeoutError):
            return None
        if response.status_code == 401 and not attempt:
            token = await _access_token(client_id, client_secret, client, force_refresh=True)
            if token is None:
                return None
            continue
        if response.status_code != 200:
            return None
        if len(response.content) > MAX_RESPONSE_BYTES:
            return None
        try:
            data = response.json()
        except ValueError:
            return None
        return data if isinstance(data, dict) else None
    return None


def _valid_symbol(symbol: str) -> str | None:
    if not isinstance(symbol, str):
        return None
    cleaned = symbol.strip().upper()
    if len(cleaned) > 16:
        return None
    if not all(char.isalnum() or char in ".-" for char in cleaned):
        return None
    return cleaned or None


def _to_unix_seconds(value: object) -> int | None:
    if isinstance(value, (int, float)) and value > 0:
        return int(value)
    if isinstance(value, str):
        try:
            from datetime import datetime

            text = value.strip()
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            parsed = datetime.fromisoformat(text)
            if parsed.tzinfo is None:
                from datetime import timezone

                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp())
        except ValueError:
            return None
    return None


def _number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


async def fetch_stock_quote(
    symbol: str,
    *,
    client_id: str,
    client_secret: str,
    client: httpx.AsyncClient,
) -> dict:
    """Fetch the latest price. Returns {"symbol", "current", ...} or error."""
    cleaned = _valid_symbol(symbol)
    if not client_id.strip() or not client_secret.strip():
        return {"symbol": symbol, "error": "not_configured"}
    if cleaned is None:
        return {"symbol": symbol, "error": "invalid_symbol"}
    data = await _authorized_get(
        "/api/v1/prices", {"symbols": cleaned},
        client_id=client_id, client_secret=client_secret, client=client,
    )
    if data is None:
        return {"symbol": cleaned, "error": "upstream_unavailable"}
    results = data.get("result")
    entry = results[0] if isinstance(results, list) and results else None
    if not isinstance(entry, dict):
        return {"symbol": cleaned, "error": "unknown_symbol"}
    current = _number(entry.get("lastPrice"))
    if current is None:
        return {"symbol": cleaned, "error": "unknown_symbol"}
    return {
        "symbol": cleaned,
        "current": current,
        "open": None,
        "high": None,
        "low": None,
        "previousClose": None,
        "timestamp": _to_unix_seconds(entry.get("timestamp")),
    }


async def fetch_candles(
    symbol: str,
    *,
    interval: str = "1d",
    count: int = 60,
    client_id: str = "",
    client_secret: str = "",
    client: httpx.AsyncClient,
) -> dict:
    """Fetch recent candles (at most MAX_CANDLES, oldest first).

    Returns {"symbol", "points": [{time, open, high, low, close, volume}]}
    or {"symbol", "error"}. Times are Unix seconds.
    """
    cleaned = _valid_symbol(symbol)
    if not client_id.strip() or not client_secret.strip():
        return {"symbol": symbol, "error": "not_configured"}
    if cleaned is None:
        return {"symbol": symbol, "error": "invalid_symbol"}
    if interval not in {"1m", "1d"}:
        return {"symbol": symbol, "error": "invalid_resolution"}
    count = max(1, min(int(count), MAX_CANDLES))
    data = await _authorized_get(
        "/api/v1/candles",
        {"symbol": cleaned, "interval": interval, "count": count},
        client_id=client_id, client_secret=client_secret, client=client,
    )
    if data is None:
        return {"symbol": cleaned, "error": "upstream_unavailable"}
    results = data.get("result")
    if not isinstance(results, list):
        return {"symbol": cleaned, "error": "unknown_symbol"}
    points = []
    for entry in results:
        if not isinstance(entry, dict):
            continue
        timestamp = _to_unix_seconds(entry.get("timestamp"))
        o = _number(entry.get("openPrice"))
        h = _number(entry.get("highPrice"))
        low = _number(entry.get("lowPrice"))
        c = _number(entry.get("closePrice"))
        if timestamp is None or None in (o, h, low, c):
            continue
        points.append({
            "time": timestamp,
            "open": o,
            "high": h,
            "low": low,
            "close": c,
            "volume": _number(entry.get("volume")) or 0.0,
        })
    points.sort(key=lambda point: point["time"])
    points = points[-count:]
    if not points:
        return {"symbol": cleaned, "error": "unknown_symbol"}
    return {"symbol": cleaned, "points": points}
