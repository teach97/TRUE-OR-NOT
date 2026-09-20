# 팩트체크 에이전트 UI MVP 작업 인계서

## 다음 작업자용 실행 인계 — 6-B 완료, 6-C·7 남음

### 최신 브라우저 검증 체크포인트: 실제 결과·내보내기·장애 표시 확인

- localhost:3000에서 실제 FastAPI/모델 요청으로 “물은 수소와 산소로 이루어져 있다.”를 검증했습니다. 완료 화면에 후보 1개, 출처 6개, 판정 “대체로 확인됨”이 표시되었습니다. 이는 실행 결과이며 판정 품질 전체 보증은 아닙니다.
- 결과 내보내기를 클릭해 받은 JSON을 파싱했습니다. demo=false, claims=1, sources=6, evidence=1, evidence의 sourceId 참조 및 quoteVerified=true를 확인했습니다. 다운로드 결과는 로컬 `.playwright-cli/factlens-result.json`에 있으며 원문 자료와 인용을 별도로 재대조한 검증은 아닙니다.
- FastAPI 종료 후 재요청 시 “검증 실패: 검증 백엔드에 연결할 수 없습니다. 다시 시도하실 수 있습니다.”가 표시되어 장애를 사실 판정으로 오인하지 않았습니다.
- 이전 실행에서는 검색 진행→사용자 취소→재시작→완료 문구를 확인했습니다. 자동 대기의 `/검증 완료/`가 실제 “검증이 완료되었습니다”와 불일치해 발생한 260초 타임아웃은 테스트 선택자 오류였습니다. 이번에는 실제 문구로 대기해 성공했습니다.
- 남은 6-C: 서버 측 취소 정리 계측, 화면 이탈, 장애 복구 후 재시도, 상세 근거 표시 검증. 127.0.0.1:3000 접속은 LOCAL_ONLY 오류가 남고 localhost:3000은 동작하므로 별도 원인 확인이 필요합니다. 6-C 전체 완료로 표시하지 않습니다.
- 테스트 브라우저와 FastAPI는 종료했습니다. Next 개발 서버 종료 도구가 타임아웃되어 3000 서버 응답이 남아 있음을 확인했습니다. 추가 종료 확인이 필요합니다. 앱 코드는 이번에 변경하지 않았습니다.

### 최신 수정 체크포인트: 로컬 요청 403 회귀 수정

- Next.js가 주입하는 단일 loopback `x-forwarded-for` 값(127.0.0.1, ::1, ::ffff:127.0.0.1)을 허용했습니다. 외부 주소·복수 주소·빈 값은 계속 거부하며 Origin/Forwarded/production 제한을 유지합니다.
- 헤더는 인증 수단이 아니므로 기본 `npm run dev`를 `next dev --hostname 127.0.0.1`로 제한했습니다. 이미 실행 중인 서버에는 소급 적용되지 않으므로 재시작이 필요합니다. 공용 인터페이스 바인딩 또는 프록시 공개는 지원하지 않습니다.
- 회귀 테스트가 수정 전 403 != 200으로 실패하는 것을 확인한 후 수정했습니다. route 테스트 6개, 타입 검사, 프로덕션 빌드 통과. 브라우저 재검증 및 전체 6-C는 아직 미완료입니다.
- 기존 shader-settings-config.ts 변경은 다른 작업으로 간주하여 수정/커밋 대상에서 제외했습니다.

### 최신 실행 체크포인트: 6-C 브라우저 연결 검사 — 차단 원인 발견, 미완료

- FastAPI를 loopback 8010 포트에서 실행한 뒤 실제 Next.js 3000의 GET /api/fact-check가 configured=true를 반환하는 것을 확인했습니다.
- Playwright 실제 브라우저에서 원문 입력·외부 전송 동의·검증 시작을 수행했습니다. POST가 LOCAL_ONLY 403으로 거부되어 UI에 안전한 오류와 재시도 가능한 시작 버튼이 표시되었습니다. 모델 검증 결과는 얻지 못했습니다.
- 원인: route.ts가 x-forwarded-for 헤더의 존재만으로 요청을 차단하지만, 설치된 Next.js의 node_modules/next/dist/server/base-server.js는 이 헤더가 없는 직접 요청에도 socket.remoteAddress를 자동으로 채웁니다. 단위 테스트 Request에는 이 자동 주입이 없어 이전 16개 테스트가 놓쳤습니다.
- 다음 작업: Next.js가 주입한 단일 loopback 주소와 외부/복수 전달 주소를 구분하는 정책을 회귀 테스트로 먼저 정의하고 수정합니다. 헤더는 위조 가능하므로 인증 수단으로 취급하지 않으며 개발 서버의 loopback 바인딩도 확인해야 합니다. 보안 검사를 통째로 제거하지 않습니다.
- 이번에는 원인 확인까지만 수행했고 애플리케이션 코드는 변경하지 않았습니다. 진행/완료/취소 전파 검증은 여전히 미완료입니다. FastAPI 실행 세션: proc_f18af0d8a601. 기존 3000 서버는 다른 세션 소유일 수 있으므로 종료하지 않았습니다.

### 최신 체크포인트: 6-B Next.js → FastAPI 프록시

- `app/api/fact-check/route.ts`의 GET은 FastAPI 상태를 조회하고 공개 필드만 반환합니다. POST는 `/api/fact-check/stream`으로 전달합니다. 기존 TypeScript runAgent 호출을 제거하여 provider 중복 호출을 피합니다. 입력 검증 유틸리티만 기존 모듈에서 재사용합니다.
- `.env.example`을 서버 전용 `FACTLENS_BACKEND_URL=http://127.0.0.1:8010` 설정으로 갱신했습니다. 실제 키는 backend/.env에만 필요합니다. 프록시는 HTTP loopback IP 주소만 허용하고 리다이렉트를 거부합니다.
- 로컬 동일 출처·본문 제한·프로세스별 동시 1건 제한을 유지합니다. upstream NDJSON을 전달하며 취소를 upstream fetch/reader에 전파합니다. 프록시 245초 제한, 응답 총 2MB 제한, 진단 정보 없는 HTTP 오류 매핑을 적용했습니다.
- `app/lib/server/route.test.mjs`를 프록시 계약 테스트로 교체했습니다. 상태 필드 투영, 인증정보 미전달, 동시 요청 거부, reader/요청 취소 후 재시도, 외부 backend URL 거부, 입력/출처 차단을 검증했습니다.
- 중단 후 검증을 재실행했습니다. 프론트엔드 테스트 파일 5개에서 **16 tests passed**, `npm run typecheck` 통과, `npm run build` 통과. route 단독 테스트는 5개 통과입니다. 이 기록은 실제 FastAPI 프로세스와 브라우저를 연결한 검증을 의미하지 않습니다.
- **다음 6-C:** 실제 로컬 Next.js 개발 서버와 FastAPI를 실행하여 UI 상태/진행/결과/취소/오류/재시도를 확인합니다. 연결 해제 시 Python 작업 종료도 별도 검증해야 합니다. production POST 차단 정책은 유지되므로 `next start`에서 유료 검증이 차단되는 것을 버그로 오인하지 않습니다.
- 프록시 경로만 변경했으며 화면 디자인은 수정하지 않았습니다. 6단계 전체 완료와 7단계 실서비스 전체 검증 완료로 표시하지 않습니다.



