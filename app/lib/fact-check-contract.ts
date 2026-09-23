/** 브라우저와 서버가 공유하는 검증 계약입니다. 비밀 설정은 포함하지 않습니다. */
import type { FactScoreBand } from './fact-score';

export const FACT_CHECK_MODEL = 'gpt-6-luna';
export const FACT_CHECK_REASONING = 'max';
export const MODEL_OPTIONS = [
  {id: 'gemini-3.8-flash', label: 'Gemini 3.8 Flash'},
  {id: 'gemini-3.7-flash', label: 'Gemini 3.7 Flash'},
  {id: 'gpt-6-luna', label: 'GPT-6 Luna Max'},
] as const;
export const VERDICTS = ['mostly_supported', 'partially_supported', 'missing_context', 'conflicting_sources', 'insufficient_evidence', 'not_checkable', 'contradicted'] as const;
export type VerdictCode = typeof VERDICTS[number];
export type Reasoning = 'max' | 'high';
export type ModelId = typeof MODEL_OPTIONS[number]['id'];
export type ModelPreference = 'auto' | ModelId;
export type ModelOption = {id: ModelId; label: string; configured: boolean};
export type FactCheckRequest = { text: string; focus: string; consent: true; modelPreference: ModelPreference };
export type YouTubeDataStatus = 'not_applicable' | 'not_configured' | 'collected' | 'unavailable';
export type FactSource = {
  id: string; url: string; title: string; publisher: string; publishedAt: string | null;
  retrievedAt: string; accessStatus: 'verified' | 'unavailable';
  sourceType: string; originGroupId: string | null;
  searchProvider?: 'openai_web_search' | 'gemini_google_search' | null;
  searchQuery?: string | null;
  candidateOrder?: number | null;
  youtubeTitle: string | null; youtubeComments: string[]; youtubeDataStatus: YouTubeDataStatus;
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
export type AnswerCitation = {sourceId: string; quote: string};
export type AnswerBlock = {text: string; citations: AnswerCitation[]};
export type AnswerSection = {
  kind: 'supporting' | 'counter' | 'uncertainty' | 'context';
  title: string;
  items: AnswerBlock[];
};
export type FactCheckAnswer = {
  status: 'grounded' | 'insufficient_evidence';
  overview: AnswerBlock | null;
  sections: AnswerSection[];
  conclusion: AnswerBlock | null;
  model: string | null;
  reasoning: Reasoning | null;
};
export type FactCheckResult = {
  text: string; focus: string; demo: false; model: string; reasoning: Reasoning; checkedAt: string;
  claims: FactClaim[]; sources: FactSource[]; evidence: FactEvidence[]; warnings: string[]; answer: FactCheckAnswer;
};
export type AgentStage = 'extracting' | 'searching' | 'reading' | 'verifying' | 'synthesizing';
export type AgentEvent =
  | {type: 'stage'; stage: AgentStage; message: string}
  | {type: 'result'; result: FactCheckResult}
  | {type: 'error'; code: string; message: string};
export type AgentStatus = {configured: boolean; model: string | null; reasoning: Reasoning | null; webSearch: boolean; modelOptions: ModelOption[]};
