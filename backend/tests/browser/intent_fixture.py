"""의도 분류 UI 회귀용 합성 서버입니다. 외부 공급자와 실제 DB를 호출하지 않습니다."""
from collections import Counter
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import json
import asyncio

app = FastAPI()
counts = Counter()
requests = []


@app.get('/qa/requests')
async def observed():
    return {'counts': dict(counts), 'requests': requests}


@app.get('/api/fact-check')
async def status():
    return {'configured': True, 'jevConfigured': False, 'webSearch': True,
            'model': 'gpt-6-luna', 'reasoning': 'max',
            'modelOptions': [{'id': id, 'configured': True} for id in
                            ['deepseek-v4.1-flash', 'gpt-6-luna', 'gemini-3.8-flash', 'gemini-3.7-flash']]}


@app.get('/api/conversations')
async def conversations():
    return {'items': [], 'nextCursor': None}


@app.get('/api/conversations/status')
async def storage_status():
    return {'configured': False, 'sessionAvailable': False}


@app.post('/api/intent')
async def intent(request: Request):
    body = await request.json()
    counts['intent'] += 1
    requests.append({'path': 'intent', 'text': body['text'], 'hasImage': bool(body.get('image')),
                     'linkUrl': body.get('linkUrl'), 'focus': body.get('focus'), 'context': body.get('context', {})})
    text = body['text']
    if text in {'분류 실패 재현', 'ㅎㅇ', '개새야'}:
        return JSONResponse({'code': 'AGENT_FAILED'}, status_code=502)
    if text == '분류 중단 재현':
        await asyncio.sleep(20)
    target = 'current'
    focus = ''
    if text.startswith('이거 봐줘'):
        action, reply = 'clarify', '내용 설명과 사실 검증 중 어떤 작업을 원하시나요?'
    elif text in {'검증해줘', '다시 검색해서 검증해줘'}:
        action, reply, target, focus = 'verify', '', 'previous', text
    elif text == '다시 봐줘':
        action, reply, target = 'clarify', '이전 자료의 설명과 검증 중 어떤 작업을 원하시나요?', 'previous'
    elif '사실인지' in text or '사실인지' in body.get('focus', ''):
        action, reply = 'verify', ''
    elif text == '왜 접근이 안되지?' or '왜 접근이' in text:
        action, reply, target = 'reply', '이전 출처를 읽지 못했습니다. 현재 기록만으로 차단이나 로그인 문제인지는 확인할 수 없습니다.', 'previous'
    elif body.get('image'):
        action, reply = 'reply', '이미지에는 Render의 구독 요금제 비교표가 있습니다.'
        target = 'previous' if body.get('context', {}).get('previousAttachment') else 'current'
    else:
        action, reply = 'reply', '검증 없이 질문에 답변했습니다.'
    linked = body.get('linkUrl') or body.get('context', {}).get('previousLinkUrl')
    if linked and '설명해줘' in text and action == 'reply':
        return {'action': action, 'target': 'current' if body.get('linkUrl') else 'previous', 'reply': reply, 'focus': focus, 'readLink': True}
    return {'action': action, 'target': target, 'reply': reply, 'focus': focus}


@app.post('/api/summarize')
async def summarize(request: Request):
    body = await request.json()
    counts['summary'] += 1
    requests.append({'path': 'summary', 'text': body['text'], 'linkUrl': body.get('linkUrl')})
    return {'result': {'title': '합성 링크 설명', 'summary': '이 페이지의 요금제 내용을 설명했습니다.',
                       'points': [], 'sourceUrl': body.get('linkUrl'), 'sourceName': '합성 링크',
                       'warnings': [], 'model': 'gpt-6-luna', 'reasoning': 'max'}}


@app.post('/api/fact-check/stream')
async def verify(request: Request):
    body = await request.json()
    counts['verify'] += 1
    requests.append({'path': 'verify', 'text': body['text'], 'focus': body['focus'],
                     'hasImage': bool(body.get('image')), 'linkUrl': body.get('linkUrl')})
    if '실패 재현' in body['text']:
        return JSONResponse({'code': 'AGENT_FAILED', 'message': '합성 검증 실패입니다.'}, status_code=502)
    result = {'text': body['text'], 'focus': body['focus'], 'demo': False,
              'checkedAt': datetime.now(timezone.utc).isoformat(), 'model': 'gpt-6-luna', 'reasoning': 'max',
              'claims': [], 'sources': [], 'evidence': [], 'warnings': ['합성 UI 시험 결과입니다.'],
              'answer': {'status': 'insufficient_evidence', 'overview': None, 'sections': [],
                         'conclusion': None, 'model': None, 'reasoning': None}}
    return StreamingResponse(iter([json.dumps({'type': 'result', 'result': result}, ensure_ascii=False)+'\n']),
                             media_type='application/x-ndjson')
