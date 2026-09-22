import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeFactScore, scoreBand, scoreLabel} from '../lib/fact-score.ts';

test('score labels use the five public fact bands', () => {
  assert.deepEqual(
    [0, 19, 20, 39, 40, 59, 60, 79, 80, 100].map(score => [scoreBand(score), scoreLabel(score)]),
    [
      ['false', '거짓'],
      ['false', '거짓'],
      ['mostly_false', '대체적으로 거짓'],
      ['mostly_false', '대체적으로 거짓'],
      ['neutral', '중립(검증되지 않음)'],
      ['neutral', '중립(검증되지 않음)'],
      ['mostly_true', '대체적으로 사실'],
      ['mostly_true', '대체적으로 사실'],
      ['verified', '검증된 사실'],
      ['verified', '검증된 사실'],
    ],
  );
});

test('client normalization mirrors evidence-grounded verdict limits', () => {
  assert.equal(normalizeFactScore('mostly_supported', 70), 80);
  assert.equal(normalizeFactScore('partially_supported', 95), 79);
  assert.equal(normalizeFactScore('contradicted', 50), 39);
  assert.equal(normalizeFactScore('missing_context', 95), 50);
});
