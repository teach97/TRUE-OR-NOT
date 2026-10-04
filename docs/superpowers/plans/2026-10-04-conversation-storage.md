# Render PostgreSQL 대화 저장 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** My Workspace에 실제 무료 PostgreSQL DB를 생성하고 익명 브라우저 소유권에 따른 대화 저장·목록·복원·이어쓰기·삭제를 제공합니다.

**Architecture:** 브라우저는 동일 출처 Next.js API만 호출하고 FastAPI가 세션 서명과 PostgreSQL 접근을 담당합니다. 저장 요청은 기존 LLM 호출과 분리하며 실패 시 생성된 답변과 저장 재시도 식별자를 유지합니다.

**Tech Stack:** 기존 Next.js 16.3.5·React 19.2.8·FastAPI·Pydantic 2·Python 3.11 이상, asyncpg >=0.30,<1, Render PostgreSQL 18.

**Spec:** [승인된 대화 저장 설계안](../specs/2026-10-04-conversation-storage-design.md). 사용자의 2026-10-04 실제 생성·구현 요청을 설계 승인으로 반영했습니다. 이 구현 계획의 검토와 실행 방식 선택은 아직 대기 중입니다.

## Global Constraints

- DB: `true-or-not-conversations`, `free`, 1GB, Singapore, PostgreSQL 18, My Workspace. 유료 전환·다른 프로젝트 서비스 변경·새 웹서비스 배포는 금지합니다.
- 무료 DB 접근은 생성 30일 뒤 만료되며 백업이 없습니다. 쿠키 유효 기간 30일은 DB 만료와 별개이고, 쿠키 삭제·만료는 데이터 삭제가 아닙니다.
- 쿠키: `ton_session`, HttpOnly, SameSite=Lax, Path=/, HTTPS Secure. HTTP 예외는 loopback 개발 환경만 허용합니다. 전용 서명 키 `CONVERSATION_SESSION_SECRET`은 백엔드에만 둡니다.
- DB 연결 환경 변수는 백엔드의 `DATABASE_URL`입니다. 브라우저 공개 접두사나 Next.js 환경 파일에 DB 연결 비밀을 넣지 않습니다.
- 저장 동의는 기본 꺼짐이며 `storageConsent=true`를 별도로 검사합니다. 전송 동의·목록 복원·새로고침으로 저장 동의를 자동 활성화하지 않습니다.
- 사용자 본문 12,000자, assistant 본문 60,000자, 저장 요청 512KB, 제목 80자, 목록 30개, 메시지 페이지 100개, DB API 작업 전체 3초, 연결 풀 최대 4개입니다.
- `conversations`·`messages` 두 테이블만 사용합니다. UUID 기반 멱등성·소유권 조건·트랜잭션·대화 삭제 CASCADE를 적용합니다.
- 최종 검증 스냅샷만 허용 필드로 정제합니다. 전체 원문·목차 본문·시장 데이터·YouTube API 메타데이터/댓글·이미지 바이너리·진행 상태·공급자 원시 응답은 저장하지 않습니다.
- 기존 검증 결과의 `text`는 사용자 제출 또는 추출된 검증 대상입니다. 외부 페이지의 별도 전체 원문은 추가 저장하지 않습니다. 정제 대상은 기존 공개 계약을 기준으로 검증합니다.
- 추가 LLM·자동 기억 요약·벡터 DB·로그인·여러 기기 동기화는 없습니다. 후속 문맥은 기존 최근 사용자 3개와 이전 원문/주장 제한을 유지합니다.
- 기존 미커밋 10개 항목을 보존합니다. 같은 파일에 변경이 필요한 경우 이번 변경만 부분 스테이징합니다. 사용자 지시에 따라 main에 일반 push하며 force push는 하지 않습니다.

## Review Focus

1. 저장 실패 후 재시도와 대화 삭제가 경합하면 삭제된 대화가 부활하지 않아야 합니다 → Task 2·4의 경합 시험.
2. 100개를 넘는 대화를 복원할 때 이전 페이지를 열 수 있고 마지막 결과를 잘못된 순서로 복원하지 않아야 합니다 → Task 2·4의 페이지 경계 시험.
3. 만료·변조된 쿠키를 조용히 새 소유자로 교체하면 이전 기록이 사라진 것처럼 보일 수 있습니다 → Task 1·3의 명시적 401와 새 세션 확인 시험.
4. 요약·JEV·일반 대화·실패·취소 경로가 하나라도 저장 연결에서 빠지면 일부 기록만 남습니다 → Task 4의 모든 최종 응답 경로 시험.
5. 저장 중 동의 끄기·새 대화·선택 변경·페이지 종료가 발생하면 이전 작업 결과가 다른 대화로 이동하지 않아야 합니다 → Task 4의 지연 응답 시험.

