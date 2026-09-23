import test from 'node:test';
import assert from 'node:assert/strict';
import {sourceDiscoveryLabel} from './source-discovery.ts';

test('labels provider candidate order without claiming Google organic rank', () => {
  assert.equal(sourceDiscoveryLabel({searchProvider: 'openai_web_search', candidateOrder: 4}), 'GPT 웹검색 후보 4');
  assert.equal(sourceDiscoveryLabel({searchProvider: 'gemini_google_search', candidateOrder: 2}), 'Gemini 검색 후보 2');
  assert.equal(sourceDiscoveryLabel({searchProvider: 'openai_web_search', candidateOrder: 1, searchQuery: 'AGI 2030년'}), 'GPT 웹검색 후보 1 · 검색어 AGI 2030년');
  assert.equal(sourceDiscoveryLabel({}), '검색 후보');
});
