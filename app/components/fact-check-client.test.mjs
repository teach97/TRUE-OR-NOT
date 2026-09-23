import test from 'node:test';
import assert from 'node:assert/strict';
import {readFactCheckStream} from './fact-check-client.ts';

const insufficientAnswer = {status:'insufficient_evidence',overview:null,sections:[],conclusion:null,model:null,reasoning:null};
const result = {text:'한글 원문',focus:'',demo:false,model:'gpt-6-luna',reasoning:'max',checkedAt:'2026-09-19',claims:[],sources:[],evidence:[],warnings:[],answer:insufficientAnswer};
const verifiedSource = {id:'s1',url:'https://example.com/article',title:'원문 제목',publisher:'example.com',publishedAt:null,retrievedAt:'2026-09-23',accessStatus:'verified',sourceType:'웹',originGroupId:null,youtubeTitle:null,youtubeComments:[],youtubeDataStatus:'not_applicable'};
const groundedResult = (source=verifiedSource) => ({...result,sources:[source],answer:{status:'grounded',overview:{text:'확인된 개요',citations:[{sourceId:'s1',quote:'원문에 실제로 있는 인용'}]},sections:[],conclusion:{text:'확인된 결론',citations:[{sourceId:'s1',quote:'원문에 실제로 있는 인용'}]},model:'gemini-3.8-flash',reasoning:'high'}});
function response(text, width=1) {
  const bytes = new TextEncoder().encode(text);
  return new Response(new ReadableStream({start(c) {for(let i=0;i<bytes.length;i+=width)c.enqueue(bytes.slice(i,i+width));c.close();}}), {headers:{'content-type':'application/x-ndjson'}});
}
test('decodes fragmented UTF-8, CRLF and final unterminated result', async () => {
 const stages=[];
 const actual=await readFactCheckStream(response(JSON.stringify({type:'stage',stage:'reading',message:'읽는 중'})+'\r\n\n'+JSON.stringify({type:'result',result})), {onStage:event=>stages.push(event.message)});
 assert.deepEqual(actual,result); assert.deepEqual(stages,['읽는 중']);
});
test('accepts a Gemini fallback result with high reasoning', async () => {
 const fallback = {...result, model:'gemini-3.8-flash', reasoning:'high'};
 const actual = await readFactCheckStream(response(JSON.stringify({type:'result',result:fallback})));
 assert.equal(actual.model,'gemini-3.8-flash');
 assert.equal(actual.reasoning,'high');
});
test('requires a well-formed answer and source-grounded citations', async () => {
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:(({answer,...rest})=>rest)(result)}))),/결과/);
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:{...result,answer:{...insufficientAnswer,status:'grounded'}}}))),/결과/);
 const unknown=groundedResult(); unknown.answer.overview.citations[0].sourceId='unknown';
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:unknown}))),/결과/);
 const unavailable=groundedResult({...verifiedSource,accessStatus:'unavailable'});
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:unavailable}))),/결과/);
 const youtubeSource={...verifiedSource,sourceType:'유튜브',youtubeDataStatus:'collected'};
 const youtube=groundedResult(youtubeSource);
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:youtube}))),/결과/);
 const accepted=await readFactCheckStream(response(JSON.stringify({type:'result',result:groundedResult()})));
 assert.equal(accepted.answer.status,'grounded');
});
test('accepts a safe insufficient-evidence answer without answer model metadata', async () => {
 const actual=await readFactCheckStream(response(JSON.stringify({type:'result',result:{...result,answer:insufficientAnswer}})));
 assert.deepEqual(actual.answer,insufficientAnswer);
});
test('accepts bounded YouTube title and comments but rejects malformed context', async () => {
 const source={id:'s1',url:'https://www.youtube.com/watch?v=aB_12345678',title:'검색 제목',youtubeTitle:'실제 영상 제목',youtubeComments:['첫 댓글'],youtubeDataStatus:'collected',publisher:'youtube.com',publishedAt:null,retrievedAt:'2026-09-23',accessStatus:'unavailable',sourceType:'유튜브',originGroupId:'youtube'};
 const youtubeResult={...result,sources:[source]};
 const actual=await readFactCheckStream(response(JSON.stringify({type:'result',result:youtubeResult})));
 assert.deepEqual(actual.sources[0].youtubeComments,['첫 댓글']);
 const tooManyComments={...youtubeResult,sources:[{...source,youtubeComments:Array(11).fill('댓글')}]};
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:tooManyComments}))),/결과/);
 const invalidStatus={...youtubeResult,sources:[{...source,youtubeDataStatus:'unknown'}]};
 await assert.rejects(readFactCheckStream(response(JSON.stringify({type:'result',result:invalidStatus}))),/결과/);
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