### 최신 추가 체크포인트: 6-A 백엔드 진행 스트림

- `backend/streaming.py`, `backend/tests/test_streaming.py` 추가, `backend/main.py` 수정. 기존 JSON POST는 유지하고 `POST /api/fact-check/stream` NDJSON 엔드포인트를 추가했습니다.
- 네 단계 시작 이벤트 → 계약 검증된 result를 전달합니다. 내부 sourceTexts·provider 진단은 노출하지 않습니다. 단계가 누락되거나 순서가 잘못되면 AGENT_FAILED로 종료합니다.
- 240초 전체 스트림 제한, TIMEOUT/AGENT_FAILED 이벤트, 그래프 iterator 종료 및 asyncio 취소 전파를 구현했습니다. timeout은 스트림 실행 구간 기준이며 요청 본문 수신 시간 제한은 별도로 필요합니다.
- 이번 검증: 전체 Python **101 passed**, 기존 의존성 경고 1건. TestClient + 실제 LangGraph에 테스트 어댑터를 연결한 스트림 검증, 오류/timeout 및 태스크 취소 정리를 확인했습니다. 실제 브라우저 연결 해제→서버 취소는 아직 미검증입니다.
- **6단계 전체 완료가 아닙니다.** Next.js route는 아직 기존 TypeScript provider를 사용합니다. 기존 화면과 API 호출 경로는 전환하지 않았습니다. 실서비스 전체 요청·브라우저 테스트도 수행하지 않았습니다.
- 다음 **6-B**: Next.js GET 상태 및 POST를 FastAPI 스트림으로 프록시 전환합니다. API 키는 Python에만 두고 중복 provider 호출을 제거합니다. localhost 경계·본문 제한·동시성 제한·취소 전파·안전한 오류 매핑을 보존/보강하며 route 및 client 테스트를 추가합니다.
- 이후 **6-C**: UI 진행·결과·오류·취소/화면 이탈·재시도 브라우저 확인, 타입 검사/빌드. 동시 실행 제한과 실제 연결 해제 취소 정리를 확인합니다. 원격 공개 배포하지 않습니다.
- 이번 작업에 커밋·원격 푸시는 포함하지 않았습니다. 다음 세션은 이 기록을 먼저 읽고 6-B부터 진행합니다.


> 이 절과 바로 아래 최신 체크포인트를 우선 적용합니다. 이후의 ‘이전 체크포인트’와 최초 UI MVP 설명은 과거 기록이며, 당시의 미구현·키 부재 설명을 현재 상태로 해석하지 않습니다.

### 현재 상태와 범위

- 작업 루트: `C:/Users/rlagn/Desktop/Develop/frontend_tools/React/my-app`.
- 목표: 기존 Next.js UI를 유지하면서 FastAPI + LangGraph 기반 **로컬 팩트체크 MVP**를 연결합니다. 로그인, DB 영속 저장, 공개 배포는 현재 7단계 범위 밖입니다.
- 실제 구현·검증된 범위는 **주장 추출·검색 후보·HTML/plain text 원문 수집·인용/판정·최종 응답 계약·네 단계 LangGraph 조립까지**입니다. 실제 provider를 사용하는 전체 경로의 운영 확인은 7단계에서 수행합니다.
- `backend/.env`에 사용자 API 키가 설정되어 실제 호출에 성공했습니다. 파일·키 값을 출력하거나 커밋하지 않습니다. 다른 세션에서 키가 없다고 추측하지 말고 존재 여부만 확인합니다.
- 마지막 실행 기록: Python 테스트 **96 passed**, Starlette/AnyIO deprecation 경고 1건. 실제 원문 2개 접근 및 리다이렉트 처리를 확인했고, 기본 workflow 노드 조립도 확인했습니다.
- 기존 작업에 미커밋 변경과 untracked 파일이 다수 있습니다. 초기 Git 상태를 확인하고 사용자 변경을 보존합니다. 문서 저장은 Git 커밋/원격 백업과 다릅니다.

### 전체 단계표

| 단계 | 작업 | 상태 / 완료 범위 |
|---|---|---|
| 1 | LangGraph 실행 기반 | 완료: 네 단계 순서, 상태 전달, 오류 중단 테스트 |
| 2 | FastAPI 스키마·상태 API | 완료: 요청 검증 및 상태 확인 |
| 3 | POST → LangGraph 실행 경계 | 완료: 주입 테스트, 422/502/503 처리 및 최종 계약 검증 |
| 4 | 실제 LLM·주장 추출 | 완료: `.env` 로딩, 추출 전용 그래프, 실제 Luna max 호출 성공 |
| 5 | 검색·원문·인용·판정 | 구현 완료: 5-A/5-B/5-C/5-D. 실제 provider 전체 경로 운영 확인은 7단계에서 수행 |
| 6 | UI·진행 상태·취소·타임아웃 | 진행 중: 6-A 스트림 완료, 6-B 프록시/6-C UI 검증 남음 |
| 7 | 전체 회귀·실행 검증·최종 인계 | 미완료 |

### 5단계 — 검색부터 전체 검증 그래프까지

**5-D 최종 계약·조립까지 완료했습니다. 다음 작업은 6단계 UI 연결입니다.**

- [x] **5-A 검색 커넥터:** 현재 추출된 fact 주장에 대해 실제 검색을 수행하고 후보 출처 URL·제목·기관 정보를 정규화합니다. 검색 완료 여부 확인, URL 중복 제거, 출처 개수 제한, 빈 결과·실패 테스트를 추가합니다. 기존 TypeScript 구현은 참고하되 무검토 복사하지 않습니다. 검색 요약을 검증된 원문 인용으로 취급하지 않습니다.
- [x] **5-B 원문 수집:** 후보 URL의 본문과 접근 상태를 수집합니다. SSRF 방어(내부/loopback/link-local 주소 및 리다이렉트 검증), HTTP/HTTPS 제한, 타임아웃, 응답 바이트 제한을 구현·검증합니다. 접근 실패 시 근거를 만들어내지 않습니다.
- [x] **5-C 인용·판정:** `backend/verification.py`에 원문 인용·claimId/sourceId 무결성 검사, 의견·예측·근거 부족·맥락 누락·상충 근거 판정 규칙을 추가했습니다. 검색 요약은 evidence로 사용하지 않으며, 잘못된 인용·조건 불일치·원문 접근 불가 시 보수적으로 근거 부족으로 낮춥니다.
- [x] **5-D 최종 계약·조립:** `backend/contracts.py`에 `FactCheckResult`·`FactCheckResponse`·상태 계약을 추가하여 `app/lib/fact-check-contract.ts`의 필드와 연결했습니다. claim/source/evidence 교차 참조와 `quoteVerified: true`를 검증하고, `runtime.py`에서 extracting → searching → reading → verifying 네 노드를 실제 어댑터로 조립했습니다. `main.py` 기본 workflow와 상태 API를 연결했으며, 키가 없으면 `configured/workflowReady/webSearch`를 false로 유지합니다.

