"""Concrete external-service adapters for the LangGraph stages."""
from dataclasses import dataclass
import logging
import re
from urllib.parse import urlsplit

import httpx

from answer_synthesis import direct_fact_answer, eligible_sources, insufficient_answer, synthesize_answer
from extraction import extract_claims, extract_image_claims, extract_page_claims
from jev import JevError
from kosis import KosisUnavailable, read_kosis_source, search_kosis_sources
from providers import ProviderCallError, providers_for_preference, run_with_fallback
from search import _source_identity, apply_shared_origin_groups, build_search_query, origin_group_for_url, search_sources, source_type_for_url
from settings import Settings
from sources import SourceReadResult, fetch_public_text, read_sources
from tavily_search import TavilyUnavailable, search_tavily
from text_utils import _truncate_units
from verification import verify_claims, verify_claims_jev
from workflow import FactCheckState, Stage
from youtube import fetch_youtube_data

_logger = logging.getLogger("runtime")

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

async def _fetch_market(symbols: list[str], settings: Settings) -> dict | None:
    """Fetch quote plus candles for the first detected symbol, if configured.

    Best-effort: any Finnhub failure omits market context without failing
    verification. Quote and candle access depend on the configured account.
    """
    from datetime import datetime, timezone

    from finnhub import fetch_candles as finnhub_candles
    from finnhub import fetch_stock_quote as finnhub_quote
    from stocks import build_market_context, display_name_for

    if not symbols:
        return None
    symbol = symbols[0]
    finnhub_key = settings.finnhub_api_key.get_secret_value()
    if not finnhub_key.strip():
        return None
    try:
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            quote = await finnhub_quote(symbol, api_key=finnhub_key, client=client)
            if quote.get("error"):
                return None
            candles = await finnhub_candles(symbol, api_key=finnhub_key, client=client)
        if candles.get("error"):
            return None
        context = build_market_context(
            symbol, display_name_for(symbol), quote, candles,
            data_as_of=datetime.now(timezone.utc).isoformat(),
        )
        if context is not None:
            context["source"] = "finnhub"
        return context
    except Exception:
        return None

@dataclass(frozen=True)
class RuntimeAdapters:
    """The five graph stages, injectable for offline orchestration tests."""

    extract: Stage
    search: Stage
    read: Stage
    verify: Stage
    synthesize: Stage

