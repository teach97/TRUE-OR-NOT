"""Explicit integration-test entry point ONLY; never imported by main/runtime.

No provider calls or verdicts: a real LangGraph node blocks until cancellation.
Run only through scripts/probe-cancellation.py (loopback, disposable process).
"""
import asyncio
import time
from pydantic import SecretStr
import main
from runtime import Settings
from workflow import build_workflow

counts = dict(started=0, finalized=0, adapter_started=0, adapter_finalized=0,
              adapter_cancelled=0, active=0, max_active=0)
events = []


def record(event):
    events.append(dict(event=event, monotonic=time.monotonic(), **counts))


async def blocking_extract(state):
    counts['adapter_started'] += 1
    record('adapter_started')
    try:
        await asyncio.Event().wait()
        raise AssertionError('The test adapter must never produce a verdict')
    except asyncio.CancelledError:
        counts['adapter_cancelled'] += 1
        record('adapter_cancelled')
        raise
    finally:
        counts['adapter_finalized'] += 1
        record('adapter_finalized')


async def unreachable(state):
    raise AssertionError('Downstream adapters must not run in cancellation probe')


graph = build_workflow(extract=blocking_extract, search=unreachable,
                       read=unreachable, verify=unreachable,
                       synthesize=unreachable)


class InstrumentedGraph:
    async def astream(self, *args, **kwargs):
        counts['started'] += 1
        counts['active'] += 1
        counts['max_active'] = max(counts['max_active'], counts['active'])
        record('graph_started')
        iterator = graph.astream(*args, **kwargs)
        try:
            async for update in iterator:
                yield update
        finally:
            await iterator.aclose()
            counts['finalized'] += 1
            counts['active'] -= 1
            record('graph_finalized')


# Both changes live only in this disposable test process. No .env is read.
main.app.dependency_overrides[main.get_workflow] = lambda: InstrumentedGraph()
main.load_settings = lambda: Settings(api_key=SecretStr('TEST-ONLY-NOT-A-KEY'))


def forbid_provider(*args, **kwargs):
    raise AssertionError('Provider workflow is forbidden in cancellation probe')


main.build_runtime_workflow = forbid_provider
app = main.app


@app.get('/__test__/cancellation')
async def cancellation_state():
    return dict(testOnly=True, counts=counts.copy(), events=list(events))
