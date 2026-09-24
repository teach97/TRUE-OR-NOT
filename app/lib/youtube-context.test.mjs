import test from 'node:test';
import assert from 'node:assert/strict';
import {stripYoutubeApiDataForExport, youtubeThumbnailUrl} from './youtube-context.ts';

test('builds thumbnails only for supported HTTPS YouTube video links', () => {
 assert.equal(youtubeThumbnailUrl('https://www.youtube.com/watch?v=aB_12345678&feature=share'),'https://i.ytimg.com/vi/aB_12345678/mqdefault.jpg');
 assert.equal(youtubeThumbnailUrl('https://youtu.be/aB_12345678'),'https://i.ytimg.com/vi/aB_12345678/mqdefault.jpg');
 assert.equal(youtubeThumbnailUrl('https://youtube.com/shorts/aB_12345678'),'https://i.ytimg.com/vi/aB_12345678/mqdefault.jpg');
 for (const url of [
  'http://youtube.com/watch?v=aB_12345678',
  'https://youtube.com/watch?v=aB_12345678&v=cD_12345678',
  'https://youtube.com.evil.example/watch?v=aB_12345678',
  'https://example.com/watch?v=aB_12345678',
  'https://youtube.com/watch?v=short',
  'not a URL',
 ]) assert.equal(youtubeThumbnailUrl(url),null);
});

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
