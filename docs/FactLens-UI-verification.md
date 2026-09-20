# FactLens UI 고도화 구현·검증 기록

## 구현 범위

기획서 v2 기반의 한국어 다크 근거 워크스페이스를 구현했습니다. 실제 검색·LLM·URL 수집·계정·영속 저장은 미연결입니다. 합성 예시는 가상의 달빛시 축제로 명시되며 직접 입력에는 문장 후보만 표시합니다.

### 주요 변경

- `app/components/fact-check-dashboard.tsx`: 입력·주장·원문·근거 화면, 예시 불러오기, 취소, 대화상자, JSON 내보내기
- `app/components/demo-state.ts`: 불변 입력 스냅샷, 선택, 취소·지연 응답 방어
- `app/components/demo-state.test.mjs`: 상태 동작 테스트
- `app/components/demo-fixture.ts`: 명시적인 합성 예시와 문서
- `app/components/lens-visual.tsx`: 지연 로딩 Paper Design 쉐이더와 정적 렌즈 fallback
- `app/globals.css`: 반응형 다크 글래스 디자인, 포커스·reduced-motion, 모바일 가독성
- `app/layout.tsx`: FactLens 페이지 제목

Motion은 선택·내용 전환에, Paper Design은 렌즈 장식에 사용합니다. Liquid Glass의 기존 폼 이중 렌더링은 제거하고 CSS 글래스로 대체했습니다. Three.js 계열과 사용하지 않는 패키지는 억지로 화면에 로드하지 않았으며 의존성 파일은 이번 작업에서 수정하지 않았습니다.

## 실제 검증 결과

| 검증 | 관측 결과 |
|---|---|
| `npm run typecheck -- --incremental false` | 통과 |
| `node --test app/components/demo-state.test.mjs` | 4개 통과 |
| `npm run build` | 프로덕션 빌드 통과 |
| `git diff --check` | 통과, 기존 LF/CRLF 경고만 출력 |
| 최신 빌드 HTTP | `http://127.0.0.1:3012/` HTTP 200 |
| 주장·원문·결과 선택 | 동기화 확인 |
| 근거 상세 대화상자 | 열기·Escape 닫기 확인 |
| 실행 취소 | 지연 완료가 이전 문서를 대체하지 않음 |
| 직접 입력 | 판정 없음, 예시 출처 없음 확인 |
| JSON 다운로드 | 실제 파일 저장, demo=false·문서 없음·판정 null 검사 통과 |
| URL 모드 | 미연결 안내와 텍스트 대안 확인 |
| DOM ID | 중복 없음 |
| 모바일 탭 | 원문·결과·출처 전환 및 선택 유지 확인 |
| reduced-motion | 적용 시 smooth scroll 해제 확인 |
| 브라우저 콘솔 | 관측 메시지 0개, 오류 0개, 경고 0개 |

### 화면 크기

| 뷰포트 | 문서 가로 폭 | 결과 |
|---|---|---|
| 375 × 812 | 375 | 가로 넘침 없음 |
| 390 × 844 | 390 | 가로 넘침 없음 |
| 768 × 1024 | 768 | 가로 넘침 없음 |
| 844 × 390 | 844 | 가로 넘침 없음 |
| 1440 × 1000 | 1440 | 가로 넘침 없음 |

## 검증 중 발견하여 보완한 사항

모바일에서 텍스트를 숨기는 아이콘 버튼의 접근성 이름이 사라지는 문제와 14px 입력 글자 크기를 실패하는 브라우저 검사로 확인했습니다. 가이드·초기화 버튼에 명시적인 aria-label을 추가하고 모바일 입력을 16px로 조정한 뒤 재검사했습니다. 최종 빌드에서 이름과 크기 검사가 통과했고 전체 뷰포트의 넘침도 다시 확인했습니다.

## 산출물

- `output/playwright/factlens-desktop-final.png`
- `output/playwright/factlens-mobile-final.png`
- `output/playwright/factlens-custom-download.json`

브라우저 자동화 과정에서 `.playwright-cli/`와 `output/playwright/`에 스냅샷·이미지·다운로드가 생성되었습니다. 기존 사용자 변경은 초기화하지 않았으며 커밋하지 않았습니다.

## 남은 범위와 한계

- 사용자의 확인 요청은 보존하지만 의미 기반 주장 추출은 하지 않습니다. 로컬 후보는 앞의 최대 3문장입니다.
- API 검증·실제 인용·영속 저장을 구현한 것으로 간주해서는 안 됩니다.
- 전체 WCAG 인증, 모든 브라우저 엔진, 실제 스크린리더, WebGL 강제 실패 환경은 별도 검증이 필요합니다.
- 소스 내 일부 JSX/CSS가 긴 줄 형태이므로 후속 기능 개발 전 가독성 정리를 권장합니다.
- 최신 결과 확인 주소는 3012입니다. 이전 QA 서버 3011은 종료 시도가 중단되어 남아 있을 수 있으며 오래된 빌드를 제공할 수 있습니다.
