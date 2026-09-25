import type { AnswerCitation, FactCheckAnswer, FactCheckResult, FactSource } from '../lib/fact-check-contract';
// @ts-ignore -- explicit extension is required by the Node native test runner.
import { safeSourceUrl } from './fact-check-client.ts';

type ReplyResult = Pick<FactCheckResult, 'answer' | 'sources' | 'evidence' | 'model' | 'claims'>;

export type AssistantReply =
  | {answer: FactCheckAnswer; sources: FactSource[]; meta: string; factScore?: never}
  | {factScore: number | null; verdict: string | null; answer?: never; sources?: never; meta?: never};

export type ResolvedAnswerCitation = {source: FactSource; href: string};
export type AnswerCitationDisplay = {
  citation: AnswerCitation;
  number: number;
  source: FactSource | null;
  href: string | null;
  linkTarget: 'external' | 'unavailable';
};

export type AnswerCitationDisplayState = {
  sourceNumbers: Map<string, number>;
  linkedSources: Set<string>;
};

export function createAnswerCitationDisplayState(sources: FactSource[] = []): AnswerCitationDisplayState {
  return {
    sourceNumbers: new Map(sources.map((source, index) => [source.id, index + 1])),
    linkedSources: new Set(),
  };
}

export function resolveAnswerCitationSource(citation: AnswerCitation, sources: FactSource[]): ResolvedAnswerCitation | null {
  const source = sources.find(item => item.id === citation.sourceId);
  if (!source || source.accessStatus !== 'verified' || source.sourceType === '유튜브') return null;
  const href = safeSourceUrl(source.url);
  return href ? {source, href} : null;
}

export function presentAnswerCitations(
  citations: AnswerCitation[],
  sources: FactSource[],
  state: AnswerCitationDisplayState,
): AnswerCitationDisplay[] {
  const seenInBlock = new Set<string>();
  const displays: AnswerCitationDisplay[] = [];

  for (const citation of citations) {
    if (seenInBlock.has(citation.sourceId)) continue;
    seenInBlock.add(citation.sourceId);

    let number = state.sourceNumbers.get(citation.sourceId);
    if (number === undefined) {
      number = state.sourceNumbers.size + 1;
      state.sourceNumbers.set(citation.sourceId, number);
    }

    const resolved = resolveAnswerCitationSource(citation, sources);
    if (!resolved) {
      displays.push({citation, number, source: null, href: null, linkTarget: 'unavailable'});
      continue;
    }
    if (state.linkedSources.has(citation.sourceId)) continue;
    state.linkedSources.add(citation.sourceId);

    displays.push({citation, number, source: resolved.source, href: resolved.href, linkTarget: 'external'});
  }

  return displays;
}

export function composeAssistantReply(result: ReplyResult): AssistantReply {
  if (result.model === 'typesafe-ai/jev') {
    return {factScore: result.claims[0]?.factScore ?? null, verdict: result.claims[0]?.verdict ?? null};
  }

  return {
    answer: result.answer,
    sources: result.sources,
    meta: `${result.sources.length}개 출처 · ${result.evidence.length}개 인용`,
  };
}
