import test from 'node:test';
import assert from 'node:assert/strict';
import {conversationClient} from './conversation-client.ts';
test('rejects malformed history instead of rendering arbitrary response fields',async()=>{
  const original=global.fetch;global.fetch=async()=>Response.json({items:[{ownerId:'private'}],nextCursor:null});
  try {await assert.rejects(()=>conversationClient.list(),/PROTOCOL/);}finally{global.fetch=original;}
});
