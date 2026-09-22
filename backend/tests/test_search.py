"""Offline search fixtures, not verified sources."""
import asyncio
import importlib.util
import json
import httpx
import pytest


@pytest.mark.parametrize(("urls", "expected"), [
    (["https://a.example/1", "https://b.example/2", "https://youtube.com/watch?v=3"],
     ["https://a.example/1", "https://b.example/2", "https://youtube.com/watch?v=3"]),
    (["https://dailymotion.com/1", "https://dailymotion.com/2", "https://dailymotion.com/3"],
     ["https://dailymotion.com/1", "https://dailymotion.com/2"]),
    (["https://a.example/story?id=1&utm_source=x", "https://a.example/story?id=1&utm_source=y", "https://a.example/story?id=2"],
     ["https://a.example/story?id=1&utm_source=x", "https://a.example/story?id=2"]),
])
def test_search_preserves_candidate_order_and_strict_duplicate_limits(urls, expected):
    from search import search_sources

    def handler(request):
        return httpx.Response(200, json={"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed", "action": {
                "sources": [{"url": url, "title": f"Result {i}"} for i, url in enumerate(urls)],
            }},
        ]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources({"claims": [{"id": "c1", "quote": "AGI", "kind": "fact"}],
                                         "consent": True}, api_key="test-only", client=client)

    result = asyncio.run(run())
    assert [s["url"] for s in result["sources"]] == expected
    assert [s["id"] for s in result["sources"]] == [f"s{i+1}" for i in range(len(expected))]


def test_search_collects_deduplicated_candidates_without_evidence():
    assert importlib.util.find_spec("search") is not None, "Search adapter missing"
    from search import search_sources

    def handler(request):
        body = json.loads(request.content)
        assert body["tools"][0]["type"] == "web_search"
        assert body["include"] == ["web_search_call.action.sources"]
        assert body["max_tool_calls"] == 4
        assert len(body["input"]) > 0
        assert body["store"] is False
        return httpx.Response(200, json={"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed", "action": {"sources": [
                {"url": "https://EXAMPLE.org/article#one"}, {"url": "https://example.org/article#two"}]}},
            {"type": "message", "content": [{"type": "output_text", "text": "Not evidence", "annotations": [
                {"type": "url_citation", "url": "https://example.org/article", "title": "Source title"}]}]}
        ]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources({"claims": [{"id": "c1", "quote": "Claim", "kind": "fact"}], "focus": "", "consent": True}, api_key="test-only", client=client)

    result = asyncio.run(run())
    assert result == {"sources": [{
        "id": "s1",
        "url": "https://example.org/article",
        "title": "Source title",
        "publisher": "example.org",
        "sourceType": "웹 출처",
        "originGroupId": "example.org",
        "accessStatus": "pending",
    }]}


def test_search_keeps_completed_sources_when_response_has_nonterminal_search_item():
    from search import search_sources

    def handler(request):
        return httpx.Response(200, json={"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed", "action": {"sources": [
                {"url": "https://example.org/primary", "title": "Primary source"}]}},
            {"type": "web_search_call", "status": "searching"},
            {"type": "message", "content": []},
        ]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources(
                {"claims": [{"id": "c1", "quote": "Claim", "kind": "fact"}], "focus": "", "consent": True},
                api_key="test-only",
                client=client,
            )

    assert asyncio.run(run()) == {
        "sources": [{
            "id": "s1",
            "url": "https://example.org/primary",
            "title": "Primary source",
            "publisher": "example.org",
            "sourceType": "웹 출처",
            "originGroupId": "example.org",
            "accessStatus": "pending",
        }]
    }


