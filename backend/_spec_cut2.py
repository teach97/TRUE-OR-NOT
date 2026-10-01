import glob, os
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
fs = [x for x in glob.glob(os.path.join(root, 'docs', '*.md')) if os.path.getsize(x) > 30000]
assert len(fs) == 1, fs
f = fs[0]
text = open(f, encoding='utf-8-sig').read()
before = len(text.splitlines())

# Section 16: drop past schedule, keep roles + cutback order
i16 = text.index('## 16.')
i17 = text.index('## 17.')
new16 = ('## 16. 팀 역할\n\n'
         '| 역할 | 주요 산출물 | 의존성 |\n'
         '|---|---|---|\n'
         '| 에이전트 | 추출·비교·판정, 출력 스키마 검사 | 공유 계약, 검색·근거 데이터 |\n'
         '| 검색·근거 | URL 안전 처리, 수집, 인용 위치, 출처 관계 | 검색 provider, 수집 정책 |\n'
         '| 프론트엔드 | 입력·원문·근거 비교·상태 관리 | 안정된 타입, 명시적 fixture |\n'
         '| 데이터·QA | 테스트 사례, 판정 기준 조정, 통합·발표 | 기대 결과·근거·실행 환경 |\n'
         '\n'
         '### 지연 시 축소 순서\n\n'
         '1. 추가 애니메이션·PNG 개선·관리 지표를 후순위로 둡니다.\n'
         '2. 고급 의미 기반 중복 판정은 보류하고 URL 중복과 명시적 공동 원자료 링크에 집중합니다.\n'
         '3. 지원 URL 범위를 명시적으로 좁히고 비지원 사이트는 본문 입력으로 안내합니다.\n'
         '4. 실검색을 준비하지 못하면 본래 MVP 미달로 기록하고 명확하게 표시한 fixture 데모로 발표합니다.\n'
         '\n'
         '인용 정확성·데모 표시·근거 부족 처리·URL 안전 대책은 축소하지 않습니다.\n\n')
text = text[:i16] + new16 + text[i17:]

# Section 18: keep only undecided rows
i18 = text.index('## 18.')
i19 = text.index('## 19.')
new18 = ('## 18. 미확정 사항\n\n'
         '| 미확정 사항 | 권장안 | 영향 |\n'
         '|---|---|---|\n'
         '| 공개 범위 | 비공개 팀 실증부터 시작 | 호출 제한·운영·법무 대응 |\n'
         '| 보존 기간 | 단기 세션 저장안 검토 | DB·삭제 처리·안내 문구 |\n'
         '| 부분 판정 경계 | QA 사례로 합의 | 평가 재현성 |\n\n'
         '확정됨: 백엔드 FastAPI, 검색 Tavily→LLM 폴백, 배포는 로컬 상주.\n\n')
text = text[:i18] + new18 + text[i19:]

# Section 19: short intro + demo notice only
i19 = text.index('## 19.')
i20 = text.index('## 20.')
new19 = ('## 19. 소개 문구와 데모 안내\n\n'
         '> 그 주장, 근거까지 보이나요? True or Not은 기사와 댓글의 주장을 출처에 연결하여 확인된 내용과 불확실한 내용을 함께 비교하는 검증 도구입니다.\n\n'
         '> 데모 모드입니다. 표시된 주장·출처·결과는 화면 흐름을 설명하기 위한 예시이며 실제 검증 결과가 아닙니다.\n\n')
text = text[:i19] + new19 + text[i20:]

# Section 20: trim history
i20 = text.index('## 20.')
new20 = ('## 20. 기준 자료와 문서 이력\n\n'
         '- 제품 원안: 사용자 제공 본문 1~13절.\n'
         '- v3에서 구현 반영 확정. 원안의 제품 방향은 유지한다.\n')
text = text[:i20] + new20

with open(f, 'w', encoding='utf-8', newline='') as fh:
    fh.write(text)
print('lines:', before, '->', len(text.splitlines()))
