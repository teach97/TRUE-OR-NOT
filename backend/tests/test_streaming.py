"""Offline streaming tests; fixtures do not represent real verification."""
import asyncio
import importlib.util
import json
from fastapi.testclient import TestClient
import main
import pytest


@pytest.mark.parametrize('mode', ['failure','timeout','missing'])
def test_stream_errors_are_safe(mode):
    from streaming import stream_events
    class Broken:
        async def astream(self, *args, **kwargs):
            if mode == 'failure': raise RuntimeError('PRIVATE_DIAGNOSTIC')
            if mode == 'timeout': await asyncio.sleep(1)
            if False: yield {}
    async def run():
        return [json.loads(line) async for line in stream_events(Broken(), {}, timeout=0.01)]
    events = asyncio.run(run())
    assert events[-1]['type'] == 'error'
    assert events[-1]['code'] == ('TIMEOUT' if mode == 'timeout' else 'AGENT_FAILED')
    assert 'PRIVATE_DIAGNOSTIC' not in str(events)
    assert not any(e['type']=='result' for e in events)


def test_stream_explains_that_a_pinned_model_failed_without_exposing_provider_details():
    from streaming import stream_events

    class PinnedModelFailure:
        async def astream(self, *args, **kwargs):
            raise ValueError('MODEL_FAILED: PRIVATE_PROVIDER_DIAGNOSTIC')
            yield {}

    async def run():
        return [json.loads(line) async for line in stream_events(PinnedModelFailure(), {})]

    events = asyncio.run(run())
    assert events[-1] == {
        'type': 'error',
        'code': 'MODEL_FAILED',
        'message': '선택한 모델이 응답하지 않았습니다. 다른 모델을 선택해 다시 시도해 주세요.',
    }


def test_task_cancellation_reaches_graph_cleanup():
    from streaming import stream_events
    closed = []
    async def run():
        entered = asyncio.Event()
        class Waiting:
            async def astream(self, *args, **kwargs):
                try:
                    entered.set()
                    await asyncio.sleep(60)
                    yield {}
                finally: closed.append(True)
        async def consume():
            async for _ in stream_events(Waiting(), {}): pass
        task = asyncio.create_task(consume())
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError): await task
    asyncio.run(run())
    assert closed == [True]

from runtime import RuntimeAdapters, Settings, build_runtime_workflow
from pydantic import SecretStr


def graph():
    async def noop(state): return {}
    async def verify(state): return {'claims':[], 'evidence':[]}
    async def synthesize(state):
        return {
            'answer': {'status':'insufficient_evidence','overview':None,'sections':[],
                       'conclusion':None,'model':None,'reasoning':None},
            'answerModel':None,'answerReasoning':None,
        }
    return build_runtime_workflow(
        Settings(api_key=SecretStr('test-only')),
        adapters=RuntimeAdapters(
            extract=noop,search=noop,read=noop,verify=verify,synthesize=synthesize,
        ),
    )


def test_stream_endpoint_emits_ordered_stages_and_valid_result():
    main.app.dependency_overrides[main.get_workflow] = graph
    try:
        with TestClient(main.app) as client:
            response = client.post('/api/fact-check/stream',json={'text':'claim','focus':'','consent':True})
        assert response.status_code == 200
        assert response.headers['content-type'].startswith('application/x-ndjson')
        events = [json.loads(line) for line in response.text.splitlines()]
        assert [e['stage'] for e in events if e['type']=='stage'] == ['extracting','searching','reading','verifying','synthesizing']
        assert [e['type'] for e in events] == ['stage'] * 4 + ['preview','stage','result']
        assert events[-1]['type'] == 'result'
        assert events[-1]['result']['demo'] is False
        assert events[-1]['result']['answer']['status'] == 'insufficient_evidence'
        assert 'sourceTexts' not in response.text
    finally:
        main.app.dependency_overrides.clear()


