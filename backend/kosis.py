"""Small KOSIS adapter for discovering and reading official statistics."""
import asyncio
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from search import _source_identity, build_search_query, candidate_url, origin_group_for_url, source_type_for_url
from sources import SourceReadResult


_SEARCH_URL = "https://kosis.kr/openapi/statisticsSearch.do"
_DATA_URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
_META_URL = "https://kosis.kr/openapi/statisticsData.do"
_MAX_SOURCE_TEXT = 12_000
_MAX_ROWS = 36
_STOP_WORDS = {
    "그", "것", "대한", "에서", "으로", "이다", "있는", "있다", "한다", "합니다",
    "그리고", "또는", "관련", "자료", "통계", "얼마", "어떻게", "무엇",
}


class KosisUnavailable(Exception):
    """KOSIS did not return usable data for this request."""


async def _get_json(client: httpx.AsyncClient, url: str, params: dict) -> list[dict]:
    try:
        response = await client.get(url, params=params, timeout=12.0)
        if response.status_code != 200:
            raise KosisUnavailable("upstream_status")
        payload = response.json()
    except KosisUnavailable:
        raise
    except (httpx.HTTPError, TimeoutError, ValueError):
        raise KosisUnavailable("upstream_unavailable") from None

    if isinstance(payload, dict):
        raise KosisUnavailable("invalid_or_error_response")
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise KosisUnavailable("invalid_response")
    if any(item.get("err") or item.get("ERR") for item in payload):
        raise KosisUnavailable("upstream_error")
    return payload


def _field(row: dict, name: str) -> str:
    value = row.get(name)
    return value.strip()[:1000] if isinstance(value, str) else ""


