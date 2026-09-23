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
from contracts import FactCheckResult
from extraction import extract_claims
from providers import ProviderCallError, providers_for_preference, run_with_fallback
from schemas import FactCheckRequest
from search import search_sources
from sources import read_sources
from verification import verify_claims
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


def load_settings(env_path: Path | None = None) -> Settings:
    """Read the backend-local file without mutating process environment."""
    path = env_path if env_path is not None else Path(__file__).with_name(".env")
    values = dotenv_values(path, encoding="utf-8-sig", interpolate=False)
    key = os.environ.get("OPENAI_API_KEY", values.get("OPENAI_API_KEY") or "")
    gemini_key = os.environ.get("GEMINI_API_KEY", values.get("GEMINI_API_KEY") or "")
    youtube_key = os.environ.get("YOUTUBE_API_KEY", values.get("YOUTUBE_API_KEY") or "")
    return Settings(
        api_key=SecretStr(key.strip()),
        gemini_api_key=SecretStr(gemini_key.strip()),
        youtube_api_key=SecretStr(youtube_key.strip()),
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
        async with httpx.AsyncClient(timeout=90) as client:
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
        return await with_fallback(
            state,
            lambda provider, client: extract_claims(
                state, client=client, provider=provider
            ),
            "EXTRACTION_FAILED",
        )

    async def search(state: FactCheckState):
        return await with_fallback(
            state,
            lambda provider, client: search_sources(
                state, client=client, provider=provider
            ),
            "SEARCH_FAILED",
        )

    async def read(state: FactCheckState):
        youtube_key = settings.youtube_api_key.get_secret_value()
        if not youtube_key or not any(
            source.get("sourceType") == "유튜브" for source in state.get("sources", [])
        ):
            return await read_sources(state)
        async with httpx.AsyncClient(timeout=8.0, trust_env=False) as client:
            async def youtube_reader(url):
                return await fetch_youtube_data(url, api_key=youtube_key, client=client)

            return await read_sources(state, youtube_reader=youtube_reader)

    async def verify(state: FactCheckState):
        return await with_fallback(
            state,
            lambda provider, client: verify_claims(
                state, client=client, provider=provider
            ),
            "VERIFICATION_FAILED",
        )

    async def synthesize(state: FactCheckState):
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
        "youtubeComments": raw.get("youtubeComments", []),
        "youtubeDataStatus": raw.get("youtubeDataStatus", "not_applicable"),
    }


def _result_warnings(sources: list[dict]) -> list[str]:
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
        "warnings": _result_warnings(sources),
        "answer": answer,
    })


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