5단계 완료 조건: 실제 비민감 입력으로 추출→검색→원문→판정 경로를 실행하고, 출처·인용 연결과 근거 부족 처리를 확인해야 합니다. 외부 서비스 실패와 코드 결함을 구분하여 기록합니다.

### 6단계 — 기존 UI 연결

- [ ] 현재 `app/api/fact-check/route.ts`, `app/components/fact-check-client.ts`, 공유 계약과 대시보드를 먼저 읽습니다. 기존 Next.js provider 경로와 Python 경로를 동시에 중복 호출하지 않습니다.
- [ ] Next.js 서버 경계를 통해 FastAPI로 연결하고 API 키를 브라우저에 전달하지 않습니다. 기존 UI 디자인과 레거시 파일은 범위 밖 변경을 하지 않습니다.
- [ ] `extracting/searching/reading/verifying` 단계 이벤트와 최종 결과·오류 이벤트를 전달합니다. 현재 Python 임시 JSON 응답은 기존 NDJSON 클라이언트와 바로 호환되지 않으므로 계약을 맞춥니다.
- [ ] 취소, 화면 이탈, 중복 제출, 동시 실행 제한, end-to-end 타임아웃, 오류 후 재시도를 처리하고 서버 작업 정리까지 검증합니다.
- [ ] 실제 결과와 데모 데이터를 분리합니다. 개발용 mock을 추가한다면 명시적 모드와 테스트 데이터 표시를 사용하며 실제 API 실패 시 몰래 mock으로 대체하지 않습니다.

6단계 완료 조건: 브라우저에서 입력→진행→실제 결과 및 오류/취소 흐름을 확인하고 타입 검사·빌드·회귀 테스트를 통과해야 합니다.

### 7단계 — 최종 검증 및 인계

- [ ] Python 전체 테스트, 프론트엔드 기존 테스트, `npm run typecheck`, `npm run build`를 실행합니다. 프로젝트의 실제 스크립트와 테스트 파일을 확인한 뒤 명령을 선택합니다.
- [ ] 잘못된 JSON, 동의 없음, 긴 본문, provider 실패, 검색 결과 없음, 원문 차단, 인용 불일치, 취소·타임아웃을 검증합니다.
- [ ] 데스크톱·모바일 브라우저에서 기존 화면과 리포트 기능의 회귀 여부를 확인합니다.
- [ ] 비밀정보 노출·Git 제외·서버 전용 키 경계를 점검합니다. 키나 `.env` 원문은 테스트 로그·스크린샷·문서에 넣지 않습니다.
- [ ] 임시 서버/테스트 브라우저를 종료하고 실제 실행 명령, 환경변수 이름, 검증 결과, 미해결 문제를 인계서에 갱신합니다.

### 우선 읽을 파일

| 파일 | 역할 / 주의 |
|---|---|
| `backend/runtime.py` | `.env` 로딩 및 실제 네 단계 전체 그래프 조립 |
| `backend/extraction.py` | 실제 OpenAI 주장 추출 어댑터 |
| `backend/workflow.py` | 네 노드 순차 그래프 팩토리, 어댑터 주입 필요 |
| `backend/main.py`, `backend/schemas.py` | API 경계·요청 검증. 서버 키가 있으면 기본 POST가 조립된 workflow를 실행 |
| `backend/tests/` | 기존 오프라인 회귀 테스트 |
| `app/lib/fact-check-contract.ts` | 기존 프론트엔드 요청·결과·이벤트 계약 |
| `app/lib/server/agent.ts`, `public-source.ts` | 기존 TypeScript 처리 참고. Python 대체 완료로 착각하지 않음 |
| `app/api/fact-check/route.ts` | 기존 Next.js 서버 경계 |
| `app/components/fact-check-client.ts` | 스트림 소비 및 클라이언트 요청 처리 |

### 작업·모델 운영 원칙

1. 작은 세부 작업 하나를 구현하고 테스트한 뒤 결과와 다음 시작점을 이 파일에 저장하고 멈춥니다. 쿼터 소진을 피하기 위해 여러 단계를 연속 진행하지 않습니다.
2. 변경 전 파일을 읽고 Git 상태를 확인합니다. 동작 변경은 실패 테스트→최소 구현→전체 회귀 순서로 진행합니다.
3. 구현용 AI 모델과 서비스 모델을 혼동하지 않습니다. 서비스는 현재 `gpt-5.6-luna` / reasoning `max`를 실제 확인했습니다. 개발 모델의 변경은 사용자 선택이며 이 인계로 변경을 지시하지 않습니다.
4. Luna Max로 개발하는 방안은 논의했지만 변경이 확정된 것은 아닙니다. 사용한다면 보안·인용·판정 로직은 별도 검토를 권장합니다. 모델 성능이나 쿼터 절감량은 비교 측정하지 않았습니다.
5. 로컬 테스트는 `cd backend` 후 `uv sync --locked`, `uv run pytest -q`로 재현합니다. 실제 provider 검증은 유료 호출일 수 있으므로 작고 비민감한 입력으로 제한하고 오프라인 테스트와 구분하여 기록합니다.

## 최신 체크포인트: 5-D 최종 계약·조립 완료

