"""Offline contract tests for the optional, free-only Google organic adapter."""
import asyncio

import httpx
import pytest


def test_free_google_search_uses_exact_keyword_and_preserves_organic_positions():
    from google_serp import search_google_free

    paths = []

    def handler(request):
        paths.append(request.url.path)
        assert request.url.params["api_key"] == "test-serp-key"
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free", "plan_monthly_price": 0,
                "plan_searches_left": 3, "extra_credits": 0,
            })
        assert request.url.path == "/search.json"
        assert request.url.params["engine"] == "google"
        assert request.url.params["q"] == "AGI 2030년"
        assert request.url.params["gl"] == "kr"
        assert request.url.params["hl"] == "ko"
        return httpx.Response(200, json={
            "search_metadata": {"status": "Success"},
            "organic_results": [
                {"position": 1, "title": "국내 기사", "link": "https://www.aitimes.com/news/1"},
                {"position": 3, "title": "해외 분석", "link": "https://example.org/report"},
            ],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free(
                {"consent": True, "claims": [{"id": "c1", "kind": "prediction", "quote": "AGI는 2030년 안에 오나?"}],
                 "searchQueries": {"c1": "AGI 2030년"}},
                api_key="test-serp-key", client=client,
            )

    result = asyncio.run(run())
    assert paths == ["/account.json", "/search.json"]
    assert [source["url"] for source in result["sources"]] == [
        "https://www.aitimes.com/news/1", "https://example.org/report",
    ]
    assert [source["candidateOrder"] for source in result["sources"]] == [1, 3]
    assert all(source["searchProvider"] == "serpapi_google" for source in result["sources"])
    assert all(source["searchQuery"] == "AGI 2030년" for source in result["sources"])


def test_actual_free_plan_label_allows_a_zero_price_search():
    from google_serp import search_google_free

    paths = []

    def handler(request):
        paths.append(request.url.path)
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free Plan", "plan_monthly_price": 0.0,
                "plan_searches_left": 250, "extra_credits": 0,
            })
        return httpx.Response(200, json={
            "search_metadata": {"status": "Success"}, "organic_results": [],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free(
                {"consent": True, "claims": [{"id": "c1", "kind": "fact", "quote": "AGI 2030년"}]},
                api_key="test-serp-key", client=client,
            )

    assert asyncio.run(run()) == {"sources": []}
    assert paths == ["/account.json", "/search.json"]


@pytest.mark.parametrize(("account", "reason"), [
    ({"plan_name": "Starter", "plan_monthly_price": 25, "plan_searches_left": 1000, "extra_credits": 0}, "not_free_plan"),
    ({"plan_name": "Free", "plan_monthly_price": 0, "plan_searches_left": 0, "extra_credits": 0}, "free_quota_exhausted"),
    ({"plan_name": "Free", "plan_monthly_price": 0, "plan_searches_left": 1, "extra_credits": 1}, "extra_credits_present"),
    ({"plan_name": "Free", "plan_searches_left": 1, "extra_credits": 0}, "unverified_free_plan"),
])
def test_account_guard_never_starts_a_search_without_confirmed_free_quota(account, reason):
    from google_serp import FreeSearchUnavailable, search_google_free

    paths = []

    def handler(request):
        paths.append(request.url.path)
        return httpx.Response(200, json=account)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free(
                {"consent": True, "claims": [{"id": "c1", "kind": "fact", "quote": "AGI 2030년"}]},
                api_key="test-serp-key", client=client,
            )

    with pytest.raises(FreeSearchUnavailable, match=f"^{reason}$"):
        asyncio.run(run())
    assert paths == ["/account.json"]


def test_organic_results_follow_google_position_even_if_api_array_is_unsorted():
    from google_serp import search_google_free

    def handler(request):
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free", "plan_monthly_price": 0,
                "plan_searches_left": 2, "extra_credits": 0,
            })
        return httpx.Response(200, json={
            "search_metadata": {"status": "Success"},
            "organic_results": [
                {"position": 3, "title": "Third", "link": "https://third.example/a"},
                {"position": 1, "title": "First", "link": "https://first.example/a"},
            ],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free(
                {"consent": True, "claims": [{"id": "c1", "kind": "fact", "quote": "AGI 2030년"}]},
                api_key="test-serp-key", client=client,
            )

    result = asyncio.run(run())
    assert [source["candidateOrder"] for source in result["sources"]] == [1, 3]


def test_google_results_exclude_japanese_pages_and_request_korean_or_english():
    from google_serp import search_google_free

    def handler(request):
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free", "plan_monthly_price": 0,
                "plan_searches_left": 1, "extra_credits": 0,
            })
        assert request.url.params["lr"] == "lang_ko|lang_en"
        return httpx.Response(200, json={
            "search_metadata": {"status": "Success"},
            "organic_results": [
                {"position": 1, "title": "2030年のAGI", "snippet": "人工知能の予測", "link": "https://dx.mri.co.jp/agi"},
                {"position": 2, "title": "한국어 전망", "snippet": "2030년 AGI 예측", "link": "https://news.example.kr/agi"},
                {"position": 3, "title": "AGI ニュース", "snippet": "予測と人工知能", "link": "https://example.com/japanese"},
                {"position": 4, "title": "English AGI forecast", "snippet": "A 2030 outlook", "link": "https://example.com/english"},
            ],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free(
                {"consent": True, "claims": [{"id": "c1", "kind": "prediction", "quote": "AGI 2030년"}]},
                api_key="test-serp-key", client=client,
            )

    sources = asyncio.run(run())["sources"]
    assert [source["url"] for source in sources] == [
        "https://news.example.kr/agi", "https://example.com/english",
    ]
    assert [source["candidateOrder"] for source in sources] == [2, 4]


def test_each_distinct_claim_query_gets_its_own_ranked_search_when_free_quota_covers_all():
    from google_serp import search_google_free

    requested_queries = []

    def handler(request):
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free", "plan_monthly_price": 0,
                "plan_searches_left": 2, "extra_credits": 0,
            })
        query = request.url.params["q"]
        requested_queries.append(query)
        return httpx.Response(200, json={
            "search_metadata": {"status": "Success"},
            "organic_results": [{"position": 1, "title": query, "link": f"https://example.com/{len(requested_queries)}"}],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free({
                "consent": True,
                "claims": [
                    {"id": "c1", "kind": "fact", "quote": "첫 주장"},
                    {"id": "c2", "kind": "prediction", "quote": "둘째 주장"},
                ],
                "searchQueries": {"c1": "첫 검색어", "c2": "둘째 검색어"},
            }, api_key="test-serp-key", client=client)

    result = asyncio.run(run())
    assert requested_queries == ["첫 검색어", "둘째 검색어"]
    assert [source["searchQuery"] for source in result["sources"]] == requested_queries


def test_completed_google_search_without_organic_results_returns_no_sources():
    from google_serp import search_google_free

    def handler(request):
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free", "plan_monthly_price": 0,
                "plan_searches_left": 1, "extra_credits": 0,
            })
        return httpx.Response(200, json={"search_metadata": {"status": "Success"}})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free(
                {"consent": True, "claims": [{"id": "c1", "kind": "fact", "quote": "검색 결과 없는 주장"}]},
                api_key="test-serp-key", client=client,
            )

    assert asyncio.run(run()) == {"sources": []}


