import test from 'node:test';
import assert from 'node:assert/strict';
import {sanitizeSnapshot, restoreSnapshot} from './conversation-contract.ts';

test('snapshot preserves citations and time without article bodies or API metadata', () => {
  const result = {text:'Claim',focus:'',demo:false,model:'gpt-6-luna',reasoning:'max',checkedAt:'2026-10-04T01:00:00Z',claims:[],warnings:[],sources:[{id:'s1',url:'https://example.org/article',title:'기사 제목',publisher:'뉴스',publishedAt:null,retrievedAt:'2026-10-04',accessStatus:'verified',sourceType:'한국 기사',originGroupId:null,youtubeComments:['private'],youtubeTitle:'private',youtubeDataStatus:'collected'}],evidence:[{id:'e1',claimId:'c1',sourceId:'s1',quote:'Claim',quoteVerified:true,relation:'context',sectionText:'whole article'}],answer:{status:'insufficient_evidence',overview:null,sections:[],conclusion:null,model:null,reasoning:null},market:{candles:['private']}};
  const snapshot = sanitizeSnapshot(result);
  assert.equal(snapshot.sources[0].title,'기사 제목');
  assert.equal(snapshot.sources[0].url,result.sources[0].url);
  assert.equal(snapshot.checkedAt,result.checkedAt);
  assert.equal(snapshot.evidence[0].sectionText,undefined);
  assert.equal(snapshot.sources[0].youtubeComments,undefined);
  assert.equal(snapshot.market,undefined);
  const restored = restoreSnapshot(snapshot);
  assert.deepEqual(restored.sources[0].youtubeComments,[]);
  assert.equal(restored.market,null);
  assert.equal(restored.checkedAt,result.checkedAt);
});
