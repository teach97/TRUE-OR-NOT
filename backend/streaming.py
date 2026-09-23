"""NDJSON boundary: only stage labels and validated final results are public."""
import asyncio
from contextlib import aclosing
import json
from contracts import FactCheckResponse

STAGES = ('extracting', 'searching', 'reading', 'verifying', 'synthesizing')
MESSAGES = ('주장을 추출하고 있습니다.', '근거 출처를 검색하고 있습니다.', '출처 원문을 읽고 있습니다.', '인용과 판정을 검증하고 있습니다.', '확인된 원문 근거로 답변을 구성하고 있습니다.')


def encode(event):
    return json.dumps(event, ensure_ascii=False) + '\n'


async def stream_events(graph, payload, *, timeout=240):
    """Propagate cancellation and close the graph iterator on every exit path."""
    try:
        async with asyncio.timeout(timeout):
            yield encode({'type':'stage','stage':STAGES[0],'message':MESSAGES[0]})
            expected = 0
            async with aclosing(graph.astream(payload, stream_mode='updates')) as updates:
                async for update in updates:
                    for stage, values in update.items():
                        if expected >= len(STAGES) or stage != STAGES[expected]:
                            raise ValueError('Unexpected stage')
                        expected += 1
                        if stage == 'synthesizing':
                            response = FactCheckResponse.model_validate({'result':values.get('result')})
                            yield encode({'type':'result','result':response.result.model_dump(mode='json')})
                        else:
                            yield encode({'type':'stage','stage':STAGES[expected],'message':MESSAGES[expected]})
            if expected != len(STAGES):
                raise ValueError('Incomplete graph')
    except TimeoutError:
        yield encode({'type':'error','code':'TIMEOUT','message':'검증 시간이 초과되었습니다.'})
    except ValueError as exc:
        code = str(exc).split(':', 1)[0]
        if code == 'MODEL_FAILED':
            yield encode({'type':'error','code':'MODEL_FAILED','message':'선택한 모델이 응답하지 않았습니다. 다른 모델을 선택해 다시 시도해 주세요.'})
        elif code == 'MODEL_UNAVAILABLE':
            yield encode({'type':'error','code':'MODEL_UNAVAILABLE','message':'선택한 모델의 API 키가 설정되어 있지 않습니다.'})
        else:
            yield encode({'type':'error','code':'AGENT_FAILED','message':'검증을 완료하지 못했습니다.'})
    except Exception:
        yield encode({'type':'error','code':'AGENT_FAILED','message':'검증을 완료하지 못했습니다.'})