- 추가: `backend/verification.py`, `backend/tests/test_verification.py`. Pydantic strict 모델로 판정 출력과 evidence 후보를 검증하고, `verify_claims` provider adapter는 검증된 원문만 모델에 전달합니다.
- `ground_judgments`는 fact 주장마다 정확히 한 번의 `claimId` 판정을 요구하며, 존재하지 않거나 접근 불가한 `sourceId`, 원문에 없는 인용, 10자 미만 인용, 검색 snippet만 있는 인용을 evidence에서 제외합니다.
- 인용은 수집된 `sourceTexts`에서 공백 정규화 후 실제 포함 여부를 확인합니다. 검증된 원문이 없으면 provider 호출 없이 `insufficient_evidence`로 남기며, 검색 요약·출처 메타데이터는 evidence로 사용하지 않습니다.
- `comparison`이 `same`이 아닌 지지·반박 인용은 직접 근거로 인정하지 않습니다. `missing_context`는 조건 차이가 표시된 배경 인용을 요구하고, 동일 조건의 지지·반박이 서로 다른 출처에서 확인되면 `conflicting_sources`로 구분합니다.
- 의견·예측은 `not_checkable`, 원문 검증이 실패한 사실 주장은 `insufficient_evidence`로 처리합니다. 모델이 일부 허위 인용을 섞으면 유효 인용은 보존하되 판정은 보수적으로 근거 부족으로 낮추고 경고를 추가합니다.
- 추가: `backend/contracts.py`, `backend/tests/test_contracts.py`, `backend/tests/test_runtime_assembly.py`. 최종 결과를 strict Pydantic 모델로 검증하고, 내부 `sourceTexts`·`resolvedUrl` 필드가 HTTP 결과에 섞이지 않도록 공개 계약으로 투영합니다.
- `build_fact_check_result`는 `FactCheckResult`를 통해 원문·주장·출처·evidence 필드를 검증하며, 알 수 없는 ID·미검증 evidence·미연결 evidence를 거부합니다. `main.py`는 임시 비어 있지 않은 dict 검사를 제거하고 `FactCheckResponse`를 검증한 뒤 반환합니다.
- `build_runtime_workflow`는 실제 extraction/search/read/verification 어댑터를 네 단계에 주입하고 verifying 단계에서 최종 결과를 조립합니다. 테스트에서는 fake 어댑터로 네 단계 순서와 최종 frontend 계약을 확인했습니다.
- 상태 API는 backend `.env` 또는 프로세스 환경변수에 키가 없을 때 `configured: false`, `workflowReady: false`, `webSearch: false`, `phase: api-foundation`을 유지합니다. 키가 있으면 `workflow-ready`를 보고하지만 provider 성공을 의미하지는 않습니다.
- 검증: `uv run pytest -q` **96 passed**, `uv lock --check` 통과, `git diff --check` 통과. `uv run python`으로 기본 workflow 노드 `extracting/searching/reading/verifying` 조립을 확인했습니다. 기존 Starlette/AnyIO deprecation 경고 1건은 유지됩니다.
- 실제 provider 전체 경로 실행은 비용·외부 의존성이 있으므로 이번 단계에서 반복하지 않았습니다. 7단계에서 비민감 입력으로 추출→검색→원문→판정 및 실패·근거 부족을 운영 확인해야 합니다.

## 이전 체크포인트: 5-B 원문 수집 완료

- 추가: `backend/sources.py`, `tests/test_sources.py`, `tests/test_source_fetch.py`, `tests/test_read_graph.py`. `backend/workflow.py`에 내부 `sourceTexts` 상태를 추가하였고 aiohttp 의존성/잠금 파일을 갱신했습니다.
- 공개 주소만 반환하는 resolver를 실제 연결에 사용합니다. DNS 응답에 비공개 주소가 하나라도 있으면 거부하고, 검증한 숫자 주소를 connector에 전달하여 재조회하지 않습니다. URL의 명시적 내부 IP도 차단합니다. TLS 검증은 유지하며 환경 프록시·쿠키·자동 리다이렉트는 사용하지 않습니다.
- 매 리다이렉트 대상 URL 및 연결 DNS를 재검증합니다. 최대 리다이렉트 2회, 요청 전체 8초, 응답 512,000 bytes, 저장 본문 18,000자, 출처 최대 6개입니다.
- HTML/plain text만 지원합니다. script/style/noscript/template를 제거하고 공백을 정규화합니다. PDF·압축 응답·빈 문서·접근 실패는 unavailable로 남깁니다. JS 실행, OCR, PDF 파싱은 구현하지 않았습니다. UTF-8 외 문자셋 처리는 제한적입니다.
- `verified`는 원문을 읽었다는 의미이며 사실 판정이나 인용 일치 검증을 의미하지 않습니다. `sourceTexts`는 내부 상태이며 최종 API 응답에 그대로 노출하지 않아야 합니다. `resolvedUrl`로 최종 URL을 보존합니다.
- RED→GREEN 검증 후 전체 **72 passed**, 기존 의존성 경고 1건. 내부/혼합 DNS, 위험한 리다이렉트, 바이트·형식 제한, 빈 본문, 성공/실패 상태, LangGraph 원문 전달을 테스트했습니다.
- 실제 실행: IAPWS MeltSub 페이지의 리다이렉트 후 원문 3,686자 및 example.com 142자를 수집했습니다. 실제 LLM 호출은 이번 단계에서 수행하지 않았습니다.
- UI·FastAPI 기본 전체 workflow는 변경하지 않았습니다. POST 503 유지. 공개 배포 보안 인증 및 전체 실행 취소/타임아웃은 후속 단계 범위입니다.
- **다음은 5-C 인용·판정**이며 이후 5-D 전체 계약/조립을 진행합니다.

## 이전 체크포인트: 5-A 검색 커넥터 완료

- 추가 파일: `backend/search.py`, `backend/tests/test_search.py`, `backend/tests/test_search_errors.py`. 기존 UI·API·모델 설정·의존성은 변경하지 않았습니다.
- 실제 Responses web_search를 요청하고 검색 실행 완료 여부를 확인합니다. fact가 없으면 호출을 생략하며 동의/키가 없으면 네트워크 요청을 보내지 않습니다.
- 후보 URL 정규화·fragment 제거·중복 제거·최대 6개 제한을 적용하였습니다. publisher는 검증된 기관명이 아닌 호스트명이며 제목이 없으면 호스트명을 사용합니다.
- 후보의 `accessStatus: pending`은 Python 내부 임시 계약입니다. 원문 확인 없이 verified로 표시하지 않으며 최종 frontend FactSource와 아직 호환되지 않습니다. 검색 요약·모델 설명을 evidence로 저장하지 않습니다.
- 비 HTTP URL, 자격 증명 포함 URL, 별도 포트, 일부 명시적 내부 주소를 제외합니다. 이는 완전한 SSRF 방어가 아닙니다. DNS·redirect·연결 대상 IP 검증은 반드시 5-B fetcher에서 구현해야 합니다.
- 검색 요청은 90초 전체 제한과 응답 1MB 제한을 적용합니다. 원문 페이지를 직접 요청하지 않습니다.
- 검증: 미구현/실패 처리 RED 후 GREEN, 전체 **46 passed**. 빈 검색 결과, 비사실 주장, 미완료 검색, 동의/키 부재, HTTP 실패, URL 필터링·중복·개수 제한을 확인했습니다.
- 실제 호출: 첫 요청은 SEARCH_FAILED 계열 오류로 종료했으나 상세 원인은 수집하지 못했습니다. 비밀을 제외한 진단 재시도에서는 HTTP 200, completed 응답 및 completed web_search_call을 확인하고 후보 출처 6개를 반환했습니다. 모든 후보는 pending이며 원문 접근 가능성·인용·독립성은 확인하지 않았습니다. 성공 한 번으로 안정성을 보장하지 않습니다.
- 검색 어댑터는 상태 업데이트 함수로 추가되었으며 기본 FastAPI 전체 그래프에는 아직 등록하지 않았습니다. POST 503 유지. 자동 재시도 정책도 추가하지 않았습니다.
- **다음: 5-B 원문 수집**. 그 다음 5-C 인용/판정, 5-D 계약/조립, 6 UI 연결, 7 최종 검증 순서입니다.

