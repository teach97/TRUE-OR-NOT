import type { AnswerCitation, FactCheckAnswer, FactCheckResult, FactSource } from '../lib/fact-check-contract';
// @ts-ignore -- explicit extension is required by the Node native test runner.
import { safeSourceUrl } from './fact-check-client.ts';

type ReplyResult = Pick<FactCheckResult, 'answer' | 'sources' | 'evidence'>;

export type AssistantReply = {
  answer: FactCheckAnswer;
  sources: FactSource[];
  meta: string;
};

export type ResolvedAnswerCitation = {source: FactSource; href: string};

export function resolveAnswerCitationSource(citation: AnswerCitation, sources: FactSource[]): ResolvedAnswerCitation | null {
  const source = sources.find(item => item.id === citation.sourceId);
  if (!source || source.accessStatus !== 'verified' || source.sourceType === '유튜브') return null;
  const href = safeSourceUrl(source.url);
  return href ? {source, href} : null;
}

export function composeAssistantReply(result: ReplyResult): AssistantReply {
  return {
    answer: result.answer,
    sources: result.sources,
    meta: `${result.sources.length}개 출처 · ${result.evidence.length}개 인용`,
  };
}
