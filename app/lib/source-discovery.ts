import type { FactSource } from './fact-check-contract';

export function sourceDiscoveryLabel(source: FactSource): string {
  if (source.searchProvider === 'serpapi_google') {
    const rank = source.candidateOrder == null ? '후보' : `${source.candidateOrder}위`;
    const query = source.searchQuery?.trim();
    return `Google 자연검색 ${rank}${query ? ` · 검색어 ${query}` : ''}`;
  }
  const provider = source.searchProvider === 'openai_web_search'
    ? 'GPT 웹검색 후보'
    : source.searchProvider === 'gemini_google_search'
      ? 'Gemini 검색 후보'
      : '검색 후보';
  const order = source.candidateOrder == null ? '' : ` ${source.candidateOrder}`;
  const query = source.searchQuery?.trim();
  return `${provider}${order}${query ? ` · 검색어 ${query}` : ''}`;
}