## 이전 체크포인트: 4단계 완료 — 실제 주장 추출 확인

- `backend/runtime.py` 추가: backend 기준 `.env`를 읽고 프로세스 환경변수를 우선 적용합니다. 키는 SecretStr로 보관하며 repr에 노출하지 않습니다. 환경변수를 전역 변경하지 않습니다.
- `build_extraction_graph`는 START → extracting → END 구조입니다. 실제 `extract_claims` 어댑터를 주입하여 실행하였습니다. 검색/판정을 흉내 내지 않고 주장 추출에서 종료합니다.
- `python-dotenv` 의존성 및 잠금 파일을 갱신하고 `backend/tests/test_runtime.py`를 추가하였습니다.
- **실제 호출 성공:** backend/.env의 자격 증명으로 OpenAI Responses API에 `gpt-5.6-luna`, reasoning `max`, Structured Outputs 요청을 수행했습니다. 비민감 테스트 문장 `Water freezes at 0 degrees Celsius at standard atmospheric pressure.`에서 fact 주장 1개, 원문 위치 0~68을 반환했습니다. 판정 결과는 생성하지 않았습니다.
- 키 값·provider 원시 응답·인증 헤더는 출력하지 않았으며 `.env`는 수정하지 않았습니다. `git check-ignore backend/.env`로 제외 규칙을 확인했습니다.
- 검증: RED 확인 후 구현, 전체 **36 passed**, 기존 Starlette/AnyIO 경고 1건. 실제 추출 LangGraph 실행까지 확인하였습니다.
- UI 및 전체 팩트체크 POST는 아직 연결하지 않았습니다. `main.py`의 전체 workflow는 여전히 미구성이므로 503을 유지합니다. 자격 증명 확보와 추출 성공을 전체 검증 준비 완료로 표시하지 않습니다.
- **다음은 5단계:** 실제 검색 → 원문 수집 → 인용 검증 → 판정입니다. 작업량이 크므로 검색 커넥터부터 세부 단계로 나누어 진행합니다. 6 UI/진행/취소, 7 전체 회귀 검증은 이후입니다.

## 이전 체크포인트: 4단계 부분 완료 — 실제 호출은 자격 증명 대기

- 공식 모델 문서 https://developers.openai.com/api/docs/models/gpt-5.6-luna 에서 `gpt-5.6-luna`, reasoning `max`, Structured Outputs 지원을 확인하였습니다. 이는 계정별 접근 권한이나 실제 요청 성공을 보장하지 않습니다.
- `backend/extraction.py` 추가: OpenAI Responses 요청을 구성하는 서버 전용 비동기 주장 추출 어댑터입니다. 최대 3개 주장, 원문 연속 인용, 유형 분류, JS 호환 UTF-16 위치를 반환합니다. `store:false`와 요청 타임아웃을 설정합니다.
- 빈 키, HTTP 오류, 미완료 응답, 거절, 중복/원문에 없는 인용, 복수 출력은 오류로 처리하며 가짜 주장을 생성하지 않습니다.
- `backend/tests/test_extraction.py`에 MockTransport 오프라인 테스트를 추가하였습니다. 먼저 실패를 확인한 뒤 구현했으며 전체 **34 passed**, 기존 의존성 경고 1건입니다. `uv lock --check` 통과.
- `httpx`를 runtime 의존성에도 명시하고 잠금 파일을 갱신하였습니다. UI·Next.js·기존 그래프·FastAPI 엔드포인트는 변경하지 않았습니다.
- **막힌 부분:** 프로젝트에는 `.env.example`만 존재하며 backend 환경 파일 및 현재 프로세스의 `OPENAI_API_KEY`가 없습니다. 비밀 값은 읽거나 출력하지 않았습니다. 실제 provider 호출을 하지 않았으므로 4단계 전체 완료가 아닙니다.
- 어댑터는 아직 기본 그래프에 등록하지 않았습니다. API는 계속 503 미구성 상태이며 검색/판정 노드도 미구현입니다. 전체 단계가 없는 상태에서 성공 팩트체크 결과로 포장하지 않습니다.
- 다음 작업: 안전한 로컬 자격 증명 설정 후 작은 비민감 입력으로 실제 주장 추출을 확인하고 LangGraph 추출 노드에 연결합니다. 이 확인 전에는 5단계로 자동 진행하지 않습니다. 키를 채팅이나 저장소에 기록하지 않습니다.
- 추가 한계: 응답 바이트 제한, end-to-end timeout 및 최종 결과 계약은 후속 단계에서 보강해야 합니다.

## 이전 체크포인트: POST → LangGraph 3단계 완료

- 수정: `backend/main.py`, `backend/tests/test_api.py`. 추가: `backend/tests/test_execution.py`. UI·Next.js API·provider 설정·의존성은 변경하지 않았습니다.
- `POST /api/fact-check`에 `FactCheckRequest`를 연결하였습니다. 기본 `get_workflow()`는 `None`이므로 유효한 요청도 **503 NOT_CONFIGURED**로 차단하며 데모 판정을 생성하지 않습니다.
- FastAPI dependency override로 실제 컴파일된 LangGraph와 테스트 전용 어댑터를 주입하여 HTTP 요청 → 네 단계 실행 → 결과 반환을 검증하였습니다. 테스트용 어댑터는 운영 앱에 등록하지 않았습니다.
- 입력 오류·잘못된 JSON: **422 INVALID_REQUEST**. 원문이나 내부 검증 오류를 응답에 반사하지 않으며 그래프를 실행하지 않습니다.
- 그래프 예외·누락/null 결과: **502 AGENT_FAILED**. 내부 provider 진단 및 부분 상태는 반환하지 않습니다. 응답에는 `Cache-Control: no-store`를 설정합니다.
- 현재 성공 계약은 임시 JSON `{result: {...}}`입니다. 결과는 비어 있지 않은 dict인지까지만 검사합니다. 최종 FactCheckResult 스키마, NDJSON 스트리밍 및 클라이언트 호환 연결은 아직 완료하지 않았습니다.
- 검증: 미구현/오류 처리 RED 확인 후 GREEN. 전체 **26 passed**, 기존 Starlette/AnyIO deprecation 경고 1건. TestClient ASGI 요청으로 실제 LangGraph 실행을 검증하였고 외부 LLM 호출이나 브라우저 검증은 하지 않았습니다.
- 총 7단계 중 3단계까지 완료: 1 그래프 기반, 2 API 스키마/상태, 3 POST 실행 경계, **4 실제 LLM·주장 추출·모델 지원 확인**, 5 검색/원문/인용/판정, 6 UI/진행/취소/타임아웃, 7 전체 회귀 검증.
- **다음 한 단계는 4단계**입니다. 실제 모델 식별자와 reasoning 지원을 확인한 뒤 연결해야 합니다. 기존 `gpt-5.6-luna` 및 `max`를 검증 없이 지원된다고 간주하지 않습니다.
- 상태 API는 계속 미구성 상태를 반환합니다. 인증·바이트 제한·취소/타임아웃·공개 배포 보안은 미구현이며 로컬 전용 원칙을 유지합니다.

