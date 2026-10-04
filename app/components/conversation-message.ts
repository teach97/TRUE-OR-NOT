import type {FactCheckAnswer,FactCheckResult} from '../lib/fact-check-contract';
import type {MessageCreate} from '../lib/conversation-contract';
// @ts-ignore -- Node 24 시험에서도 동일 정제 코드를 사용합니다.
import {sanitizeSnapshot} from '../lib/conversation-contract.ts';
type FinalMessage = {role:'user'|'assistant';text?:string;thinking?:boolean;progress?:unknown;imagePreview?:string;tone?:'normal'|'error';storageStatus?:'cancelled';answer?:FactCheckAnswer;summary?:{title:string;summary:string;points:string[];sourceUrl?:string|null}};
export function toStoredMessage(message:FinalMessage,result?:FactCheckResult):MessageCreate|null {
  if(message.thinking||message.progress)return null;
  const summary=message.summary;
  const answer=message.answer;
  const content=summary?[summary.title,summary.summary,...summary.points,summary.sourceUrl].filter(Boolean).join('\n'):answer?[answer.overview?.text,...answer.sections.flatMap(section=>[section.title,...section.items.map(item=>item.text)]),answer.conclusion?.text].filter(Boolean).join('\n'):message.text;
  if(!content?.trim())return null;
  return {storageConsent:true,requestId:crypto.randomUUID(),role:message.role,content,status:message.storageStatus??(message.tone==='error'?'failed':'completed'),snapshot:result?sanitizeSnapshot(result):null};
}
