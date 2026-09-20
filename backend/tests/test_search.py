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
