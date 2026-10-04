import test from 'node:test';
import assert from 'node:assert/strict';
import {ConversationStorage} from './conversation-storage.ts';
const message = role => ({storageConsent:true,requestId:crypto.randomUUID(),role,content:role,status:'completed',snapshot:null});
function api() {
  const rows=[];const conversation={id:crypto.randomUUID(),title:'대화',createdAt:'2026-10-04',updatedAt:'2026-10-04'};
  return {rows,session:async()=>{},create:async()=>conversation,append:async(id,data)=>{rows.push({id,...data});},list:async()=>({items:[conversation],nextCursor:null}),get:async()=>({conversation,messages:[],beforeSequence:null}),delete:async()=>{}};
}
test('consent defaults off and disabling it prevents new saves',async()=>{
  const client=api();const store=new ConversationStorage(client,()=>{});
  await store.saveMessage(message('user'),store.epoch);
  assert.equal(client.rows.length,0);
  store.setConsent(true);
  await store.saveMessage(message('user'),store.epoch);
  assert.equal(client.rows.length,1);
  store.setConsent(false);
  await store.saveMessage(message('assistant'),store.epoch);
  assert.equal(client.rows.length,1);
});
test('retry retains UUID and saves user before assistant without invoking LLM',async()=>{
  const client=api();const append=client.append;let failed=true;
  client.append=async(id,data)=>{if(failed)throw Error('STORAGE_UNAVAILABLE');return append(id,data);};
  const store=new ConversationStorage(client,()=>{});store.setConsent(true);
  const user=message('user'),assistant=message('assistant');
  await store.saveMessage(user,store.epoch);await store.saveMessage(assistant,store.epoch);
  assert.equal(store.pending[0].requestId,user.requestId);
  failed=false;await store.retrySave();
  assert.deepEqual(client.rows.map(item=>item.role),['user','assistant']);
  assert.equal(client.rows[0].requestId,user.requestId);
});
test('switching conversation ignores delayed create and late generation writes',async()=>{
  const client=api();let resolve;client.create=()=>new Promise(done=>{resolve=done;});
  const store=new ConversationStorage(client,()=>{});store.setConsent(true);const epoch=store.epoch;
  const save=store.saveMessage(message('user'),epoch);
  while(!resolve)await Promise.resolve();
  store.newConversation();resolve({id:crypto.randomUUID()});await save;
  await store.saveMessage(message('assistant'),epoch);
  assert.equal(client.rows.length,0);assert.equal(store.active,null);
});
test('message queued during history refresh is flushed before becoming idle',async()=>{
  const client=api();let resolve;client.list=()=>new Promise(done=>{resolve=done;});
  const store=new ConversationStorage(client,()=>{});store.setConsent(true);
  const saving=store.saveMessage(message('user'),store.epoch);
  while(!resolve)await Promise.resolve();
  const second=store.saveMessage(message('assistant'),store.epoch);
  resolve({items:[],nextCursor:null});client.list=async()=>({items:[],nextCursor:null});
  await saving;await second;
  for(let n=0;n<20&&client.rows.length<2;n++)await Promise.resolve();
  assert.deepEqual(client.rows.map(item=>item.role),['user','assistant']);
});
