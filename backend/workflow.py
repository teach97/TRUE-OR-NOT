"""Provider-independent graph. All real service adapters must be supplied explicitly.

This module does not produce fallback judgments or call external services itself.
Dictionary payloads are internal extension points, not a validated HTTP contract.
"""
from collections.abc import Awaitable, Callable
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph


class FactCheckState(TypedDict, total=False):
    text: str
    focus: str
    consent: bool
    modelPreference: str
    linkUrl: str | None
    image: dict[str, Any] | None
    jevMode: bool
    claims: list[dict[str, Any]]
    searchQueries: dict[str, str]
    searchNotice: str
    stockSymbols: list[str]
    market: dict[str, Any] | None
    sources: list[dict[str, Any]]
    sourceTexts: dict[str, str]
    sourceSections: dict[str, list[dict[str, Any]]]
    evidence: list[dict[str, Any]]
    result: dict[str, Any]
    answer: dict[str, Any]
    answerModel: str | None
    answerReasoning: str | None
    llmModel: str
    llmReasoning: str
    claimSnapshot: list[dict[str, Any]]
    diagnostics: list[dict[str, Any]]
    recoveryRequested: bool
    recoveryCount: int
    recoveryTrace: list[dict[str, Any]]
    excludedSourceUrls: list[str]


Stage = Callable[[FactCheckState], Awaitable[dict[str, Any]]]


def build_workflow(
    *,
    extract: Stage,
    search: Stage,
    read: Stage,
    verify: Stage,
    synthesize: Stage,
):
    """Compile five stages; a reviewed failure may return to search once."""
    builder = StateGraph(FactCheckState)
    stages = {
        "extracting": extract,
        "searching": search,
        "reading": read,
        "verifying": verify,
        "synthesizing": synthesize,
    }
    previous = START
    for name, handler in stages.items():
        builder.add_node(name, handler)
        if previous != "verifying":
            builder.add_edge(previous, name)
        previous = name
    builder.add_conditional_edges(
        "verifying",
        lambda state: "searching" if state.get("recoveryRequested") is True
        and state.get("recoveryCount") == 1 else "synthesizing",
        {"searching": "searching", "synthesizing": "synthesizing"},
    )
    builder.add_edge(previous, END)
    return builder.compile()
