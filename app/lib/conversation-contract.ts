import type {FactCheckResult, FactSource, FactEvidence, AnswerBlock} from './fact-check-contract';

export type StoredSnapshot = Omit<FactCheckResult, 'demo' | 'market' | 'sources' | 'evidence'> & {
  scoreMode?:'jev'|'claims'|null;
  sources: Pick<FactSource,'id'|'url'|'title'|'publisher'|'publishedAt'|'retrievedAt'|'accessStatus'|'sourceType'|'originGroupId'>[];
  evidence: Pick<FactEvidence,'id'|'claimId'|'sourceId'|'quote'|'quoteTranslation'|'quoteVerified'|'relation'>[];
};
export type ConversationCreate = {storageConsent: true; createRequestId: string; title: string};
export type MessageCreate = {storageConsent: true; requestId: string; role: 'user'|'assistant'; content: string; status:'completed'|'failed'|'cancelled'; snapshot?:StoredSnapshot|null};
export type Conversation = {id:string; title:string; createdAt:string; updatedAt:string};
export type StoredMessage = Omit<MessageCreate,'storageConsent'> & {id:string; sequence:number; createdAt:string; snapshot:StoredSnapshot|null};
export type ConversationPage = {items:Conversation[]; nextCursor:string|null};
export type MessagePage = {conversation:Conversation; messages:StoredMessage[]; beforeSequence:number|null};

function block(value:AnswerBlock|null):AnswerBlock|null {
  return value ? {text:value.text,citations:value.citations.map(({sourceId,quote})=>({sourceId,quote}))} : null;
}
export function sanitizeSnapshot(result:FactCheckResult):StoredSnapshot {
  return {
    text:result.text,focus:result.focus,model:result.model,reasoning:result.reasoning,checkedAt:result.checkedAt,
    claims:result.claims.map(({id,quote,start,end,kind,factScore,scoreBand,scoreLabel,verdictCode,verdict,tone,summary,confirmed,unresolved,warnings,evidenceIds})=>({id,quote,start,end,kind,factScore,scoreBand,scoreLabel,verdictCode,verdict,tone,summary,confirmed:[...confirmed],unresolved:[...unresolved],warnings:[...warnings],evidenceIds:[...evidenceIds]})),
    sources:result.sources.map(({id,url,title,publisher,publishedAt,retrievedAt,accessStatus,sourceType,originGroupId})=>({id,url,title,publisher,publishedAt,retrievedAt,accessStatus,sourceType,originGroupId})),
    evidence:result.evidence.map(({id,claimId,sourceId,quote,quoteTranslation,quoteVerified,relation})=>({id,claimId,sourceId,quote,quoteTranslation,quoteVerified,relation})),
    warnings:[...result.warnings],
    answer:{status:result.answer.status,overview:block(result.answer.overview),conclusion:block(result.answer.conclusion),model:result.answer.model,reasoning:result.answer.reasoning,sections:result.answer.sections.map(({kind,title,items})=>({kind,title,items:items.map(item=>block(item)!)}))},
  };
}
export function restoreSnapshot(snapshot:StoredSnapshot):FactCheckResult {
  return {...snapshot,demo:false,market:null,sources:snapshot.sources.map(source=>({...source,youtubeTitle:null,youtubeChannelTitle:null,youtubePublishedAt:null,youtubeViewCount:null,youtubeComments:[],youtubeDataStatus:'not_applicable'}))};
}
