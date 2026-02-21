# Research: Multikit CLI (MVP)

## Decision 1: CLI 프레임워크는 `cyclopts` 유지

- Decision: 모든 명령(`init/install/list/uninstall/diff`)을 `cyclopts` App + subcommand 구조로 구성한다.
- Rationale: 헌법의 Intuitive CLI Experience/타입힌트 기반 규칙과 직접 정합된다.
- Alternatives considered:
  - `argparse`: 표준 라이브러리지만 서브앱 구성/타입힌트 경험이 상대적으로 약함.
  - `click/typer`: 가능하지만 기존 코드/가이드가 cyclopts 중심이라 전환 이득이 낮음.

## Decision 2: 원격 통신은 `httpx` sync + timeout/상태코드 기반 에러 처리

- Decision: `httpx` sync client로 `registry.json`, `manifest.json`, 각 파일 다운로드를 수행한다.
- Rationale: 현재 MVP는 CLI 단발 실행 위주이며 async 복잡도 없이 충분한 안정성을 제공한다.
- Alternatives considered:
  - `requests`: 기능적으로 가능하지만 프로젝트 기존 의존성과 중복.
  - async client: 향후 확장 가능하나 MVP 구현 비용 증가.

## Decision 3: 파일 탐색은 `manifest.json` 선언 기반

- Decision: 킷 파일 목록은 `manifest.json`의 `agents[]`, `prompts[]`만 신뢰한다.
- Rationale: 파일 시스템 스캔보다 예측 가능하며 계약 기반 검증이 가능하다.
- Alternatives considered:
  - 디렉토리 스캔: 암묵적 규칙 증가, 누락/오탐 가능성 높음.

## Decision 4: 설치 전략은 atomic staging

- Decision: 임시 디렉토리 전체 다운로드 성공 후에만 `.github/`로 반영한다.
- Rationale: 중간 실패 시 부분 설치를 방지해 clean operation 원칙을 만족한다.
- Alternatives considered:
  - 즉시 반영(streaming install): 부분 실패 시 롤백 부담이 커짐.

## Decision 5: 충돌 해결은 파일별 diff + 대화식 선택

- Decision: 기존 파일과 원격 파일이 다르면 diff 출력 후 `[y/n/a/s]`로 결정하고, `--force`는 일괄 덮어쓰기.
- Rationale: 사용자 제어와 안전성 균형.
- Alternatives considered:
  - 무조건 덮어쓰기: 로컬 커스터마이징 손실 위험.
  - 무조건 스킵: 업데이트 적용이 어려움.

## Decision 6: uninstall은 단독 소유 모델(MVP)

- Decision: `multikit.toml`의 킷별 `files[]`를 기준으로 삭제한다. 공유 참조 감지 시 삭제하지 않고 경고한다.
- Rationale: 현재 기본 킷 네이밍 구조에서 공유 소유 가능성이 낮아 MVP 복잡도를 줄인다.
- Alternatives considered:
  - ownership 역인덱스 도입: 안전성은 높지만 데이터 모델/마이그레이션 복잡도 증가.

## Decision 7: 버전 정책은 최신 우선 설치

- Decision: `multikit install <kit>`은 항상 원격 최신 버전을 기준으로 비교/설치한다.
- Rationale: 사용자 경험 단순화, 별도 업그레이드 명령 없이 일관된 동작.
- Alternatives considered:
  - 버전 pinning 기본: 운영 안정성은 높지만 UX와 옵션 복잡도 증가.
  - 별도 upgrade 명령 도입: MVP 범위 초과.

## Decision 8: 테스트 전략은 명령 중심 회귀 검증

- Decision: 명령별 테스트(`test_init/install/list/uninstall/diff`)와 파일시스템 side effect 검증을 우선한다.
- Rationale: 헌법의 idempotent/clean operation 검증 요구 충족.
- Alternatives considered:
  - 통합 E2E만 수행: 실패 원인 지역화가 어려움.
  - 단위 테스트만 수행: 명령 조합 시나리오 누락 가능.
