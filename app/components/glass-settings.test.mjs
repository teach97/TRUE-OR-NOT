import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';

test('dashboard uses plain panels without the liquid GlassSurface component', () => {
  const source = readFileSync(new URL('./fact-check-dashboard.tsx', import.meta.url), 'utf8');
  assert.doesNotMatch(source, /GlassSurface|glass-surface|liquid-glass-react|glassLab|glassSettings/);
  assert.equal(existsSync(new URL('./react-bits/GlassSurface.tsx', import.meta.url)), false);
  assert.equal(existsSync(new URL('./react-bits/GlassSurface.css', import.meta.url)), false);
});
