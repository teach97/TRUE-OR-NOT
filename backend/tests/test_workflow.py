"""Offline orchestration tests; fixtures are not real fact-check results."""
import asyncio
import importlib.util

import pytest


def test_updates_stream_uses_five_frontend_stage_names():
    from workflow import build_workflow

    async def stage(state):
        return {"sources": []}

    async def collect():
        graph = build_workflow(
            extract=stage, search=stage, read=stage, verify=stage, synthesize=stage,
        )
        return [list(update)[0] async for update in graph.astream(
            {"text": "Test claim"}, stream_mode="updates"
        )]

    assert asyncio.run(collect()) == [
        "extracting", "searching", "reading", "verifying", "synthesizing",
    ]


def test_provider_failure_stops_graph_without_fabricated_result():
    from workflow import build_workflow
    calls = []

    async def failing(state):
        raise RuntimeError("provider unavailable")

    async def subsequent(state):
        calls.append("unexpected")
        return {}

    graph = build_workflow(
        extract=failing, search=subsequent, read=subsequent, verify=subsequent,
        synthesize=subsequent,
    )
    with pytest.raises(RuntimeError, match="provider unavailable"):
        asyncio.run(graph.ainvoke({"text": "Test claim"}))
    assert calls == []


def test_workflow_runs_stages_in_order_and_passes_state():
    assert importlib.util.find_spec("workflow") is not None, "LangGraph workflow is not implemented"
    from workflow import build_workflow

    seen = []

    async def extract(state):
        seen.append("extracting")
        assert state["text"] == "Test claim"
        return {"claims": [{"id": "c1", "quote": state["text"]}]}

    async def search(state):
        seen.append("searching")
        assert state["claims"][0]["id"] == "c1"
        return {"sources": []}

    async def read(state):
        seen.append("reading")
        assert state["sources"] == []
        return {"evidence": []}

    async def verify(state):
        seen.append("verifying")
        assert state["evidence"] == []
        return {"result": {"verdictCode": "insufficient_evidence"}}

    async def synthesize(state):
        seen.append("synthesizing")
        assert state["result"]["verdictCode"] == "insufficient_evidence"
        return {"answer": {"status": "insufficient_evidence"}}

    graph = build_workflow(
        extract=extract, search=search, read=read, verify=verify, synthesize=synthesize,
    )
    result = asyncio.run(graph.ainvoke({"text": "Test claim", "focus": "", "consent": True}))
    assert seen == ["extracting", "searching", "reading", "verifying", "synthesizing"]
    assert result["result"] == {"verdictCode": "insufficient_evidence"}
    assert result["answer"] == {"status": "insufficient_evidence"}
