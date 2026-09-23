import test from 'node:test';
import assert from 'node:assert/strict';
import {stripYoutubeApiDataForExport} from './youtube-context.ts';

test('removes YouTube API title and comments from downloaded results', () => {
 const sources=[
  {id:'s1',sourceType:'유튜브',youtubeTitle:'API title',youtubeComments:['Raw comment'],youtubeDataStatus:'collected'},
  {id:'s2',sourceType:'한국 기사',youtubeTitle:null,youtubeComments:[],youtubeDataStatus:'not_applicable'},
 ];
 const stripped=stripYoutubeApiDataForExport(sources);
 assert.deepEqual(stripped[0],{...sources[0],youtubeTitle:null,youtubeComments:[],youtubeDataStatus:'not_applicable'});
 assert.deepEqual(stripped[1],sources[1]);
 assert.notEqual(stripped[0],sources[0]);
});
