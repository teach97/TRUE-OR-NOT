import test from 'node:test';
import assert from 'node:assert/strict';
const make=(body,headers={})=>new Request('http://localhost:3000/api/fact-check',{method:'POST',headers:{origin:'http://localhost:3000','content-type':'application/json',...headers},body:JSON.stringify(body)});
const input={text:'claim',focus:'',consent:true};

test('status uses backend configuration and projects only safe fields',async()=>{
 const {GET}=await import('../../api/fact-check/route.ts');
 const saved=globalThis.fetch;
 globalThis.fetch=async(url)=>{assert.equal(String(url),'http://127.0.0.1:8010/api/fact-check');return Response.json({configured:true,workflowReady:true,model:'gpt-5.6-luna',reasoning:'max',webSearch:true,private:'SECRET'});};
 try { const r=await GET();const body=await r.json();assert.equal(body.configured,true);assert.equal(body.private,undefined);assert.equal(r.headers.get('cache-control'),'no-store'); }
 finally{globalThis.fetch=saved;}
});

test('POST forwards NDJSON without credentials; cancellation releases concurrency',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');
 const saved=globalThis.fetch;let observed;let cancelled=false;
 globalThis.fetch=async(url,init)=>{
  assert.equal(String(url),'http://127.0.0.1:8010/api/fact-check/stream');
  assert.equal(new Headers(init.headers).has('authorization'),false);
  assert.deepEqual(JSON.parse(init.body),input);observed=init.signal;
  return new Response(new ReadableStream({start(c){c.enqueue(new TextEncoder().encode('{"type":"stage","stage":"extracting","message":"test"}\n'));},cancel(){cancelled=true;}}),{headers:{'Content-Type':'application/x-ndjson'}});
 };
 try {
  const r=await POST(make(input));assert.equal(r.status,200);
  assert.equal((await POST(make(input))).status,429);
  const reader=r.body.getReader();assert.equal((await reader.read()).done,false);await reader.cancel();
  assert.equal(observed.aborted,true);assert.equal(cancelled,true);
  globalThis.fetch=async()=>{throw new Error('SECRET');};
  const failed=await POST(make(input));assert.equal(failed.status,503);assert.ok(!(await failed.text()).includes('SECRET'));
 }finally{globalThis.fetch=saved;}
});

test('request abort releases an idle proxy stream',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');const saved=globalThis.fetch;
 globalThis.fetch=async()=>new Response(new ReadableStream({start(c){c.enqueue(new Uint8Array([10]));}}),{headers:{'Content-Type':'application/x-ndjson'}});
 const controller=new AbortController();
 try {
  const request=new Request('http://localhost:3000/api/fact-check',{method:'POST',headers:{origin:'http://localhost:3000','content-type':'application/json'},body:JSON.stringify(input),signal:controller.signal});
  const response=await POST(request);controller.abort();
  globalThis.fetch=async()=>{throw new Error('unavailable');};
  assert.equal((await POST(make(input))).status,503);
  await response.body.cancel();
 }finally{globalThis.fetch=saved;}
});

test('upstream errors are sanitized and external backend URLs rejected',async()=>{
 const {GET,POST}=await import('../../api/fact-check/route.ts');const saved=globalThis.fetch,savedUrl=process.env.FACTLENS_BACKEND_URL;
 try {
  globalThis.fetch=async()=>new Response('PRIVATE_DIAGNOSTIC',{status:503});
  const failed=await POST(make(input));assert.equal(failed.status,503);assert.ok(!(await failed.text()).includes('PRIVATE_DIAGNOSTIC'));
  process.env.FACTLENS_BACKEND_URL='https://remote.example';
  globalThis.fetch=async()=>{assert.fail('Remote backend must not be requested');};
  assert.equal((await GET()).status,503);
 }finally{globalThis.fetch=saved;if(savedUrl===undefined)delete process.env.FACTLENS_BACKEND_URL;else process.env.FACTLENS_BACKEND_URL=savedUrl;}
});

test('invalid bodies and foreign origins never reach backend',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');
 assert.equal((await POST(make({...input,consent:false}))).status,400);
 assert.equal((await POST(make(input,{origin:'https://evil.test'}))).status,403);
 assert.equal((await POST(make(input,{'x-forwarded-for':'127.0.0.1'}))).status,403);
});
