"""Offline search fixtures, not verified sources."""
import asyncio
import importlib.util
import json
import httpx


def test_search_collects_deduplicated_candidates_without_evidence():
    assert importlib.util.find_spec("search") is not None, "Search adapter missing"
    from search import search_sources

    def handler(request):
        body = json.loads(request.content)
        assert body["tools"][0]["type"] == "web_search"
        assert body["include"] == ["web_search_call.action.sources"]
        assert body["max_tool_calls"] == 1
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
    assert result == {"sources": [{"id": "s1", "url": "https://example.org/article", "title": "Source title", "publisher": "example.org", "accessStatus": "pending"}]}


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
            "accessStatus": "pending",
        }]
    }


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
        "accessStatus": "pending",
    }]
