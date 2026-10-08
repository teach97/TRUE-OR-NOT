"""LangGraph composition root with compatibility exports for existing callers."""
from langgraph.graph import END, START, StateGraph

from answer_synthesis import eligible_sources, insufficient_answer
from jev_runtime import run_jev_fast_check
from recovery import review_recovery
from result_projection import (
    _MODEL,
    _normalize_source,
    _result_warnings,
    build_fact_check_result,
    build_progress_preview,
    build_progress_sources,
)
from runtime_adapters import (
    RuntimeAdapters,
    _fetch_market,
    _http_status_from_exception,
    make_runtime_adapters,
)
from search import _source_identity
from settings import Settings, load_settings
from text_utils import _truncate_units
from workflow import FactCheckState, Stage, build_workflow


def build_runtime_workflow(
    settings: Settings,
    *,
    adapters: RuntimeAdapters | None = None,
):
    """Compile five stages, review failures once, and assemble after synthesis."""
    runtime_adapters = adapters or make_runtime_adapters(settings)

    async def extracting(state: FactCheckState):
        update = await runtime_adapters.extract(state)
        return {**update, "claimSnapshot": [dict(c) for c in update.get("claims", [])],
                "recoveryCount": 0, "recoveryRequested": False, "recoveryTrace": []}

    async def searching(state: FactCheckState):
        update = await runtime_adapters.search(state)
        excluded = {_source_identity(url) for url in state.get("excludedSourceUrls", [])}
        sources = [s for s in update.get("sources", [])
                   if _source_identity(s["url"]) not in excluded]
        return {**update, "sources": sources, "sourceTexts": {}, "sourceSections": {},
                "evidence": [], "diagnostics": [], "recoveryRequested": False}

    async def verifying(state: FactCheckState):
        update = await runtime_adapters.verify(state)
        update = {**update, "diagnostics": update.get("diagnostics", [])}
        return {**update, **review_recovery({**state, **update})}

    async def reading(state: FactCheckState):
        update = await runtime_adapters.read(state)
        excluded = {_source_identity(url) for url in state.get("excludedSourceUrls", [])}
        sources = [s for s in update.get("sources", []) if not any(
            _source_identity(url) in excluded for url in (s.get("url"), s.get("resolvedUrl"))
            if isinstance(url, str) and url
        )]
        ids = {s["id"] for s in sources}
        return {**update, "sources": sources,
                "sourceTexts": {sid: text for sid, text in update.get("sourceTexts", {}).items() if sid in ids},
                "sourceSections": {sid: sections for sid, sections in update.get("sourceSections", {}).items() if sid in ids}}

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
        extract=extracting,
        search=searching,
        read=reading,
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
