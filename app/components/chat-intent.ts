import type { FactCheckResult } from '../lib/fact-check-contract';

export type ChatIntent =
  | {kind: 'meta'; topic: 'history' | 'greeting' | 'thanks' | 'identity'}
  | {kind: 'followup'}
  | {kind: 'verify'};

const FOLLOW_UP_PATTERNS = [/그럼/, /그거/, /그것/, /그건/, /이어서/, /계속/, /추가/, /더 찾아/, /검색해서/, /알아봐/, /찾아줘/, /찾아$/];

const META_PATTERNS: Array<{topic: 'history' | 'greeting' | 'thanks' | 'identity'; patterns: RegExp[]}> = [
  {topic: 'history', patterns: [/볼\s*수\s*있/, /보여줘/, /기억/, /대화/, /지금까지/, /여태까지/, /뭘 검증했/, /뭐 검증했/, /검증 기록/, /검증한 거/, /무슨 검증/, /대화 기록/, /채팅 기록/]},
  {topic: 'greeting', patterns: [/^안녕/, /^하이/, /^헬로/, /^반가워/, /^안녕하세요/]},
  {topic: 'thanks', patterns: [/고마워/, /감사/, /고생했/, /땡큐/, /수고했/]},
  {topic: 'identity', patterns: [/너는 누구/, /너가 누구/, /너는 뭐야/, /너가 뭐야/, /자기소개/, /뭐하는/, /뭘 할 수 있/, /뭐 할 수 있/]},
];

export function classifyChatInput(
  text: string,
  options: {hasPrevious: boolean; hasAttachment: boolean},
): ChatIntent {
  const trimmed = text.trim();
  if (!trimmed || options.hasAttachment) return {kind: 'verify'};
  if (trimmed.length <= 100) {
    for (const group of META_PATTERNS) {
      if (group.patterns.some(pattern => pattern.test(trimmed))) return {kind: 'meta', topic: group.topic};
    }
  }
  if (options.hasPrevious && trimmed.length <= 60 && FOLLOW_UP_PATTERNS.some(pattern => pattern.test(trimmed))) {
    return {kind: 'followup'};
  }
  return {kind: 'verify'};
}

export function describeHistory(
  messages: Array<{role: string; text?: string}>,
  result: FactCheckResult | null,
  demoText = '',
): string {
  const past = messages
    .filter(message => message.role === 'user' && message.text && message.text.trim() && message.text.trim() !== demoText.trim())
    .map(message => message.text!.trim().slice(0, 40));
  if (!past.length && !result) return '아직 검증한 게 없어. 확인할 원문·링크·이미지를 보내면 시작할게.';
  const lines = [`응, 이 대화는 다 보여. 지금까지 ${past.length}번 검증 요청이 있었어.`];
  for (const item of past.slice(-3)) lines.push(`· "${item}"`);
  if (result && result.claims.length) {
    const verdicts = result.claims.map(claim => `"${claim.quote.slice(0, 30)}" ${claim.verdict}(${claim.factScore}점)`);
    lines.push(`마지막 검증: 주장 ${result.claims.length}개 — ${verdicts.join(' / ')}`);
  }
  return lines.join('\n');
}

export function metaReply(topic: 'history' | 'greeting' | 'thanks' | 'identity'): string {
  if (topic === 'greeting') return '안녕! 확인할 주장·원문·링크·이미지를 보내면 근거랑 같이 따져볼게.';
  if (topic === 'thanks') return '별말씀을요. 또 확인할 거 있으면 보내줘.';
  return '난 True or Not야. 원문 속 주장을 나누고 출처 원문이랑 대조해서 보여주는 팩트체크 에이전트야. 검증은 원문·링크·이미지를 보내면 시작해.';
}
