import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

test('candidate cards show each source search route and rank, not just the source index', () => {
  const source = readFileSync(new URL('./fact-check-dashboard.tsx', import.meta.url), 'utf8');
  assert.match(source, /className="source-caption">\{sourceDiscoveryLabel\(source\)\}/);
});
