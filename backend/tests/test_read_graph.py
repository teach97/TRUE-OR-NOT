"""Read-node integration preserves source text for later citation verification."""
import asyncio
from workflow import build_workflow
from sources import read_sources


def test_graph_keeps_source_texts_for_verification():
    async def extract(state): return {}
    async def search(state): return {'sources':[{'id':'s1','url':'https://example.org/'}]}
    async def reader(url): return 'Source body for citation.', url
    async def read(state): return await read_sources(state, reader=reader)
    async def verify(state):
        assert state.get('sourceTexts') == {'s1':'Source body for citation.'}
        return {'result':{'testOnly':True}}
    async def synthesize(state):
        assert state['sourceTexts'] == {'s1':'Source body for citation.'}
        return {}
    graph = build_workflow(
        extract=extract, search=search, read=read, verify=verify, synthesize=synthesize,
    )
    asyncio.run(graph.ainvoke({'text':'claim','focus':'','consent':True}))
