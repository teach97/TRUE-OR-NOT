# Agent State 및 Node 설계

기준일: 2026-10-08. 코드 기준: `a30c704`의 메인 팩트체크 그래프입니다.

## Agent State 설계

Node 간 공유할 입력·처리 결과·재탐색 정보를 보관합니다. 주석의 분석·검색·수집·검증·응답은 아래 5개 Node를 뜻하며, `생성 → 사용: 의미` 순서입니다.

```python
from typing import Any, TypedDict

class FactCheckState(TypedDict, total=False):
    text: str                              # 요청·분석 → 분석·검색·검증·응답: 검증 본문
    focus: str                             # 요청 → 분석·검색·검증·응답: 확인 범위
    consent: bool                          # 요청 → 분석·검색·수집·응답: 외부 전송 동의
    modelPreference: str                   # 요청 → 분석·모델 검색·검증·응답: 모델 선택
    linkUrl: str | None                     # 요청 → 분석·수집·검증·응답: 제공 링크
    image: dict[str, Any] | None            # 요청 → 분석·응답: 이미지 자료·직접 조립 조건
    jevMode: bool                          # 요청 → 검증·응답: JEV 판정·합성 생략 분기
    claims: list[dict[str, Any]]            # 분석·검증 → 검색·검증·응답: 주장·판정·근거 ID
    searchQueries: dict[str, str]           # 분석·검증 → 검색·검증·응답: 주장별 검색어
    searchNotice: str                      # 기본 생성 경로 없음 → 응답: 검색 경고 코드
    stockSymbols: list[str]                 # 검색 → 검색·수집: 금융 출처 정렬·시장 조회
    market: dict[str, Any] | None           # 검색 → 재검색·응답: 시세·일봉 참고 정보
    sources: list[dict[str, Any]]           # 검색·수집 → 수집·검증·응답: 출처·접근 상태
    sourceTexts: dict[str, str]             # 수집 → 검증·응답: 출처 ID별 원문
    sourceSections: dict[str, list[dict[str, Any]]]  # 수집 → 검증: 인용에 연결할 섹션
    evidence: list[dict[str, Any]]           # 검증 → 응답: 검사된 직접 인용·출처·주장 연결
    result: dict[str, Any]                  # 응답 → API·스트림: 공개 최종 결과
    answer: dict[str, Any]                  # 응답 → 같은 Node의 결과 조립: 설명·답변 상태
    answerModel: str | None                 # 응답 → 결과 조립: 답변 모델, 생략 시 None
    answerReasoning: str | None             # 응답 → 결과 조립: 답변 추론 설정
    llmModel: str                          # 분석·모델 검색·검증 → 응답: 처리 모델
    llmReasoning: str                      # 분석·모델 검색·LLM 검증 → 응답: 추론 설정
    claimSnapshot: list[dict[str, Any]]     # 분석 → 검증: 재탐색 때 복원할 주장 사본
    diagnostics: list[dict[str, Any]]       # 검증 → 같은 Node의 복구 판단: 인용 거절 진단
    recoveryRequested: bool                # 분석·검색·검증 → Edge·응답·스트림: 복귀 여부
    recoveryCount: int                     # 분석·검증 → 검색·수집·검증·응답·Edge·스트림: 복귀 횟수
    recoveryTrace: list[dict[str, Any]]     # 분석·검증 → 다음 검증: 재탐색 이유·대상·결과
    excludedSourceUrls: list[str]          # 검증 → 검색·수집: 접근 불가·인용 오류 URL 제외
```

API가 초기 State를 만들고 Node는 반환한 키만 교체합니다. 키 생략이 가능하며 리스트도 자동 누적하지 않습니다. API 키·클라이언트·지역 캐시는 State 밖에서 관리합니다.

## Node 설계

처리 흐름: **입력 분석 → 출처 검색 → 원문 수집 → 주장 검증 → 최종 응답 → END**. 관련 기능은 각 Node 안에서 함께 처리합니다.

