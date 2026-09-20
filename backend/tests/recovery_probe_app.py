"""TEST ONLY deterministic recovery app. Never imported by runtime/main."""
from pydantic import SecretStr
import main
from runtime import Settings
from workflow import build_workflow
from contracts import FactCheckResult

mode = 'failure'
attempts = []

async def extract(state):
    attempts.append(mode)
    if mode == 'failure':
        raise RuntimeError('TEST_ONLY_PRIVATE_DIAGNOSTIC')
    return {}

async def noop(state):
    return {}

async def verify(state):
    quotes = state['text'].split(' | ')
    claims = []
    cursor = 0
    for i, quote in enumerate(quotes):
        claims.append(dict(id=f'c{i}', quote=quote, start=cursor, end=cursor+len(quote), kind='fact',
            verdictCode='insufficient_evidence', verdict='테스트 전용 근거 부족', tone='neutral',
            summary=f'TEST ONLY summary {i}', confirmed=[f'TEST ONLY confirmed {i}'],
            unresolved=[f'TEST ONLY uncertainty {i}'], warnings=[f'TEST ONLY warning {i}'],
            evidenceIds=['e0'] if i == 0 else []))
        cursor += len(quote)+3
    result = FactCheckResult.model_validate(dict(text=state['text'],focus=state['focus'],demo=False,
        model='TEST ONLY deterministic fixture',reasoning='max',checkedAt='2026-09-21T00:00:00Z',claims=claims,
        sources=[dict(id='s0',url='https://example.org/test-only-source',title='TEST ONLY source',publisher='example.org',
            publishedAt=None,retrievedAt='2026-09-21T00:00:00Z',accessStatus='verified',sourceType='TEST ONLY',originGroupId=None)],
        evidence=[dict(id='e0',claimId='c0',sourceId='s0',quote='TEST ONLY evidence quotation, not a factual finding.',
            quoteVerified=True,relation='context')],warnings=['TEST ONLY synthetic fixture; no provider or source was called.']))
    return {'result': result.model_dump(mode='json')}

graph = build_workflow(extract=extract,search=noop,read=noop,verify=verify)
main.app.dependency_overrides[main.get_workflow] = lambda: graph
main.load_settings = lambda: Settings(api_key=SecretStr('TEST-ONLY-NOT-A-KEY'))
def forbidden(*args, **kwargs):
    raise AssertionError('Paid provider forbidden in test probe')
main.build_runtime_workflow = forbidden
app = main.app

@app.get('/__test__/recovery')
async def status():
    return dict(testOnly=True,mode=mode,attempts=attempts)

@app.post('/__test__/recover')
async def recover():
    global mode
    mode = 'success'
    return await status()
