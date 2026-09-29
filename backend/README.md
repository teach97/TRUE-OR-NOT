# FactLens 백엔드

이 디렉터리는 FastAPI와 LangGraph로 구성된 팩트체크 API입니다. 주장을 분류하고 검색어를 만들며, 관련 출처를 찾고 원문을 읽은 뒤 직접 인용을 검증해 근거 기반 답변을 구성합니다. 기본 실행 주소는 `http://127.0.0.1:8010`입니다.

## 요구 사항

- Python 3.11 이상
- [uv](https://docs.astral.sh/uv/) 패키지 관리자
- 지원되는 LLM 제공자 중 하나 이상의 서버 측 API 키

## 설치 및 실행

저장소 루트에서 백엔드 디렉터리로 이동해 의존성을 설치하고 환경 파일을 만듭니다.

```powershell
Set-Location backend
uv sync --locked
Copy-Item .env.example .env
```

`backend/.env`를 열어 사용할 키를 설정한 다음 백엔드를 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8010
```

백엔드 상태는 `http://127.0.0.1:8010/health`에서 확인할 수 있습니다. 이 경로는 프로세스가 실행 중인지 확인하며, LLM 키나 외부 제공자 응답 가능성까지 검사하지는 않습니다. 프런트엔드 실행법은 저장소 루트의 [README](../README.md)를 참고하세요.

## 환경 변수

키는 `backend/.env` 또는 백엔드 프로세스 환경 변수에 설정합니다. `.env`는 Git에서 제외됩니다. 키를 소스 코드, 프런트엔드 환경 변수, 브라우저 번들 또는 저장소에 넣지 마세요.

| 변수 | 용도 |
|---|---|
| `GEMINI_API_KEY` | Gemini 3.8 Flash 및 Gemini 3.7 Flash 사용에 필요합니다. |
| `OPENAI_API_KEY` | GPT-6 Luna 사용과 OpenAI 웹 검색 경로에 필요합니다. |
| `SERPAPI_API_KEY` | 선택 사항입니다. 무료 요금제 조건이 확인되면 Google 자연검색을 사용합니다. |
| `YOUTUBE_API_KEY` | 선택 사항입니다. 검색 결과에 YouTube 영상이 있을 때 영상 정보와 공개 댓글을 가져오는 데 사용합니다. |

Gemini 또는 OpenAI 키 중 하나 이상을 설정해야 LLM 검증을 시작할 수 있습니다. 두 제공자 키를 모두 설정하고 모델을 `auto`로 선택하면 다음 순서로 시도합니다.

1. Gemini 3.8 Flash (`high`)
2. Gemini 3.7 Flash (`high`)
3. GPT-6 Luna (`max`)

`auto`가 아닌 특정 모델을 선택하면 그 모델만 호출합니다. 선택한 모델이 설정되어 있지 않거나 응답하지 않으면 다른 모델로 자동 전환하지 않습니다.

## 검색·검증 흐름

1. 입력에서 검증할 주장과 검색어를 추출합니다. 최대 3개 주장을 처리합니다.
2. `SERPAPI_API_KEY`가 있으면 계정이 무료 요금제이고, 월 요금이 0이며, 추가 크레딧이 없고, 필요한 무료 검색 쿼터가 남았는지 먼저 확인합니다. 조건을 확인할 수 없으면 SerpApi 검색 요청을 보내지 않고 기존 LLM 웹 검색으로 대체합니다.
3. 검색 후보 중 최대 6개 출처를 읽고 페이지 원문을 정리합니다. 검색 요약만으로 직접 인용을 만들지 않습니다.
4. 모델이 제시한 인용을 실제로 읽은 원문과 대조하고, 근거가 확인된 범위에서 답변을 구성합니다.

SerpApi는 확인된 무료 쿼터 안에서만 호출하도록 제한되어 있지만, 무료 쿼리 한도는 검색 요청으로 차감됩니다. LLM 제공자 API 사용량과 비용은 SerpApi 한도와 별개입니다. 무료 요금제나 잔여량을 확인할 수 없으면 일반 웹 검색으로 대체되며, 이때 표시되는 검색 후보 순서는 Google 자연검색 순위가 아닙니다. YouTube 공개 댓글은 맥락 정보로만 표시하며 팩트 점수나 직접 인용 근거로 사용하지 않습니다.

## API

| 메서드와 경로 | 설명 |
|---|---|
| `GET /health` | 프로세스 생존 상태와 실행 중인 코드 리비전을 반환합니다. 제공자 연결 검사는 하지 않습니다. |
| `GET /api/fact-check` | 설정된 모델과 워크플로 준비 상태를 반환합니다. |
| `POST /api/fact-check` | 팩트체크를 실행하고 완료된 JSON 결과를 반환합니다. |
| `POST /api/fact-check/stream` | 진행 단계와 최종 결과를 NDJSON 스트림으로 반환합니다. 프런트엔드는 이 스트리밍 경로를 사용합니다. |

팩트체크 요청 예시는 다음과 같습니다.

```json
{
  "text": "AGI는 2030년 안에 오나?",
  "focus": "",
  "consent": true,
  "modelPreference": "auto"
}
```

`consent`는 반드시 `true`여야 합니다. 텍스트는 1~12,000자, 확인 초점은 최대 500자입니다. 모델 선택값은 `auto`, `gemini-3.8-flash`, `gemini-3.7-flash`, `gpt-6-luna` 중 하나입니다.

## 테스트 및 점검

백엔드 디렉터리에서 오프라인 테스트를 실행합니다.

```powershell
uv run pytest -q
uv lock --check
```

SerpApi 연결을 실제로 확인하려면 다음 명령을 사용할 수 있습니다.

```powershell
uv run python smoke_google_serp.py
```

이 점검은 계정 상태를 확인한 뒤 `AGI 2030년`으로 Google 검색 요청 1회를 보낼 수 있으므로 무료 검색 쿼터를 사용합니다. 키 값은 출력하지 않습니다. 실제 LLM 검증은 제공자 API 사용량이 발생할 수 있으므로, 자동 테스트와 구분해 실행하세요.
