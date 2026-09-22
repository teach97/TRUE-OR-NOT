import type { FactCheckResult } from '../lib/fact-check-contract';

type ReplyResult = Pick<FactCheckResult, 'claims' | 'sources' | 'evidence'>;

export type AssistantReply = {
  text: string;
  meta: string;
};

function joinDetails(label: string, values: string[]): string {
  const details = values.filter(Boolean).slice(0, 2).join(' ');
  return details ? ` ${label}: ${details}` : '';
}

export function composeAssistantReply(result: ReplyResult): AssistantReply {
  const sourceCount = result.sources.length;
  const evidenceCount = result.evidence.length;
  const claim = result.claims.find(item => item.kind === 'fact' || item.kind === 'unclear') ?? result.claims[0];

  if (!claim) {
    return {
      text: '검증 가능한 주장을 찾지 못했어. 사실 여부를 확인할 문장을 조금 더 구체적으로 보내줘.',
      meta: `${sourceCount}개 출처 · ${evidenceCount}개 인용`,
    };
  }

  const sourceMessage = sourceCount
    ? `${sourceCount}개 출처를 확인했어.`
    : '검색된 출처가 없어 이번 결과는 사실이나 거짓으로 단정하지 않았어.';
  const evidenceMessage = evidenceCount
    ? `직접 인용 ${evidenceCount}개를 원문과 대조했어.`
    : '원문과 대조할 직접 인용은 아직 없어서 확정하지 않았어.';
  const details = [
    joinDetails('확인된 내용', claim.confirmed),
    joinDetails('남은 불확실성', claim.unresolved),
  ].join('');

  return {
    text: `${claim.summary} 현재 판정은 ${claim.verdict}이고, 팩트 점수는 ${claim.factScore}점이야. ${sourceMessage} ${evidenceMessage}${details}`,
    meta: `${sourceCount}개 출처 · ${evidenceCount}개 인용`,
  };
}
