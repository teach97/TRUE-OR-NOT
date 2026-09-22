import test from 'node:test';
import assert from 'node:assert/strict';
import {composeAssistantReply} from './fact-check-reply.ts';

test('chat reply keeps the grounded summary and gives a useful verdict', () => {
  const reply = composeAssistantReply({
    claims: [{
      kind: 'unclear',
      summary: '아직까지 AGI라고 단정할 근거는 부족하다는 의견이 다수야.',
      verdict: '근거 부족',
      verdictCode: 'insufficient_evidence',
      factScore: 50,
      confirmed: [],
      unresolved: ['AGI의 판정 기준과 독립적인 평가가 더 필요합니다.'],
      evidenceIds: [],
    }],
    sources: [{}, {}, {}],
    evidence: [{}, {}],
    warnings: [],
  });

  assert.match(reply.text, /아직까지 AGI라고 단정할 근거는 부족하다는 의견이 다수야/);
  assert.match(reply.text, /근거 부족/);
  assert.match(reply.text, /3개 출처/);
  assert.match(reply.text, /직접 인용 2개/);
  assert.equal(reply.meta, '3개 출처 · 2개 인용');
});