def test_stream_emits_candidate_sources_and_grounded_preview_before_final_result():
    from streaming import stream_events
    from runtime import build_fact_check_result

    quote = "The verified source supports this statement."
    extracted_claim = {"id": "c1", "quote": "Claim", "start": 0, "end": 5, "kind": "fact"}
    candidate_source = {
        "id": "s1", "url": "https://example.org/source", "title": "Example source",
        "publisher": "Example publisher", "publishedAt": None, "accessStatus": "pending",
        "sourceType": "기사", "originGroupId": None,
    }
    verified_source = {
        **candidate_source, "accessStatus": "verified",
        "retrievedAt": "2026-09-24T00:00:00+00:00",
    }
    verified_claim = {
        **extracted_claim, "verdictCode": "mostly_supported", "verdict": "대체로 확인됨",
        "tone": "positive", "summary": "확인된 원문은 주장을 뒷받침합니다.",
        "confirmed": ["원문이 주장을 뒷받침합니다."], "unresolved": [], "warnings": [],
        "evidenceIds": ["e1"],
    }
    evidence = {
        "id": "e1", "claimId": "c1", "sourceId": "s1", "quote": quote,
        "quoteVerified": True, "relation": "supports",
    }
    verified_state = {
        "text": "Claim", "focus": "", "consent": True,
        "claims": [verified_claim], "sources": [verified_source],
        "sourceTexts": {"s1": f"PRIVATE_FULL_SOURCE_BODY: {quote}"},
        "evidence": [evidence], "llmModel": "gpt-6-luna", "llmReasoning": "max",
    }
    citation = {"sourceId": "s1", "quote": quote}
    final_result = build_fact_check_result(verified_state, {
        "answer": {
            "status": "grounded",
            "overview": {"text": "최종 답변입니다.", "citations": [citation]},
            "sections": [],
            "conclusion": {"text": "최종 결론입니다.", "citations": [citation]},
            "model": "gemini-3.8-flash", "reasoning": "high",
        },
        "answerModel": "gemini-3.8-flash", "answerReasoning": "high",
    }).model_dump(mode="json")

    steps = [
        ("extracting", {"claims": [extracted_claim]}),
        ("searching", {"sources": [candidate_source]}),
        ("reading", {"sources": [verified_source], "sourceTexts": verified_state["sourceTexts"]}),
        ("verifying", {
            "claims": [verified_claim], "evidence": [evidence],
            "llmModel": "gpt-6-luna", "llmReasoning": "max",
        }),
        ("synthesizing", {"result": final_result}),
    ]

    class StagedGraph:
        async def astream(self, payload, *, stream_mode):
            assert stream_mode == "updates"
            state = dict(payload)
            for stage, update in steps:
                state.update(update)
                yield {stage: update}

    async def collect():
        return [json.loads(line) async for line in stream_events(
            StagedGraph(), {"text": "Claim", "focus": "", "consent": True},
        )]

    events = asyncio.run(collect())
    types = [event["type"] for event in events]
    assert types == [
        "stage", "stage", "sources", "stage", "sources", "stage",
        "preview", "stage", "result",
    ]
    source_events = [event for event in events if event["type"] == "sources"]
    assert source_events[0]["phase"] == "found"
    assert source_events[0]["sources"][0]["accessStatus"] == "candidate"
    assert source_events[1]["phase"] == "read"
    assert source_events[1]["sources"][0]["accessStatus"] == "verified"
    preview = next(event for event in events if event["type"] == "preview")
    assert preview["claims"][0]["summary"] == "확인된 원문은 주장을 뒷받침합니다."
    assert preview["claims"][0]["citations"] == [citation]
    assert events[-1]["type"] == "result"
    assert "PRIVATE_FULL_SOURCE_BODY" not in json.dumps(events, ensure_ascii=False)
    assert "sourceTexts" not in json.dumps(events, ensure_ascii=False)
