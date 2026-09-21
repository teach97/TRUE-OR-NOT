import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

test('dashboard renders official GlassSurface once without legacy measurement trees', () => {
  const source = readFileSync(new URL('./fact-check-dashboard.tsx', import.meta.url), 'utf8');
  assert.match(source, /import GlassSurface from '.\/react-bits\/GlassSurface'/);
  assert.doesNotMatch(source, /liquid-glass-react|createLiquidSizer|cloneElement|panel-sizer/);
});
