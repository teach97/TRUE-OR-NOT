import type { AnswerCitation, FactCheckAnswer, FactCheckResult, FactSource } from '../lib/fact-check-contract';
// @ts-ignore -- explicit extension is required by the Node native test runner.
import { MODEL_OPTIONS } from '../lib/fact-check-contract.ts';
// @ts-ignore -- explicit extension is required by the Node native test runner.
import { safeSourceUrl } from './fact-check-client.ts';

type ReplyResult = Pick<FactCheckResult, 'answer' | 'sources' | 'evidence' | 'model' | 'claims'>;

export type AssistantReply = {
  answer: FactCheckAnswer;
  sources: FactSource[];
  meta: string;
  factScore?: number | null;
  verdict?: string | null;
  search?: string | null;
};

export function modelLabel(model: string | null): string {
  if (!model) return '모델 미확인';
  return MODEL_OPTIONS.find(option => option.id === model)?.label ?? model;
}

export function searchBackendLabel(sources: FactSource[]): string | null {
  const providers = new Set(sources.map(source => source.searchProvider));
  const tavily = providers.has('tavily_search');
  const llm = providers.has('openai_web_search') || providers.has('gemini_google_search');
  if (tavily && llm) return 'Tavily+LLM 검색';
  if (tavily) return 'Tavily 검색';
  if (llm) return 'LLM 검색';
  return null;
}

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

export function composeAssistantReply(result: ReplyResult, jevResult: ReplyResult | null = null): AssistantReply {
  const search = searchBackendLabel(result.sources);
  const meta = `${modelLabel(result.answer.model ?? result.model)}${search ? ` · ${search}` : ''} · ${result.sources.length}개 출처 · ${result.evidence.length}개 인용`;
  const reply: AssistantReply = {
    answer: result.answer,
    sources: result.sources,
    meta,
  };
  const claim = jevResult?.claims[0];
  if (claim) {
    reply.factScore = claim.factScore ?? null;
    reply.verdict = claim.verdict ?? null;
    reply.search = searchBackendLabel(jevResult?.sources ?? []);
  }
  return reply;
}
