import test from 'node:test';
import assert from 'node:assert/strict';
import {toStoredMessage} from './conversation-message.ts';
test('only final user, chat, summary, failure and cancelled messages are stored',()=>{
  assert.equal(toStoredMessage({role:'assistant',thinking:true}),null);
  assert.equal(toStoredMessage({role:'assistant',progress:{}}),null);
  assert.equal(toStoredMessage({role:'user',imagePreview:'binary'}),null);
  for(const role of ['user','assistant'])assert.equal(toStoredMessage({role,text:'본문'}).content,'본문');
  assert.match(toStoredMessage({role:'assistant',summary:{title:'제목',summary:'요약',points:['핵심'],sourceUrl:'https://example.org'}}).content,/제목\n요약\n핵심/);
  assert.equal(toStoredMessage({role:'assistant',text:'실패',tone:'error'}).status,'failed');
  assert.equal(toStoredMessage({role:'assistant',text:'취소',storageStatus:'cancelled'}).status,'cancelled');
});
