import type {FactCheckAnswer,FactCheckResult} from '../lib/fact-check-contract';
import type {MessageCreate} from '../lib/conversation-contract';
// @ts-ignore -- Node 24 시험에서도 동일 정제 코드를 사용합니다.
import {sanitizeSnapshot} from '../lib/conversation-contract.ts';
type FinalMessage = {role:'user'|'assistant';text?:string;thinking?:boolean;progress?:unknown;imagePreview?:string;tone?:'normal'|'error';storageStatus?:'cancelled';scoreMode?:'jev'|'claims';answer?:FactCheckAnswer;summary?:{title:string;summary:string;points:string[];sourceUrl?:string|null}};
export function toStoredMessage(message:FinalMessage,result?:FactCheckResult):MessageCreate|null {
  if(message.thinking||message.progress)return null;
  const summary=message.summary;
  const answer=message.answer;
  const blocks=answer?[answer.overview?.text,...answer.sections.flatMap(section=>[section.title,...section.items.map(item=>item.text)]),answer.conclusion?.text].filter(Boolean).join('\n'):'';
  const fallback=result?(result.claims.map(claim=>`${claim.verdict} · ${claim.factScore}점\n${claim.summary}`).join('\n')||'검증 결과를 저장했습니다. 확인 가능한 근거가 부족합니다.'):'';
  const content=summary?[summary.title,summary.summary,...summary.points,summary.sourceUrl].filter(Boolean).join('\n'):blocks||message.text||fallback;
  if(!content?.trim())return null;
  return {storageConsent:true,requestId:crypto.randomUUID(),role:message.role,content,status:message.storageStatus??(message.tone==='error'?'failed':'completed'),snapshot:result?{...sanitizeSnapshot(result),scoreMode:message.scoreMode??null}:null};
}
