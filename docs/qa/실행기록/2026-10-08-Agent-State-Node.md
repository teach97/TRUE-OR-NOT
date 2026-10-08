# 2026년 10월 8일 Agent State Node 설계서 확인

범위: 현재 구현을 설명하는 설계서 작성과 문서 연결입니다. 코드 기준은 `feat/search`의 `0d9a690423a5bcb5ae92e46c6bc370bca5b98235`입니다. 애플리케이션 동작과 기존 정책은 변경하지 않았습니다.

## 산출물

- [Agent State Node 설계서](../../Agent-State-Node-설계서.md): State 필드와 수명·작성자, Node 입력·출력·외부 작업·분기, 재탐색·스트림·실패 경계를 설명합니다.
- 문서 안내와 아키텍처에서 상세 설계서로 연결하고 작업현황에 문서 작성 범위를 반영했습니다.

## 코드 대조

| 확인 항목 | 기준 코드 | 확인 내용 |
|---|---|---|
| State 정의 | `workflow.py` | `TypedDict(total=False)`의 28개 필드와 부분 갱신을 반영했습니다. |
| Node와 Edge | `workflow.py`, `runtime.py` | Node 5개와 판정 이후 최대 1회 검색 복귀를 반영했습니다. |
| 입력과 중간 자료 | `schemas.py`, `extraction.py`, `sources.py`, `verification.py` | 본문 교체, UTF-16 주장 위치, 섹션·근거 자료, 인용 검사 경계를 반영했습니다. |
| 답변과 복구 | `answer_synthesis.py`, `recovery.py` | 직접 조립·합성·생략, 초기화 필드, 제외 URL과 복구 결과를 반영했습니다. |
| 공개 경계 | `contracts.py`, `streaming.py`, `main.py`, 프런트 계약·프록시 | State 전체와 공개 결과를 구분하고 단계·출처·미리보기·완료·오류를 반영했습니다. |
| 실제 작성 경로 | `runtime.py`의 필드 참조 | `searchNotice`는 선언·소비되지만 기본 메인 어댑터가 작성하지 않는 점을 명시했습니다. |

## 실행한 확인

| 명령 또는 확인 | 결과 |
|---|---|
| `git status --short --branch`, `git rev-parse HEAD` | 기준 브랜치·리비전과 기존 `AGENTS.md` 변경을 확인했습니다. |
| `Get-Content -Encoding UTF8`, `rg -n` | 관련 코드·기존 문서를 읽고 함수·필드 작성 경로를 대조했습니다. |
| Python AST와 문서 표·절 대조 | State 28개 필드와 Node 5개를 모두 포함하는 것을 확인했습니다. 애플리케이션 모듈은 실행하지 않았습니다. |
| Markdown 로컬 링크·코드 블록 검사 | 문서 7개의 로컬 링크 107개가 실제 파일을 가리키고 코드 블록 시작·종료가 맞는 것을 확인했습니다. |
| `git diff --check` | 공백 오류가 없음을 확인했습니다. |

첫 Python 확인은 PowerShell 파이프의 한글 경로 인코딩으로 실패했습니다. 경로를 `pathlib.glob()`으로 찾도록 바꾼 뒤 같은 확인을 통과했습니다.

## 미실행 범위

문서만 변경하여 애플리케이션 테스트·타입 검사·빌드·브라우저·실공급자·DB·Render 호출은 실행하지 않았습니다. 기존 테스트 통과 기록을 이번 실행 결과로 표시하지 않습니다. T10·T12·T14·T17·T19·T20 등 구현 잔여 범위는 [작업현황](../../작업현황.md)을 따릅니다.
