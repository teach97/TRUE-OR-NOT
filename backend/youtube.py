"""Small, read-only adapter for documented public YouTube Data API fields."""
import json
import re
from urllib.parse import parse_qs, urlsplit

import httpx


API_ROOT = "https://www.googleapis.com/youtube/v3"
MAX_COMMENT_COUNT = 10
MAX_RESPONSE_BYTES = 256_000
_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def youtube_video_id(raw_url: str) -> str | None:
    """Extract an 11-character video ID from a recognized YouTube video URL."""
    if not isinstance(raw_url, str) or len(raw_url) > 2048:
        return None
    try:
        parsed = urlsplit(raw_url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if (
            parsed.scheme != "https"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
        ):
            return None
        if host == "youtu.be":
            parts = parsed.path.strip("/").split("/")
            candidate = parts[0] if len(parts) == 1 else ""
        elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            if parsed.path == "/watch":
                values = parse_qs(parsed.query, keep_blank_values=True).get("v", [])
                candidate = values[0] if len(values) == 1 else ""
            else:
                parts = parsed.path.strip("/").split("/")
                candidate = parts[1] if len(parts) == 2 and parts[0] in {
                    "embed", "live", "shorts", "v",
                } else ""
        else:
            return None
    except ValueError:
        return None
    return candidate if _VIDEO_ID.fullmatch(candidate) else None


async def _request_json(
    client: httpx.AsyncClient,
    endpoint: str,
    *,
    params: dict[str, str],
) -> dict:
    async with client.stream("GET", endpoint, params=params) as response:
        response.raise_for_status()
        media_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if media_type != "application/json":
            raise ValueError("INVALID_API_RESPONSE")
        content_length = response.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
            except ValueError:
                raise ValueError("INVALID_API_RESPONSE") from None
            if length < 0:
                raise ValueError("INVALID_API_RESPONSE")
            if length > MAX_RESPONSE_BYTES:
                raise ValueError("API_RESPONSE_TOO_LARGE")
        body = bytearray()
        async for chunk in response.aiter_bytes():
            if len(body) + len(chunk) > MAX_RESPONSE_BYTES:
                raise ValueError("API_RESPONSE_TOO_LARGE")
            body.extend(chunk)
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("INVALID_API_RESPONSE") from None
    if not isinstance(payload, dict):
        raise ValueError("INVALID_API_RESPONSE")
    return payload


def _unavailable(title: str | None = None) -> dict:
    return {"title": title, "comments": [], "status": "unavailable"}


async def fetch_youtube_data(
    raw_url: str,
    *,
    api_key: str,
    client: httpx.AsyncClient,
) -> dict:
    """Fetch the current title and at most ten top-level comments for one video."""
    if not isinstance(api_key, str) or not api_key.strip():
        return {"title": None, "comments": [], "status": "not_configured"}
    video_id = youtube_video_id(raw_url)
    if video_id is None:
        return _unavailable()

    try:
        video_payload = await _request_json(
            client,
            f"{API_ROOT}/videos",
            params={"part": "snippet", "id": video_id, "key": api_key},
        )
    except (httpx.HTTPError, TimeoutError, ValueError):
        return _unavailable()

    videos = video_payload.get("items")
    snippet = videos[0].get("snippet") if isinstance(videos, list) and videos and isinstance(videos[0], dict) else None
    title = snippet.get("title") if isinstance(snippet, dict) else None
    if not isinstance(title, str) or not title.strip():
        return _unavailable()

    try:
        comments_payload = await _request_json(
            client,
            f"{API_ROOT}/commentThreads",
            params={
                "part": "snippet",
                "videoId": video_id,
                "maxResults": str(MAX_COMMENT_COUNT),
                "order": "relevance",
                "textFormat": "plainText",
                "key": api_key,
            },
        )
    except (httpx.HTTPError, TimeoutError, ValueError):
        return _unavailable(title)

    threads = comments_payload.get("items")
    if not isinstance(threads, list):
        return _unavailable(title)
    comments = []
    for thread in threads[:MAX_COMMENT_COUNT]:
        thread_snippet = thread.get("snippet") if isinstance(thread, dict) else None
        top_level = thread_snippet.get("topLevelComment") if isinstance(thread_snippet, dict) else None
        comment_snippet = top_level.get("snippet") if isinstance(top_level, dict) else None
        comment_text = comment_snippet.get("textDisplay") if isinstance(comment_snippet, dict) else None
        if isinstance(comment_text, str) and comment_text.strip():
            comments.append(comment_text)
    return {"title": title, "comments": comments, "status": "collected"}
