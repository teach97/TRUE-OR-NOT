# True or Not 팩트 검증 에이전트 설계

> 최종 갱신: 2026-09-30. 아래는 현재 코드 기준(as-built)이며, 기획서 v4·PRD와 함께 본다.

## 선택한 연결 방식

- 공급자 우선순위: GPT-6 Luna Max → Gemini 3.8 Flash → Gemini 3.7 Flash
- OpenAI: `gpt-6-luna`; Responses API의 `reasoning.effort = max`와 `service_tier = fast`를 사용합니다. Fast 처리는 표준 대비 약 2배 요금입니다.
- Gemini: `gemini-3.8-flash`, 이후 `gemini-3.7-flash`; Interactions API의 `thinking_level = high`와 Google Search를 사용합니다.
- 인증: 서버 환경변수 `GEMINI_API_KEY`, `OPENAI_API_KEY`
- 주의: ChatGPT/Codex 구독 인증과 별도의 API 인증이며, 모델·웹 검색 사용량은 각 공급자의 API 정책에 따라 과금됩니다.

모델 선택(`modelPreference`: auto·개별 모델)은 브라우저에서 고를 수 있습니다. auto는 위 우선순위대로 시도하고, 개별 선택은 해당 모델만 단독 사용합니다(실패 시 자동 전환 없음). 각 단계에서 현재 공급자 요청이 실패하면 키가 설정된 다음 공급자를 우선순위대로 시도합니다. 성공한 모델 ID와 추론 강도는 결과에 표시합니다.

## 구성

```text
현재 True or Not UI
  → GET /api/fact-check : 설정 유무 확인
  → POST /api/intent : 짧은 입력은 로컬·게이트 답변, 검증 대상은 파이프라인 실행
  → POST /api/fact-check : 동의한 원문·확인 요청 전송 (NDJSON 스트림)
      → 주장 추출 (최대 3개, 원문 위치 검증)
      → 검색 (Tavily 있으면 Tavily, 없으면 LLM 웹검색) + 주가 질문이면 시장 데이터(Toss 우선, Finnhub 대체)
      → 주식 질문이면 신뢰 언론사(investing.com·reuters.com·wsj.com·bloomberg.com) 우선 정렬
      → 검색 메타데이터에 존재하는 URL의 원문 수집 (링크 단독 입력은 페이지 본문으로 폴백)
      → 실제 수집 본문과 인용문 일치 확인
      → 조건·찬반 근거 비교 및 구조화 판정
      → 검증된 원문 인용으로 AI 개요 합성
  → POST /api/fact-check/jev : JEV 빠른 경로 (검색→읽기→TypeSafe 판정, 점수만 반환)
  ← 단계 이벤트 / 최종 결과 / 안전한 오류
```

진행 중 작업은 줄바꿈으로 구분한 JSON 스트림으로 전달합니다. 진행률 퍼센트는 임의로 생성하지 않습니다. 취소·새 문서·예시 불러오기·화면 이탈은 진행 중 요청을 중단하고 늦게 도착한 결과를 무시해야 합니다.

## 신뢰 경계

1. 사용자가 입력한 내용과 웹 자료는 모두 비신뢰 데이터입니다. 문서 속 지시문을 시스템 명령으로 실행하지 않습니다.
2. 모델이 텍스트에 적은 임의 URL은 출처로 승인하지 않습니다. 검색 도구가 반환한 출처 메타데이터에서 수집 대상을 가져옵니다.
3. 실제 본문에서 확인되지 않는 인용은 검증된 근거로 표시하지 않습니다.
4. 출처 접근 실패와 검색 공급자 장애를 구분합니다. 공급자 장애를 사실 판정으로 위장하지 않습니다.
5. 같은 도메인이라는 이유로 동일 원자료라고 단정하지 않습니다. 계보가 불명확하면 미확인으로 남깁니다.
6. 작성일·원자료 관계가 확인되지 않으면 빈 값이나 미확인으로 표시합니다.
7. 직접 근거를 확인할 수 없으면 긍정·부정 판정을 유보합니다.

## 데이터 계약

공유 타입은 `app/lib/fact-check-contract.ts`에 있고, 서버 검증은 `backend/contracts.py`가 맡습니다.