def test_search_selects_diverse_source_types_instead_of_one_publisher():
    from search import search_sources

    def handler(request):
        body = json.loads(request.content)
        plan = json.loads(body["input"])["searchPlan"]
        assert {item["sourceType"] for item in plan} >= {
            "한국 기사",
            "한국 블로그",
            "커뮤니티",
            "유튜브",
        }
        return httpx.Response(200, json={"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed", "action": {"sources": [
                {"url": "https://blog.google/one", "title": "Google one"},
                {"url": "https://blog.google/two", "title": "Google two"},
                {"url": "https://deepmind.google/three", "title": "Google three"},
                {"url": "https://www.hankyung.com/ai/article", "title": "한국 경제 기사"},
                {"url": "https://blog.naver.com/example/post", "title": "한국 블로그 글"},
                {"url": "https://www.reddit.com/r/artificial/comments/example", "title": "Reddit discussion"},
                {"url": "https://www.youtube.com/watch?v=example", "title": "YouTube interview"},
                {"url": "https://www.nytimes.com/2026/01/01/ai.html", "title": "International report"},
            ]}},
            {"type": "message", "content": []},
        ]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources(
                {"claims": [{"id": "c1", "quote": "아스트라가 AGI인가", "kind": "unclear"}], "focus": "", "consent": True},
                api_key="test-only",
                client=client,
            )

    sources = asyncio.run(run())["sources"]
    assert len(sources) == 6
    assert {source["sourceType"] for source in sources} >= {
        "공식·기술 문서",
        "한국 기사",
        "한국 블로그",
        "Reddit",
        "유튜브",
    }
    assert sum(source["originGroupId"] == "google" for source in sources) <= 2


def test_search_supports_gemini_google_search_citations():
    from providers import LLMProvider
    from search import search_sources

    def handler(request):
        assert str(request.url) == "https://generativelanguage.googleapis.com/v1beta/interactions"
        assert request.headers["x-goog-api-key"] == "gemini-test-only"
        body = json.loads(request.content)
        assert body["model"] == "gemini-3.8-flash"
        assert body["tools"] == [{"type": "google_search"}]
        assert body["generation_config"]["thinking_level"] == "high"
        return httpx.Response(200, json={
            "status": "completed",
            "steps": [
                {"type": "google_search_call", "arguments": {"queries": ["claim"]}},
                {"type": "model_output", "content": [{
                    "type": "text",
                    "text": "A grounded answer.",
                    "annotations": [{
                        "type": "url_citation",
                        "url": "https://example.org/gemini-source",
                        "title": "Gemini source",
                    }],
                }]},
            ],
        })

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources(
                {"claims": [{"id": "c1", "quote": "Claim", "kind": "fact"}], "focus": "", "consent": True},
                client=client,
                provider=LLMProvider("gemini", "gemini-3.8-flash", "high", "gemini-test-only"),
            )

    assert asyncio.run(run())["sources"] == [{
        "id": "s1",
        "url": "https://example.org/gemini-source",
        "title": "Gemini source",
        "publisher": "example.org",
        "sourceType": "웹 출처",
        "originGroupId": "example.org",
        "accessStatus": "pending",
    }]


def test_build_search_query_keeps_entity_and_year_from_forecast_question():
    from search import build_search_query

    assert build_search_query("AGI는 2030년 안에 오나?") == "AGI 2030년"


@pytest.mark.parametrize(("question", "expected"), [
    ("  AGI는   2030년 안에 오나요?  ", "AGI 2030년"),
    ("AGI는 2030년까지 오지 않는다", "AGI 2030년까지 오지 않는다"),
    ("Is AGI unlikely before 2030?", "Is AGI unlikely before 2030"),
    ("가수 아이유 은퇴설", "가수 아이유 은퇴설"),
    ("GPT-5.6 가격 20달러", "GPT-5.6 가격 20달러"),
])
def test_query_fallback_preserves_negation_names_and_numbers(question, expected):
    from search import build_search_query

    assert build_search_query(question) == expected


def test_prediction_claims_are_searched_with_primary_query_in_provider_order():
    from search import search_sources

    requested = False

    def handler(request):
        nonlocal requested
        requested = True
        body = json.loads(request.content)
        search_input = json.loads(body["input"])
        assert search_input["primaryQueries"] == ["AGI 2030년"]
        assert search_input["claims"][0]["searchQuery"] == "AGI 2030년"
        return httpx.Response(200, json={"status": "completed", "output": [
            {"type": "web_search_call", "status": "completed", "action": {"sources": [
                {"url": "https://first.example/report", "title": "First result"},
                {"url": "https://second.example/report", "title": "Second result"},
            ]}},
        ]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources(
                {
                    "claims": [{"id": "c1", "quote": "AGI는 2030년 안에 오나?", "kind": "prediction"}],
                    "focus": "",
                    "consent": True,
                },
                api_key="test-only",
                client=client,
            )

    result = asyncio.run(run())
    assert requested is True
    assert [source["url"] for source in result["sources"]] == [
        "https://first.example/report",
        "https://second.example/report",
    ]