---

## 파일 경계

| 파일 | 책임 |
|---|---|
| `backend/conversation_contracts.py`, `app/lib/conversation-contract.ts` | 저장 전용 입력·출력·스냅샷 정제·복원 계약 |
| `backend/conversation_session.py` | 소유권 서명·검증·환경 설정 검증 |
| `backend/conversation_store.py`, `backend/migrations/001_conversations.sql` | 연결 풀·3초 제한·소유권 SQL·멱등성·페이지·테이블 생성 |
| `backend/conversation_api.py`, `backend/main.py` | 전용 라우터·안전한 오류·생명주기 연결 |
| `app/lib/server/conversation-proxy.ts`, `app/api/conversations/[[...path]]/route.ts` | 쿠키·동일 출처·제한된 프록시·토큰 비노출 |
| `app/components/conversation-client.ts`, `app/components/use-conversation-storage.ts` | 클라이언트 검증·저장 큐·재시도·복원 실행 식별자 |
| `app/components/conversation-history.tsx`, `app/components/fact-check-dashboard.tsx`, `app/app.css` | 동의·목록·이전 페이지·새 대화·삭제·복원·기존 답변 경로 연결 |
| `backend/migrate_conversations.py`, `backend/smoke_test_conversations.py` | 명시적 마이그레이션과 실제 DB 합성 시험 |

## Task 1: 저장 계약과 익명 소유권

**Files:** 위 계약·세션 파일을 생성하고 `backend/tests/test_conversation_contracts.py`, `backend/tests/test_conversation_session.py`, `app/lib/conversation-contract.test.mjs`를 추가합니다.

**Interfaces:** `issue_session(secret: str, now: int) -> str`, `verify_session(token: str, secret: str, now: int) -> UUID`; Python `ConversationCreate`, `MessageCreate`, `StoredMessage`, `StoredSnapshot`, `Conversation`, `ConversationPage`, `MessagePage`; TypeScript 동명 타입과 `sanitizeSnapshot(result: FactCheckResult): StoredSnapshot`, `restoreSnapshot(snapshot: StoredSnapshot): FactCheckResult`. 공개 `Conversation`은 `id/title/createdAt/updatedAt`, `ConversationPage`는 `items/nextCursor`, `MessagePage`는 `conversation/messages/beforeSequence`입니다. 생성 입력은 `storageConsent/createRequestId/title`, 메시지 입력은 `storageConsent/requestId/role/content/status/snapshot`입니다.

- [ ] `test_session_roundtrip_and_expiry`, `test_session_rejects_tampering_and_missing_secret`, `test_message_requires_consent_and_limits`, `test_snapshot_strips_private_and_api_fields` 실패 시험을 작성합니다. `verify_session(issue_session(secret, now), secret, now)`는 유효한 UUID를 반환하며 서명 변조·미래 발급·30일 경과·키 누락은 거부합니다. `storageConsent` 누락/false, user 12,001자, assistant 60,001자, 잘못된 역할·상태·UUID는 거부합니다.
- [ ] 실패 확인: `uv run pytest tests/test_conversation_contracts.py tests/test_conversation_session.py -q`와 `node --test app/lib/conversation-contract.test.mjs`. 아직 모듈이 없어 실패해야 합니다.
- [ ] 위 인터페이스를 구현합니다. 스냅샷 허용 필드를 명시적으로 복사하고 기존 검증 계약의 관계 검사를 적용합니다. 금지 필드는 응답·DB 양쪽에서 빠져야 합니다. 모델/표시용 기본값은 서버 비밀값 없이 복원합니다.
- [ ] 통과 확인: 같은 시험과 왕복 시험에서 인용 URL·제목·점수·원래 `checkedAt`이 동일하며 YouTube 댓글·`sectionText`·`market`·원시 응답은 없음을 단언합니다. 토큰/소유자 ID는 공개 저장 계약에 포함하지 않습니다.
- [ ] 해당 파일만 커밋합니다: `feat: add anonymous conversation contracts`.

