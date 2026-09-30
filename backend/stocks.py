"""Stock-question detection and market-context assembly.

KRX is on hold: this module resolves symbols for any market data source and
records which source supplied each context, so a KRX adapter can plug in
later without changing the contract. Detection is deterministic (curated
names plus validated ticker patterns) and never spends an LLM call.
"""
import re

_TICKER = re.compile(r"(?<![A-Z])[A-Z]{2,5}(?![A-Z])")

# Curated well-known names. Finnhub coverage is verified live per symbol;
# unknown names resolve to no symbol (safe fallback: no chart, no penalty).
COMPANY_SYMBOLS = {
    # US majors (Finnhub native)
    "테슬라": "TSLA",
    "엔비디아": "NVDA",
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "마이크로소프트사": "MSFT",
    "알파벳": "GOOGL",
    "구글": "GOOGL",
    "아마존": "AMZN",
    "메타": "META",
    "넷플릭스": "NFLX",
    # KR majors (Finnhub international coverage; verified per symbol)
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "하이닉스": "000660",
    "현대차": "005380",
    "현대자동차": "005380",
    "기아": "000270",
    "기아차": "000270",
    "셀트리온": "068270",
    "삼성바이오로직스": "207940",
    "카카오": "035720",
    "네이버": "035420",
    "NAVER": "035420",
    "포스코홀딩스": "005490",
    "POSCO": "005490",
    "LG에너지솔루션": "373220",
    "LG화학": "051910",
    "삼성SDI": "006400",
}

_FINANCE_HINTS = (
    "주가", "주식", "시세", "상장", "증시", "코스피", "코스닥", "나스닥",
    "실적", "영업이익", "매출", "배당", "공매도", "거래량", "급등", "급락",
    "상한가", "하한가", "신고가", "신저가", "시가총액", "PER", "PBR",
    "stock", "share", "ticker", "nasdaq", "nyse",
)

_MAX_SYMBOLS = 1


def display_name_for(symbol: str) -> str | None:
    """Reverse the curated map so the chart header can show a Korean name."""
    for name, mapped in COMPANY_SYMBOLS.items():
        if mapped == symbol:
            return name
    return None


def _strip_particles(token: str) -> str:
    """Remove Korean particles attached to a Latin ticker (TSLA는 -> TSLA)."""
    return re.sub(r"(은|는|이|가|을|를|의|에|에서|으로|로|와|과|도|만)$", "", token)


def detect_stock_symbols(text: str, focus: str = "") -> list[str]:
    """Return up to one validated-looking ticker symbol for market context.

    Accepts curated company names and bare Latin tickers. Anything else
    resolves to [] so a missed detection only hides the chart.
    """
    haystack = f"{text or ''}\n{focus or ''}"
    found: list[str] = []
    for name, symbol in COMPANY_SYMBOLS.items():
        if name in haystack and symbol not in found:
            found.append(symbol)
        if len(found) >= _MAX_SYMBOLS:
            return found
    for raw in _TICKER.findall(haystack.upper()):
        token = _strip_particles(raw)
        if (
            2 <= len(token) <= 5
            and token not in found
            and not any(word in token for word in ("ETF", "USD", "KRW", "CEO", "AI", "TV", "PC", "IT"))
        ):
            found.append(token)
        if len(found) >= _MAX_SYMBOLS:
            break
    return found


def is_finance_question(text: str, focus: str = "") -> bool:
    """Cheap hint check used only to decide press preference, not verdicts."""
    haystack = f"{text or ''}\n{focus or ''}".lower()
    return (
        bool(detect_stock_symbols(text, focus))
        or any(hint.lower() in haystack for hint in _FINANCE_HINTS)
    )


def build_market_context(
    symbol: str,
    display_name: str | None,
    quote: dict,
    candles: dict,
    *,
    data_as_of: str | None,
) -> dict | None:
    """Combine a quote and candles into a contract-shaped market context.

    Returns None when either leg failed, so a data outage only hides
    the chart instead of failing verification.
    """
    if not isinstance(quote, dict) or not isinstance(candles, dict):
        return None
    if quote.get("error") or candles.get("error"):
        return None
    points = candles.get("points")
    if not isinstance(points, list) or not points:
        return None
    current = quote.get("current")
    if not isinstance(current, (int, float)):
        current = points[-1].get("close")
    previous_close = quote.get("previousClose")
    change_percent = None
    if isinstance(current, (int, float)) and isinstance(previous_close, (int, float)) and previous_close:
        change_percent = round((current - previous_close) / previous_close * 100, 2)
    return {
        "source": "finnhub",
        "symbol": symbol,
        "displayName": display_name,
        "current": current,
        "previousClose": previous_close,
        "changePercent": change_percent,
        "dataAsOf": data_as_of,
        "candles": points,
    }
