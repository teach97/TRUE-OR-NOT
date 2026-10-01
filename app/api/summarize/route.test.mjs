import test from 'node:test';
import assert from 'node:assert/strict';
const make=(body,headers={})=>new Request('http://localhost:3000/api/summarize',{method:'POST',headers:{host:'localhost:3000',origin:'http://localhost:3000','content-type':'application/json',...headers},body:JSON.stringify(body)});
const input={text:'긴 원문이다.',focus:'',consent:true,modelPreference:'auto'};

test('summarize route rejects foreign requests before backend',async()=>{
 const {POST}=await import('./route.ts');
 const saved=globalThis.fetch;
 globalThis.fetch=async()=>{assert.fail('Rejected requests must not reach backend');};
 try {
  assert.equal((await POST(make(input,{origin:'https://evil.test'}))).status,403);
 }finally{globalThis.fetch=saved;}
});

test('summarize route forwards to the backend and returns the summary',async()=>{
 const {POST}=await import('./route.ts');
 const saved=globalThis.fetch;
 const result={title:'제목',summary:'요약문',points:['첫째'],sourceName:null,sourceUrl:null,warnings:[],model:'gpt-6-luna',reasoning:'max'};
 globalThis.fetch=async(url,init)=>{
  assert.equal(String(url),'http://127.0.0.1:8010/api/summarize');
  assert.deepEqual(JSON.parse(init.body),input);
  return Response.json({result});
 };
 try {
  const response=await POST(make(input));
  assert.equal(response.status,200);
  assert.deepEqual(await response.json(),{result});
  assert.equal(response.headers.get('cache-control'),'no-store');
 }finally{globalThis.fetch=saved;}
});

test('summarize route surfaces backend error codes',async()=>{
 const {POST}=await import('./route.ts');
 const saved=globalThis.fetch;
 globalThis.fetch=async()=>Response.json({code:'SOURCE_TOO_LONG',message:'긴 영상'}, {status:422});
 try {
  const response=await POST(make(input));
  assert.equal(response.status,422);
  assert.equal((await response.json()).code,'SOURCE_TOO_LONG');
 }finally{globalThis.fetch=saved;}
});
