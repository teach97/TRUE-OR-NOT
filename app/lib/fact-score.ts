export const FACT_SCORE_BANDS = ['verified', 'mostly_true', 'neutral', 'mostly_false', 'false'] as const;
export type FactScoreBand = typeof FACT_SCORE_BANDS[number];

export const FACT_SCORE_LABELS: Record<FactScoreBand, string> = {
  verified: '검증된 사실',
  mostly_true: '대체적으로 사실',
  neutral: '중립(검증되지 않음)',
  mostly_false: '대체적으로 거짓',
  false: '거짓',
};

export function scoreBand(score: number): FactScoreBand {
  if (score >= 80) return 'verified';
  if (score >= 60) return 'mostly_true';
  if (score >= 40) return 'neutral';
  if (score >= 20) return 'mostly_false';
  return 'false';
}

export function scoreLabel(score: number): string {
  return FACT_SCORE_LABELS[scoreBand(score)];
}

export function normalizeFactScore(verdictCode: string, requestedScore: number): number {
  const score = Math.max(0, Math.min(100, Math.trunc(requestedScore)));
  if (verdictCode === 'mostly_supported') return Math.max(80, score);
  if (verdictCode === 'partially_supported') return Math.min(79, Math.max(60, score));
  if (verdictCode === 'contradicted') return Math.min(39, score);
  return 50;
}
