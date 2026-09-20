import test from 'node:test';
import assert from 'node:assert/strict';
const make=(body,headers={})=>new Request('http://localhost:3000/api/fact-check',{method:'POST',headers:{origin:'http://localhost:3000','content-type':'application/json',...headers},body:JSON.stringify(body)});

test('route status reveals no secret; missing config 503 and invalid bodies 400',async()=>{
  const {GET,POST}=await import('../../api/fact-check/route.ts');
  const saved=process.env.OPENAI_API_KEY; delete process.env.OPENAI_API_KEY;
  try {
    const status=await GET(); assert.deepEqual(await status.json(),{configured:false,model:'gpt-5.6-luna',reasoning:'max',webSearch:true});
    assert.equal(status.headers.get('cache-control'),'no-store');
    assert.equal((await POST(make({text:'x',focus:'',consent:true}))).status,503);
    assert.equal((await POST(make({text:'x',focus:'',consent:false}))).status,400);
    assert.equal((await POST(make({text:'x',focus:'',consent:true},{origin:'https://evil.test'}))).status,403);
    assert.equal((await POST(make({text:'x',focus:'',consent:true},{'x-forwarded-for':'127.0.0.1'}))).status,403);
    process.env.OPENAI_API_KEY='secret-test-value';
    assert.equal((await (await GET()).json()).configured,true);
    assert.ok(!(await (await GET()).text()).includes('secret-test-value'));
  }finally{if(saved===undefined)delete process.env.OPENAI_API_KEY;else process.env.OPENAI_API_KEY=saved;}
});

test('NDJSON cancellation aborts in-flight provider request; errors contain no diagnostic secrets',async()=>{
  const {POST}=await import('../../api/fact-check/route.ts');
  const savedKey=process.env.OPENAI_API_KEY, savedFetch=globalThis.fetch;
  process.env.OPENAI_API_KEY='test-secret';
  let observed;
  let began;const started=new Promise(resolve=>{began=resolve;});
  globalThis.fetch=async(_url,init)=>{observed=init.signal;began();return await new Promise((_,reject)=>init.signal.addEventListener('abort',()=>reject(new Error('test-secret')),{once:true}));};
  try {
    const response=await POST(make({text:'claim',focus:'',consent:true}));
    assert.equal(response.headers.get('content-type'),'application/x-ndjson; charset=utf-8');
    const reader=response.body.getReader(); await reader.read();await started;await reader.cancel();
    assert.equal(observed.aborted,true);
    globalThis.fetch=async()=>{throw new Error('test-secret');};
    const failed=await POST(make({text:'claim',focus:'',consent:true}));
    const body=await failed.text(); assert.ok(!body.includes('test-secret'));
    assert.equal(JSON.parse(body.trim().split('\n').at(-1)).type,'error');
  }finally{globalThis.fetch=savedFetch;if(savedKey===undefined)delete process.env.OPENAI_API_KEY;else process.env.OPENAI_API_KEY=savedKey;}
});
