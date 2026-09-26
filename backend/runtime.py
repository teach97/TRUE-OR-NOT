"""Server settings and the assembled four-stage verification workflow."""
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import dotenv_values
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, SecretStr

from answer_synthesis import eligible_sources, insufficient_answer, synthesize_answer
from contracts import (
    FactCheckProgressCitation,
    FactCheckProgressClaim,
    FactCheckProgressSource,
    FactCheckResult,
)
from extraction import extract_claims, extract_image_claims, extract_page_claims
from jev import JevError
from tavily_search import TavilyUnavailable, search_tavily
from providers import ProviderCallError, providers_for_preference, run_with_fallback
from schemas import FactCheckRequest
from search import build_search_query, origin_group_for_url, search_sources, source_type_for_url
from sources import fetch_public_text, read_sources
from verification import (
    verify_claims,
    verify_claims_jev,
)
from youtube import fetch_youtube_data
from workflow import FactCheckState, Stage, build_workflow


_MODEL = "gpt-6-luna"
_logger = logging.getLogger(__name__)


def _http_status_from_exception(error: BaseException) -> int | None:
    """Return only an upstream HTTP status from an exception chain."""
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        response = getattr(current, "response", None)
        status_code = getattr(response, "status_code", None)
        if isinstance(status_code, int):
            return status_code
        current = current.__cause__ or current.__context__
    return None


class Settings(BaseModel):
    api_key: SecretStr
    gemini_api_key: SecretStr = SecretStr("")
    youtube_api_key: SecretStr = SecretStr("")
    tavily_api_key: SecretStr = SecretStr("")
    ai_gateway_api_key: SecretStr = SecretStr("")


def load_settings(env_path: Path | None = None) -> Settings:
    """Read the backend-local file without mutating process environment."""
    path = env_path if env_path is not None else Path(__file__).with_name(".env")
    values = dotenv_values(path, encoding="utf-8-sig", interpolate=False)
    key = os.environ.get("OPENAI_API_KEY", values.get("OPENAI_API_KEY") or "")
    gemini_key = os.environ.get("GEMINI_API_KEY", values.get("GEMINI_API_KEY") or "")
    youtube_key = os.environ.get("YOUTUBE_API_KEY", values.get("YOUTUBE_API_KEY") or "")
    tavily_key = os.environ.get("TAVILY_API_KEY", values.get("TAVILY_API_KEY") or "")
    gateway_key = os.environ.get("AI_GATEWAY_API_KEY", values.get("AI_GATEWAY_API_KEY") or "")
    return Settings(
        api_key=SecretStr(key.strip()),
        gemini_api_key=SecretStr(gemini_key.strip()),
        youtube_api_key=SecretStr(youtube_key.strip()),
        tavily_api_key=SecretStr(tavily_key.strip()),
        ai_gateway_api_key=SecretStr(gateway_key.strip()),
    )


@dataclass(frozen=True)
class RuntimeAdapters:
    """The five graph stages, injectable for offline orchestration tests."""

    extract: Stage
    search: Stage
    read: Stage
    verify: Stage
    synthesize: Stage


