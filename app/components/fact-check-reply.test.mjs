import test from 'node:test';
import assert from 'node:assert/strict';
import {composeAssistantReply, resolveAnswerCitationSource} from './fact-check-reply.ts';

const source = {id:'s1',url:'https://example.com/article',title:'AGI 전망',publisher:'예시 연구소',accessStatus:'verified',sourceType:'웹'};
const answer = {
  status:'grounded',
  overview:{text:'AGI 전망은 아직 불확실합니다.',citations:[{sourceId:'s1',quote:'시점은 여러 요인에 따라 달라집니다.'}]},
  sections:[{kind:'uncertainty',title:'남은 불확실성',items:[{text:'AGI 정의와 평가 기준이 다릅니다.',citations:[{sourceId:'s1',quote:'평가 기준의 합의가 부족합니다.'}]}]}],
  conclusion:{text:'2030년 이전 도래를 확정할 수 없습니다.',citations:[{sourceId:'s1',quote:'시점은 여러 요인에 따라 달라집니다.'}]},
  model:'gemini-3.8-flash',reasoning:'high',
};

test('chat reply preserves the structured grounded answer and source mapping', () => {
  const reply = composeAssistantReply({
    answer,
    claims: [{
      kind: 'unclear',
      summary: '이 검증 문장은 새 AI 개요에 섞이지 않아야 해.',
      verdict: '근거 부족',
      verdictCode: 'insufficient_evidence',
      factScore: 50,
      confirmed: [],
      unresolved: ['AGI의 판정 기준과 독립적인 평가가 더 필요합니다.'],
      evidenceIds: [],
    }],
    sources: [source, {}, {}],
    evidence: [{}, {}],
    warnings: [],
  });

  assert.equal(reply.answer.overview.text, 'AGI 전망은 아직 불확실합니다.');
  assert.equal(reply.answer.sections[0].title, '남은 불확실성');
  assert.equal(reply.answer.conclusion.text, '2030년 이전 도래를 확정할 수 없습니다.');
  assert.equal(reply.sources[0].id, 's1');
  assert.equal(reply.meta, '3개 출처 · 2개 인용');
});

test('insufficient evidence does not fall back to a claim summary', () => {
  const reply = composeAssistantReply({
    answer:{status:'insufficient_evidence',overview:null,sections:[],conclusion:null,model:null,reasoning:null},
    claims:[{summary:'이 요약을 AI 답변처럼 보이면 안 돼.'}],
    sources:[],evidence:[],
  });
  assert.equal(reply.answer.status,'insufficient_evidence');
  assert.equal(reply.answer.overview,null);
  assert.equal(reply.text,undefined);
});

test('citation resolution never links missing, unverified, YouTube or unsafe sources', () => {
  const citation={sourceId:'s1',quote:'원문 인용'};
  assert.deepEqual(resolveAnswerCitationSource(citation,[source]),{source,href:'https://example.com/article'});
  assert.equal(resolveAnswerCitationSource(citation,[]),null);
  assert.equal(resolveAnswerCitationSource(citation,[{...source,accessStatus:'unavailable'}]),null);
  assert.equal(resolveAnswerCitationSource(citation,[{...source,sourceType:'유튜브'}]),null);
  assert.equal(resolveAnswerCitationSource(citation,[{...source,url:'javascript:alert(1)'}]),null);
});
