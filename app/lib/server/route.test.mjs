import test from 'node:test';
import assert from 'node:assert/strict';
const make=(body,headers={})=>new Request('http://localhost:3000/api/fact-check',{method:'POST',headers:{host:'localhost:3000',origin:'http://localhost:3000','content-type':'application/json',...headers},body:JSON.stringify(body)});
const input={text:'claim',focus:'',consent:true,modelPreference:'auto'};

test('same-origin loopback Host survives Next server URL reconstruction',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');
 const {NextRequest}=await import('next/server.js');
 for(const host of ['localhost:3000','127.0.0.1:3000','[::1]:3000']) {
  const request=new NextRequest(`http://${host}/api/fact-check`,{method:'POST',headers:{host,origin:`http://${host}`,'content-type':'application/json'},body:JSON.stringify({...input,consent:false})});
  assert.equal(new URL(request.url).hostname,'localhost');
  const response=await POST(request);
  assert.equal(response.status,400,host);
  assert.equal((await response.json()).code,'INVALID_REQUEST');
 }
});

test('local Host does not relax same-origin or hostile forwarding restrictions',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');
 const saved=globalThis.fetch;
 globalThis.fetch=async()=>assert.fail('Rejected requests must not reach backend');
 try {
  for(const headers of [
   {host:'127.0.0.1:3000'},
   {origin:'http://localhost:3001'},
   {origin:'https://localhost:3000'},
   {origin:'null'},
   {host:''},
   {host:'evil.test:3000',origin:'http://evil.test:3000'},
   {host:'localhost:3000@evil.test',origin:'http://localhost:3000@evil.test'},
   {host:'localhost:3000,127.0.0.1:3000'},
   {'x-forwarded-host':'evil.test'},
   {'x-forwarded-host':'127.0.0.1:3000'},
   {'x-forwarded-proto':'https'},
   {'x-forwarded-port':'3001'},
   {forwarded:'for=127.0.0.1'},
   {'sec-fetch-site':'cross-site'},
  ]) {
   const response=await POST(make({...input,consent:false},headers));
   assert.equal(response.status,403,JSON.stringify(headers));
   assert.equal((await response.json()).code,'LOCAL_ONLY');
  }
 }finally{globalThis.fetch=saved;}
});

test('production remains blocked for both local authorities',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');const saved=process.env.NODE_ENV;
 try {
  process.env.NODE_ENV='production';
  for(const host of ['localhost:3000','127.0.0.1:3000'])assert.equal((await POST(make({...input,consent:false},{host,origin:`http://${host}`}))).status,403);
 }finally{if(saved===undefined)delete process.env.NODE_ENV;else process.env.NODE_ENV=saved;}
});

test('status uses backend configuration and projects only safe fields',async()=>{
 const {GET}=await import('../../api/fact-check/route.ts');
 const saved=globalThis.fetch;
 const modelOptions=[{id:'gemini-3.8-flash',label:'Gemini 3.8 Flash',configured:true},{id:'gemini-3.7-flash',label:'Gemini 3.7 Flash',configured:true},{id:'gpt-6-luna',label:'GPT-6 Luna Max',configured:false}];
 globalThis.fetch=async(url)=>{assert.equal(String(url),'http://127.0.0.1:8010/api/fact-check');return Response.json({configured:true,workflowReady:true,model:'gemini-3.8-flash',reasoning:'high',webSearch:true,modelOptions,private:'SECRET'});};
 try { const r=await GET();const body=await r.json();assert.equal(body.configured,true);assert.deepEqual(body.modelOptions,modelOptions);assert.equal(body.private,undefined);assert.equal(r.headers.get('cache-control'),'no-store'); }
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

test('POST forwards the explicit model preference to the backend',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');const saved=globalThis.fetch;
 const selected={...input,modelPreference:'gpt-6-luna'};let forwarded;
 globalThis.fetch=async(_url,init)=>{forwarded=JSON.parse(init.body);return new Response('{"type":"stage","stage":"extracting","message":"test"}\n',{headers:{'Content-Type':'application/x-ndjson'}});};
 try { const response=await POST(make(selected));assert.equal(response.status,200);assert.equal((await response.text()).includes('stage'),true);assert.deepEqual(forwarded,selected); }
 finally{globalThis.fetch=saved;}
});

test('request abort releases an idle proxy stream',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');const saved=globalThis.fetch;
 globalThis.fetch=async()=>new Response(new ReadableStream({start(c){c.enqueue(new Uint8Array([10]));}}),{headers:{'Content-Type':'application/x-ndjson'}});
 const controller=new AbortController();
 try {
  const request=new Request('http://localhost:3000/api/fact-check',{method:'POST',headers:{host:'localhost:3000',origin:'http://localhost:3000','content-type':'application/json'},body:JSON.stringify(input),signal:controller.signal});
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
 for(const address of ['192.168.1.2','127.0.0.1, 1.2.3.4','unknown','']) {
  assert.equal((await POST(make(input,{'x-forwarded-for':address}))).status,403);
 }
});

test('Next injected single loopback addresses allow local requests',async()=>{
 const {POST}=await import('../../api/fact-check/route.ts');const saved=globalThis.fetch;
 globalThis.fetch=async()=>new Response('{"type":"stage"}\n',{headers:{'Content-Type':'application/x-ndjson'}});
 try {
  for(const address of ['127.0.0.1','::1','::ffff:127.0.0.1']) {
   const response=await POST(make(input,{'x-forwarded-for':address}));
   assert.equal(response.status,200);await response.text();
  }
 } finally {globalThis.fetch=saved;}
});
