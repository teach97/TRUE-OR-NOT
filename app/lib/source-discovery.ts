import type { FactSource } from './fact-check-contract';

export function sourceDiscoveryLabel(source: FactSource): string {
  const provider = source.searchProvider === 'tavily_search'
    ? 'Tavily 검색 후보'
    : source.searchProvider === 'openai_web_search'
    ? 'GPT 웹검색 후보'
    : source.searchProvider === 'gemini_google_search'
      ? 'Gemini 검색 후보'
      : '검색 후보';
  const order = source.candidateOrder == null ? '' : ` ${source.candidateOrder}`;
  const query = source.searchQuery?.trim();
  return `${provider}${order}${query ? ` · 검색어 ${query}` : ''}`;
}