def make_runtime_adapters(settings: Settings) -> RuntimeAdapters:
    """Create provider-backed stages without exposing credentials to graph state."""
    async def with_client(operation):
        async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
            return await operation(client)

    async def with_fallback(state: FactCheckState, operation, failure_code: str):
        preference = state.get("modelPreference", "auto")
        try:
            providers = providers_for_preference(settings, preference)
        except ValueError as exc:
            if str(exc) == "MODEL_UNAVAILABLE":
                raise
            raise ValueError("MODEL_UNAVAILABLE") from None

        async def attempt(provider, client):
            try:
                return await operation(provider, client)
            except ProviderCallError as exc:
                _logger.warning(
                    "provider attempt failed stage=%s provider=%s error_type=%s http_status=%s",
                    failure_code,
                    provider.model,
                    type(exc).__name__,
                    _http_status_from_exception(exc),
                )
                raise
            except ValueError as exc:
                _logger.warning(
                    "provider attempt failed stage=%s provider=%s error_type=%s http_status=%s",
                    failure_code,
                    provider.model,
                    type(exc).__name__,
                    _http_status_from_exception(exc),
                )
                if str(exc) in {"INVALID_REQUEST", "NOT_CONFIGURED", "MODEL_UNAVAILABLE"}:
                    raise
                raise ProviderCallError("Provider stage failed") from None

        try:
            update, provider = await with_client(
                lambda client: run_with_fallback(
                    providers,
                    lambda provider: attempt(provider, client),
                )
            )
        except ProviderCallError:
            if preference != "auto":
                raise ValueError("MODEL_FAILED") from None
            raise ValueError(failure_code) from None
        except ValueError as exc:
            if str(exc) == "NOT_CONFIGURED":
                raise
            raise ValueError(failure_code) from None
        return {
            **update,
            "llmModel": provider.model,
            "llmReasoning": provider.reasoning,
        }

    async def extract(state: FactCheckState):
        image = state.get("image")
        if isinstance(image, dict) and image.get("data"):
            return await with_fallback(
                state,
                lambda provider, client: extract_image_claims(
                    state, image, client=client, provider=provider
                ),
                "EXTRACTION_FAILED",
            )
        link_url = state.get("linkUrl")
        if (
            isinstance(link_url, str)
            and link_url
            and state.get("text", "").strip() == link_url.strip()
        ):
            try:
                page_text, _ = await fetch_public_text(link_url)
            except Exception:
                page_text = ""
            if isinstance(page_text, str) and page_text.strip():
                async def page_operation(provider, client):
                    return await extract_page_claims(
                        page_text,
                        focus=state.get("focus", ""),
                        client=client,
                        provider=provider,
                    )

                update = await with_fallback(state, page_operation, "EXTRACTION_FAILED")
                return {**update, "text": page_text}
        return await with_fallback(
            state,
            lambda provider, client: extract_claims(
                state, client=client, provider=provider
            ),
            "EXTRACTION_FAILED",
        )

    async def search(state: FactCheckState):
        tavily_key = settings.tavily_api_key.get_secret_value()
        if tavily_key.strip():
            try:
                async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                    return await search_tavily(state, api_key=tavily_key, client=client)
            except (TavilyUnavailable, ValueError) as exc:
                _logger.warning("tavily search unavailable reason=%s", type(exc).__name__)
        return await with_fallback(
            state,
            lambda provider, client: search_sources(
                state, client=client, provider=provider
            ),
            "SEARCH_FAILED",
        )

    async def read(state: FactCheckState):
        sources = state.get("sources", [])
        link_url = state.get("linkUrl")
        if (
            isinstance(link_url, str)
            and link_url
            and not any(
                isinstance(source, dict)
                and (source.get("url") == link_url or source.get("resolvedUrl") == link_url)
                for source in sources
            )
        ):
            host = urlsplit(link_url).hostname or link_url
            seed = {
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
            }
            # Keep the linked page plus at most five searched candidates.
            sources = [seed, *sources][:6]
        read_state = {**state, "sources": sources}
        youtube_key = settings.youtube_api_key.get_secret_value()
        if not youtube_key or not any(
            source.get("sourceType") == "유튜브" for source in sources if isinstance(source, dict)
        ):
            return await read_sources(read_state)
        async with httpx.AsyncClient(timeout=8.0, trust_env=False) as client:
            async def youtube_reader(url):
                return await fetch_youtube_data(url, api_key=youtube_key, client=client)

            return await read_sources(read_state, youtube_reader=youtube_reader)

    async def verify(state: FactCheckState):
        if state.get("jevMode"):
            try:
                async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
                    update = await verify_claims_jev(
                        state,
                        client=client,
                        api_key=settings.ai_gateway_api_key.get_secret_value(),
                    )
                return {**update, "llmModel": "typesafe-ai/jev"}
            except JevError as exc:
                _logger.warning("jev verify failed, escalating to llm: %s", type(exc).__name__)
        return await with_fallback(
            state,
            lambda provider, client: verify_claims(
                state, client=client, provider=provider
            ),
            "VERIFICATION_FAILED",
        )

    async def synthesize(state: FactCheckState):
        if state.get("jevMode"):
            return {
                "answer": insufficient_answer(),
                "answerModel": None,
                "answerReasoning": None,
            }
        if not eligible_sources(state):
            return {
                "answer": insufficient_answer(),
                "answerModel": None,
                "answerReasoning": None,
            }

        async def operation(provider, client):
            return {
                "answer": await synthesize_answer(
                    state, client=client, provider=provider,
                ),
            }

        update = await with_fallback(state, operation, "SYNTHESIS_FAILED")
        answer = update["answer"]
        return {
            "answer": answer,
            "answerModel": answer["model"],
            "answerReasoning": answer["reasoning"],
        }

    return RuntimeAdapters(
        extract=extract, search=search, read=read, verify=verify, synthesize=synthesize,
    )


