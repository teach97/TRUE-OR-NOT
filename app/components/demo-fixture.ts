import { createPreview } from './demo-state';
import type { Preview } from './demo-state';

export const DEMO_TEXT = '달빛시의 가을빛 축제가 10월 12일부터 사흘간 열립니다. 모든 프로그램은 예약 없이 무료로 참여할 수 있습니다. 올해 방문객은 지난해보다 두 배 늘어날 전망입니다.';
export const DEMO_FOCUS = '행사 일정과 무료 참여 조건을 확인하고 싶습니다.';
export const documents = [
  { id: 'doc-1', title: '가을빛 축제 운영 안내', publisher: '가상 달빛시 문화과', date: '가상 설정 · 2026.09.01', group: 'A', relation: '직접 안내', text: '이 문서는 UI 시연을 위해 작성한 합성 자료입니다.\n\n가을빛 축제는 10월 12일부터 14일까지 달빛공원에서 진행합니다. 야외 전시와 거리 공연은 무료입니다. 공예 체험은 사전 예약이 필요하며 재료비 5,000원이 있습니다.\n\n방문객 예상 규모는 이 안내에 포함하지 않았습니다.' },
  { id: 'doc-2', title: '축제 프로그램 소개', publisher: '가상 달빛 문화소식', date: '가상 설정 · 2026.09.03', group: 'A', relation: '같은 안내 재인용', text: '이 문서는 UI 시연을 위해 작성한 합성 자료입니다.\n\n달빛시 문화과의 가을빛 축제 운영 안내를 옮깁니다. 행사는 10월 12일부터 14일까지 열립니다. 야외 전시와 거리 공연은 무료이며, 공예 체험은 별도 예약과 재료비가 필요합니다.\n\n이 문서는 별도의 독립 취재 자료가 아닙니다.' },
] as const;
const base = createPreview({text: DEMO_TEXT, focus: DEMO_FOCUS});
const results = [
  {factScore: 94, scoreBand: 'verified', scoreLabel: '검증된 사실', verdict: '대체로 확인됨', tone: 'cyan', summary: '예시 안내의 10월 12~14일은 원문에 나온 사흘간의 일정과 일치합니다.', evidenceIds: ['doc-1', 'doc-2']},
  {factScore: 50, scoreBand: 'neutral', scoreLabel: '중립', verdict: '맥락이 생략됨', tone: 'amber', summary: '야외 전시와 공연은 무료이지만, 공예 체험에는 사전 예약과 재료비가 필요합니다.', evidenceIds: ['doc-1', 'doc-2']},
  {factScore: 50, scoreBand: 'neutral', scoreLabel: '중립', verdict: '검증 대상 아님', tone: 'violet', summary: '미래 방문객에 대한 전망입니다. 예시 문서에는 추정 방식이나 비교 수치가 없습니다.', evidenceIds: []},
] as const;
export const demoPreview: Preview = Object.freeze({...base, demo: true, claims: Object.freeze(base.claims.map((claim, i) => Object.freeze({...claim, ...results[i], evidenceIds: Object.freeze(results[i].evidenceIds)})))});
