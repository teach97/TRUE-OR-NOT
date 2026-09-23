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
        assert [e['stage'] for e in events if e['type']=='stage'] == ['extracting','searching','reading','verifying']
        assert events[-1]['type'] == 'result'
        assert events[-1]['result']['demo'] is False
        assert 'sourceTexts' not in response.text
    finally:
        main.app.dependency_overrides.clear()