def _normalize_source(raw: dict, checked_at: str) -> dict:
    """Project internal source state onto the public TypeScript contract."""
    if not isinstance(raw, dict):
        raise ValueError("INVALID_STATE")

    raw_url = raw.get("resolvedUrl") or raw.get("url")
    if not isinstance(raw_url, str) or not raw_url.strip():
        raise ValueError("INVALID_STATE")
    hostname = urlsplit(raw_url).hostname
    publisher = raw.get("publisher") or hostname or "알 수 없는 출처"
    title = raw.get("title") or raw_url
    access_status = raw.get("accessStatus")
    if access_status not in {"verified", "unavailable"}:
        raise ValueError("INVALID_STATE")

    return {
        "id": raw.get("id"),
        "url": raw_url,
        "title": title,
        "publisher": publisher,
        "publishedAt": raw.get("publishedAt"),
        "retrievedAt": raw.get("retrievedAt") or checked_at,
        "accessStatus": access_status,
        "sourceType": raw.get("sourceType") or "유형 미확인",
        "originGroupId": raw.get("originGroupId"),
        "searchProvider": raw.get("searchProvider"),
        "searchQuery": raw.get("searchQuery"),
        "candidateOrder": raw.get("candidateOrder"),
        "youtubeTitle": raw.get("youtubeTitle"),
        "youtubeChannelTitle": raw.get("youtubeChannelTitle"),
        "youtubePublishedAt": raw.get("youtubePublishedAt"),
        "youtubeViewCount": raw.get("youtubeViewCount"),
        "youtubeComments": raw.get("youtubeComments", []),
        "youtubeDataStatus": raw.get("youtubeDataStatus", "not_applicable"),
    }


def _result_warnings(sources: list[dict], search_notice: str | None = None) -> list[str]:
    warnings = [
        "최대 3개 주장·6개 출처를 대상으로 한 제한된 검증입니다.",
        "출처 간 독립성과 원자료 계보는 확인되지 않았습니다.",
    ]
    if any(source.get("accessStatus") == "unavailable" for source in sources):
        warnings.append(
            "일부 출처 원문에 접근하지 못했습니다. 검색 요약은 직접 인용으로 사용하지 않았습니다."
        )
    if any(source.get("sourceType") == "유튜브" for source in sources):
        warnings.append(
            "유튜브 공개 댓글은 영상별 의견 맥락으로만 표시하며 판정과 인용 근거에는 사용하지 않았습니다."
        )
    if search_notice == "LLM_SEARCH_UNAVAILABLE":
        warnings.append(
            "웹검색을 사용할 수 없어 검색 원문을 확보하지 못했습니다."
        )
    return warnings


