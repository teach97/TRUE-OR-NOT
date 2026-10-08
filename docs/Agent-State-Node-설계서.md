# Agent State 및 Node 설계

기준일: 2026-10-08. 기준 코드: `feat/search` 브랜치의 `a4cb245`.

- [Agent State 설계](#agent-state-설계)
- [Node 설계](#node-설계)

## Agent State 설계

True or Not Agent가 입력한 주장을 검증하는 동안 유지할 정보를 `FactCheckState`로 정의합니다. 핵심 공유 정보는 **입력 본문, 추출한 주장, 검색어, 출처, 수집 원문, 검증 근거**입니다. 이후 Node가 같은 정보를 사용하거나 재탐색을 이어갈 수 있도록 State에 보관합니다.

현재 코드의 State 28개 필드를 기준으로 각 값의 생성·사용 관계를 정리합니다. 모델 정보와 최종 출력도 현재 계약에 포함되어 있으므로 함께 설명합니다. 여기서 생성은 Node가 갱신값을 반환하는 것을 뜻하며, Tool 호출 결과도 호출한 Node가 State 형식으로 정리합니다.

### 1. Node 이름

| 설명에 사용하는 이름 | 코드 이름 |
|---|---|
| 입력 분석 Node | `extracting` |
| 출처 검색 Node | `searching` |
| 원문 수집 Node | `reading` |
| 주장 검증 Node | `verifying` |
| 최종 응답 Node | `synthesizing` |

### 2. State 정의

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

### 3. State 값의 생성과 사용

#### 3.1. 요청 입력과 실행 설정

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

#### 3.2. 주장·검색·원문·근거

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

#### 3.3. 재탐색 제어와 복구 자료

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

#### 3.4. 모델 메타데이터

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

#### 3.5. 최종 출력과 선언된 보조 필드

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

### 4. State 갱신과 수명

API는 `FactCheckRequest.model_dump(exclude_defaults=True)`를 초기 State로 전달합니다. `text`, `focus`, `consent`는 요청 필수 필드이며 기본 설정은 생략될 수 있습니다. 처리 결과 필드는 해당 Node가 실행될 때 생성합니다.

| 시점 | 유지·갱신 규칙 |
|---|---|
| 일반 Node 완료 | Node가 반환한 키만 갱신합니다. 반환하지 않은 키는 유지합니다. 별도 reducer가 없어 같은 키의 리스트·딕셔너리는 교체됩니다. |
| 재탐색 결정 | `claims`를 스냅샷으로 복원하고 대상 검색어에 `공식 원문`을 추가합니다. 제외 URL을 정하고 `recoveryRequested=True`, `recoveryCount=1`로 바꿉니다. |
| 재탐색의 검색 시작 | `sourceTexts`, `sourceSections`, `evidence`, `diagnostics`를 비우고 `recoveryRequested=False`로 바꿉니다. 새 출처를 검색합니다. |
| 재탐색의 판정 완료 | 복구 결과를 이력에 기록합니다. 추가 복귀 없이 최종 응답으로 진행합니다. |

State는 요청 실행 중 메모리에 유지됩니다. 현재 메인 그래프에는 checkpointer나 실행 중 State를 저장·재개하는 기능이 연결되어 있지 않습니다.

### 5. State에 보관할 정보의 기준

**다른 Node가 필요로 하는 처리 결과, 단계 선택에 필요한 제어값, 최종 결과 계약에 필요한 정보**를 중심으로 보관합니다.

| 정보 | 현재 처리 위치 |
|---|---|
| 주장·검색어·출처·원문·근거 | 다음 Node가 사용하므로 State에 보관합니다. |
| 재탐색 대상·제외 URL·횟수 | 반복 실행 사이에 공유하므로 State에 보관합니다. |
| 최종 결과와 모델 정보 | 응답 조립·출력 계약에 필요하여 State에 보관합니다. |
| 관련 원문 발췌·프롬프트·HTTP 응답 객체·Node 내부 캐시 | 각 처리 함수의 지역 자료로 관리합니다. |
| API 키·클라이언트·DB 접속정보 | 설정·어댑터에서 관리합니다. State에 포함하지 않습니다. |
| 실행 오류 | 예외와 API·스트림의 오류 응답으로 처리합니다. 현재 State에는 별도 `error` 필드가 없습니다. |

기준 구현은 [workflow.py](../backend/workflow.py), [runtime.py](../backend/runtime.py), [recovery.py](../backend/recovery.py)입니다. State 설계는 현재 계약을 설명하며, 코드 변경이나 필드 추가를 적용하지 않습니다.

## Node 설계

Node는 Agent 내부에서 판단하거나 데이터를 처리하는 단계입니다. 현재 메인 그래프의 5개 Node를 기준으로 설계합니다. 입력 종류별 분석, 검색 Tool 선택, 출처별 수집, 인용 검사 등은 관련 Node 안에서 함께 처리합니다.

입력 State는 해당 Node가 읽는 값이고, 출력 State는 해당 Node가 반환하는 갱신값입니다. 출력에 포함하지 않은 기존 State 값은 유지합니다. 선택적 출력은 실행 분기에 따라 달라집니다.

### 1. 처리 흐름

```text
입력 분석 Node (extracting)
        ↓
출처 검색 Node (searching)
        ↓
원문 수집 Node (reading)
        ↓
주장 검증 Node (verifying)
        ↓
최종 응답 Node (synthesizing)
        ↓
       END
```

주장 검증 Node에서 재탐색을 결정하면 출처 검색 Node로 최대 한 번 돌아갑니다. 입력 분석 Node는 다시 실행하지 않습니다.

```text
주장 검증 Node
        ├─ recoveryRequested=True이고 recoveryCount=1
        │       → 출처 검색 Node → 원문 수집 Node → 주장 검증 Node
        └─ 그 외
                → 최종 응답 Node
```

### 2. 입력 분석 Node (`extracting`)

```text
Node 이름
입력 분석 (extracting)

역할
사용자 입력에서 검증할 주장과 검색어를 만듭니다.

입력 State
text, focus, consent, modelPreference
linkUrl, image

처리
1. 이미지가 있으면 관측문과 주장을 추출하고 text를 교체합니다.
2. 링크만 입력한 경우 본문·자막을 수집하여 주장을 추출합니다.
3. 일반 본문에서 최대 3개 주장과 주장별 검색어를 추출합니다.
4. 주장 인용문·위치·유형을 정리하고 재탐색용 사본을 만듭니다.

출력 State
claims
searchQueries — 별도 검색어가 추출된 경우
text — 링크 본문·이미지 관측문으로 교체한 경우
llmModel, llmReasoning
claimSnapshot
recoveryCount=0, recoveryRequested=False, recoveryTrace=[]

다음 Node
출처 검색 Node (searching)

예외 상황
- 링크 본문·자막 수집 실패 시 입력 본문 추출 경로를 사용할 수 있습니다.
- 본문에서 주장이 없으면 제공 링크의 본문 추출을 추가로 시도합니다.
- 구조화 추출·검사 실패는 모델 정책에 따라 재시도하거나 종료합니다.
- Auto의 모델 시도가 모두 실패하면 EXTRACTION_FAILED가 전파됩니다.
- claims가 비어 있어도 다음 Node로 진행합니다.
```

### 3. 출처 검색 Node (`searching`)

```text
Node 이름
출처 검색 (searching)

역할
주장을 확인할 출처 후보를 찾고 다음 수집 단계의 자료를 준비합니다.

입력 State
claims, searchQueries
text, focus, consent, modelPreference
excludedSourceUrls, recoveryCount, market

처리
1. fact·unclear·prediction 주장과 주장별 검색어를 선택합니다.
2. 종목을 탐지하고 Tavily 또는 모델 웹검색으로 후보를 찾습니다.
3. URL 중복·제외 목록과 후보 선택 규칙을 적용하여 최대 6개를 고릅니다.
4. 필요 시 시장 정보를 조회하고 수집·근거·진단 필드를 초기화합니다.

출력 State
sources, stockSymbols, market
llmModel, llmReasoning — 모델 검색을 사용한 경우
sourceTexts={}, sourceSections={}
evidence=[], diagnostics=[]
recoveryRequested=False

다음 Node
원문 수집 Node (reading)

예외 상황
- 검색할 주장이 없으면 빈 sources를 반환할 수 있습니다.
- Tavily 실패·미설정이면 설정된 모델의 웹검색으로 전환합니다.
- 시장 조회 실패는 market=None으로 처리하며 검증을 계속합니다.
- Auto의 모델 검색 시도가 모두 실패하면 SEARCH_FAILED가 전파됩니다.
```

재탐색에서도 같은 Node를 사용합니다. 제외 URL과 보완된 검색어를 반영하고, 시장 정보는 기존 값을 사용합니다. 이전에 수집한 원문과 근거는 다음 검색에서 자동 재사용하지 않습니다.

### 4. 원문 수집 Node (`reading`)

```text
Node 이름
원문 수집 (reading)

역할
출처 후보의 원문과 섹션을 수집하여 검증에 사용할 자료를 만듭니다.

입력 State
sources, linkUrl, consent
stockSymbols, recoveryCount, excludedSourceUrls

처리
1. 제공 링크가 후보에 없고 제외 대상도 아니면 직접 출처로 추가합니다.
2. 첫 실행에서는 필요한 경우 링크 제목으로 추가 검색합니다.
3. 웹 본문·YouTube 자막을 수집하고 원문 섹션을 정리합니다.
4. 접근 상태·최종 URL·출처 그룹을 갱신하고 중복·제외 출처를 제거합니다.

출력 State
sources
sourceTexts
sourceSections

다음 Node
주장 검증 Node (verifying)

예외 상황
- 개별 수집 실패는 해당 출처의 unavailable 상태로 기록합니다.
- 링크 제목 확인·추가 검색 실패 시 기존 후보를 계속 수집합니다.
- 일본어 본문 출처는 수집 결과에서 제외합니다.
- 본문을 확보하지 못해도 수집 결과를 다음 Node로 전달합니다.
- 예상 밖의 처리 예외는 그래프 실패로 전파됩니다.
```

최대 6개 출처를 대상으로 Node 내부에서 최대 4개를 동시에 읽습니다. 제외된 출처의 본문·섹션도 함께 제거합니다. 재탐색에서는 링크 제목 추가 검색을 반복하지 않습니다.

### 5. 주장 검증 Node (`verifying`)

```text
Node 이름
주장 검증 (verifying)

역할
주장과 원문을 비교하여 판정·근거를 만들고 재탐색 필요 여부를 판단합니다.

입력 State
claims, sources, sourceTexts, sourceSections
text, focus, searchQueries, linkUrl
modelPreference, jevMode
claimSnapshot, recoveryCount, recoveryTrace

처리
1. fact·unclear 주장을 검증 대상으로 선택합니다.
2. 원문 발췌와 주장 문맥을 비교하고 제안된 직접 인용을 검사합니다.
3. 판정·점수·유효 근거·인용 진단을 정리합니다.
4. 접근 불가·인용 오류와 근거 부족을 함께 확인하여 재탐색을 판단합니다.

출력 State
claims, evidence, diagnostics
llmModel, llmReasoning — LLM 판정 경로
llmModel — JEV 판정 경로에서는 jev-latest
recoveryRequested
searchQueries, excludedSourceUrls, recoveryCount — 재탐색 결정 시
recoveryTrace — 재탐색 결정 또는 재탐색 후 결과 기록 시

다음 Node
재탐색 결정 시 출처 검색 Node (searching)
그 외에는 최종 응답 Node (synthesizing)

예외 상황
- 의견·예측은 not_checkable로 처리합니다.
- 검증 대상·읽힌 출처가 없으면 외부 판정 호출 없이 보수적 결과를 만듭니다.
- 거절된 인용은 근거에서 제거하고 판정·진단에 반영합니다.
- jevMode=True에서 JevError가 발생하면 LLM 판정으로 전환합니다.
- Auto의 LLM 판정 시도가 모두 실패하면 VERIFICATION_FAILED가 전파됩니다.
```

재탐색은 아직 재탐색하지 않았고, `fact`·`unclear` 주장이 근거 부족이며, 접근 불가 출처 또는 해당 주장의 `CITATION_REJECTED`가 있을 때 결정합니다. `claims`를 `claimSnapshot`으로 복원하고 대상 검색어에 `공식 원문`을 추가하며 문제 출처 URL을 제외합니다.

두 번째 검증에서는 추가 재탐색을 요청하지 않고 결과 이력만 갱신합니다. 공급자 예외 자체는 검색 단계로 복귀하는 조건이 아닙니다.

### 6. 최종 응답 Node (`synthesizing`)

```text
Node 이름
최종 응답 (synthesizing)

역할
판정과 검증 근거를 바탕으로 답변을 구성하고 공개 결과를 조립합니다.

입력 State
text, focus, consent, modelPreference
claims, sources, sourceTexts, evidence, searchQueries
linkUrl, image, jevMode
llmModel, llmReasoning, market, searchNotice
recoveryRequested, recoveryCount

처리
1. 답변 인용에 적합한 verified 비 YouTube 출처와 본문을 확인합니다.
2. 조건에 따라 직접 답변 조립·LLM 합성·합성 생략을 선택합니다.
3. 답변 인용과 모델 정보를 정리합니다.
4. 요청·주장·출처·근거 참조를 FactCheckResult로 검사하여 결과를 만듭니다.

출력 State
answer
answerModel
answerReasoning
result

다음 Node
END — API·스트림 처리에서 result를 응답으로 반환합니다.

예외 상황
- 적합한 출처가 없거나 jevMode=True이면 합성을 생략합니다.
- NOT_CONFIGURED·SYNTHESIS_FAILED는 insufficient_answer()로 처리합니다.
- 어댑터의 답변이 딕셔너리 형태가 아니면 근거 부족 답변으로 처리합니다.
- 지정 모델의 MODEL_FAILED 등 다른 예외는 전파됩니다.
- 최종 결과의 계약 검사 실패는 그래프 실패로 전파됩니다.
```

직접 조립 조건을 만족하면 추가 생성 호출을 하지 않습니다. 직접 조립·합성 생략 시 답변 모델 정보는 `None`입니다. 현재 합성 생략·일부 생성 실패의 답변 상태는 `insufficient_evidence`로 표현하며 주장 판정은 별도로 유지합니다.

### 7. 공통 예외 처리

위의 실패 이름은 Node 내부의 예외 구분입니다. 지정 모델 실패는 `MODEL_FAILED`, 선택 가능한 모델이 없는 경우는 `MODEL_UNAVAILABLE`로 전파될 수 있습니다. 공개 스트림은 이 두 코드를 구분하고, 나머지 단계 실패는 `AGENT_FAILED`로 안내합니다.

스트림 전체 제한은 240초이며 재탐색으로 초기화하지 않습니다. 시간 초과는 `TIMEOUT`으로 안내하고, 연결 취소는 실행 이터레이터 정리로 전파합니다. 오류 처리를 위한 새 Node나 State 필드는 추가하지 않습니다.

Node 등록·다음 단계의 기준은 [workflow.py](../backend/workflow.py), 처리 조립은 [runtime.py](../backend/runtime.py), 재탐색 판단은 [recovery.py](../backend/recovery.py), 공개 스트림 오류는 [streaming.py](../backend/streaming.py)입니다.
