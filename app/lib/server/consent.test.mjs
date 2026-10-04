import test from 'node:test';
import assert from 'node:assert/strict';

const routes = [
  ['intent', '../../api/intent/route.ts', {text: '안녕하세요', context: {}, modelPreference: 'auto'}],
  ['summarize', '../../api/summarize/route.ts', {text: '요약할 원문', focus: '', modelPreference: 'auto'}],
  ['fact-check', '../../api/fact-check/route.ts', {text: '검증할 원문', focus: '', modelPreference: 'auto'}],
  ['fact-check/jev', '../../api/fact-check/jev/route.ts', {text: '검증할 원문', focus: '', modelPreference: 'auto', jevMode: true}],
];
const request = (path, body) => new Request(`http://localhost:3000/api/${path}`, {
  method: 'POST', headers: {host: 'localhost:3000', origin: 'http://localhost:3000', 'content-type': 'application/json'}, body: JSON.stringify(body),
});

for (const [path, module, input] of routes) {
  for (const consent of [undefined, false, 'true', 1, null]) {
    test(`${path} blocks ${JSON.stringify(consent)} consent before contacting the backend`, async () => {
      const {POST} = await import(module);
      const saved = globalThis.fetch;
      let calls = 0;
      globalThis.fetch = async () => { calls++; return Response.json({}); };
      try {
        const response = await POST(request(path, {...input, ...(consent === undefined ? {} : {consent})}));
        assert.equal(response.status, 400);
        assert.equal(calls, 0);
      } finally { globalThis.fetch = saved; }
    });
  }
}

test('intent forwards explicit true consent and selected model on repeated requests', async () => {
  const {POST} = await import('../../api/intent/route.ts');
  const saved = globalThis.fetch;
  const bodies = [];
  globalThis.fetch = async (url, init) => {
    assert.equal(String(url), 'http://127.0.0.1:8010/api/intent');
    bodies.push(JSON.parse(init.body));
    return Response.json({action: 'reply', reply: '안녕하세요', focus: null});
  };
  try {
    const input = {text: '안녕하세요', context: {}, consent: true, modelPreference: 'gpt-6-luna'};
    for (let index = 0; index < 2; index++) {
      const response = await POST(request('intent', input));
      assert.equal(response.status, 200);
      assert.equal((await response.json()).reply, '안녕하세요');
    }
    assert.deepEqual(bodies, [input, input]);
  } finally { globalThis.fetch = saved; }
});
