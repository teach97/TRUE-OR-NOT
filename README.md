# True or Not

True or Not은 Next.js 프론트엔드와 FastAPI·LangGraph 백엔드로 주장과 원문 근거를 연결하는 검증 애플리케이션입니다. 제품·코드·남은 작업·배포·QA의 기준은 [문서 안내](docs/README.md)에서 확인합니다.

## 개발 환경 시작

Docker 구성과 같은 Node.js 24와 npm을 권장합니다. 저장소 루트에서 실행합니다.

```bash
npm ci
npm run dev
```

브라우저에서 `http://localhost:3000`을 엽니다. 팩트체크를 실행하려면 별도의 터미널에서 백엔드도 실행해야 합니다. 백엔드 설치와 API 키 설정은 [백엔드 안내](backend/README.md)를 참고하세요.

기본적으로 프런트엔드는 `http://127.0.0.1:8010`의 백엔드에 연결합니다. 다른 로컬 포트를 사용한다면 Next.js 서버 환경 변수 `FACTLENS_BACKEND_URL`에 `http://127.0.0.1:<포트>` 또는 `http://[::1]:<포트>` 형식으로 지정한 뒤 프런트엔드 서버를 다시 시작하세요. 기본 프록시는 이 두 루프백 호스트만 허용하며, Render에서는 아래의 공개·원격 HTTPS 환경 설정을 명시적으로 활성화합니다.

## npm 명령

| 명령 | 설명 |
|---|---|
| `npm run dev` | 개발 서버를 실행합니다. |
| `npm run build` | 프로덕션 빌드를 생성합니다. |
| `npm run start` | 생성된 프로덕션 빌드를 실행합니다. |
| `npm run typecheck` | TypeScript 타입을 검사합니다. |
| `npm test` | 기본 Node 테스트를 실행합니다. 추가 요약 route 테스트는 [QA 안내](docs/qa/검증기준.md)를 따릅니다. |

## 주요 디렉터리

- `app/page.tsx`, `app/layout.tsx`: Next.js 페이지와 공통 레이아웃입니다.
- `app/api/fact-check/route.ts`: 브라우저 요청을 백엔드에 전달하는 서버 측 프록시입니다.
- `app/components/`: 팩트체크 입력·대화와 결과 대시보드 UI입니다.
- `app/lib/`: API 계약, 점수 계산, 출처 탐색 및 서버 유틸리티입니다.
- `backend/`: FastAPI·LangGraph 팩트체크 백엔드입니다.

## 검색과 검증

검증 흐름·모델 설정·API·재탐색과 제한값은 [아키텍처](docs/아키텍처.md), 완료·남은 작업과 미결정 정책은 [작업현황](docs/작업현황.md)을 따릅니다.

## 프로덕션 실행

```bash
npm run build
npm run start
```

프로덕션 환경에서도 백엔드가 실행 중이어야 하며, LLM 제공자 키는 백엔드에만 설정해야 합니다. 브라우저에 비밀 키를 노출하거나 `NEXT_PUBLIC_` 변수로 설정하지 마세요.

## Render 배포 계획 (실환경 검증 대기)

배포 플랫폼은 Render로 결정했으며 실제 배포·원격 검증은 아직 수행하지 않았습니다. Docker 구성·환경변수·공유 시크릿·적용 순서와 완료 기준은 [배포 안내](docs/배포.md)를 따릅니다. 공개 대상·호출 한도·사용자 동의의 미결정 사항은 작업현황에서 관리합니다.