## 이전 체크포인트: FastAPI 2단계 완료

- 작업 범위: `backend/main.py`, `backend/schemas.py`, `backend/tests/test_api.py`를 추가하고 `backend/pyproject.toml`, `backend/uv.lock`을 갱신하였습니다. 기존 UI·Next.js API·LangGraph 그래프·모델 설정은 수정하지 않았습니다.
- `GET /health`: 프로세스 생존 상태를 반환합니다. 실제 provider 준비 상태를 의미하지 않습니다.
- `GET /api/fact-check`: `configured: false`, `workflowReady: false`, `webSearch: false`, `model: null`, `reasoning: null`을 반환합니다. 비밀 설정을 읽거나 출력하지 않습니다.
- `FactCheckRequest`: 기존 `text`, `focus`, `consent` 필드를 모두 요구합니다. 원문은 보존하며 공백 본문, 추가 필드, 타입 변환, 동의 누락/거부를 차단합니다. 본문 12,000·focus 500 제한은 JavaScript와 동일한 UTF-16 단위를 사용합니다.
- 요청 스키마는 독립 검증만 완료하였습니다. HTTP POST 연결은 아직 없으므로 `POST /api/fact-check`는 405입니다. 해당 요청 스키마는 아직 OpenAPI 요청 본문으로 노출되지 않습니다.
- 검증: 스키마·앱 미구현 RED 확인 후 구현하였습니다. `uv run pytest -q` **18 passed**, `uv lock --check` 통과. Starlette TestClient에서 AnyIO 별칭 관련 의존성 deprecation 경고 1건이 발생하였으나 테스트 실패는 없습니다.
- 실제 Uvicorn을 임시 loopback 포트에서 실행하여 두 GET API의 HTTP JSON 응답을 확인하고 서버를 종료하였습니다.
- 실행: `cd backend` → `uv sync --locked` → `uv run uvicorn main:app --host 127.0.0.1 --port 8010`. 8010은 예시이며 사용 중인 포트는 피해야 합니다.
- **다음 한 단계:** FastAPI POST와 LangGraph를 연결하는 실행 경계를 테스트용 어댑터 주입으로 검증합니다. 기본 실행은 실제 어댑터가 없으면 503으로 차단하며, 가짜 판정을 반환하지 않아야 합니다. 실제 provider 이전과 프론트엔드 전환은 이후 별도 단계입니다.
- 인증, body 바이트 제한, 취소·타임아웃, 외부 서비스 지원 검증, 공개 배포 보안은 아직 구현하지 않았습니다. 현재는 로컬 개발용이며 공개 배포하지 않습니다.
- 단계별 구현·검증·체크포인트 저장 후 중단 원칙을 유지합니다.

## 이전 체크포인트: LangGraph 1단계 완료

> 아래 기존 UI MVP 기록은 과거 기록입니다. 현재 `app/api/fact-check/route.ts` 및 `app/lib/server/agent.ts`가 존재하므로 기존의 API 미구현 설명을 현재 상태로 해석하지 않아야 합니다. 기존 provider의 실서비스 지원 여부는 이번 단계에서 확인하지 않았습니다.

- 작업 범위: `backend/`에 Python LangGraph 실행 기반만 추가하였습니다. 기존 UI, Next.js API, 모델 설정은 수정하지 않았습니다.
- `backend/workflow.py`: 명시적으로 전달받은 비동기 어댑터를 `extracting → searching → reading → verifying` 순서로 실행합니다. 기존 프론트엔드 단계 이름을 유지합니다.
- `backend/pyproject.toml`, `backend/uv.lock`: LangGraph 및 테스트 의존성을 관리합니다. 실제 설치 버전은 LangGraph 1.2.11입니다.
- `backend/.gitignore`: 가상환경, 캐시, 비밀 환경설정 파일을 제외합니다.
- `backend/tests/test_workflow.py`: 실행 순서·상태 전달, 단계 스트리밍, 실패 시 후속 실행 중단을 검증합니다.
- 검증: 최초 미구현 실패 확인 후 구현하였으며, `cd backend && uv run pytest -q` 결과 **3 passed**입니다. `git diff --check`도 통과하였습니다.
- 중요: 실제 LangGraph 엔진을 실행하였지만 어댑터는 테스트 전용입니다. LLM·검색 호출, FastAPI, 프론트엔드 연결, HTTP 입력 검증, 취소, 영속 저장은 아직 추가하지 않았습니다. 내부 TypedDict는 HTTP 검증 스키마가 아닙니다.
- 재실행: `cd backend` → `uv sync --locked` → `uv run pytest -q`.
- **다음 한 단계:** FastAPI 요청 스키마·상태 확인 API를 추가하고 테스트합니다. 기존 Next.js 경로 교체나 provider 이전은 별도 단계로 진행합니다.
- 작업 방식: 한 단계씩 구현·검증하고 이 체크포인트를 갱신한 뒤 중단합니다. 여러 단계를 한 번에 진행하지 않습니다.


- **작성일:** 2026-09-18 (KST)
- **프로젝트 경로:** `C:/Users/rlagn/Desktop/Develop/frontend_tools/React/my-app`
- **현재 상태:** Next.js App Router 기반 프론트엔드 UI MVP 구현 완료
- **실제 백엔드 연결:** 아직 연결하지 않음. 현재 검증 흐름과 결과는 데모 상태임

## 1. 작업 요약

설치되어 있던 시각 효과·애니메이션 패키지를 활용하여 한국어 중심의 다크 글래스모피즘 팩트체크 대시보드를 구현하였습니다.

구현된 주요 영역은 다음과 같습니다.

