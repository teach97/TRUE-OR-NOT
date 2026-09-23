import type { AgentEvent, AnswerBlock, FactCheckAnswer, FactCheckResult, FactSource } from '../lib/fact-check-contract';
// @ts-ignore -- explicit extension is required by the Node 24 native test runner.
import { FACT_SCORE_BANDS, scoreBand, scoreLabel } from '../lib/fact-score.ts';

type Options = {signal?: AbortSignal; onStage?: (event: Extract<AgentEvent, {type: 'stage'}>) => void};
export class FactCheckError extends Error {
  code: string;
  constructor(code: string, message: string) {super(message); this.name = 'FactCheckError'; this.code = code;}
}
export function safeSourceUrl(value: string): string | null {
  try {const url = new URL(value); return ['http:', 'https:'].includes(url.protocol) ? url.href : null;} catch {return null;}
}
function validAnswer(value: unknown, sources: FactSource[]): value is FactCheckAnswer {
  if (!value || typeof value !== 'object') return false;
  const answer = value as FactCheckAnswer;
  if (!['grounded','insufficient_evidence'].includes(answer.status) || !Array.isArray(answer.sections) || answer.sections.length > 4
      || !(answer.model === null || (typeof answer.model === 'string' && answer.model.length <= 100))
      || !(answer.reasoning === null || answer.reasoning === 'max' || answer.reasoning === 'high')) return false;
  const validBlock = (value: unknown, citationsRequired: boolean): value is AnswerBlock => {
    if (!value || typeof value !== 'object') return false;
    const block = value as AnswerBlock;
    return typeof block.text === 'string' && block.text.length >= 1 && block.text.length <= 1200
      && Array.isArray(block.citations) && block.citations.length <= 3 && (!citationsRequired || block.citations.length > 0)
      && block.citations.every(citation => citation && typeof citation.sourceId === 'string' && citation.sourceId.length >= 1 && citation.sourceId.length <= 100
        && typeof citation.quote === 'string' && citation.quote.length >= 1 && citation.quote.length <= 2000
        && sources.some(source => source.id === citation.sourceId && source.accessStatus === 'verified' && source.sourceType !== '유튜브'));
  };
  const citationsRequired = answer.status === 'grounded';
  if (answer.overview !== null && !validBlock(answer.overview, citationsRequired)) return false;
  if (answer.conclusion !== null && !validBlock(answer.conclusion, citationsRequired)) return false;
  if (citationsRequired && (answer.overview === null || answer.conclusion === null)) return false;
  if (answer.status === 'insufficient_evidence' && answer.sections.length > 0) return false;
  return answer.sections.every(section => section && typeof section === 'object'
    && ['supporting','counter','uncertainty','context'].includes(section.kind)
    && typeof section.title === 'string' && section.title.length >= 1 && section.title.length <= 120
    && Array.isArray(section.items) && section.items.length >= 1 && section.items.length <= 3
    && section.items.every(item => validBlock(item, citationsRequired)));
}
function validResult(value: unknown): value is FactCheckResult {
  if (!value || typeof value !== 'object') return false;
  const r = value as FactCheckResult;
  return r.demo === false && typeof r.text === 'string' && typeof r.focus === 'string' && typeof r.checkedAt === 'string' && typeof r.model === 'string' && (r.reasoning === 'max' || r.reasoning === 'high')
    && Array.isArray(r.claims) && r.claims.length <= 3 && r.claims.every(c => typeof c.id === 'string' && typeof c.quote === 'string' && Number.isInteger(c.start) && Number.isInteger(c.end) && c.start >= 0 && c.end > c.start && r.text.slice(c.start, c.end) === c.quote && Number.isInteger(c.factScore) && c.factScore >= 0 && c.factScore <= 100 && FACT_SCORE_BANDS.includes(c.scoreBand) && c.scoreBand === scoreBand(c.factScore) && c.scoreLabel === scoreLabel(c.factScore) && typeof c.summary === 'string' && typeof c.tone === 'string' && typeof c.verdict === 'string' && [c.confirmed,c.unresolved,c.warnings,c.evidenceIds].every(a=>Array.isArray(a)&&a.every(s=>typeof s==='string')))
    && Array.isArray(r.sources) && r.sources.every(s => ['id','url','title','publisher','retrievedAt','sourceType'].every(k=>typeof s[k as keyof typeof s]==='string') && ['verified','unavailable'].includes(s.accessStatus) && (s.publishedAt === null || typeof s.publishedAt === 'string') && (s.originGroupId === null || typeof s.originGroupId === 'string') && (s.youtubeTitle === null || (typeof s.youtubeTitle === 'string' && s.youtubeTitle.length <= 300)) && Array.isArray(s.youtubeComments) && s.youtubeComments.length <= 10 && s.youtubeComments.every(comment => typeof comment === 'string' && comment.length <= 10000) && ['not_applicable','not_configured','collected','unavailable'].includes(s.youtubeDataStatus) && (s.sourceType === '유튜브' ? s.youtubeDataStatus !== 'not_applicable' : s.youtubeDataStatus === 'not_applicable'))
    && Array.isArray(r.evidence) && r.evidence.every(e=>['id','claimId','sourceId','quote'].every(k=>typeof e[k as keyof typeof e]==='string') && (e.quoteTranslation === undefined || e.quoteTranslation === null || typeof e.quoteTranslation === 'string') && typeof e.quoteVerified === 'boolean')
    && Array.isArray(r.warnings) && r.warnings.every(w=>typeof w==='string') && validAnswer(r.answer,r.sources);
}
export async function readFactCheckStream(response: Response, options: Options = {}): Promise<FactCheckResult> {
  options.signal?.throwIfAborted();
  if (!response.ok) {
    const error = await response.json().catch(()=>null);
    throw new FactCheckError(typeof error?.code === 'string' ? error.code : 'HTTP_ERROR', typeof error?.message === 'string' ? error.message : `서버 요청에 실패했습니다 (${response.status}).`);
  }
  if (!response.headers.get('content-type')?.includes('application/x-ndjson') || !response.body) throw new FactCheckError('PROTOCOL', '검증 응답 형식이 올바르지 않습니다.');
  const reader = response.body.getReader();
  const abort = () => {void reader.cancel().catch(()=>{});};
  options.signal?.addEventListener('abort', abort, {once:true});
  const decoder = new TextDecoder();
  let buffer = '';
  let result: FactCheckResult | undefined;
  function line(value: string) {
    if (!value.trim()) return;
    let event: AgentEvent;
    try {event = JSON.parse(value);} catch {throw new FactCheckError('PROTOCOL', '검증 스트림을 읽을 수 없습니다.');}
    if (!event || !['stage','result','error'].includes(event.type)) throw new FactCheckError('PROTOCOL', '알 수 없는 스트림 이벤트입니다.');
    if (event.type === 'error') throw new FactCheckError(event.code, event.message || '검증 요청에 실패했습니다.');
    if (event.type === 'stage') {if(typeof event.message !== 'string') throw new FactCheckError('PROTOCOL','잘못된 스트림 단계입니다.'); options.onStage?.(event);}
    if (event.type === 'result') {if (!validResult(event.result)) throw new FactCheckError('PROTOCOL', '검증 결과 형식이 올바르지 않습니다.'); result = event.result;}
  }
  try {
    while (true) {
      options.signal?.throwIfAborted();
      const {done, value} = await reader.read();
      options.signal?.throwIfAborted();
      buffer += decoder.decode(value, {stream: !done});
      if (buffer.length > 2_000_000) throw new FactCheckError('PROTOCOL', '검증 스트림이 너무 큽니다.');
      let boundary: number;
      while ((boundary = buffer.indexOf('\n')) >= 0) {line(buffer.slice(0, boundary)); buffer = buffer.slice(boundary + 1);}
      if (done) break;
    }
    line(buffer);
    if (!result) throw new FactCheckError('INCOMPLETE', '검증 완료 전에 연결이 종료되었습니다. 다시 시도해 주세요.');
    return result;
  } finally {options.signal?.removeEventListener('abort', abort); await reader.cancel().catch(()=>{}); reader.releaseLock();}
}
