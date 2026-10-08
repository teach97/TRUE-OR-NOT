# Agent State 설계

기준일: 2026-10-08. 기준 코드: `feat/search` 브랜치의 `fa1b940`.

True or Not Agent가 입력한 주장을 검증하는 동안 유지할 정보를 `FactCheckState`로 정의합니다. 핵심 공유 정보는 **입력 본문, 추출한 주장, 검색어, 출처, 수집 원문, 검증 근거**입니다. 이후 Node가 같은 정보를 사용하거나 재탐색을 이어갈 수 있도록 State에 보관합니다.

현재 코드의 State 28개 필드를 기준으로 각 값의 생성·사용 관계를 정리합니다. 모델 정보와 최종 출력도 현재 계약에 포함되어 있으므로 함께 설명합니다. 여기서 생성은 Node가 갱신값을 반환하는 것을 뜻하며, Tool 호출 결과도 호출한 Node가 State 형식으로 정리합니다.

## 1. Node 이름

| 설명에 사용하는 이름 | 코드 이름 |
|---|---|
| 입력 분석 Node | `extracting` |
| 출처 검색 Node | `searching` |
| 원문 수집 Node | `reading` |
| 주장 검증 Node | `verifying` |
| 최종 응답 Node | `synthesizing` |

## 2. State 정의

아래 정의는 [backend/workflow.py](../backend/workflow.py)의 필드명과 타입을 유지하고, 설명을 위해 항목별로 묶었습니다.

```python
from typing import Any, TypedDict


class FactCheckState(TypedDict, total=False):
    # 요청 입력과 실행 설정
    text: str
    focus: str
    consent: bool
    modelPreference: str
    linkUrl: str | None
    image: dict[str, Any] | None
    jevMode: bool

    # Node 사이에 전달하는 처리 자료
    claims: list[dict[str, Any]]
    searchQueries: dict[str, str]
    sources: list[dict[str, Any]]
    sourceTexts: dict[str, str]
    sourceSections: dict[str, list[dict[str, Any]]]
    evidence: list[dict[str, Any]]
    stockSymbols: list[str]
    market: dict[str, Any] | None

    # 재탐색 제어와 복구 자료
    claimSnapshot: list[dict[str, Any]]
    diagnostics: list[dict[str, Any]]
    recoveryRequested: bool
    recoveryCount: int
    recoveryTrace: list[dict[str, Any]]
    excludedSourceUrls: list[str]

    # 모델 메타데이터
    llmModel: str
    llmReasoning: str
    answerModel: str | None
    answerReasoning: str | None

    # 최종 출력
    answer: dict[str, Any]
    result: dict[str, Any]

    # 선언되어 있으나 기본 실행 경로에서 생성하지 않는 필드
    searchNotice: str
```

`total=False`이므로 모든 필드가 처음부터 존재할 필요는 없습니다. API는 요청을 검사한 뒤 초기 State를 만들고, 각 Node가 처리 결과를 채웁니다. TypedDict 자체는 실행 중 값의 유효성을 검사하지 않습니다.

## 3. State 값의 생성과 사용

### 3.1. 요청 입력과 실행 설정

```text
text — 검증할 본문
→ API 요청에서 생성
→ 입력 분석 Node에서 사용하며, 링크 본문·이미지 관측문으로 교체 가능
→ 출처 검색 Node에서 종목 탐지에 사용
→ 주장 검증 Node에서 주장 주변 문맥 확인에 사용
→ 최종 응답 Node에서 질문과 결과 본문으로 사용

focus — 사용자가 확인하려는 범위
→ API 요청에서 생성
→ 입력 분석·출처 검색·주장 검증·최종 응답 Node에서 사용

consent — 외부 전송 동의
→ API 요청에서 생성하며 True인지 검사
→ 입력 분석 Node에서 요청 유효성 검사에 사용
→ 출처 검색 Node에서 검색 허용 여부 확인에 사용
→ 원문 수집 Node에서 링크 제목 추가 검색 조건으로 사용
→ 최종 응답 Node에서 최종 요청 재검사에 사용

modelPreference — 사용할 모델의 선택 정책
→ API 요청에서 생성하며 생략 시 auto
→ 입력 분석·출처 검색·주장 검증·최종 응답 Node의 모델 선택에 사용

linkUrl — 사용자가 제공한 링크
→ API 요청에서 생성
→ 입력 분석 Node에서 링크 본문·자막 추출에 사용
→ 원문 수집 Node에서 직접 제공 출처 추가에 사용
→ 주장 검증 Node에서 링크 기사 제목·날짜 맥락 확인에 사용
→ 최종 응답 Node에서 직접 답변 조립 조건 확인에 사용

image — 이미지의 MIME과 base64 데이터
→ API 요청에서 생성
→ 입력 분석 Node에서 이미지 관측문과 주장 추출에 사용
→ 최종 응답 Node에서 직접 답변 조립 조건 확인에 사용

jevMode — 메인 그래프에서 JEV 판정을 사용할지 나타내는 값
→ API 요청에서 생성하며 생략 시 False
→ 주장 검증 Node에서 JEV 판정 분기에 사용
→ 최종 응답 Node에서 답변 합성 생략 분기에 사용
```

