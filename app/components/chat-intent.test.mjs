import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyChatInput, describeHistory, metaReply} from './chat-intent.ts';

test('routes meta questions away from verification', () => {
  const previous = {hasPrevious: true, hasAttachment: false};
  assert.deepEqual(classifyChatInput('너 지금 나랑 대화한 기록 볼수있어?', previous), {kind: 'meta', topic: 'history'});
  assert.deepEqual(classifyChatInput('방금 뭐 검증했어?', previous), {kind: 'meta', topic: 'history'});
  assert.deepEqual(classifyChatInput('안녕', previous), {kind: 'meta', topic: 'greeting'});
  assert.deepEqual(classifyChatInput('고마워', previous), {kind: 'meta', topic: 'thanks'});
  assert.deepEqual(classifyChatInput('너는 뭐야?', previous), {kind: 'meta', topic: 'identity'});
  assert.deepEqual(classifyChatInput('너 지금 나랑 대화한 기록 볼수있어?', {hasPrevious: false, hasAttachment: false}), {kind: 'meta', topic: 'history'});
});

test('routes short follow-ups to the previous verification', () => {
  const previous = {hasPrevious: true, hasAttachment: false};
  assert.deepEqual(classifyChatInput('그럼 검색해서 찾아', previous), {kind: 'followup'});
  assert.deepEqual(classifyChatInput('그것에 대해 더 자세히 알아봐줘', previous), {kind: 'followup'});
  assert.deepEqual(classifyChatInput('그럼 검색해서 찾아', {hasPrevious: false, hasAttachment: false}), {kind: 'verify'});
});

test('keeps substantive inputs and attachments on verification', () => {
  const previous = {hasPrevious: true, hasAttachment: false};
  assert.deepEqual(classifyChatInput('마크저커버그는 뱀파이어인가', previous), {kind: 'verify'});
  assert.deepEqual(classifyChatInput('이 기사가 사실인지 확인해줘: 경제가 성장했다', previous), {kind: 'verify'});
  assert.deepEqual(classifyChatInput('기억해? 이 문장이 맞는지 봐줘 ' + '가'.repeat(200), previous), {kind: 'verify'});
  assert.deepEqual(classifyChatInput('그거 맞아?', {hasPrevious: true, hasAttachment: true}), {kind: 'verify'});
  assert.deepEqual(classifyChatInput('', previous), {kind: 'verify'});
});

test('summarizes visible conversation history without providers', () => {
  assert.equal(describeHistory([], null), '아직 검증한 게 없어. 확인할 원문·링크·이미지를 보내면 시작할게.');
  const summary = describeHistory(
    [{role: 'assistant', text: 'welcome'}, {role: 'user', text: '마크저커버그는 뱀파이어인가'}],
    {claims: [{quote: '마크저커버그는 뱀파이어이다', verdict: '근거 부족', factScore: 50}]},
  );
  assert.ok(summary.includes('1번 검증 요청'));
  assert.ok(summary.includes('마크저커버그는 뱀파이어인가'));
  assert.ok(summary.includes('근거 부족(50점)'));
  assert.ok(metaReply('greeting').length > 0 && metaReply('identity').length > 0);
});
