"""Offline failure, safety and empty-result tests."""
import asyncio
import httpx
import pytest
from search import search_sources


@pytest.mark.parametrize("case", ["no_consent", "missing_key", "http_error", "incomplete", "no_call", "failed_call"])
def test_search_fails_closed(case):
    def handler(request):
        assert case not in {"no_consent", "missing_key"}, "Request must not be sent"
        if case == "http_error":
            return httpx.Response(429, text="private diagnostics")
        return httpx.Response(200, json={"status": "incomplete" if case == "incomplete" else "completed", "output": [] if case == "no_call" else [
            {"type": "web_search_call", "status": "failed" if case == "failed_call" else "completed", "action": {"sources": []}}]})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources({"claims": [{"id":"c1", "quote":"claim", "kind":"fact"}], "consent": case != "no_consent"}, api_key="" if case == "missing_key" else "test-only", client=client)
    with pytest.raises(ValueError, match="^(INVALID_REQUEST|NOT_CONFIGURED|SEARCH_FAILED)$"):
        asyncio.run(run())


def test_nonfacts_skip_network():
    def handler(request):
        raise AssertionError("Opinions must not trigger paid search")
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources({"claims": [{"kind":"opinion", "quote":"opinion"}], "consent":True}, api_key="", client=client)
    assert asyncio.run(run()) == {"sources": []}


def test_candidates_filter_unsafe_urls_and_limit_results():
    urls = ["file:///etc/passwd", "http://localhost/a", "http://127.0.0.1/", "http://user:password@example.org", "https://example.org:8080/", "https://example.org/\nfoo"] + [f"https://example.org/{i}" for i in range(10)]
    def handler(request):
        return httpx.Response(200, json={"status":"completed", "output":[{"type":"web_search_call", "status":"completed", "action":{"sources":[{"url":u} for u in urls]}}]})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources({"claims":[{"id":"c1", "kind":"fact", "quote":"claim"}], "consent":True}, api_key="test-only", client=client)
    sources = asyncio.run(run())["sources"]
    assert [s["url"] for s in sources] == [f"https://example.org/{i}" for i in range(6)]


def test_completed_empty_search_is_not_a_verdict():
    def handler(request):
        return httpx.Response(200, json={"status":"completed", "output":[{"type":"web_search_call", "status":"completed", "action":{"sources":[]}}]})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await search_sources({"claims":[{"id":"c1", "kind":"fact", "quote":"claim"}], "consent":True}, api_key="test-only", client=client)
    assert asyncio.run(run()) == {"sources": []}