- 주장 입력 및 검증 시작 UI
- 검증 파이프라인 진행률 표시
- 최근 검증 결과 목록
- 신뢰도·출처 커버리지·검토 대기 지표
- 출처 품질 패널
- 시스템 활동 로그
- 데스크톱 사이드바 및 모바일 오프캔버스 메뉴
- PNG 리포트 내보내기
- 쉐이더 배경과 Liquid Glass 카드 효과
- Motion 및 Anime.js 기반의 상태·진입 애니메이션

## 2. 실행 방법

프로젝트 루트에서 다음 명령을 실행합니다.

```bash
npm ci
npm run dev
```

개발 서버 기본 주소는 다음과 같습니다.

```text
http://localhost:3000
```

프로덕션 빌드 및 실행은 다음과 같습니다.

```bash
npm run build
npm run start
```

정적 타입 검사는 다음 명령으로 실행합니다.

```bash
npm run typecheck
```

## 3. 주요 파일과 책임

| 파일 | 역할 |
|---|---|
| `app/page.tsx` | Next.js 홈 페이지에서 대시보드 컴포넌트를 렌더링합니다. |
| `app/components/fact-check-dashboard.tsx` | 대시보드 전체 UI, 상태, 이벤트, 데모 검증 흐름을 담당합니다. |
| `app/globals.css` | 전체 색상 토큰, 글래스모피즘, 반응형 레이아웃, 모바일 메뉴, 카드 스타일을 담당합니다. |
| `app/layout.tsx` | App Router 루트 레이아웃 및 페이지 메타데이터를 담당합니다. |
| `next.config.ts` | 현재 기본 Next.js 설정을 유지합니다. |
| `postcss.config.mjs` | Tailwind CSS v4 PostCSS 플러그인을 설정합니다. |
| `tsconfig.json` | Next.js TypeScript 설정 및 보존된 React Router 파일 제외 규칙을 포함합니다. |
| `package.json` | 실행 스크립트와 의존성을 정의합니다. |
| `package-lock.json` | 재현 가능한 npm 의존성 트리를 고정합니다. |

## 4. 현재 사용 중인 시각 효과 패키지

| 패키지 | 버전 | 현재 사용처 |
|---|---:|---|
| `@paper-design/shaders-react` | `0.0.81` | `MeshGradient` 기반 배경 쉐이더 |
| `liquid-glass-react` | `1.1.1` | 카드·입력 패널의 Liquid Glass 효과 |
| `motion` | `13.4.0` | 페이지 진입, 카드 등장, 상태 전환, 토스트 애니메이션 |
| `animejs` | `4.5.0` | 실시간 상태 점(`pulse-signal`) 펄스 애니메이션 |
| `html2canvas` | `1.4.1` | 대시보드 PNG 리포트 내보내기 |
| `@shadergradient/react` | `2.4.20` | 설치 완료, 현재 화면에서는 미사용 |
| `@react-three/fiber` | `9.7.0` | 설치 완료, 추후 3D/WebGL 확장용 |
| `@react-three/drei` | `10.7.8` | 설치 완료, 추후 Three.js 보조 컴포넌트용 |
| `three` | `0.186.0` | 설치 완료, 현재 화면에서는 미사용 |
| `three-stdlib` | `2.36.1` | 설치 완료, 추후 Three.js 확장용 |
| `camera-controls` | `3.1.2` | 설치 완료, 현재 화면에서는 미사용 |

## 5. 화면 구조

### 5.1 전역 화면

- 좌측 데스크톱 사이드바
- 상단 워크스페이스 헤더
- 오늘의 검증 인사이트 영역
- 새 검증 입력 카드
- 네 개의 요약 지표 카드
- 최근 검증 목록
- 출처 품질 패널
- 시스템 활동 로그
- 하단 검증 원칙 안내

### 5.2 반응형 처리

- 데스크톱에서는 좌측 사이드바와 2열 콘텐츠 레이아웃을 사용합니다.
- 모바일에서는 사이드바가 오프캔버스 메뉴로 전환됩니다.
- 390px 폭에서 가로 스크롤이 발생하지 않도록 확인하였습니다.
- 모바일 메뉴가 열리면 배경을 불투명하게 처리하여 메뉴 글자와 본문이 겹쳐 보이지 않도록 하였습니다.

### 5.3 Liquid Glass 구현 주의사항

`liquid-glass-react`는 내부적으로 여러 레이어를 Fragment 형태로 렌더링하고 콘텐츠 크기를 측정합니다. 일반적인 문서 흐름에 바로 넣으면 카드 위치와 콘텐츠 너비가 어긋날 수 있으므로 `GlassPanel`에서 다음 구조를 유지해야 합니다.

```tsx
<div className="glass-surface">
  <div className="glass-sizer" aria-hidden="true">
    {children}
  </div>
  <LiquidGlass className="glass-live" ...>
    {children}
  </LiquidGlass>
</div>
```

`glass-sizer`는 레이아웃 높이를 확보하는 숨김 측정 레이어이고, 실제 인터랙션은 `glass-live` 내부 콘텐츠에서 처리합니다. 관련 CSS의 `.glass-live .glass` 및 `.glass-sizer` 규칙을 임의로 삭제하지 않아야 합니다.

## 6. 현재 인터랙션 동작

### 주장 검증 흐름

1. 입력창에 주장을 입력합니다.
2. `검증 시작` 버튼 또는 `Ctrl/Cmd + Enter`를 실행합니다.
3. 상태가 `checking`으로 전환됩니다.
4. 주장 분해 → 출처 대조 → 맥락 평가 단계와 진행률이 표시됩니다.
5. 진행이 완료되면 결과 스트립이 `확인 대기 완료`, 신뢰도 `88%`로 변경됩니다.
6. 해당 주장이 최근 검증 목록의 맨 앞에 추가됩니다.

현재 단계 진행은 실제 API 요청이 아닌 클라이언트 타이머로 구현되어 있습니다.

### 리포트 내보내기

`리포트 내보내기` 버튼은 `html2canvas`로 `#factcheck-dashboard`를 캡처하여 다음 파일명으로 다운로드합니다.

```text
factcheck-agent-report.png
```

WebGL 쉐이더 캔버스는 `ignoreElements`로 제외합니다. 이 처리를 하지 않으면 `preserveDrawingBuffer=false`인 WebGL 컨텍스트를 복제할 때 브라우저 경고가 발생할 수 있습니다.

### 데모 메뉴

아직 실제 페이지가 연결되지 않은 메뉴는 토스트로 `준비 중` 상태를 표시합니다.

- 리포트 보관함
- 출처 모니터
- 검증 가이드
- 설정
- 도움말
- 전체 보기
- 상세 결과
- 출처 품질 상세

## 7. 검증 결과

다음 검증을 완료하였습니다.

