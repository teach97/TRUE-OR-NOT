/** 브라우저와 서버가 공유하는 검증 계약입니다. 비밀 설정은 포함하지 않습니다. */
import type { FactScoreBand } from './fact-score';

export const FACT_CHECK_MODEL = 'gpt-5.6-luna';
export const FACT_CHECK_REASONING = 'max';
export const VERDICTS = ['mostly_supported', 'partially_supported', 'missing_context', 'conflicting_sources', 'insufficient_evidence', 'not_checkable', 'contradicted'] as const;
export type VerdictCode = typeof VERDICTS[number];
export type Reasoning = 'max' | 'high';
export type FactCheckRequest = { text: string; focus: string; consent: true };
export type FactSource = {
  id: string; url: string; title: string; publisher: string; publishedAt: string | null;
  retrievedAt: string; accessStatus: 'verified' | 'unavailable';
  sourceType: string; originGroupId: string | null;
};
export type FactEvidence = {
  id: string; claimId: string; sourceId: string; quote: string;
  quoteTranslation?: string | null;
  quoteVerified: boolean; relation: 'supports' | 'contradicts' | 'context';
};
export type FactClaim = {
  id: string; quote: string; start: number; end: number;
  kind: 'fact' | 'opinion' | 'prediction' | 'unclear';
  factScore: number; scoreBand: FactScoreBand; scoreLabel: string;
  verdictCode: VerdictCode; verdict: string; tone: string; summary: string;
  confirmed: string[]; unresolved: string[]; warnings: string[]; evidenceIds: string[];
};
export type FactCheckResult = {
  text: string; focus: string; demo: false; model: string; reasoning: Reasoning; checkedAt: string;
  claims: FactClaim[]; sources: FactSource[]; evidence: FactEvidence[]; warnings: string[];
};
export type AgentStage = 'extracting' | 'searching' | 'reading' | 'verifying';
export type AgentEvent =
  | {type: 'stage'; stage: AgentStage; message: string}
  | {type: 'result'; result: FactCheckResult}
  | {type: 'error'; code: string; message: string};
export type AgentStatus = {configured: boolean; model: string | null; reasoning: Reasoning | null; webSearch: boolean};
