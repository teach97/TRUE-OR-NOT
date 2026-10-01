"""Content summarization path; no live traffic (all transports mocked)."""
import asyncio


def test_gather_prefers_youtube_transcript_over_page(monkeypatch):
    import sources
    import summarize
    import youtube

    async def fake_transcript(video_id):
        assert video_id == "aB_12345678"
        return {"text": "영상 내용입니다.", "status": "collected"}

    async def no_page(url):
        raise AssertionError("page fetch must not run for YouTube links")

    monkeypatch.setattr(youtube, "fetch_transcript_text", fake_transcript)
    monkeypatch.setattr(sources, "fetch_public_text", no_page)
    source = asyncio.run(summarize.gather_summary_source(
        text="https://www.youtube.com/watch?v=aB_12345678 요약해줘",
        link_url="https://www.youtube.com/watch?v=aB_12345678",
        image=None, consent=True, client=None,
    ))
    assert source["body"] == "영상 내용입니다."
    assert source["sourceName"] == "유튜브 자막"


def test_gather_blocks_long_videos_and_empty_input(monkeypatch):
    import summarize
    import youtube

    async def too_long(video_id):
        return {"text": None, "status": "too_long"}

    monkeypatch.setattr(youtube, "fetch_transcript_text", too_long)
    try:
        asyncio.run(summarize.gather_summary_source(
            text="x", link_url="https://www.youtube.com/watch?v=aB_12345678",
            image=None, consent=True, client=None,
        ))
    except ValueError as exc:
        assert str(exc) == "SOURCE_TOO_LONG"
    else:
        raise AssertionError("long videos must be blocked")

    try:
        asyncio.run(summarize.gather_summary_source(
            text="  ", link_url=None, image=None, consent=True, client=None,
        ))
    except ValueError as exc:
        assert str(exc) == "NO_CONTENT"
    else:
        raise AssertionError("blank input must be rejected")


def test_summarize_endpoint_returns_structured_summary(monkeypatch):
    import main
    from fastapi.testclient import TestClient
    from main import app

    async def fake_summarize(**kwargs):
        assert kwargs["link_url"] is None
        return {
            "title": "긴 글 요약", "summary": "핵심만 모음.", "points": ["첫째"],
            "sourceName": None, "sourceUrl": None, "warnings": [],
            "model": "gpt-6-luna", "reasoning": "max",
        }

    monkeypatch.setattr(main, "summarize_content", fake_summarize)
    with TestClient(app) as client:
        response = client.post("/api/summarize", json={
            "text": "긴 원문이다. " * 30, "focus": "", "consent": True,
        })
        assert response.status_code == 200
        assert response.json()["result"]["title"] == "긴 글 요약"
        image_rejected = client.post("/api/summarize", json={
            "text": "x", "focus": "", "consent": True,
            "image": {"mime": "image/jpeg", "data": "eA=="},
        })
        assert image_rejected.status_code == 422


def test_summary_contract_rejects_verdict_language_shape():
    from pydantic import ValidationError

    from contracts import ContentSummary

    parsed = ContentSummary.model_validate({
        "title": "t", "summary": "s", "points": ["p"],
        "sourceName": None, "sourceUrl": None, "warnings": [],
        "model": "gpt-6-luna", "reasoning": "max",
    })
    assert parsed.points == ["p"]
    try:
        ContentSummary.model_validate({**parsed.model_dump(), "points": ["x"] * 6})
    except ValidationError:
        pass
    else:
        raise AssertionError("point cap must hold")
