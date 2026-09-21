# UI 의존성 정리: 파티클 로고 및 미사용 패키지 제거

## 범위와 결과

사용자 지시에 따라 `animejs`, `particles-gl`, `tweakpane` 의존성과 해당 파티클 로고 기능을 정리했습니다. 이 문서는 정리 범위와 검증 결과를 기록하기 위한 문서입니다.

- `particles-gl` 기반 `ParticlesLogo` 컴포넌트와 `tweakpane` 개발용 조정 패널을 제거했습니다.
- 파티클 설정 타입·기본값·localStorage 이벤트·타입 선언·전용 SVG·전용 CSS를 함께 제거했습니다.
- `animejs`는 실행 코드에서 사용되지 않는 직접 의존성이므로 manifest와 lockfile에서 제거했습니다.
- `FactCheckDashboard`의 문서 입력, 근거 검토, GlassSurface 조정 기능은 유지합니다.

## 보존

- `FactCheckDashboard` → `FloatingLinesBackground` → 동적 `FloatingLines` 및 Three.js 배경은 유지합니다.
- Liquid Glass 패널, Motion, 모바일·데모 흐름은 유지합니다.
- React Router 레거시 컴포넌트·설정은 이번 범위 밖이므로 보존합니다.
- Three.js는 Floating Lines 배경에서 직접 사용하므로 제거하지 않습니다.

## 실제 검증

- `npm run typecheck`: 통과.
- `npm run build`: Next.js 프로덕션 빌드 통과.
- `git diff --check`: 통과.
- 유료 provider 호출은 수행하지 않았습니다.
