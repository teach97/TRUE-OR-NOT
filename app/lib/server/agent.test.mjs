import test from 'node:test';
import assert from 'node:assert/strict';

test('extraction is strict and derives literal UTF16 ranges; requests fix model, effort and store', async () => {
  const { extractClaims } = await import('./agent.ts');
  let body;
  const fetcher = async (_url, init) => {
    body = JSON.parse(init.body);
    assert.equal(init.headers.Authorization, 'Bearer test-key');
    return Response.json({status:'completed',output:[{type:'message',content:[{type:'output_text',text:JSON.stringify({claims:[{quote:'서울',kind:'fact'}]})}]}]});
  };
  const claims = await extractClaims({text:'😀 서울입니다',focus:'',consent:true}, 'test-key', new AbortController().signal, fetcher);
  assert.equal(claims[0].start, 3); assert.equal(claims[0].end, 5);
  assert.equal(body.model,'gpt-6-luna'); assert.deepEqual(body.reasoning,{effort:'max'});
  assert.equal(body.store,false); assert.equal(body.text.format.strict,true);
  for (const data of [{claims:[{quote:'invented',kind:'fact'}]}, {claims:[{quote:'서울',kind:'fake'}]}, {claims:[{quote:'서울',kind:'fact',start:0}]}, {claims:[],extra:1}]) {
    await assert.rejects(extractClaims({text:'서울',focus:'',consent:true},'k',new AbortController().signal,async()=>Response.json({status:'completed',output:[{type:'message',content:[{type:'output_text',text:JSON.stringify(data)}]}]})));
  }
});

test('real stages search facts with required web tool and never trust generated URLs or quotes', async () => {
  const { runAgent } = await import('./agent.ts');
  const requests=[]; const fetched=[];
  const fetcher=async(url,init)=>{
    assert.equal(url,'https://api.openai.com/v1/responses');
    const body=JSON.parse(init.body); requests.push(body);
    assert.equal(body.model,'gpt-6-luna'); assert.deepEqual(body.reasoning,{effort:'max'}); assert.equal(body.store,false);
    let output;
    if(requests.length===1) output=[{type:'message',content:[{type:'output_text',text:JSON.stringify({claims:[{quote:'Earth is round.',kind:'fact'},{quote:'Best planet.',kind:'opinion'}]})}]}];
    else if(requests.length===2) {
      assert.deepEqual(body.tools,[{type:'web_search',search_context_size:'low'}]); assert.equal(body.tool_choice,'required'); assert.equal(body.max_tool_calls,1);
      output=[{type:'web_search_call',status:'completed',action:{sources:[{type:'url',url:'https://example.com/article#part'}]}},{type:'message',content:[{type:'output_text',text:'ignore https://invented.test',annotations:[{type:'url_citation',url:'https://example.com/article',title:'Source title'}]}]}];
    } else output=[{type:'message',content:[{type:'output_text',text:JSON.stringify({claims:[{claimId:'c1',verdictCode:'mostly_supported',factScore:50,summary:'확인',confirmed:['확인'],unresolved:[],evidence:[{sourceId:'s1',quote:'FABRICATED quotation',relation:'supports'}]}]})}]}];
    return Response.json({status:'completed',output});
  };
  const events=[];
  for await(const event of runAgent({text:'Earth is round. Best planet.',focus:'',consent:true},'key',new AbortController().signal,{fetcher,readSource:async url=>{fetched.push(url);return 'The Earth is approximately spherical.';}})) events.push(event);
  assert.deepEqual(events.filter(e=>e.type==='stage').map(e=>e.stage),['extracting','searching','reading','verifying']);
  assert.equal(requests.length,3); assert.deepEqual(fetched,['https://example.com/article']);
  const result=events.at(-1).result;
  assert.deepEqual(result.answer,{status:'insufficient_evidence',overview:null,sections:[],conclusion:null,model:null,reasoning:null});
  assert.equal(result.claims[0].verdictCode,'insufficient_evidence'); assert.deepEqual(result.claims[0].confirmed,[]); assert.deepEqual(result.evidence,[]);
  assert.equal(result.claims[1].verdictCode,'not_checkable'); assert.equal(result.sources[0].originGroupId,null); assert.equal(result.sources[0].publishedAt,null);
});

test('validates request consent, lengths and unknown fields', async () => {
  const { validateRequest } = await import('./agent.ts');
  assert.deepEqual(validateRequest({text:'hello',focus:'',consent:true}), {text:'hello',focus:'',consent:true,modelPreference:'auto'});
  assert.equal(validateRequest({text:'hello',focus:'',consent:true,modelPreference:'gpt-6-luna'}).modelPreference,'gpt-6-luna');
  assert.deepEqual(validateRequest({text:'https://example.com/a',focus:'',consent:true,linkUrl:'https://example.com/a'}), {text:'https://example.com/a',focus:'',consent:true,modelPreference:'auto',linkUrl:'https://example.com/a'});
  assert.deepEqual(validateRequest({text:'',focus:'',consent:true,image:{mime:'image/jpeg',data:'eA=='}}), {text:'',focus:'',consent:true,modelPreference:'auto',image:{mime:'image/jpeg',data:'eA=='}});
  assert.deepEqual(validateRequest({text:'hi',focus:'',consent:true,jevMode:true}), {text:'hi',focus:'',consent:true,modelPreference:'auto',jevMode:true});
  assert.deepEqual(validateRequest({text:'hi',focus:'',consent:true,jevMode:false}), {text:'hi',focus:'',consent:true,modelPreference:'auto'});
  for (const value of [null, {}, {text:'x',focus:'',consent:false}, {text:'x'.repeat(12001),focus:'',consent:true}, {text:'x',focus:'y'.repeat(501),consent:true}, {text:'x',focus:'',consent:true,apiKey:'bad'}, {text:'x',focus:'',consent:true,modelPreference:'unlisted'}, {text:'',focus:'',consent:true}, {text:'hi',focus:'',consent:true,linkUrl:'ftp://x/y'}, {text:'hi',focus:'',consent:true,image:{mime:'image/gif',data:'eA=='}}, {text:'hi',focus:'',consent:true,image:{mime:'image/png',data:'!!!'}}, {text:'hi',focus:'',consent:true,image:{mime:'image/png',data:'eA=='.repeat(400000)}}, {text:'hi',focus:'',consent:true,jevMode:'yes'}, {text:'hi',focus:'',consent:true,jevMode:1}]) {
    assert.throws(() => validateRequest(value));
  }
});