- 요청: 원문(UTF-16 12,000자 이하), 확인 요청(500자 이하), 전송 동의(`consent: true` 필수), 모델 선택, 링크(http/https), 이미지(jpeg/png/webp)
- 응답: 원문 범위가 연결된 주장(UTF-16 start·end), 판정, 요약, 확인·미확인 항목, 경고
- 출처: URL(리다이렉트 최종 우선), 제목, 기관 또는 호스트명, 발행일, 수집 시각, 접근 상태, 검색 출처·검색어·순위, 유튜브 메타
- 근거: 주장·출처 ID, 실제 인용문, 원문 일치 여부, 지지·반박·배경 관계
- 시장 맥락(주식 질문 한정): 심볼, 현재가·전일종가·등락률, 일봉 최대 90개, 출처(tossinvest·finnhub·krx)
- 실행 정보: 실제 지정 모델, 추론 강도, 검증 시각
- 점수 밴드: 0~19 거짓, 20~39 대체로 거짓, 40~59 중립, 60~79 대체로 사실, 80~100 검증된 사실

링크 단독 입력은 서버가 페이지 본문을 수집해 추출하며, 본문이 길면 12,000자 기준으로 재검증합니다. 출처 수집은 서버가 실제 검색으로 얻은 URL에 대해서만 수행합니다.

## 환경 설정

1. `backend/.env`에 필요한 키를 설정합니다. 키 종류는 `backend/README.md`와 `.env.example`을 따릅니다 (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `YOUTUBE_API_KEY`, `TAVILY_API_KEY`, `TYPESAFE_API_KEY`, `FINNHUB_API_KEY`, `TOSS_CLIENT_ID`, `TOSS_CLIENT_SECRET`). 토스증권 키는 WTS에서 발급받고 허용 IP를 등록해야 합니다.
2. 키가 있으면 GPT-6 Luna가 1순위, 이후 Gemini 3.8 Flash와 Gemini 3.7 Flash 순으로 사용됩니다. 키가 없는 공급자는 건너뜁니다.
3. 백엔드를 재시작합니다 (`backend/*.py` 변경 시 필수. 프론트는 저장 시 자동 반영).
4. 화면에서 설정 상태를 확인합니다. 설정됨 표시는 계정의 모델 권한·잔액·호출 성공을 보장하지 않습니다.
5. 공개해도 되는 짧은 원문으로 실제 요청을 실행하고, 결과에 기록된 실제 모델과 출처 링크·원문 근거를 확인합니다.

`.env*` 파일은 Git에서 제외하고 비밀값이 없는 `.env.example`만 예외로 둡니다. `NEXT_PUBLIC_OPENAI_API_KEY`처럼 클라이언트에 노출되는 변수는 사용하지 않습니다.

## 운영 경계

- 이 단계의 API는 로컬 개발·개인 검증용입니다. 인증·사용자별 한도·악용 방지 없이 인터넷에 공개하면 안 됩니다. 공개 배포 준비물(프록시 env 게이트·공유 시크릿·Docker 2종·`render.yaml`)은 갖춰져 있으나 실행은 보류 중입니다.
- API 호출 타임아웃과 취소는 비용을 완전히 되돌리지 않습니다. 요청이 공급자에 전달된 이후 이미 사용된 토큰·검색 비용은 발생할 수 있습니다.
- GPT-6 Luna에는 `reasoning.effort = max`와 `service_tier = fast`, Gemini 모델에는 `thinking_level = high`를 사용합니다. Fast 처리는 표준 대비 약 2배 요금이며, 프로젝트에서 허용하지 않으면 400 오류가 납니다.
- `store:false`는 응답 객체 저장 설정이며, OpenAI의 모든 보존 정책이 없다는 의미가 아닙니다.
- 서버 상태 스트림은 영속 작업 큐가 아닙니다. 프로세스 재시작 시 작업 복구를 보장하지 않습니다.
- 외부 웹페이지를 가져오는 기능에는 사설망·메타데이터 주소 차단, DNS/리다이렉트 검사, 시간·크기 제한이 필요합니다.
- 백엔드에는 인증이 없습니다. loopback 밖으로 노출하지 않는 것이 전제이며, 노출 시 `BACKEND_SHARED_SECRET` 게이트를 켭니다.

## 근거 문서

- GPT-6 Luna 및 max: https://developers.openai.com/api/docs/models/gpt-6-luna
- Gemini Interactions API 및 모델 ID: https://ai.google.dev/gemini-api/docs/interactions-overview
- 웹 검색: https://developers.openai.com/api/docs/guides/tools-web-search
- 구조화 출력: https://developers.openai.com/api/docs/guides/structured-outputs

## 검증 상태

이 문서는 설계와 연결 계약을 설명합니다. 테스트·빌드·브라우저·실제 공급자 연결 결과는 별도 검증 기록에서 구분합니다. API 키가 없는 상태의 모의 테스트를 실제 모델 응답 성공으로 간주하지 않습니다.
