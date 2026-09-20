import test from 'node:test';
import assert from 'node:assert/strict';
import {readFactCheckStream} from './fact-check-client.ts';

const result = {text:'한글 원문',focus:'',demo:false,model:'gpt-5.6-luna',reasoning:'max',checkedAt:'2026-09-19',claims:[],sources:[],evidence:[],warnings:[]};
function response(text, width=1) {
  const bytes = new TextEncoder().encode(text);
  return new Response(new ReadableStream({start(c) {for(let i=0;i<bytes.length;i+=width)c.enqueue(bytes.slice(i,i+width));c.close();}}), {headers:{'content-type':'application/x-ndjson'}});
}
test('decodes fragmented UTF-8, CRLF and final unterminated result', async () => {
 const stages=[];
 const actual=await readFactCheckStream(response(JSON.stringify({type:'stage',stage:'reading',message:'읽는 중'})+'\r\n\n'+JSON.stringify({type:'result',result})), {onStage:event=>stages.push(event.message)});
 assert.deepEqual(actual,result); assert.deepEqual(stages,['읽는 중']);
});
test('surfaces structured HTTP and streamed errors; rejects malformed and incomplete streams', async () => {
 await assert.rejects(readFactCheckStream(new Response(JSON.stringify({code:'CONFIG_MISSING',message:'키 설정 필요'}),{status:503})), /키 설정 필요/);
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'error',code:'UPSTREAM',message:'모델 접근 실패'}))), /모델 접근 실패/);
 await assert.rejects(readFactCheckStream(response('{bad}')), /스트림/);
 await assert.rejects(readFactCheckStream(response('')), /완료/);
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:{}}))), /결과/);
 await assert.rejects(readFactCheckStream(new Response('html')), /형식/);
});
test('aborts a pending read, cancels reader and emits no stale stage', async () => {
 const controller=new AbortController();let cancelled=false;const events=[];
 const stream=new ReadableStream({cancel(){cancelled=true;}});
 const pending=readFactCheckStream(new Response(stream,{headers:{'content-type':'application/x-ndjson'}}), {signal:controller.signal,onStage:e=>events.push(e)});
 controller.abort();
 await assert.rejects(pending, {name:'AbortError'});
 assert.equal(cancelled,true);assert.deepEqual(events,[]);
});