def build_fact_check_result(
    state: FactCheckState,
    update: dict,
    *,
    checked_at: str | None = None,
) -> FactCheckResult:
    """Validate and assemble the only result shape exposed by the API."""
    if not isinstance(update, dict):
        raise ValueError("INVALID_STATE")
    merged_state = {**state, **update}
    request = FactCheckRequest.model_validate({
        "text": state.get("text"),
        "focus": state.get("focus"),
        "consent": state.get("consent"),
    })
    claims = state.get("claims")
    evidence = state.get("evidence")
    raw_sources = state.get("sources", [])
    if not isinstance(claims, list) or not isinstance(evidence, list) or not isinstance(raw_sources, list):
        raise ValueError("INVALID_STATE")

    timestamp = checked_at or datetime.now(timezone.utc).isoformat()
    sources = [_normalize_source(source, timestamp) for source in raw_sources]
    answer = merged_state.get("answer") if "answer" in update else None
    if not isinstance(answer, dict):
        answer = insufficient_answer()
    answer = {
        **answer,
        "model": update.get("answerModel"),
        "reasoning": update.get("answerReasoning"),
    }
    return FactCheckResult.model_validate({
        "text": request.text,
        "focus": request.focus,
        "demo": False,
        "model": state.get("llmModel") or _MODEL,
        "reasoning": state.get("llmReasoning") or "max",
        "checkedAt": timestamp,
        "claims": claims,
        "sources": sources,
        "evidence": evidence,
        "warnings": _result_warnings(sources, merged_state.get("searchNotice")),
        "answer": answer,
    })


def _truncate_units(text: str, max_units: int) -> str:
    """Truncate to a UTF-16 unit budget without splitting astral characters."""
    units = 0
    out: list[str] = []
    for char in text:
        units += 2 if ord(char) > 0xFFFF else 1
        if units > max_units:
            break
        out.append(char)
    return "".join(out)


async def run_jev_fast_check(
    *,
    text: str,
    focus: str = "",
    link_url: str | None = None,
    client: httpx.AsyncClient,
    api_key: str | None,
    settings: Settings,
    consent: bool = True,
) -> FactCheckResult:
    """Search and read evidence, then return Jev's score-only claim result."""
    full_text = _truncate_units(text.strip(), 12_000)
    if not full_text:
        raise JevError("Nothing to judge")

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
                    providers = providers_for_preference(settings, "auto")
                    search_result, _ = await run_with_fallback(providers, search_once)
                except (ProviderCallError, ValueError) as exc:
                    _logger.warning("Jev LLM search unavailable reason=%s", type(exc).__name__)
                    search_notice = "LLM_SEARCH_UNAVAILABLE"
            if search_result is not None:
                sources.extend(search_result.get("sources", []))

    if read_result is None:
        state["sources"] = sources[:6]
        read_result = await read_sources(state, reader=fetch_public_text)
    state.update(read_result)
    judgment_result = await verify_claims_jev(
        state,
        client=client,
        api_key=api_key,
    )
    if not judgment_result.get("claims"):
        raise JevError("Jev returned no judgment")

    timestamp = datetime.now(timezone.utc).isoformat()
    normalized_sources = [
        _normalize_source(source, timestamp) for source in read_result.get("sources", [])
    ]
    warnings = _result_warnings(normalized_sources, search_notice)
    return FactCheckResult.model_validate({
        "text": full_text,
        "focus": focus,
        "demo": False,
        "model": "typesafe-ai/jev",
        "reasoning": "max",
        "checkedAt": timestamp,
        "claims": judgment_result["claims"],
        "sources": normalized_sources,
        "evidence": judgment_result.get("evidence", []),
        "warnings": warnings,
        "answer": insufficient_answer(),
    })


