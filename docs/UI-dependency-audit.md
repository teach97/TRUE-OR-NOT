# UI 의존성 점검: ShaderGradient 제거 요청

## 범위와 결과

사용자 추가 지시에 따라 `@shadergradient/react`만 우선 점검하였습니다. 다른 UI 라이브러리·레거시 컴포넌트·Python/backend/build 의존성은 삭제하지 않았습니다.

- 점검 시작 시 `package.json`, `package-lock.json`, `node_modules/@shadergradient/react`에 대상 패키지가 없었습니다. `npm ls @shadergradient/react --all`은 `(empty)`, `npm explain`은 일치 의존성 없음으로 확인되었습니다.
- `npm uninstall @shadergradient/react --ignore-scripts --no-audit --no-fund` 실행 결과 `up to date`. manifest/lockfile 변경은 없습니다.
- 전체 추적 파일 검색에서 ShaderGradient 참조는 `HANDOFF.md`의 **과거** 설치 기록뿐입니다. 실행 코드, CSS, 스크립트, 테스트, import/re-export/dynamic import 및 렌더링 연결에 제거할 참조가 없습니다. 과거 기록을 현재 설치 목록으로 해석하면 안 됩니다.
- 이번 작업으로 제거한 패키지, 컴포넌트, 시각적 배경은 **없습니다**. 이미 제거되어 있던 패키지를 새로 제거했다고 주장하지 않습니다.

## 보존

- `FactCheckDashboard` → `FloatingLinesBackground` → 동적 `FloatingLines` 및 Three.js 배경은 유지합니다.
- Liquid Glass 패널, Motion, particles-gl 로고, 개발용 Tweakpane/UI Component Lab, 모바일·데모 흐름은 수정하지 않습니다.
- `animejs`, `html2canvas`, `liquid-gl` 등 다른 의존성의 추가 삭제 여부는 이번 변경 범위 밖입니다. 직접 import 부재만으로 peer 의존성을 제거하지 않습니다.
- React Router 레거시 컴포넌트·설정도 이번 범위 밖으로 보존합니다.

## 실제 검증

- `npm run typecheck`: 통과.
- 저장소의 Node 테스트 파일 5개를 명시적으로 실행: **20 passed, 0 failed**.
- `npm run build`: Next.js 프로덕션 빌드 통과.
- 빌드가 자동 변경한 `next-env.d.ts`의 경로만 작업 전 상태로 복구하였습니다.
- UI 런타임/의존성 변화가 없어 별도 브라우저 smoke는 실행하지 않았습니다. 유료 provider 호출, 커밋, 푸시는 하지 않았습니다.
