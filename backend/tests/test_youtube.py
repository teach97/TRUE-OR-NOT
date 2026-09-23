"""Offline YouTube Data API contract tests; no Google credentials or traffic."""
import asyncio

import httpx

from youtube import MAX_COMMENT_COUNT, fetch_youtube_data, youtube_video_id


def test_youtube_video_id_accepts_video_urls_and_rejects_lookalikes():
    video_id = "aB_12345678"
    assert youtube_video_id(f"https://www.youtube.com/watch?v={video_id}&feature=share") == video_id
    assert youtube_video_id(f"https://youtu.be/{video_id}?si=tracking") == video_id
    assert youtube_video_id(f"https://youtube.com/shorts/{video_id}") == video_id
    assert youtube_video_id(f"https://youtu.be/{video_id}/extra") is None
    assert youtube_video_id(f"https://youtube.com.evil.test/watch?v={video_id}") is None
    assert youtube_video_id("https://www.youtube.com/channel/not-a-video") is None


def test_fetches_official_video_title_and_bounded_plain_text_comments():
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.path.endswith("/videos"):
            return httpx.Response(200, json={"items": [{"snippet": {"title": "AGI 전망 인터뷰"}}]})
        return httpx.Response(200, json={"items": [
            {"snippet": {"topLevelComment": {"snippet": {"textDisplay": f"댓글 {index}"}}}}
            for index in range(20)
        ]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await fetch_youtube_data(
                "https://www.youtube.com/watch?v=aB_12345678",
                api_key="youtube-test-key",
                client=client,
            )

    result = asyncio.run(run())
    assert result == {
        "title": "AGI 전망 인터뷰",
        "comments": [f"댓글 {index}" for index in range(MAX_COMMENT_COUNT)],
        "status": "collected",
    }
    assert len(requests) == 2
    video_request, comments_request = requests
    assert video_request.url.host == "www.googleapis.com"
    assert video_request.url.path.endswith("/youtube/v3/videos")
    assert video_request.url.params["part"] == "snippet"
    assert video_request.url.params["id"] == "aB_12345678"
    assert video_request.url.params["key"] == "youtube-test-key"
    assert comments_request.url.path.endswith("/youtube/v3/commentThreads")
    assert comments_request.url.params["videoId"] == "aB_12345678"
    assert comments_request.url.params["maxResults"] == str(MAX_COMMENT_COUNT)
    assert comments_request.url.params["textFormat"] == "plainText"
    assert "author" not in str(result).lower()


def test_comments_unavailable_keeps_video_title_without_exposing_provider_error():
    def handler(request):
        if request.url.path.endswith("/videos"):
            return httpx.Response(200, json={"items": [{"snippet": {"title": "제목"}}]})
        return httpx.Response(403, json={"error": {"message": "private diagnostic"}})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await fetch_youtube_data(
                "https://youtu.be/aB_12345678",
                api_key="youtube-test-key",
                client=client,
            )

    assert asyncio.run(run()) == {"title": "제목", "comments": [], "status": "unavailable"}


def test_missing_key_or_invalid_video_url_makes_no_api_request():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(500)

    async def run(url, key):
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await fetch_youtube_data(url, api_key=key, client=client)

    assert asyncio.run(run("https://youtube.com/watch?v=aB_12345678", "")) == {
        "title": None, "comments": [], "status": "not_configured"
    }
    assert asyncio.run(run("https://youtube.com/channel/abc", "test-key")) == {
        "title": None, "comments": [], "status": "unavailable"
    }
    assert requests == []


def test_oversized_api_payload_is_treated_as_unavailable():
    def handler(request):
        if request.url.path.endswith("/videos"):
            return httpx.Response(200, json={"items": [{"snippet": {"title": "제목"}}]})
        return httpx.Response(200, content=b"{" + b" " * 300_000 + b"}", headers={"content-type": "application/json"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await fetch_youtube_data(
                "https://youtube.com/watch?v=aB_12345678",
                api_key="youtube-test-key",
                client=client,
            )

    assert asyncio.run(run()) == {"title": "제목", "comments": [], "status": "unavailable"}