## Task 2: 소유권 기반 PostgreSQL 저장과 실제 DB 생성

**Files:** 저장소·마이그레이션·명령 파일과 `backend/tests/test_conversation_store.py`를 생성합니다. `backend/pyproject.toml`·`backend/uv.lock`·`backend/.env.example`을 필요한 항목만 갱신합니다.

**Interfaces:** `ConversationStore.open() -> None`, `close() -> None`, `create(owner: UUID, payload: ConversationCreate) -> Conversation`, `list(owner: UUID, cursor: str | None) -> ConversationPage`, `get(owner: UUID, id: UUID, before: int | None) -> MessagePage`, `append(owner: UUID, id: UUID, payload: MessageCreate) -> StoredMessage`, `delete(owner: UUID, id: UUID) -> None`. 모두 async이며 오류는 `StorageError(code: str)`로 변환합니다.

공통 오류 코드는 `NOT_CONFIGURED`·`STORAGE_UNAVAILABLE`(503), `SESSION_REQUIRED`·`SESSION_INVALID`(401), `NOT_FOUND`(404), `IDEMPOTENCY_CONFLICT`(409), `INVALID_REQUEST`(422), `BODY_TOO_LARGE`(413)입니다. 프록시는 `FORBIDDEN`(403)을 별도로 반환합니다.

- [ ] 실패 시험 작성: 동일 생성 UUID는 같은 대화, 동일 메시지 UUID·역할은 같은 메시지를 반환합니다. 내용 변경 재전송은 409이고 타 소유자의 읽기·추가·삭제는 404입니다. 삭제 후 추가는 404이며 지연 연결/풀 대기는 전체 3초 이내 저장 장애로 종료됩니다.
- [ ] 실패 확인: `uv run pytest tests/test_conversation_store.py -q`. 실제 DB 시험은 환경 변수로 별도 선택하며 로컬 단위 시험은 오프라인으로 실행합니다.
- [ ] Render 목록에서 동일 이름을 먼저 조회합니다. 없을 때만 확인된 My Workspace에 Free·1GB·Singapore·18로 생성합니다. 결과가 불명확하면 목록/상태로 확인하고 재생성하지 않습니다. 사용 가능 상태·만료를 기록하고 자격증명은 출력하지 않습니다.
- [ ] 연결 URL과 무작위 서명 키를 무시되는 `backend/.env`에만 설정합니다. 읽기·쓰기 전에 실제 경로·Git ignore 상태를 확인합니다. 기존 값과 설정을 보존하며 외부 TLS를 사용합니다. 개발 IP 제한은 Render의 지원 기능을 확인하고 적용 또는 미적용 이유를 기록합니다.
- [ ] asyncpg 최대 4개 풀과 트랜잭션을 구현합니다. 연결·풀 획득·SQL·반납을 포함하는 DB 작업 제한을 적용합니다. SQL은 바인딩 매개변수와 소유자 조건을 사용하고 메시지 순서는 대화 행 잠금으로 정합니다. 제목은 최초 입력 최대 80자로 생성합니다.
- [ ] 목록 커서는 `(updated_at, id)` 내림차순, 메시지는 `beforeSequence`로 최신 100개를 조회한 뒤 순서 오름차순으로 반환합니다. `nextCursor`와 `beforeSequence`는 형식·범위를 검증합니다.
- [ ] 반복 가능한 명령 `uv run python migrate_conversations.py`로 두 테이블·제약·인덱스만 생성합니다. 실제 DB 시험에서 생성→조회→동시 중복→재연결 복원→타인 차단→삭제→삭제 후 추가 거부와 101개 메시지 페이지를 확인합니다. 합성 대화만 삭제하고 풀을 종료합니다.
- [ ] 해당 파일만 커밋합니다: `feat: persist conversations in Render PostgreSQL`.

## Task 3: FastAPI와 동일 출처 Next.js API

**Files:** 라우터·프록시·route 파일과 `backend/tests/test_conversation_api.py`, `app/lib/server/conversation-proxy.test.mjs`를 생성합니다. `backend/main.py`에 라우터·풀 종료 생명주기를 연결합니다.

