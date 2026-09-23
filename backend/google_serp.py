"""Optional SerpApi Google organic discovery, restricted to a free account."""
import json
from itertools import zip_longest

import httpx

from search import _project_candidates, build_search_query


_BASE = "https://serpapi.com"
_MAX_RESPONSE_BYTES = 512_000


class FreeSearchUnavailable(Exception):
    """Safe failure code for the optional, free-only search path."""


async def _json_response(client: httpx.AsyncClient, path: str, params: dict) -> dict:
    try:
        async with client.stream(
            "GET", f"{_BASE}{path}", params=params, timeout=20.0,
            follow_redirects=False,
        ) as response:
            if response.status_code != 200:
                raise FreeSearchUnavailable("upstream_unavailable")
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > _MAX_RESPONSE_BYTES:
                    raise FreeSearchUnavailable("response_too_large")
        data = json.loads(body)
        if not isinstance(data, dict) or "error" in data:
            raise FreeSearchUnavailable("invalid_response")
        return data
    except FreeSearchUnavailable:
        raise
    except (httpx.HTTPError, TimeoutError, ValueError, TypeError):
        raise FreeSearchUnavailable("upstream_unavailable") from None


async def search_google_free(state: dict, *, api_key: str, client: httpx.AsyncClient) -> dict:
    """Use only an account confirmed to be on the free plan with quota left."""
    if state.get("consent") is not True:
        raise ValueError("INVALID_REQUEST")
    claims = [
        claim for claim in state.get("claims", [])
        if claim.get("kind") in {"fact", "unclear", "prediction"}
    ]
    if not claims:
        return {"sources": []}
    if len(claims) > 3:
        raise ValueError("INVALID_REQUEST")
    if not api_key.strip():
        raise FreeSearchUnavailable("not_configured")

    queries = []
    search_queries = state.get("searchQueries") or {}
    for claim in claims:
        extracted = search_queries.get(claim.get("id"))
        query = (
            " ".join(extracted.split())[:300]
            if isinstance(extracted, str) and extracted.strip()
            else build_search_query(claim["quote"])
        )
        if query not in queries:
            queries.append(query)
    account = await _json_response(client, "/account.json", {"api_key": api_key})
    if str(account.get("plan_name", "")).strip().lower() not in {"free", "free plan"}:
        raise FreeSearchUnavailable("not_free_plan")
    price = account.get("plan_monthly_price")
    if type(price) not in {int, float}:
        raise FreeSearchUnavailable("unverified_free_plan")
    if price != 0:
        raise FreeSearchUnavailable("not_free_plan")
    if account.get("extra_credits") != 0:
        raise FreeSearchUnavailable("extra_credits_present")
    left = account.get("plan_searches_left")
    if type(left) is not int:
        raise FreeSearchUnavailable("unverified_free_plan")
    if left < len(queries):
        raise FreeSearchUnavailable("free_quota_exhausted")

    candidate_groups = []
    for query in queries:
        data = await _json_response(client, "/search.json", {
            "api_key": api_key, "engine": "google", "q": query,
            "gl": "kr", "hl": "ko", "google_domain": "google.com",
        })
        metadata = data.get("search_metadata")
        if not isinstance(metadata, dict) or metadata.get("status") != "Success":
            raise FreeSearchUnavailable("search_incomplete")
        results = data.get("organic_results", [])
        if not isinstance(results, list):
            raise FreeSearchUnavailable("missing_organic_results")
        ranked_results = sorted(
            (
                result for result in results
                if isinstance(result, dict)
                and type(result.get("position")) is int
                and 1 <= result["position"] <= 1000
            ),
            key=lambda result: result["position"],
        )
        candidate_groups.append([
            {
                "url": result.get("link"), "title": result.get("title"),
                "searchProvider": "serpapi_google", "searchQuery": query,
                "googlePosition": result["position"],
            }
            for result in ranked_results
        ])
    candidates = [candidate for row in zip_longest(*candidate_groups) for candidate in row if candidate]
    selected = _project_candidates(candidates)
    return {"sources": [{"id": f"s{i+1}", **source} for i, source in enumerate(selected)]}
