# True or Not 프런트엔드

True or Not은 기사와 댓글의 주장을 출처에 연결하여 확인된 내용과 불확실한 내용을 함께 비교하는 생활형 AI 검증 서비스입니다. Next.js App Router, TypeScript, Tailwind CSS로 만든 웹 애플리케이션으로, 질문 입력과 검증 진행 표시, 주장별 검증 카드와 근거 출처 대시보드를 제공하며, 서버 측 API 경로를 통해 로컬 FastAPI 백엔드와 통신합니다.

## 검증 흐름

텍스트·링크·이미지 입력 → 주장 추출(최대 3개) → 검색 → 원문 읽기 → 주장별 판정 → AI 개요 합성의 5단계 파이프라인으로 동작합니다. JEV 빠른 경로(점수 전용), 내용 요약(`/api/summarize`), 유튜브 자막 근거(30분 미만), 주식 질문 시 시장 맥락(토스증권 우선·Finnhub 대체) 확장이 연결되어 있습니다. 상세 기획은 `docs/True_or_Not_기획서-v4.md`와 `docs/True_or_Not_구현현황-및-잔여범위.md`를 참고하십시오.

## 개발 환경 시작

Node.js 20 이상과 npm을 설치한 뒤 저장소 루트에서 실행합니다.

```bash
npm ci
npm run dev
```

브라우저에서 `http://localhost:3000`을 엽니다. 팩트체크를 실행하려면 별도의 터미널에서 백엔드도 실행해야 합니다. 백엔드 설치와 API 키 설정은 [백엔드 안내](backend/README.md)를 참고하세요.

기본적으로 프런트엔드는 `http://127.0.0.1:8010`의 백엔드에 연결합니다. 다른 로컬 포트를 사용한다면 Next.js 서버 환경 변수 `FACTLENS_BACKEND_URL`에 `http://127.0.0.1:<포트>` 또는 `http://[::1]:<포트>` 형식으로 지정한 뒤 프런트엔드 서버를 다시 시작하세요. 보안을 위해 현재 프록시는 이 두 루프백 호스트만 허용합니다. 환경 변수 이름의 `FACTLENS_` 접두사는 기존 코드와의 호환을 위해 유지됩니다.

## npm 명령

| 명령 | 설명 |
|---|---|
| `npm run dev` | 개발 서버를 실행합니다. |
| `npm run build` | 프로덕션 빌드를 생성합니다. |
| `npm run start` | 생성된 프로덕션 빌드를 실행합니다. |
| `npm run typecheck` | TypeScript 타입을 검사합니다. |

## 주요 디렉터리

- `app/page.tsx`, `app/layout.tsx`: Next.js 페이지와 공통 레이아웃입니다.
- `app/api/fact-check/route.ts`: 브라우저 요청을 백엔드에 전달하는 서버 측 프록시입니다.
- `app/components/`: 팩트체크 입력·대화와 결과 대시보드 UI입니다.
- `app/lib/`: API 계약, 점수 계산, 출처 탐색 및 서버 유틸리티입니다.
- `backend/`: FastAPI·LangGraph 팩트체크 백엔드입니다.

## 검색·출처 정책

Tavily 키가 있으면 Tavily 검색을 우선 사용하고, 키가 없거나 실패하면 LLM 웹검색으로 대체합니다. 링크 제목 기반 관련 기사 추가 검색과 주장별 검색어를 함께 사용하며, 출처는 최대 6개(같은 사이트 최대 2개)로 제한합니다. 검색 스니펫·LLM 요약·유튜브 제목/댓글은 인용 근거로 사용하지 않으며, 실제 읽은 원문과 대조한 인용만 근거로 사용합니다. 키 설정과 한도 검사는 [백엔드 안내](backend/README.md)에 설명되어 있습니다.

## 프로덕션 실행

```bash
npm run build
npm run start
```

프로덕션 환경에서도 백엔드가 실행 중이어야 하며, LLM 제공자 키는 백엔드에만 설정해야 합니다. 브라우저에 비밀 키를 노출하거나 `NEXT_PUBLIC_` 변수로 설정하지 마세요.

## Render 배포 준비 (미실행)

코드는 배포 가능 상태로 준비되어 있으나 실제 배포는 보류 중입니다.

- 프론트/백엔드 Docker 이미지: 루트 `Dockerfile`, `backend/Dockerfile`
- Render 블루프린트: `render.yaml` (대시보드에서 적용, 시크릿 9종 입력 필요)
- 공개 배포용 환경변수 (기본값은 로컬 동작, 설정해야만 열림):
  - 프론트: `FACTLENS_PUBLIC_DEPLOY=1`, `FACTLENS_ALLOW_REMOTE_BACKEND=1`,
    `FACTLENS_BACKEND_URL=https://<백엔드>` , `FACTLENS_BACKEND_SECRET=<공유 시크릿>`
  - 백엔드: `BACKEND_SHARED_SECRET=<공유 시크릿, 프론트와 동일>`
- 유료 Starter 이상 권장 (무료 티어 슬립으로 장시간 검증이 중단될 수 있음)