def _official_table_url(*values: str) -> str | None:
    for raw in values:
        url = candidate_url(raw)
        if not url:
            continue
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        if host != "kosis.kr" and not host.endswith(".kosis.kr"):
            continue
        query = urlencode([
            (key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if key.lower() not in {"apikey", "api_key", "key"}
        ])
        return urlunsplit(("https", parts.netloc, parts.path, query, ""))
    return None


async def search_kosis_sources(
    state: dict, *, api_key: str, client: httpx.AsyncClient,
) -> list[dict]:
    """Return up to one official statistics table per checkable claim."""
    if state.get("consent") is not True or not api_key.strip():
        return []
    claims = [
        claim for claim in state.get("claims", [])
        if isinstance(claim, dict) and claim.get("kind") in {"fact", "unclear", "prediction"}
    ][:3]
    if not claims:
        return []

    search_queries = state.get("searchQueries") or {}
    queries = []
    for claim in claims:
        query = search_queries.get(claim.get("id"))
        if not isinstance(query, str) or not query.strip():
            query = build_search_query(str(claim.get("quote") or ""))
        query = " ".join(query.split())[:300]
        if query and query not in queries:
            queries.append(query)

    excluded = {
        _source_identity(url) for url in state.get("excludedSourceUrls", [])
        if isinstance(url, str)
    }

    async def lookup(query: str) -> list[dict]:
        try:
            rows = await _get_json(client, _SEARCH_URL, {
                "method": "getList",
                "apiKey": api_key,
                "searchNm": query,
                "sort": "RANK",
                "startCount": "1",
                "resultCount": "5",
                "format": "json",
            })
        except KosisUnavailable:
            return []

        for position, row in enumerate(rows, 1):
            org_id = _field(row, "ORG_ID")
            table_id = _field(row, "TBL_ID")
            table_title = _field(row, "TBL_NM")
            if not org_id or not table_id or not table_title:
                continue
            url = _official_table_url(_field(row, "LINK_URL"), _field(row, "TBL_VIEW_URL"))
            if not url or _source_identity(url) in excluded:
                continue
            return [{
                "url": url,
                "title": table_title[:300],
                "publisher": _field(row, "ORG_NM")[:300] or "국가통계포털 KOSIS",
                "sourceType": source_type_for_url(url),
                "originGroupId": origin_group_for_url(url),
                "accessStatus": "pending",
                "searchProvider": "kosis_api",
                "searchQuery": query,
                "candidateOrder": position,
                "kosisOrgId": org_id,
                "kosisTblId": table_id,
                "kosisTableTitle": table_title[:300],
                "kosisOrgName": _field(row, "ORG_NM")[:300],
                "kosisStatName": _field(row, "STAT_NM")[:300],
                "kosisStartPeriod": _field(row, "STRT_PRD_DE")[:20],
                "kosisEndPeriod": _field(row, "END_PRD_DE")[:20],
            }]
        return []

    groups = await asyncio.gather(*(lookup(query) for query in queries))
    sources = []
    seen = set()
    for group in groups:
        for source in group:
            identity = _source_identity(source["url"])
            if identity not in seen:
                sources.append(source)
                seen.add(identity)
    return sources


def _query_year(query: str) -> str | None:
    match = re.search(r"(?<!\d)((?:19|20)\d{2})(?:\s*년)?", query)
    return match.group(1) if match else None


def _frequency(rows: list[dict], query: str) -> str:
    available = {_field(row, "PRD_SE").upper() for row in rows}
    available.discard("")
    if not available:
        raise KosisUnavailable("period_metadata_missing")

    if re.search(r"\d{4}\s*년?\s*\d{1,2}\s*월|월별|매월|monthly", query, re.I):
        preferred = ["M", "D", "Q", "Y", "S", "F", "IR"]
    elif re.search(r"\d{4}\s*년?\s*[1-4]\s*분기|분기별|quarter", query, re.I):
        preferred = ["Q", "M", "Y", "S", "F", "IR"]
    elif re.search(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|일별|daily", query, re.I):
        preferred = ["D", "M", "Q", "Y", "S", "F", "IR"]
    elif _query_year(query):
        preferred = ["Y", "F", "M", "Q", "S", "D", "IR"]
    else:
        preferred = ["M", "Q", "Y", "D", "S", "F", "IR"]
    return next((period for period in preferred if period in available), sorted(available)[0])


def _period_params(query: str, frequency: str) -> dict[str, str]:
    year = _query_year(query)
    if not year:
        return {"newEstPrdCnt": "3"}

    if frequency == "M":
        month = re.search(r"(?:19|20)\d{2}\s*년?\s*(0?[1-9]|1[0-2])\s*월", query)
        start, end = (f"{year}{int(month.group(1)):02d}",) * 2 if month else (f"{year}01", f"{year}12")
    elif frequency == "Q":
        quarter = re.search(r"(?:19|20)\d{2}\s*년?\s*([1-4])\s*분기", query)
        start, end = (f"{year}0{quarter.group(1)}",) * 2 if quarter else (f"{year}01", f"{year}04")
    elif frequency == "D":
        date = re.search(r"((?:19|20)\d{2})[-/.](\d{1,2})[-/.](\d{1,2})", query)
        if not date:
            return {"newEstPrdCnt": "3"}
        day = f"{date.group(1)}{int(date.group(2)):02d}{int(date.group(3)):02d}"
        start, end = day, day
    elif frequency in {"Y", "F", "IR"}:
        start, end = year, year
    else:
        return {"newEstPrdCnt": "3"}
    return {"startPrdDe": start, "endPrdDe": end}


def _row_context(row: dict) -> str:
    fields = [
        _field(row, "TBL_NM"), _field(row, "STAT_NM"), _field(row, "ITM_NM"),
        _field(row, "UNIT_NM"),
    ]
    for level in range(1, 9):
        fields.extend((_field(row, f"C{level}_OBJ_NM"), _field(row, f"C{level}_NM")))
    return " ".join(value for value in fields if value)


def _query_tokens(query: str) -> list[str]:
    tokens = re.findall(r"[0-9A-Za-z]+|[가-힣]+", query.lower())
    result = []
    for token in tokens:
        if re.fullmatch(r"[가-힣]+", token):
            token = re.sub(r"(?:으로|에서|에게|까지|부터|처럼|보다|은|는|이|가|을|를|의|에|와|과|도)$", "", token)
        if len(token) >= 2 and token not in _STOP_WORDS and token not in result:
            result.append(token)
    return result


def _format_rows(source: dict, query: str, rows: list[dict]) -> str:
    title = source.get("kosisTableTitle") or "KOSIS 통계표"
    lines = [
        "출처: 국가통계포털 KOSIS 공식 통계자료",
        f"통계표: {title}",
    ]
    if source.get("kosisOrgName"):
        lines.append(f"작성기관: {source['kosisOrgName']}")
    if source.get("kosisStatName"):
        lines.append(f"통계명: {source['kosisStatName']}")
    if source.get("kosisStartPeriod") or source.get("kosisEndPeriod"):
        lines.append(f"수록기간: {source.get('kosisStartPeriod') or '?'} ~ {source.get('kosisEndPeriod') or '?'}")
    lines.append("아래 수치는 KOSIS API 응답 원문을 표기한 것입니다.")

    tokens = _query_tokens(query)
    ranked = sorted(
        rows,
        key=lambda row: (
            sum(token in _row_context(row).lower() for token in tokens),
            _field(row, "PRD_DE"),
        ),
        reverse=True,
    )
    for row in ranked[:_MAX_ROWS]:
        period = _field(row, "PRD_DE") or "시점 미제공"
        context = " / ".join(
            value for value in (
                _field(row, "ITM_NM"),
                *[
                    f"{_field(row, f'C{level}_OBJ_NM')}: {_field(row, f'C{level}_NM')}"
                    for level in range(1, 9)
                    if _field(row, f"C{level}_NM")
                ],
            ) if value
        )
        value = _field(row, "DT") or "값 미제공"
        unit = _field(row, "UNIT_NM")
        line = f"{period} | {context or title} | {value}{(' ' + unit) if unit else ''}"
        if sum(len(item) + 1 for item in lines) + len(line) > _MAX_SOURCE_TEXT:
            break
        lines.append(line)
    return "\n".join(lines)


async def read_kosis_source(
    source: dict, *, api_key: str, client: httpx.AsyncClient,
) -> SourceReadResult:
    """Fetch bounded recent or requested-period values for one discovered table."""
    org_id = source.get("kosisOrgId")
    table_id = source.get("kosisTblId")
    query = source.get("searchQuery") or ""
    if not api_key.strip() or not isinstance(org_id, str) or not isinstance(table_id, str):
        raise KosisUnavailable("missing_configuration")

    metadata = await _get_json(client, _META_URL, {
        "method": "getMeta",
        "type": "PRD",
        "apiKey": api_key,
        "orgId": org_id,
        "tblId": table_id,
        "format": "json",
    })
    frequency = _frequency(metadata, query)
    params = {
        "method": "getList",
        "apiKey": api_key,
        "orgId": org_id,
        "tblId": table_id,
        "objL1": "ALL",
        "itmId": "ALL",
        "prdSe": frequency,
        "format": "json",
        "jsonVD": "Y",
        **_period_params(query, frequency),
    }
    rows = await _get_json(client, _DATA_URL, params)
    if not rows or not any(_field(row, "DT") for row in rows):
        raise KosisUnavailable("no_values")
    text = _format_rows(source, query, rows)
    if len(text) <= len("출처: 국가통계포털 KOSIS 공식 통계자료\n통계표: KOSIS 통계표"):
        raise KosisUnavailable("empty_content")
    return SourceReadResult(
        text=text,
        url=source["url"],
        title=source.get("kosisTableTitle") or source.get("title") or "KOSIS 통계표",
    )
