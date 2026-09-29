import test from 'node:test';
import assert from 'node:assert/strict';
const make=(body,headers={})=>new Request('http://localhost:3000/api/fact-check/jev',{method:'POST',headers:{host:'localhost:3000',origin:'http://localhost:3000','content-type':'application/json',...headers},body:JSON.stringify(body)});
const input={text:'claim',focus:'',consent:true,modelPreference:'auto',jevMode:true};

test('jev route rejects non-jev, image and foreign requests before backend',async()=>{
 const {POST}=await import('./route.ts');
 const saved=globalThis.fetch;
 globalThis.fetch=async()=>{assert.fail('Rejected requests must not reach backend');};
 try {
  assert.equal((await POST(make({text:'hi',focus:'',consent:true}))).status,400);
  assert.equal((await POST(make({...input,image:{mime:'image/jpeg',data:'eA=='}}))).status,400);
  assert.equal((await POST(make(input,{origin:'https://evil.test'}))).status,403);
 }finally{globalThis.fetch=saved;}
});

test('jev route forwards to the backend fast endpoint and returns JSON',async()=>{
 const {POST}=await import('./route.ts');
 const saved=globalThis.fetch;
 const result={model:'typesafe-ai/jev',claims:[]};
 globalThis.fetch=async(url,init)=>{
  assert.equal(String(url),'http://127.0.0.1:8010/api/fact-check/jev');
  assert.deepEqual(JSON.parse(init.body),input);
  return Response.json(result);
 };
 try {
  const response=await POST(make(input));
  assert.equal(response.status,200);
  assert.deepEqual(await response.json(),result);
  assert.equal(response.headers.get('cache-control'),'no-store');
 }finally{globalThis.fetch=saved;}
});
