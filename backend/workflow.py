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
    claims: list[dict[str, Any]]
    searchQueries: dict[str, str]
    sources: list[dict[str, Any]]
    sourceTexts: dict[str, str]
    evidence: list[dict[str, Any]]
    result: dict[str, Any]
    answer: dict[str, Any]
    answerModel: str | None
    answerReasoning: str | None
    llmModel: str
    llmReasoning: str


Stage = Callable[[FactCheckState], Awaitable[dict[str, Any]]]


def build_workflow(
    *,
    extract: Stage,
    search: Stage,
    read: Stage,
    verify: Stage,
    synthesize: Stage,
):
    """Compile the five explicit stages with no implicit provider."""
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
        builder.add_edge(previous, name)
        previous = name
    builder.add_edge(previous, END)
    return builder.compile()