def build_progress_sources(state: FactCheckState) -> list[dict[str, object]]:
    """Expose only source identity and access state before final answer assembly."""
    raw_sources = state.get("sources", [])
    if not isinstance(raw_sources, list):
        return []

    projected: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for raw in raw_sources:
        if not isinstance(raw, dict):
            continue
        source_id = raw.get("id")
        raw_url = raw.get("resolvedUrl") or raw.get("url")
        if not isinstance(source_id, str) or not source_id or source_id in seen_ids:
            continue
        if not isinstance(raw_url, str) or len(raw_url) > 2048:
            continue
        try:
            parsed_url = urlsplit(raw_url)
        except ValueError:
            continue
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
            continue

        status = raw.get("accessStatus")
        if status not in {"verified", "unavailable"}:
            status = "candidate"
        source = FactCheckProgressSource.model_validate({
            "id": source_id,
            "url": raw_url,
            "title": str(raw.get("title") or parsed_url.hostname)[:300],
            "publisher": str(raw.get("publisher") or parsed_url.hostname)[:300],
            "accessStatus": status,
            "sourceType": str(raw.get("sourceType") or "유형 미확인")[:100],
        })
        projected.append(source.model_dump(mode="json"))
        seen_ids.add(source_id)
        if len(projected) == 6:
            break
    return projected


def build_progress_preview(state: FactCheckState) -> dict[str, object]:
    """Build an early, strictly projected claim summary from validated evidence."""
    result = build_fact_check_result(state, {})
    evidence_by_id = {evidence.id: evidence for evidence in result.evidence}
    sources_by_id = {source.id: source for source in result.sources}
    claims: list[dict[str, object]] = []

    for claim in result.claims:
        citations: list[dict[str, str]] = []
        for evidence_id in claim.evidenceIds:
            evidence = evidence_by_id.get(evidence_id)
            source = sources_by_id.get(evidence.sourceId) if evidence else None
            if (
                evidence is None
                or source is None
                or source.accessStatus != "verified"
                or source.sourceType == "유튜브"
            ):
                continue
            citation = FactCheckProgressCitation.model_validate({
                "sourceId": evidence.sourceId,
                "quote": evidence.quote,
            })
            citations.append(citation.model_dump(mode="json"))
            if len(citations) == 3:
                break

        preview_claim = FactCheckProgressClaim.model_validate({
            "id": claim.id,
            "quote": claim.quote,
            "summary": claim.summary,
            "verdict": claim.verdict,
            "citations": citations,
        })
        claims.append(preview_claim.model_dump(mode="json"))

    return {"claims": claims}


def build_runtime_workflow(
    settings: Settings,
    *,
    adapters: RuntimeAdapters | None = None,
):
    """Compile five ordered stages and assemble the result after synthesis."""
    runtime_adapters = adapters or make_runtime_adapters(settings)

    async def verifying(state: FactCheckState):
        return await runtime_adapters.verify(state)

    async def synthesizing(state: FactCheckState):
        try:
            if not eligible_sources(state):
                update = {
                    "answer": insufficient_answer(),
                    "answerModel": None,
                    "answerReasoning": None,
                }
            else:
                update = await runtime_adapters.synthesize(state)
        except ValueError as exc:
            if str(exc) not in {"NOT_CONFIGURED", "SYNTHESIS_FAILED"}:
                raise
            update = {
                "answer": insufficient_answer(),
                "answerModel": None,
                "answerReasoning": None,
            }

        if not isinstance(update, dict):
            update = {}
        answer = update.get("answer")
        if not isinstance(answer, dict):
            update = {
                "answer": insufficient_answer(),
                "answerModel": None,
                "answerReasoning": None,
            }
        result = build_fact_check_result(state, update)
        return {**update, "result": result.model_dump(mode="json")}

    return build_workflow(
        extract=runtime_adapters.extract,
        search=runtime_adapters.search,
        read=runtime_adapters.read,
        verify=verifying,
        synthesize=synthesizing,
    )


def build_extraction_graph(extract: Stage):
    """End after extraction; do not simulate search, sources, or judgments."""
    builder = StateGraph(FactCheckState)
    builder.add_node("extracting", extract)
    builder.add_edge(START, "extracting")
    builder.add_edge("extracting", END)
    return builder.compile()