**Interfaces:** 설계의 7개 API를 같은 `/api/conversations` prefix로 제공합니다. 프록시 `handleConversationRequest(req: Request, path: string[]): Promise<Response>`는 쿠키·경로·상태를 처리합니다. FastAPI 전용 헤더 `x-ton-session`에서 서명 토큰을 읽습니다.

- [ ] 실패 시험 작성: 무동의 생성/추가/세션 발급 422, 무세션/변조/만료 401, 타인 대화 404, 중복 내용 변경 409, DB 미설정/장애 503, 과대 본문 413, 교차 출처 변경 요청 403을 확인합니다. 응답·오류에 URL 비밀번호·서명 키·토큰이 없어야 합니다.
- [ ] 실패 확인: `uv run pytest tests/test_conversation_api.py -q`, `node --test app/lib/server/conversation-proxy.test.mjs`.
- [ ] 코드를 작성하기 전에 설치된 Next.js의 `cookies`·Route Handlers·authentication 가이드를 읽습니다. 프록시는 고정 허용 경로·기존 백엔드 주소/공유 키 규칙·redirect error·no-store를 사용하고 클라이언트 소유권 헤더를 그대로 전달하지 않습니다.
- [ ] 상태 API는 비밀값 없이 `configured`·`sessionAvailable`을 제공합니다. 세션 API의 백엔드 토큰은 Next.js가 쿠키로만 변환하고 브라우저 JSON에서 제거합니다. 유효 기존 세션은 유지하며 만료 세션은 명시적 오류 후 사용자의 새 세션 요청으로만 교체합니다.
- [ ] JSON 요청/응답 스트림을 각각 512KB까지 읽습니다. Origin/Fetch Metadata를 검사하고 저장 실패를 검증 실패와 다른 코드/문구로 전달합니다. 기존 공유 키 미들웨어를 우회하지 않습니다.
- [ ] 같은 시험과 기존 `backend/tests/test_api.py` 통과를 확인한 뒤 해당 변경만 커밋합니다: `feat: add private conversation persistence APIs`.

## Task 4: 채팅 저장·목록·복원·이어쓰기 UI

**Files:** 클라이언트·hook·history 컴포넌트와 `app/components/conversation-client.test.mjs`, `app/components/conversation-storage.test.mjs`를 생성합니다. 대시보드·CSS를 최소 변경합니다. 상태 경합 시험은 hook에서 쓰는 순수 전이/큐 로직을 대상으로 합니다.

**Interfaces:** `useConversationStorage()`는 동의 상태·목록·현재 대화·저장 오류와 `setConsent`, `saveMessage(message: MessageCreate, epoch: number): Promise<void>`, `retrySave`, `loadConversation(id: string): Promise<MessagePage | null>`, `loadEarlier(): Promise<MessagePage | null>`, `newConversation`, `deleteConversation`을 제공합니다. `saveMessage`는 생성 당시 대화 실행 ID·요청 UUID를 보존하고 저장 완료를 LLM 생성 성공과 분리합니다. 대시보드는 선택/새 대화/삭제 전에 기존 `stop()`을 실행하고 반환된 페이지를 기존 화면 상태에 반영합니다.