링크 또는 이미지에서 본문이 만들어지면 이후 Node는 교체된 `text`를 기준으로 처리합니다. 화면의 JEV 선택은 별도 빠른 API를 호출하므로, 여기서 설명하는 메인 그래프의 `jevMode` 실행 경로와 구분합니다.

### 3.2. 주장·검색·원문·근거

```text
claims — 검증할 주장과 판정 결과
→ 입력 분석 Node에서 주장 ID·인용문·위치·유형을 생성
→ 출처 검색 Node에서 검색할 주장 선택에 사용
→ 주장 검증 Node에서 사용하고 판정·점수·근거 ID를 추가
→ 주장 검증 Node에서 재탐색 결정 시 추출 당시 형태로 복원
→ 최종 응답 Node에서 답변과 공개 결과 생성에 사용

searchQueries — 주장 ID별 검색어
→ 입력 분석 Node에서 생성
→ 출처 검색 Node에서 검색에 사용
→ 주장 검증·최종 응답 Node에서 관련 원문 발췌 선택에 사용
→ 주장 검증 Node에서 재탐색 대상 검색어를 보완
→ 두 번째 출처 검색 Node에서 보완된 검색어 사용

sources — 출처 후보와 수집 상태
→ 출처 검색 Node에서 검색 Tool 결과를 출처 후보로 정리하여 생성
→ 원문 수집 Node에서 사용하며 직접 링크·수집 상태·최종 URL 등을 갱신
→ 주장 검증 Node에서 근거 출처 확인과 재탐색 판단에 사용
→ 최종 응답 Node에서 답변에 사용할 출처와 공개 출처 목록 구성에 사용

sourceTexts — 출처 ID별 수집 본문
→ 출처 검색 Node에서 빈 딕셔너리로 초기화
→ 원문 수집 Node에서 웹·자막 수집 결과로 생성
→ 주장 검증 Node에서 원문 비교와 직접 인용 검사에 사용
→ 최종 응답 Node에서 발췌 구성과 답변 인용 검사에 사용

sourceSections — 출처 ID별 원문 섹션
→ 출처 검색 Node에서 빈 딕셔너리로 초기화
→ 원문 수집 Node에서 제목·본문 구간을 정리하여 생성
→ 주장 검증 Node에서 직접 인용에 해당하는 섹션 연결에 사용
→ 연결된 섹션 정보는 evidence를 통해 최종 응답 Node로 전달

evidence — 주장과 출처를 연결한 검증 근거
→ 출처 검색 Node에서 빈 리스트로 초기화
→ 주장 검증 Node에서 유효한 직접 인용·출처 ID·주장 ID·관계로 생성
→ 최종 응답 Node에서 근거에 기반한 답변과 공개 결과 구성에 사용

stockSymbols — 입력에서 탐지한 종목 코드
→ 출처 검색 Node에서 생성
→ 출처 검색 Node에서 금융 출처 우선 정렬과 시장 조회에 사용
→ 원문 수집 Node의 선택적 링크 제목 검색에서도 출처 정렬에 사용

market — 시세와 일봉 참고 정보
→ 출처 검색 Node에서 Finnhub Tool 결과를 정리하여 생성
→ 재탐색 시 출처 검색 Node에서 기존 값을 재사용
→ 최종 응답 Node에서 공개 결과의 시장 참고 정보로 사용
```

