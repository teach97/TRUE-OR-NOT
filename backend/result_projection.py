"""Validated projections from internal workflow state to public responses."""
from datetime import datetime, timezone
from urllib.parse import urlsplit

from answer_synthesis import insufficient_answer
from contracts import (
    FactCheckProgressCitation,
    FactCheckProgressClaim,
    FactCheckProgressSource,
    FactCheckResult,
)
from schemas import FactCheckRequest
from workflow import FactCheckState

_MODEL = "gpt-6-luna"

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

def _result_warnings(
    sources: list[dict],
    search_notice: str | None = None,
    youtube_transcript_verified: bool = False,
) -> list[str]:
    warnings = [
        "최대 3개 주장·6개 출처를 대상으로 한 제한된 검증입니다.",
    ]
    groups: dict[str, int] = {}
    for source in sources:
        group = source.get("originGroupId") if isinstance(source, dict) else None
        if isinstance(group, str) and group.startswith("shared-"):
            groups[group] = groups.get(group, 0) + 1
    if not any(count >= 2 for count in groups.values()):
        warnings.append(
            "출처 간 독립성과 원자료 계보는 확인되지 않았습니다.",
        )
    if any(source.get("accessStatus") == "unavailable" for source in sources):
        warnings.append(
            "일부 출처 원문에 접근하지 못했습니다. 검색 요약은 직접 인용으로 사용하지 않았습니다."
        )
    youtube_sources = [
        source for source in sources if source.get("sourceType") == "유튜브"
    ]
    if youtube_sources and not youtube_transcript_verified:
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
    warnings = _result_warnings(
        sources,
        merged_state.get("searchNotice"),
        youtube_transcript_verified=any(
            isinstance(raw, dict) and raw.get("youtubeTranscript") for raw in raw_sources
        ),
    )
    if merged_state.get("recoveryCount"):
        warnings.append("원문 수집·인용 검증 문제로 검색어를 바꿔 1회 재탐색했습니다.")
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
        "warnings": warnings,
        "market": merged_state.get("market"),
        "answer": answer,
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
        seen_sources: set[str] = set()
        for evidence_id in claim.evidenceIds:
            evidence = evidence_by_id.get(evidence_id)
            source = sources_by_id.get(evidence.sourceId) if evidence else None
            if (
                evidence is None
                or source is None
                or source.accessStatus != "verified"
                or source.sourceType == "유튜브"
                or evidence.sourceId in seen_sources
            ):
                continue
            seen_sources.add(evidence.sourceId)
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