def make_runtime_adapters(settings: Settings) -> RuntimeAdapters:
    """그래프 노드 처리기를 만들고 비밀 키가 그래프 State에 들어가지 않게 합니다.

    각 처리기는 State 변경분만 반환합니다. 공급자 선택·실패 대체와
    ``llmModel``·``llmReasoning`` 기록은 아래 공통 처리 함수에서 맡습니다.
    """
    async def with_client(operation):
        """공급자 재시도 사이에 HTTP 클라이언트를 재사용합니다(기본 요청 제한 90초)."""
        async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
            return await operation(client)

    async def with_fallback(
        state: FactCheckState,
        operation,
        failure_code: str,
        *,
        first_attempt_timeout_seconds: float | None = None,
    ):
        """설정된 공급자를 호출하고 성공한 모델 정보를 결과에 기록합니다.

        모델을 명시하면 해당 공급자만 사용합니다. ``auto``는 호출이
        ProviderCallError로 실패할 때 설정 순서대로 다음 공급자를 시도합니다.
        짧은 제한 시간은 지정된 경우 첫 시도에만 전달합니다. 성공하면 선택된
        모델과 추론 수준을 ``llmModel``·``llmReasoning``으로 State에 남깁니다.
        """
        preference = state.get("modelPreference", "auto")
        try:
            providers = providers_for_preference(settings, preference, search=failure_code == "SEARCH_FAILED")
        except ValueError as exc:
            if str(exc) == "MODEL_UNAVAILABLE":
                raise
            raise ValueError("MODEL_UNAVAILABLE") from None

        async def attempt(provider, client):
            try:
                if first_attempt_timeout_seconds is not None and provider is providers[0]:
                    return await operation(
                        provider, client, first_attempt_timeout_seconds
                    )
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
        """텍스트·이미지·링크에서 검증할 주장을 추출합니다.

        이미지는 이미지 추출기로 전달합니다. URL만 입력한 경우 자막이나 페이지를
        먼저 읽습니다. 문장과 URL을 함께 입력한 경우 문장부터 분석하고, 주장을
        찾지 못했을 때만 링크 본문을 가져옵니다. 추출한 ``claims``를 다음 단계에
        전달하며, 페이지 본문을 분석한 경로에서는 State의 ``text``도 그 본문으로 갱신합니다.
        """
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
        has_link = isinstance(link_url, str) and bool(link_url)
        link_only = (
            has_link
            and state.get("text", "").strip() == link_url.strip()
        )

        async def extract_from_page(page_text):
            # 모델 요청과 State에 저장하는 원문을 맞춥니다. 최종 조립의 입력 상한 검사에
            # 실패하지 않도록 원문을 12,000단위까지 줄입니다.
            page_text = _truncate_units(page_text.strip(), 12_000)
            async def page_operation(provider, client):
                return await extract_page_claims(
                    page_text,
                    focus=state.get("focus", ""),
                    client=client,
                    provider=provider,
                )

            update = await with_fallback(state, page_operation, "EXTRACTION_FAILED")
            return {**update, "text": page_text}

        async def fetch_page():
            """페이지를 읽지 못하면 빈 문자열을 반환해 기본 추출 경로를 계속합니다."""
            try:
                page_text, _ = await fetch_public_text(link_url)
            except Exception:
                return ""
            return page_text if isinstance(page_text, str) else ""

        async def fetch_youtube_transcript():
            """링크에서 YouTube 영상 ID를 찾을 수 있을 때 자막을 가져옵니다."""
            from youtube import fetch_transcript_text, youtube_video_id

            video_id = youtube_video_id(link_url) if has_link else None
            if not video_id:
                return ""
            try:
                result = await fetch_transcript_text(video_id)
            except Exception:
                return ""
            text = result.get("text") if isinstance(result, dict) else None
            return text if isinstance(text, str) and text.strip() else ""

        async def fetch_link_text():
            """YouTube 자막을 우선 사용하고, 없으면 링크 페이지 본문을 읽습니다."""
            transcript = await fetch_youtube_transcript()
            if transcript.strip():
                return transcript
            return await fetch_page()

        if link_only:
            page_text = await fetch_link_text()
            if page_text.strip():
                return await extract_from_page(page_text)
        update = await with_fallback(
            state,
            lambda provider, client: extract_claims(
                state, client=client, provider=provider
            ),
            "EXTRACTION_FAILED",
        )
        if has_link and not link_only and not update.get("claims"):
            # 사용자 문장에서 주장을 찾지 못했을 때만 링크 본문을 추가로 가져옵니다.
            page_text = await fetch_link_text()
            if page_text.strip():
                try:
                    return await extract_from_page(page_text)
                except ValueError:
                    # 페이지 본문으로 재추출하지 못하면 첫 추출 결과를 유지합니다.
                    pass
        return update

    async def include_kosis_sources(update: dict, state: FactCheckState) -> dict:
        """조건에 맞는 일반 검색 결과에 KOSIS 보조 출처를 추가합니다.

        주식 종목 검색이 아니고 KOSIS 키가 설정된 경우에만 동작합니다. KOSIS 출처는
        최대 두 개를 앞에 배치하고 URL 중복을 제거하며, 전체 후보는 여섯 개로 제한합니다.
        KOSIS 장애는 기본 출처 검색 실패로 처리하지 않습니다.
        """
        kosis_key = settings.kosis_api_key.get_secret_value()
        if not kosis_key.strip() or state.get("stockSymbols"):
            return update
        try:
            async with httpx.AsyncClient(timeout=14.0, trust_env=False) as client:
                kosis_sources = await search_kosis_sources(
                    state, api_key=kosis_key, client=client,
                )
        except (KosisUnavailable, httpx.HTTPError, TimeoutError) as exc:
            _logger.warning("KOSIS search unavailable reason=%s", type(exc).__name__)
            return update
        if not kosis_sources:
            return update

        sources = []
        seen = set()
        for source in [*kosis_sources[:2], *update.get("sources", [])]:
            if not isinstance(source, dict) or not isinstance(source.get("url"), str):
                continue
            identity = _source_identity(source["url"])
            if identity in seen:
                continue
            seen.add(identity)
            sources.append({**source, "id": f"s{len(sources) + 1}"})
            if len(sources) == 6:
                break
        return {**update, "sources": sources}

    async def search(state: FactCheckState):
        """판정에 사용할 출처 후보를 찾고 필요한 통계·시장 정보를 덧붙입니다.

        먼저 주식 종목을 찾습니다. Tavily 키가 있으면 Tavily 검색을 우선 사용하고,
        사용할 수 없을 때 모델 검색으로 전환합니다. KOSIS는 보조 출처로 추가합니다.
        복구 검색에서는 첫 검색의 시장 데이터를 재사용해 API를 다시 부르지 않습니다.
        결과 State에는 출처 후보 ``sources``, 종목 ``stockSymbols``, 시장 정보 ``market``을 기록합니다.
        """
        from stocks import detect_stock_symbols

        symbols = detect_stock_symbols(state.get("text", ""), state.get("focus", ""))
        search_state = {**state, "stockSymbols": symbols} if symbols else state
        tavily_key = settings.tavily_api_key.get_secret_value()
        if tavily_key.strip():
            try:
                async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                    update = await search_tavily(search_state, api_key=tavily_key, client=client)
            except (TavilyUnavailable, ValueError) as exc:
                _logger.warning("tavily search unavailable reason=%s", type(exc).__name__)
                update = None
            if update is not None:
                update = await include_kosis_sources(update, search_state)
                market = state.get("market") if state.get("recoveryCount") else await _fetch_market(symbols, settings)
                return {**update, "stockSymbols": symbols, "market": market}
        update = await with_fallback(
            search_state,
            lambda provider, client: search_sources(
                search_state, client=client, provider=provider
            ),
            "SEARCH_FAILED",
        )
        update = await include_kosis_sources(update, search_state)
        market = state.get("market") if state.get("recoveryCount") else await _fetch_market(symbols, settings)
        return {**update, "stockSymbols": symbols, "market": market}

    async def read(state: FactCheckState):
        """출처 후보의 원문을 읽어 근거 기반 판정에 사용할 텍스트를 저장합니다.

        직접 입력 URL이 검색 후보에 없고 제외 목록에도 없으면 첫 후보(s0)로 추가합니다.
        최대 여섯 후보를 병렬로 읽고 리다이렉트가 같은 페이지를 가리키면 중복을 제거합니다.
        YouTube와 KOSIS는 전용 reader를 사용합니다. 첫 처리에서는 동의가 있고
        링크 제목을 읽을 수 있을 때 관련 출처 검색을 한 번 보탭니다. 원문은
        ``sourceTexts``, 제목별 본문 구간은 ``sourceSections``에 저장합니다.
        """
        sources = state.get("sources", [])
        link_url = state.get("linkUrl")
        kosis_sources = {
            source.get("url"): source for source in sources
            if isinstance(source, dict)
            and source.get("searchProvider") == "kosis_api"
            and isinstance(source.get("url"), str)
        }
        kosis_key = settings.kosis_api_key.get_secret_value()
        if (
            isinstance(link_url, str)
            and link_url
            and _source_identity(link_url) not in {
                _source_identity(url) for url in state.get("excludedSourceUrls", [])
            }
            and not any(
                isinstance(source, dict)
                and (source.get("url") == link_url or source.get("resolvedUrl") == link_url)
                for source in sources
            )
        ):
            # 직접 입력 URL을 첫 후보로 두고, 나머지 검색 후보는 최대 다섯 개로 제한합니다.
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
        link_cache: dict[str, object] = {}

        async def cached_reader(url):
            if url not in link_cache:
                # 제목 조회와 후보 일괄 읽기에서 URL이 겹칠 수 있으므로 읽은 결과를 캐시합니다.
                kosis_source = kosis_sources.get(url)
                if kosis_source and kosis_key.strip():
                    try:
                        async with httpx.AsyncClient(timeout=14.0, trust_env=False) as client:
                            link_cache[url] = await read_kosis_source(
                                kosis_source, api_key=kosis_key, client=client,
                            )
                    except KosisUnavailable as exc:
                        _logger.warning("KOSIS read unavailable reason=%s", type(exc).__name__)
                        link_cache[url] = SourceReadResult("", url, kosis_source.get("title", ""))
                else:
                    link_cache[url] = await fetch_public_text(url)
            return link_cache[url]

        if (
            isinstance(link_url, str) and link_url and state.get("consent") is True
            and any(isinstance(source, dict) and source.get("id") == "s0" for source in sources)
        ):
            try:
                link_result = await cached_reader(link_url)
                link_title = link_result.title if isinstance(link_result, SourceReadResult) else ""
            except Exception:
                link_title = ""
            tavily_key = settings.tavily_api_key.get_secret_value()
            # 제목 기반 보충 검색은 최초 실행에서만 수행하고 복구 단계에서는 반복하지 않습니다.
            if link_title.strip() and tavily_key.strip() and not state.get("recoveryCount"):
                try:
                    async with httpx.AsyncClient(timeout=30.0, trust_env=False) as search_client:
                        extra = await search_tavily(
                            state, api_key=tavily_key, client=search_client,
                            queries=[build_search_query(link_title)],
                        )
                    known = {link_url}
                    for source in sources:
                        if isinstance(source, dict):
                            known.add(source.get("url"))
                            known.add(source.get("resolvedUrl"))
                    additions = [
                        source for source in extra.get("sources", [])
                        if source.get("url") not in known
                    ]
                    if additions:
                        max_id = 0
                        for source in sources:
                            if isinstance(source, dict) and isinstance(source.get("id"), str):
                                match = re.fullmatch(r"s(\d+)", source["id"])
                                if match:
                                    max_id = max(max_id, int(match.group(1)))
                        for addition in additions:
                            max_id += 1
                            addition["id"] = f"s{max_id}"
                        sources = [sources[0], *additions, *sources[1:]][:6]
                        read_state = {**state, "sources": sources}
                except (TavilyUnavailable, ValueError) as exc:
                    _logger.warning("link-title search unavailable reason=%s", type(exc).__name__)
        youtube_key = settings.youtube_api_key.get_secret_value()
        if not youtube_key or not any(
            source.get("sourceType") == "유튜브" for source in sources if isinstance(source, dict)
        ):
            read_result = await read_sources(read_state, reader=cached_reader)
        else:
            async with httpx.AsyncClient(timeout=8.0, trust_env=False) as client:
                async def youtube_reader(url):
                    return await fetch_youtube_data(url, api_key=youtube_key, client=client)

                read_result = await read_sources(read_state, reader=cached_reader, youtube_reader=youtube_reader)
        read_result["sources"] = apply_shared_origin_groups(
            read_result.get("sources", []), read_result.get("sourceTexts", {}),
        )
        return read_result

    async def verify(state: FactCheckState):
        """읽은 원문으로 주장을 판정하고 검증된 인용 근거를 반환합니다.

        JEV 모드에서는 JEV를 먼저 호출하고 JevError가 발생한 경우에만 LLM 판정으로
        전환합니다. 일반 LLM 경로의 첫 공급자 요청은 60초로 제한하고, 자동 대체 공급자는
        공통 90초 제한을 사용합니다. 판정 결과와 검증된 인용을 ``claims``·``evidence``로 반환합니다.
        """
        if state.get("jevMode"):
            try:
                async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
                    update = await verify_claims_jev(
                        state,
                        client=client,
                        api_key=settings.typesafe_api_key.get_secret_value(),
                    )
                return {**update, "llmModel": "jev-latest"}
            except JevError as exc:
                _logger.warning("jev verify failed, escalating to llm: %s", type(exc).__name__)

        async def verify_with_provider(
            provider, client, request_timeout_seconds=90.0
        ):
            return await verify_claims(
                state,
                client=client,
                provider=provider,
                request_timeout_seconds=request_timeout_seconds,
            )

        return await with_fallback(
            state,
            verify_with_provider,
            "VERIFICATION_FAILED",
            first_attempt_timeout_seconds=60.0,
        )

    async def synthesize(state: FactCheckState):
        """판정 결과를 사용자가 읽을 최종 답변으로 정리합니다.

        JEV 모드·직접 생성 가능한 답·사용할 출처 없음은 모델 호출을 건너뜁니다.
        그 외에는 ``synthesize_answer``가 판정과 별도의 구조화 응답을 요청하고,
        생성 답변의 인용을 출처 원문과 대조합니다. 이 단계는 공통 90초 제한을 사용합니다.
        최종 ``answer``와 사용 모델·추론 수준을 ``answerModel``·``answerReasoning``으로 반환합니다.
        """
        if state.get("jevMode"):
            return {
                "answer": insufficient_answer(),
                "answerModel": None,
                "answerReasoning": None,
            }
        direct_answer = direct_fact_answer(state)
        if direct_answer is not None:
            return {"answer": direct_answer, "answerModel": None, "answerReasoning": None}
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