```text
Node 이름: 입력 분석 (extracting)
역할: 검증할 주장과 검색어를 만듭니다.
입력 State: text, focus, consent, modelPreference, linkUrl, image
처리: 본문·링크·이미지를 분석하고 최대 3개 주장·인용 위치·유형을 추출합니다.
출력 State: claims, claimSnapshot, llmModel, llmReasoning; 선택적 text·searchQueries; recoveryCount=0, recoveryRequested=False, recoveryTrace=[]
다음 Node: 출처 검색 (searching)
예외 상황: 링크 수집 실패 시 입력 본문 추출을 시도합니다. 빈 주장은 계속 진행하며 Auto 추출 실패는 EXTRACTION_FAILED로 전파합니다.

Node 이름: 출처 검색 (searching)
역할: 검증에 사용할 출처 후보를 찾습니다.
입력 State: claims, searchQueries, text, focus, consent, modelPreference, excludedSourceUrls, recoveryCount, market
처리: 종목 탐지·Tavily/모델 검색·후보 필터링으로 최대 6개 출처를 선택합니다.
출력 State: sources, stockSymbols, market; 모델 검색 시 llmModel·llmReasoning; sourceTexts={}, sourceSections={}, evidence=[], diagnostics=[], recoveryRequested=False
다음 Node: 원문 수집 (reading)
예외 상황: Tavily 실패는 모델 검색으로 전환합니다. 시세 조회 실패는 market=None, 검색 대상 없음은 빈 sources, Auto 모델 검색 실패는 SEARCH_FAILED입니다.

Node 이름: 원문 수집 (reading)
역할: 원문과 섹션을 수집합니다.
입력 State: sources, linkUrl, consent, stockSymbols, recoveryCount, excludedSourceUrls
처리: 제공 링크를 추가하고 최대 4개를 동시에 읽어 접근 상태·최종 URL·출처 그룹을 갱신합니다.
출력 State: sources, sourceTexts, sourceSections
다음 Node: 주장 검증 (verifying)
예외 상황: 개별 수집 실패는 unavailable로 기록하고 진행합니다. 일본어 본문·중복·제외 URL은 제거하며 예상 밖 예외는 전파합니다.

Node 이름: 주장 검증 (verifying)
역할: 판정·직접 근거를 만들고 재탐색을 판단합니다.
입력 State: claims, sources, sourceTexts, sourceSections, text, focus, searchQueries, linkUrl, modelPreference, jevMode, claimSnapshot, recoveryCount, recoveryTrace
처리: fact·unclear를 원문과 비교하고 인용을 검사합니다. 의견·예측은 not_checkable이며 검증할 주장·원문이 없으면 보수적 결과를 만듭니다.
출력 State: claims, evidence, diagnostics, recoveryRequested; llmModel(JEV/LLM)·llmReasoning(LLM); 조건부 searchQueries·excludedSourceUrls·recoveryCount·recoveryTrace
다음 Node: 재탐색 결정 시 출처 검색 (searching), 그 외 최종 응답 (synthesizing)
예외 상황: 거절된 인용은 제거합니다. 메인 그래프의 JevError는 LLM 판정으로 전환하고 Auto LLM 판정 실패는 VERIFICATION_FAILED로 전파합니다.

Node 이름: 최종 응답 (synthesizing)
역할: 답변을 구성하고 공개 결과를 조립합니다.
입력 State: text, focus, consent, modelPreference, claims, sources, sourceTexts, evidence, searchQueries, linkUrl, image, jevMode, llmModel, llmReasoning, market, searchNotice, recoveryRequested, recoveryCount
처리: 직접 조립·LLM 합성·합성 생략을 선택하고 인용·ID 연결을 FactCheckResult로 검사합니다.
출력 State: answer, answerModel, answerReasoning, result
다음 Node: END; API·스트림이 result를 반환합니다.
예외 상황: 적합한 출처 없음·JEV 모드는 합성을 생략합니다. NOT_CONFIGURED·SYNTHESIS_FAILED는 근거 부족 답변으로 처리하고 지정 모델·최종 계약 실패는 전파합니다.
```

재탐색은 미실행 상태에서 사실·불명확 주장이 근거 부족이고 접근 불가 출처 또는 해당 인용 거절이 있을 때 결정합니다. `recoveryRequested=True`, `recoveryCount=1`이면 검색으로 최대 1회 복귀합니다.
복귀 시 주장을 스냅샷으로 복원하고 검색어에 `공식 원문`을 추가하며 문제 URL을 제외합니다. 검색은 원문·섹션·근거·진단을 초기화하고, 두 번째 검증 후에는 응답으로 진행합니다.

공통 예외: 지정 모델 실패는 `MODEL_FAILED`, 선택 모델 미설정은 `MODEL_UNAVAILABLE`, 기타 스트림 실패는 `AGENT_FAILED`입니다. 전체 240초 초과는 `TIMEOUT`이며 재탐색으로 제한을 초기화하지 않습니다.

기준 코드: [State·그래프](../backend/workflow.py), [Node 구현](../backend/runtime.py), [재탐색](../backend/recovery.py), [스트림](../backend/streaming.py).
