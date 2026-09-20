import test from 'node:test';
import assert from 'node:assert/strict';
import { createPreview, transition, initialState } from './demo-state.ts';

test('submitted snapshot remains independent from subsequent draft edits', () => {
  const draft = { text: '달빛시 축제가 열립니다. 입장은 무료입니다.', focus: '입장' };
  const snapshot = createPreview(draft);
  draft.text = '변경한 원문';
  draft.focus = '일정';
  assert.equal(snapshot.text, '달빛시 축제가 열립니다. 입장은 무료입니다.');
  assert.equal(snapshot.focus, '입장');
  assert.ok(Object.isFrozen(snapshot));
  assert.ok(Object.isFrozen(snapshot.claims));
});

test('custom text produces at most three exact sentence candidates, never evidence or verdicts', () => {
  const text = '첫 문장입니다. 둘째 문장입니다! 셋째 🙂 문장입니다. 넷째 문장입니다.';
  const preview = createPreview({text, focus: ''});
  assert.equal(preview.claims.length, 3);
  for (const claim of preview.claims) {
    assert.equal(text.slice(claim.start, claim.end), claim.quote);
    assert.equal(claim.verdict, null);
    assert.deepEqual(claim.evidenceIds, []);
  }
  assert.equal(preview.demo, false);
});

test('selection resolves from the same snapshot and invalid IDs are ignored', () => {
  const snapshot = createPreview({text: '첫 문장. 둘째 문장.', focus: ''});
  const loaded = transition(initialState, {type: 'load', snapshot});
  const selected = transition(loaded, {type: 'select', id: 'claim-2'});
  assert.equal(selected.selectedId, snapshot.claims[1].id);
  assert.equal(selected.snapshot, snapshot);
  assert.equal(transition(selected, {type: 'select', id: 'missing'}), selected);
});

test('cancel rejects late completion; subsequent run accepts only its own token', () => {
  const running = transition(initialState, {type: 'start'});
  assert.equal(running.status, 'loading');
  const cancelled = transition(running, {type: 'cancel'});
  assert.equal(cancelled.status, 'cancelled');
  const snapshot = createPreview({text: '후보입니다.', focus: ''});
  assert.equal(transition(cancelled, {type: 'complete', token: running.token, snapshot}), cancelled);
  const next = transition(cancelled, {type: 'start'});
  assert.equal(transition(next, {type: 'complete', token: running.token, snapshot}), next);
  assert.equal(transition(next, {type: 'complete', token: next.token, snapshot}).snapshot, snapshot);
  assert.equal(transition(next, {type: 'reset'}).snapshot, null);
});
