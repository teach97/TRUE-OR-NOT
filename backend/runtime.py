"""Server settings and the assembled four-stage verification workflow."""
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import dotenv_values
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, SecretStr

from contracts import FactCheckResult
from extraction import extract_claims
from providers import ProviderCallError, configured_providers, run_with_fallback
from schemas import FactCheckRequest
from search import search_sources
from sources import read_sources
from verification import verify_claims
from youtube import fetch_youtube_data
from workflow import FactCheckState, Stage, build_workflow


_MODEL = "gpt-6-luna"


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
    """The four graph stages, injectable for offline orchestration tests."""

    extract: Stage
    search: Stage
    read: Stage
    verify: Stage


def make_runtime_adapters(settings: Settings) -> RuntimeAdapters:
    """Create provider-backed stages without exposing credentials to graph state."""
    providers = configured_providers(settings)

    async def with_client(operation):
        async with httpx.AsyncClient(timeout=90) as client:
            return await operation(client)

    async def with_fallback(operation, failure_code: str):
        async def attempt(provider, client):
            try:
                return await operation(provider, client)
            except ValueError as exc:
                if str(exc) in {"INVALID_REQUEST", "NOT_CONFIGURED"}:
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
            lambda provider, client: extract_claims(
                state, client=client, provider=provider
            ),
            "EXTRACTION_FAILED",
        )

    async def search(state: FactCheckState):
        return await with_fallback(
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
            lambda provider, client: verify_claims(
                state, client=client, provider=provider
            ),
            "VERIFICATION_FAILED",
        )

    return RuntimeAdapters(extract=extract, search=search, read=read, verify=verify)


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
    merged_state = {**state, **(update if isinstance(update, dict) else {})}
    request = FactCheckRequest.model_validate({
        "text": merged_state.get("text"),
        "focus": merged_state.get("focus"),
        "consent": merged_state.get("consent"),
    })
    if not isinstance(update, dict):
        raise ValueError("INVALID_STATE")
    claims = update.get("claims")
    evidence = update.get("evidence")
    raw_sources = merged_state.get("sources", [])
    if not isinstance(claims, list) or not isinstance(evidence, list) or not isinstance(raw_sources, list):
        raise ValueError("INVALID_STATE")

    timestamp = checked_at or datetime.now(timezone.utc).isoformat()
    sources = [_normalize_source(source, timestamp) for source in raw_sources]
    return FactCheckResult.model_validate({
        "text": request.text,
        "focus": request.focus,
        "demo": False,
        "model": merged_state.get("llmModel") or _MODEL,
        "reasoning": merged_state.get("llmReasoning") or "max",
        "checkedAt": timestamp,
        "claims": claims,
        "sources": sources,
        "evidence": evidence,
        "warnings": _result_warnings(sources),
    })


def build_runtime_workflow(
    settings: Settings,
    *,
    adapters: RuntimeAdapters | None = None,
):
    """Compile extracting → searching → reading → verifying with final assembly."""
    runtime_adapters = adapters or make_runtime_adapters(settings)

    async def verifying(state: FactCheckState):
        update = await runtime_adapters.verify(state)
        result = build_fact_check_result(state, update)
        normalized_sources = [
            source.model_dump(mode="json") for source in result.sources
        ]
        return {
            **update,
            "sources": normalized_sources,
            "result": result.model_dump(mode="json"),
        }

    return build_workflow(
        extract=runtime_adapters.extract,
        search=runtime_adapters.search,
        read=runtime_adapters.read,
        verify=verifying,
    )


def build_extraction_graph(extract: Stage):
    """End after extraction; do not simulate search, sources, or judgments."""
    builder = StateGraph(FactCheckState)
    builder.add_node("extracting", extract)
    builder.add_edge(START, "extracting")
    builder.add_edge("extracting", END)
    return builder.compile()
