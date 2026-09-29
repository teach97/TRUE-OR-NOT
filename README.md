# FactLens 프런트엔드

FactLens는 Next.js App Router, TypeScript, Tailwind CSS로 만든 팩트체크 웹 애플리케이션입니다. 프런트엔드는 질문 입력과 검증 진행 표시, 결과·근거 출처 대시보드를 제공하며, 서버 측 API 경로를 통해 로컬 FastAPI 백엔드와 통신합니다.

## 개발 환경 시작

Node.js와 npm을 설치한 뒤 저장소 루트에서 실행합니다.

```bash
npm ci
npm run dev
```

브라우저에서 `http://localhost:3000`을 엽니다. 팩트체크를 실행하려면 별도의 터미널에서 백엔드도 실행해야 합니다. 백엔드 설치와 API 키 설정은 [백엔드 안내](backend/README.md)를 참고하세요.

기본적으로 프런트엔드는 `http://127.0.0.1:8010`의 백엔드에 연결합니다. 다른 로컬 포트를 사용한다면 Next.js 서버 환경 변수 `FACTLENS_BACKEND_URL`에 `http://127.0.0.1:<포트>` 또는 `http://[::1]:<포트>` 형식으로 지정한 뒤 프런트엔드 서버를 다시 시작하세요. 보안을 위해 현재 프록시는 이 두 루프백 호스트만 허용합니다.

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

## Google 검색 결과

선택 기능인 SerpApi 연동을 설정하면 백엔드가 계정의 무료 요금제와 남은 쿼터를 확인한 뒤 Google 자연검색 결과를 탐색합니다. 무료 사용 조건을 확인할 수 없거나 검색에 실패하면 기존 LLM 웹 검색으로 대체하며, 이 경우 결과 순서는 Google 자연검색 순위가 아닙니다. 검색 결과는 출처를 찾는 데만 사용하고, 답변의 인용은 읽어 들인 원문과 대조한 근거만 사용합니다. 키 설정과 한도 검사는 [백엔드 안내](backend/README.md)에 설명되어 있습니다.

## 프로덕션 실행

```bash
npm run build
npm run start
```

프로덕션 환경에서도 백엔드가 실행 중이어야 하며, LLM 제공자 키는 백엔드에만 설정해야 합니다. 브라우저에 비밀 키를 노출하거나 `NEXT_PUBLIC_` 변수로 설정하지 마세요.