- [ ] 실패 시험 작성: 기본/새로고침/복원 시 동의 false, 동의 없는 요청 0, user→assistant 순서, 저장만 재시도 시 외부 LLM 호출 0, 실패 후 UUID 유지, 중복 클릭 대화 1개, 대화 변경/삭제 뒤 지연 결과 미표시·미저장, 동의 끄기 뒤 신규 저장 0을 확인합니다.
- [ ] 실패 확인: `node --test app/components/conversation-client.test.mjs app/components/conversation-storage.test.mjs`.
- [ ] 클라이언트는 응답을 계약으로 검사하며 쿠키 토큰을 읽거나 저장하지 않습니다. 동의 후 세션·대화 생성과 메시지 쓰기를 직렬화합니다. 생성 UUID와 메시지 UUID를 재시도에도 유지하고 대화 변경 시 이전 쓰기 예약/LLM 요청을 취소합니다.
- [ ] 사이드바·모바일 목록에 새 대화·저장된 제목·이전 페이지·제목 기반 삭제 확인을 추가합니다. 저장 동의 안내에 목적·항목·쿠키 접근 제한·무료 DB 만료·삭제를 표시합니다. 장애 시 ‘답변은 유지되고 저장만 실패했습니다’와 저장 재시도 버튼을 표시합니다.
- [ ] 기존 submit의 일반 대화/요약/JEV/검증 완료/실패/취소 경로를 모두 연결합니다. 데모·환영·이미지·중간 진행은 제외합니다. 일반/요약 응답은 완결 본문으로, 검증 응답은 정제 스냅샷과 완결 본문으로 저장합니다. 실패·취소는 상태가 구분된 메시지로 저장합니다.
- [ ] 복원은 서버 순서·마지막 유효 결과를 `messages`, `liveResult`, 기존 reducer에 반영합니다. 과거 검증 시각을 안내하고 기존 제한된 `gateContext`를 유지합니다. 이전 100개 페이지도 열 수 있도록 구현합니다.
- [ ] 같은 시험·타입 검사와 테스트 브라우저에서 저장→새로고침→선택 복원→이어쓰기→삭제, 저장 끄기, DB 장애 재시도를 확인하고 해당 변경만 커밋합니다: `feat: restore anonymous chat history`.

## Task 5: 통합 검증·운영 안내·인계

**Files:** `README.md`, `backend/README.md`, `docs/작업현황.md`, `docs/Render-배포.md`, `docs/기획서.md` 및 승인 설계·본 계획의 확인 결과를 갱신합니다. 개인정보 안내 페이지는 읽은 뒤 저장 항목·동의·삭제 범위만 갱신합니다.

**Interfaces:** `uv run python smoke_test_conversations.py`는 합성 데이터만 사용하고 결과/시간/검사 항목만 출력합니다. DB URL·토큰·사용자 실제 대화를 출력하지 않습니다.

- [ ] 전체 명령 실행: backend `uv run pytest -q`, `uv lock --check`; frontend `npm test`, 기존 누락된 요약 시험 `node --test app/api/summarize/route.test.mjs`, `npm run typecheck`, `npm run build`, `git diff --check`. 이번 실패와 기존 실패를 구분하여 기록합니다.
- [ ] 실제 DB/브라우저 합성 시험과 연결 재생성·다른 소유권 차단·3초 DB 장애 제한·추가 LLM 호출 0을 검증합니다. 네트워크 지연 수치는 관측값만 기록합니다. 기존 사용자의 서버는 중단하지 않고 별도 포트를 사용합니다.
- [ ] 기본 테스트에 추가된 시험이 모두 포함되는지 확인합니다. 사용한 시험 데이터·프로세스·브라우저를 정리하고 임시 포트 종료를 확인합니다.
- [ ] Graphify 스킬의 update 참조를 읽고 실제 설치 인터프리터로 `graphify update .`를 실행합니다. 비밀 파일을 제외하고 추가 공급자 호출 없이 갱신합니다. 그래프의 기존 포인터 오류를 수정할 경우 원인과 변경 범위를 기록합니다.
- [ ] DB ID·리전·Free·만료일과 실제 검증 결과를 기록합니다. T33·T34는 확인한 범위만 완료로 표시하며 공개 배포·백업·유료 전환은 완료로 표시하지 않습니다.
- [ ] 기존 미커밋 내용을 다시 비교하고 이번 변경만 스테이징합니다. `git diff --cached --check`와 비밀정보 검사를 수행하고 커밋·일반 push합니다. 원격 SHA 일치를 확인한 뒤 완료 보고합니다.

## 실행 방식 검토

| 방식 | 실행과 비용 | 이번 권장 |
|---|---|---|
| Native | 현재 세션에서 직접 단계별 구현 후 최종 독립 검토를 수행합니다. 작업별 별도 컨텍스트 소비가 적습니다. | 권장. 기존 채팅 상태·프록시·저장 계약 사이의 의존성이 높고 사용량 절약 요청이 있습니다. |
| Subagent-driven | 작업마다 새 구현자·검토자, 마지막 전체 검토를 수행합니다. 별도 컨텍스트와 검토 비용이 증가합니다. | 선택 가능 |

계획 검토와 실행 방식 선택을 받은 뒤 Task 1부터 실행합니다. 실제 DB 생성은 Task 2에서 진행하며 그 전에 외부 리소스나 제품 코드를 변경하지 않습니다.
