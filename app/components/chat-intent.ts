import type { FactCheckResult } from '../lib/fact-check-contract';

export type ChatIntent =
  | {kind: 'meta'; topic: 'history' | 'greeting' | 'thanks' | 'identity' | 'control' | 'tease' | 'smalltalk' | 'help'}
  | {kind: 'followup'}
  | {kind: 'verify'};

type MetaTopic = 'history' | 'greeting' | 'thanks' | 'identity' | 'control' | 'tease' | 'smalltalk' | 'help';

// Previous conversation in short order: demonstratives pointing at it.
const FOLLOW_UP_PATTERNS = [
  /그럼/, /그거/, /그것/, /그건/, /그걸/, /그게/, /그런/, /그렇게/, /그래서/, /그러면/, /그러니까/,
  /이거/, /이것/, /이건/, /이걸/, /이게/, /이런/, /이렇게/,
  /저거/, /저것/, /저건/, /저걸/, /이어서/,
];

// Unambiguous verification signals: hearsay, truth and evidence vocabulary.
// A bare question mark is not enough ("밥 먹었어?" must stay small talk).
const CLAIM_PATTERNS = [
  /인지/, /사실/, /진실/, /거짓/, /진짜/, /정말/,
  /맞는지/, /맞아/, /맞니/, /틀린지/, /틀렸/, /틀리니/,
  /확인/, /검증/, /주장/, /근거/, /출처/, /카더라/, /라던데/, /라는데/,
];
const SHIELD_GUARD = /하지 ?마|그만해|닥쳐|조용히/;

const EARLY_META: Array<{topic: MetaTopic; patterns: RegExp[]}> = [
  {topic: 'history', patterns: [/볼\s*수\s*있/, /보여줘/, /기억/, /대화/, /지금까지/, /여태까지/, /뭘 검증했/, /뭐 검증했/, /검증 기록/, /검증한 거/, /무슨 검증/, /대화 기록/, /채팅 기록/]},
  {topic: 'greeting', patterns: [/^안녕/, /^하이/, /^헬로/, /^반가워/, /^안녕하세요/]},
  {topic: 'thanks', patterns: [/고마워/, /감사/, /고생했/, /땡큐/, /수고했/]},
  {topic: 'identity', patterns: [/너는 누구/, /너가 누구/, /너는 뭐야/, /너가 뭐야/, /자기소개/, /뭐하는/]},
];

const HELP_PATTERNS = [/뭘 할 수 있/, /뭐 할 수 있/, /뭐할 수 있/, /도와줘/, /도울 수 있/, /기능이 뭐/, /기능 뭐/, /사용법/, /어떻게 써/, /어떻게 사용/];

const LATE_META: Array<{topic: MetaTopic; patterns: RegExp[]}> = [
  {topic: 'control', patterns: [/존댓말/, /반말/, /높임말/, /말투/, /해라체/, /하게체/, /합쇼체/, /하오체/, /실시$/, /찾아줘$/, /찾아봐$/, /찾아$/, /알아봐줘$/, /해줘$/, /해라$/, /하라$/, /해봐$/, /말해봐$/, /대답해$/, /얘기해$/, /달라고$/, /줘$/, /줘요$/]},
  {topic: 'tease', patterns: [/야임마/, /야이/, /(^|[\s!?.])야([\s!?.]|$)/, /어이/, /이봐/, /바보/, /멍청/, /또라이/, /미친/, /못생겼/, /못생긴/, /하지마/, /하지 마/, /그만해/, /닥쳐/, /조용히/]},
  {topic: 'smalltalk', patterns: [/뭐해/, /뭐하냐/, /뭐하니/, /뭐하고 있/, /심심/, /놀자/, /놀아줘/, /잘자/, /잘 자/, /밥 먹었/, /밥먹었/]},
];

export function isFollowUpText(text: string): boolean {
  const trimmed = text.trim();
  return trimmed.length > 0 && trimmed.length <= 60 && FOLLOW_UP_PATTERNS.some(pattern => pattern.test(trimmed));
}

export function classifyChatInput(
  text: string,
  options: {hasPrevious: boolean; hasAttachment: boolean},
): ChatIntent {
  const trimmed = text.trim();
  if (!trimmed || options.hasAttachment || trimmed.length > 60) return {kind: 'verify'};
  for (const group of EARLY_META) {
    if (group.patterns.some(pattern => pattern.test(trimmed))) return {kind: 'meta', topic: group.topic};
  }
  if (options.hasPrevious && FOLLOW_UP_PATTERNS.some(pattern => pattern.test(trimmed))) {
    return {kind: 'followup'};
  }
  if (HELP_PATTERNS.some(pattern => pattern.test(trimmed))) return {kind: 'meta', topic: 'help'};
  if (!SHIELD_GUARD.test(trimmed) && CLAIM_PATTERNS.some(pattern => pattern.test(trimmed))) return {kind: 'verify'};
  for (const group of LATE_META) {
    if (group.patterns.some(pattern => pattern.test(trimmed))) return {kind: 'meta', topic: group.topic};
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

export function metaReply(topic: MetaTopic): string {
  if (topic === 'greeting') return '안녕! 확인할 주장·원문·링크·이미지를 보내면 근거랑 같이 따져볼게.';
  if (topic === 'thanks') return '별말씀을요. 또 확인할 거 있으면 보내줘.';
  if (topic === 'control') return '그건 아직 못 해. 확인할 주장·원문·링크·이미지를 보내주면 검증할게.';
  if (topic === 'tease') return '악, 찔렸어. 확인할 거 있으면 보내줘, 근거로 제대로 따져볼게.';
  if (topic === 'smalltalk') return '난 검증 대기 중이야. 확인할 거 보내주면 바로 시작할게.';
  if (topic === 'help') return '원문·링크·이미지를 주면 주장을 나누고 출처 원문이랑 대조해줘. 짧게 이어서 물어보면 이전 검증을 바탕으로 찾아봐.';
  return '난 True or Not야. 원문 속 주장을 나누고 출처 원문이랑 대조해서 보여주는 팩트체크 에이전트야. 검증은 원문·링크·이미지를 보내면 시작해.';
}