| 자료 | 보관할 주요 내용 |
|---|---|
| `claims` | 최대 3개 주장. 추출 시 `id`, `quote`, `start`, `end`, `kind`; 판정 후 `verdictCode`, `factScore`, `summary`, `evidenceIds` 등이 추가됩니다. |
| `searchQueries` | `{"c1": "검색어"}`처럼 주장 ID로 연결합니다. 별도 검색어가 없으면 검색 Node가 주장 인용문을 사용합니다. |
| `sources` | 최대 6개 출처의 ID·URL·제목·매체·유형·출처 그룹·접근 상태입니다. 수집 전 `pending`, 수집 후 `verified` 또는 `unavailable`입니다. |
| `sourceTexts` | `{"s1": "수집 본문"}`처럼 출처 ID로 연결합니다. 수집에 성공한 본문을 보관합니다. |
| `sourceSections` | 출처별 `level`, `title`, `text`, `truncated`를 보관합니다. |
| `evidence` | `id`, `claimId`, `sourceId`, `quote`, `quoteVerified`, `relation`과 선택적 번역·섹션 정보입니다. |

주장 위치인 `start`·`end`는 JavaScript와 동일한 UTF-16 코드 단위이며 시작 포함·끝 제외입니다. 모델이 제안한 인용은 수집 원문 등과 대조한 뒤 `evidence`에 넣습니다. 메인 그래프의 JEV 판정 경로는 직접 인용 근거를 생성하지 않습니다.

### 3.3. 재탐색 제어와 복구 자료

```text
claimSnapshot — 추출 당시 주장 사본
→ 입력 분석 Node에서 claims의 각 딕셔너리를 복사하여 생성
→ 주장 검증 Node에서 재탐색 시작 시 claims 복원에 사용

diagnostics — 인용 검사에서 발생한 진단
→ 출처 검색 Node에서 빈 리스트로 초기화
→ 주장 검증 Node에서 CITATION_REJECTED와 주장·출처 ID를 생성
→ 같은 주장 검증 Node의 재탐색 판단에서 사용

recoveryRequested — 검색 단계로 돌아갈지 나타내는 값
→ 입력 분석·출처 검색 Node에서 False로 초기화
→ 주장 검증 Node에서 재탐색 필요 여부를 생성·갱신
→ 그래프의 조건부 Edge와 스트림 처리에서 다음 단계 판단에 사용
→ 최종 응답 Node에서 직접 답변 조립 조건 확인에 사용

recoveryCount — 재탐색 횟수
→ 입력 분석 Node에서 0으로 생성
→ 주장 검증 Node에서 재탐색 결정 시 1로 갱신
→ 출처 검색 Node에서 시장 정보 재사용 여부 판단에 사용
→ 원문 수집 Node에서 링크 제목 추가 검색 반복 방지에 사용
→ 주장 검증 Node와 그래프에서 최대 1회 재탐색 제한에 사용
→ 최종 응답 Node에서 재탐색 안내 생성에 사용
→ 스트림 처리에서도 복귀 횟수 검사에 사용

recoveryTrace — 재탐색 대상·이유·검색어·제외 URL·결과
→ 입력 분석 Node에서 빈 리스트로 생성
→ 주장 검증 Node에서 재탐색 결정 시 pending 이력 생성
→ 두 번째 주장 검증 Node에서 기존 이력을 읽고 grounded 또는 unresolved로 갱신

excludedSourceUrls — 재탐색에서 제외할 URL
→ 주장 검증 Node에서 접근 불가·대상 주장 인용 거절 출처의 URL로 생성
→ 두 번째 출처 검색 Node에서 후보 제외에 사용
→ 두 번째 원문 수집 Node에서 직접 링크·최종 URL 제외에 사용
```

`diagnostics`는 생성된 Node 안에서 복구 판단에 사용하며 State에도 보관하는 보조 자료입니다. `recoveryTrace`는 첫 판정과 두 번째 판정 사이에 공유하는 내부 이력입니다. `recoveryRequested`는 Node뿐 아니라 그래프 실행 제어에서도 소비합니다.

### 3.4. 모델 메타데이터

```text
llmModel — 처리 단계에서 선택한 모델
→ 입력 분석·모델 검색·주장 검증 Node에서 생성·갱신
→ 최종 응답 Node에서 result.model 구성에 사용

llmReasoning — 처리 단계의 추론 설정
→ 입력 분석·모델 검색·LLM 주장 검증 Node에서 생성·갱신
→ 최종 응답 Node에서 result.reasoning 구성에 사용

answerModel — 최종 답변 생성 모델
→ 최종 응답 Node에서 생성
→ 같은 최종 응답 Node에서 result.answer.model 구성에 사용

answerReasoning — 최종 답변 생성의 추론 설정
→ 최종 응답 Node에서 생성
→ 같은 최종 응답 Node에서 result.answer.reasoning 구성에 사용
```

