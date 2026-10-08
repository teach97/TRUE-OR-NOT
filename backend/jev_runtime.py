"""Direct JEV check path used by the dedicated fact-check endpoint."""
from datetime import datetime, timezone
import logging
from urllib.parse import urlsplit

import httpx

from answer_synthesis import insufficient_answer
from contracts import FactCheckResult
from jev import JevError
from providers import ProviderCallError, providers_for_preference, run_with_fallback
from result_projection import _normalize_source, _result_warnings
from schemas import ModelPreference
from search import build_search_query, origin_group_for_url, search_sources, source_type_for_url
from settings import Settings
from sources import fetch_public_text, read_sources
from tavily_search import TavilyUnavailable, search_tavily
from text_utils import _truncate_units
from verification import _empty_judgments, ground_judgments, verify_claims_jev
from youtube import fetch_youtube_data

_logger = logging.getLogger("runtime")

async def run_jev_fast_check(
    *,
    text: str,
    focus: str = "",
    link_url: str | None = None,
    client: httpx.AsyncClient,
    api_key: str | None,
    settings: Settings,
    model_preference: ModelPreference = "auto",
    consent: bool = True,
) -> FactCheckResult:
    """Search and read evidence, then return Jev's score-only claim result."""
    full_text = _truncate_units(text, 12_000)
    if not full_text.strip():
        raise JevError("Nothing to judge", code="INVALID_REQUEST")

    claim = {
        "id": "c1",
        "quote": full_text,
        "start": 0,
        "end": len(full_text.encode("utf-16-le")) // 2,
        "kind": "fact",
    }
    query_text = focus.strip() or full_text
    state = {
        "text": full_text,
        "focus": focus,
        "consent": consent,
        "claims": [claim],
        "searchQueries": {"c1": build_search_query(query_text)},
    }
    sources: list[dict] = []
    if link_url:
        host = urlsplit(link_url).hostname or link_url
        sources.append({
            "id": "s0",
            "url": link_url,
            "title": host,
            "publisher": host,
            "sourceType": source_type_for_url(link_url),
            "originGroupId": origin_group_for_url(link_url),
            "accessStatus": "pending",
            "searchProvider": None,
            "searchQuery": None,
            "candidateOrder": None,
        })

    search_notice = None
    read_result = None
    if consent and link_url and sources:
        link_read = await read_sources({"sources": sources}, reader=fetch_public_text)
        if link_read.get("sourceTexts"):
            read_result = link_read
    if read_result is None:
        if not consent:
            search_notice = "LLM_SEARCH_UNAVAILABLE"
        else:
            async def search_once(provider):
                try:
                    return await search_sources(state, client=client, provider=provider)
                except ValueError as exc:
                    raise ProviderCallError(str(exc)) from None

            search_result = None
            tavily_key = settings.tavily_api_key.get_secret_value()
            if tavily_key.strip():
                try:
                    search_result = await search_tavily(state, api_key=tavily_key, client=client)
                except (TavilyUnavailable, ValueError) as exc:
                    _logger.warning("Jev Tavily search unavailable reason=%s", type(exc).__name__)
            if search_result is None:
                try:
                    providers = providers_for_preference(settings, model_preference, search=True)
                    search_result, _ = await run_with_fallback(providers, search_once)
                except (ProviderCallError, ValueError) as exc:
                    _logger.warning("Jev LLM search unavailable reason=%s", type(exc).__name__)
                    search_notice = "LLM_SEARCH_UNAVAILABLE"
            if search_result is not None:
                sources.extend(search_result.get("sources", []))

    if read_result is None:
        state["sources"] = sources[:6]
        youtube_key = settings.youtube_api_key.get_secret_value()
        if youtube_key.strip() and any(
            isinstance(source, dict) and source.get("sourceType") == "유튜브"
            for source in sources
        ):
            async def youtube_reader(url):
                return await fetch_youtube_data(url, api_key=youtube_key, client=client)

            read_result = await read_sources(state, reader=fetch_public_text, youtube_reader=youtube_reader)
        else:
            read_result = await read_sources(state, reader=fetch_public_text)
    state.update(read_result)
    try:
        judgment_result = await verify_claims_jev(
            state,
            client=client,
            api_key=api_key,
        )
    except JevError as exc:
        if exc.code != "LOW_CONFIDENCE":
            raise
        # Low confidence is deterministic: retrying the same evidence cannot
        # help, so conclude with insufficient evidence instead of failing.
        judgment_result = ground_judgments(
            [claim],
            _empty_judgments([claim]),
            state.get("sources", []),
            state.get("sourceTexts", {}),
            source_sections=state.get("sourceSections", {}),
        )
    if not judgment_result.get("claims"):
        raise JevError("Jev returned no judgment", code="NO_JUDGMENT")

    timestamp = datetime.now(timezone.utc).isoformat()
    normalized_sources = [
        _normalize_source(source, timestamp) for source in read_result.get("sources", [])
    ]
    warnings = _result_warnings(
        normalized_sources,
        search_notice,
        youtube_transcript_verified=any(
            isinstance(raw, dict) and raw.get("youtubeTranscript")
            for raw in read_result.get("sources", [])
        ),
    )
    return FactCheckResult.model_validate({
        "text": full_text,
        "focus": focus,
        "demo": False,
        "model": "jev-latest",
        "reasoning": "max",
        "checkedAt": timestamp,
        "claims": judgment_result["claims"],
        "sources": normalized_sources,
        "evidence": judgment_result.get("evidence", []),
        "warnings": warnings,
        "answer": insufficient_answer(),
    })