def test_multiple_claims_each_keep_top_organic_candidates_with_six_source_cap():
    from google_serp import search_google_free

    def handler(request):
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free", "plan_monthly_price": 0,
                "plan_searches_left": 2, "extra_credits": 0,
            })
        prefix = "first" if request.url.params["q"] == "첫 검색어" else "second"
        return httpx.Response(200, json={
            "search_metadata": {"status": "Success"},
            "organic_results": [
                {"position": i, "title": f"{prefix} {i}", "link": f"https://{prefix}{i}.example/article"}
                for i in range(1, 7)
            ],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free({
                "consent": True,
                "claims": [
                    {"id": "c1", "kind": "fact", "quote": "첫 주장"},
                    {"id": "c2", "kind": "fact", "quote": "둘째 주장"},
                ],
                "searchQueries": {"c1": "첫 검색어", "c2": "둘째 검색어"},
            }, api_key="test-serp-key", client=client)

    sources = asyncio.run(run())["sources"]
    assert len(sources) == 6
    assert {source["searchQuery"] for source in sources} == {"첫 검색어", "둘째 검색어"}
    assert sum(source["searchQuery"] == "첫 검색어" for source in sources) == 3


def test_malformed_search_metadata_is_safely_classified_as_unavailable():
    from google_serp import FreeSearchUnavailable, search_google_free

    def handler(request):
        if request.url.path == "/account.json":
            return httpx.Response(200, json={
                "plan_name": "Free", "plan_monthly_price": 0,
                "plan_searches_left": 1, "extra_credits": 0,
            })
        return httpx.Response(200, json={"search_metadata": "unexpected", "organic_results": []})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_google_free(
                {"consent": True, "claims": [{"id": "c1", "kind": "fact", "quote": "Claim"}]},
                api_key="test-serp-key", client=client,
            )

    with pytest.raises(FreeSearchUnavailable, match="search_incomplete"):
        asyncio.run(run())