| 검증 항목 | 결과 |
|---|---|
| `npm run typecheck` | 통과 |
| `npm run build` | 통과 |
| Next.js 프로덕션 서버 실행 | `next start -p 3011`로 확인 |
| 로컬 HTTP 접근 | `http://127.0.0.1:3011/` 응답 확인 |
| 데스크톱 브라우저 렌더링 | 확인 |
| 390px 모바일 렌더링 | 확인 |
| 모바일 메뉴 열기 | 확인 |
| 주장 입력 → 진행률 → 목록 추가 | 확인 |
| PNG 리포트 다운로드 | 확인 |
| 리포트 캡처 후 콘솔 오류 | 오류 0개, 경고 0개 |
| `git diff --check` | 통과 |

프로덕션 검증에 사용한 서버는 검증 후 종료하였습니다.

## 8. 현재 한계

현재 구현은 UI MVP이며 다음 항목은 아직 실제 서비스 수준으로 연결되지 않았습니다.

1. **팩트체크 API 미연결**
   - 실제 LLM 또는 FastAPI 요청을 보내지 않습니다.
   - 검증 진행률과 결과는 프론트엔드 데모 상태입니다.

2. **실제 출처 수집 미연결**
   - 정부 데이터, 언론, 논문, 검색 API 등의 커넥터가 없습니다.
   - 화면에 표시되는 출처 수와 품질 점수는 데모 값입니다.

3. **메뉴 페이지 미구현**
   - 보관함·출처 모니터·설정·도움말은 토스트만 표시합니다.

4. **정적 지표**
   - `2,648`, `92.4%`, `78%` 등의 값은 정적 샘플 데이터입니다.

5. **시간 정보 정적 표시**
   - `2026. 09. 18 14:32:09`는 현재 하드코딩된 데모 값입니다.

6. **인증 및 사용자 저장 기능 미구현**
   - 계정 메뉴와 워크스페이스는 시각적 UI만 제공하며 실제 인증·권한·저장은 없습니다.

## 9. 다음 작업 권장 순서

### 1단계: API 계약 확정

실제 백엔드 연결 전에 요청·응답 구조를 확정하는 것이 우선입니다. 예시는 다음과 같습니다.

```http
POST /api/fact-check
Content-Type: application/json
```

```json
{
  "claim": "검증할 주장"
}
```

응답 예시:

```json
{
  "verdict": "verified",
  "confidence": 0.88,
  "summary": "판정 근거 요약",
  "sources": [
    {
      "title": "출처 제목",
      "url": "https://example.com/source",
      "publisher": "출처 기관",
      "publishedAt": "2026-09-18"
    }
  ]
}
```

위 API는 현재 저장소에 구현되어 있지 않은 **제안 계약**입니다. 실제 백엔드 계약을 확정한 뒤 적용해야 합니다.

### 2단계: 데모 타이머를 API 요청으로 교체

`app/components/fact-check-dashboard.tsx`의 다음 부분을 교체합니다.

- `checkState` 기반 타이머 진행 로직
- `setTimeout`으로 결과를 추가하는 부분
- 고정된 `confidence`, `sources`, `verdict` 값

권장 구현 방식:

- `AbortController`를 사용하여 중복 요청과 화면 이탈을 처리합니다.
- `loading`, `success`, `error` 상태를 분리합니다.
- API 오류와 출처 부족 상태를 별도 UI로 표시합니다.
- 사용자 입력은 서버에 전달하기 전 길이·빈 문자열·최대 크기를 검증합니다.

### 3단계: Next.js 서버 경계 추가

외부 API 키나 LLM 인증정보는 클라이언트 컴포넌트에 넣지 않아야 합니다. 다음 중 하나를 권장합니다.

- Next.js Route Handler: `app/api/fact-check/route.ts`
- 별도 FastAPI 백엔드 호출
- 서버 측 환경변수 기반 provider adapter

인증정보, API 키, OAuth 토큰, 비밀키는 저장소에 넣지 말고 `.env.local`에만 보관해야 합니다. 저장소에는 값을 기록하지 않고 `[REDACTED]`로 처리해야 합니다.

### 4단계: 결과 상세 화면 구현

- 판정 근거 요약
- 주장 원문과 문장 단위 분석
- 출처별 찬성·반대 근거
- 출처 발행일·기관·신뢰도
- 상충하는 정보 표시
- 결과 공유·리포트 저장

### 5단계: 실제 데이터 기반 지표 연결

- 검증 완료 수
- 평균 신뢰도
- 평균 응답 시간
- 출처별 통과율
- 실패·재검토 비율

각 지표는 API 또는 저장소에서 읽도록 변경해야 합니다.

## 10. 보존된 React Router 레거시 파일

다음 파일은 참고·롤백용으로 보존되어 있으나 현재 Next.js 스크립트에서는 사용하지 않습니다.

```text
app/root.tsx
app/routes.ts
app/routes/
app/welcome/
react-router.config.ts
vite.config.ts
app/app.css
```

`tsconfig.json`의 `exclude`에 레거시 파일이 포함되어 있습니다. 실제 삭제는 별도의 정리 작업으로 진행해야 하며, 현재 인계 범위에서는 삭제하지 않습니다.

## 11. 인계 체크리스트

- [x] Next.js App Router 홈 화면 구현
- [x] 한국어 다크 글래스모피즘 스타일 구현
- [x] Paper Design 쉐이더 배경 연결
- [x] Liquid Glass 카드 연결
- [x] Motion 진입·상태 애니메이션 연결
- [x] Anime.js 상태 펄스 연결
- [x] html2canvas PNG 내보내기 연결
- [x] 데스크톱·모바일 레이아웃 확인
- [x] TypeScript 검사 및 production build 확인
- [x] 데모 검증 흐름 확인
- [ ] 실제 FastAPI 또는 LLM API 연결
- [ ] 실제 출처 수집 및 인용 처리
- [ ] 사용자 인증 및 저장소 연결
- [ ] 메뉴별 상세 페이지 구현
- [ ] 실제 데이터 기반 지표 연결

## 12. 다음 작업자에게 전달할 핵심 사항

현재 결과물은 **시각적 방향과 사용자 흐름을 검증하기 위한 프론트엔드 MVP**입니다. 실제 팩트체크 기능을 추가할 때에는 UI를 먼저 크게 변경하기보다 `handleSubmit`의 데모 타이머를 실제 API 요청 상태 머신으로 교체하고, API 응답을 `checks` 데이터 구조에 매핑하는 방식으로 진행하는 것이 안전합니다.

특히 `LiquidGlass`의 측정용 `glass-sizer` 구조와 WebGL 캡처 제외 설정은 현재 레이아웃과 리포트 export 안정성에 필요하므로 유지해야 합니다.