`llmModel`·`llmReasoning`은 단계별 전체 호출 이력을 저장하지 않고 마지막 갱신값을 유지합니다. JEV 판정은 `llmModel`을 `jev-latest`로 갱신하지만 `llmReasoning`은 별도로 갱신하지 않습니다. 직접 답변 조립·합성 생략 시 `answerModel`·`answerReasoning`은 `None`입니다.

### 3.5. 최종 출력과 선언된 보조 필드

```text
answer — 근거 기반 설명과 답변 상태
→ 최종 응답 Node에서 생성
→ 같은 최종 응답 Node에서 공개 결과 조립에 사용

result — 요청·주장·출처·근거·시장 정보·답변을 합친 공개 결과
→ 최종 응답 Node에서 FactCheckResult로 검사한 뒤 생성
→ 후속 Node가 아니라 API·스트림 처리에서 응답 반환에 사용

searchNotice — 검색 관련 안내 코드
→ 현재 기본 메인 어댑터에는 생성 경로 없음
→ 값이 전달되면 최종 응답 Node에서 결과 경고 구성에 사용
```

`answer`와 답변 모델 정보는 최종 Node 내부에서 결과를 조립하고 출력 State에도 남기는 자료입니다. `result`는 그래프 실행과 API 사이의 출력 계약입니다. `searchNotice`는 현재 기본 실행에서 채워지는 공유 정보로 간주하지 않습니다.

## 4. State 갱신과 수명

API는 `FactCheckRequest.model_dump(exclude_defaults=True)`를 초기 State로 전달합니다. `text`, `focus`, `consent`는 요청 필수 필드이며 기본 설정은 생략될 수 있습니다. 처리 결과 필드는 해당 Node가 실행될 때 생성합니다.

| 시점 | 유지·갱신 규칙 |
|---|---|
| 일반 Node 완료 | Node가 반환한 키만 갱신합니다. 반환하지 않은 키는 유지합니다. 별도 reducer가 없어 같은 키의 리스트·딕셔너리는 교체됩니다. |
| 재탐색 결정 | `claims`를 스냅샷으로 복원하고 대상 검색어에 `공식 원문`을 추가합니다. 제외 URL을 정하고 `recoveryRequested=True`, `recoveryCount=1`로 바꿉니다. |
| 재탐색의 검색 시작 | `sourceTexts`, `sourceSections`, `evidence`, `diagnostics`를 비우고 `recoveryRequested=False`로 바꿉니다. 새 출처를 검색합니다. |
| 재탐색의 판정 완료 | 복구 결과를 이력에 기록합니다. 추가 복귀 없이 최종 응답으로 진행합니다. |

State는 요청 실행 중 메모리에 유지됩니다. 현재 메인 그래프에는 checkpointer나 실행 중 State를 저장·재개하는 기능이 연결되어 있지 않습니다.

## 5. State에 보관할 정보의 기준

**다른 Node가 필요로 하는 처리 결과, 단계 선택에 필요한 제어값, 최종 결과 계약에 필요한 정보**를 중심으로 보관합니다.

| 정보 | 현재 처리 위치 |
|---|---|
| 주장·검색어·출처·원문·근거 | 다음 Node가 사용하므로 State에 보관합니다. |
| 재탐색 대상·제외 URL·횟수 | 반복 실행 사이에 공유하므로 State에 보관합니다. |
| 최종 결과와 모델 정보 | 응답 조립·출력 계약에 필요하여 State에 보관합니다. |
| 관련 원문 발췌·프롬프트·HTTP 응답 객체·Node 내부 캐시 | 각 처리 함수의 지역 자료로 관리합니다. |
| API 키·클라이언트·DB 접속정보 | 설정·어댑터에서 관리합니다. State에 포함하지 않습니다. |
| 실행 오류 | 예외와 API·스트림의 오류 응답으로 처리합니다. 현재 State에는 별도 `error` 필드가 없습니다. |

기준 구현은 [workflow.py](../backend/workflow.py), [runtime.py](../backend/runtime.py), [recovery.py](../backend/recovery.py)입니다. 본 문서는 현재 State 계약을 설명하며, 코드 변경이나 필드 추가를 적용하지 않습니다.
