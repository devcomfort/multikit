# Research: Multikit CLI Async Optimization + Update

## Decision 1: `update` 명령을 독립 command로 제공

- Decision: `multikit update [kit]`를 추가하고, 단건 + 인터랙티브 다건 흐름을 지원한다.
- Rationale: 설치된 kit 유지보수 경로를 `install`과 분리해 의도를 명확히 하고 운영 UX를 단순화한다.
- Alternatives considered:
  - `install` 재실행만 사용: 동작은 가능하나 명령 의도가 불명확하고 사용자 혼동 유발.
  - 별도 self-update 포함: CLI 패키지 업데이트 정책과 충돌.

## Decision 2: 성능 민감 경로를 `aiohttp` 중심 async로 전환

- Decision: `install`/`diff`/`update`의 원격 조회는 `aiohttp` 기반 비동기 경로로 구현한다.
- Rationale: 다파일 다운로드/비교에서 순차 I/O 병목을 줄여 NFR(<3s install/update, <2s diff)를 달성한다.
- Alternatives considered:
  - `httpx` sync 유지: 구현 단순하지만 대량 파일에서 성능 목표 달성이 어려움.
  - 전면 `httpx` async: 가능하나 기존 명세가 `aiohttp`를 명시해 기준 불일치.

## Decision 3: 파일 I/O는 `aiofiles`로 비동기화

- Decision: staging/비교 경로의 파일 read/write에 `aiofiles`를 사용한다.
- Rationale: 네트워크 async만 적용하면 디스크 I/O에서 다시 병목이 생길 수 있어 end-to-end async 정책과 불일치한다.
- Alternatives considered:
  - 동기 파일 I/O 유지: 구현 단순하지만 FR-017/FR-018 위반.

## Decision 4: 동시성 정책은 기본 8 + 설정 오버라이드

- Decision: 기본 동시성은 8로 고정하고 `multikit.toml`의 `network.max_concurrency`로 오버라이드한다.
- Rationale: 기본값은 테스트 재현성을 보장하고, 환경별 성능 튜닝 유연성도 제공한다.
- Alternatives considered:
  - 고정값만 사용: 환경 최적화 어려움.
  - 완전 적응형만 사용: 테스트/회귀 재현성이 떨어짐.

## Decision 5: 재시도 정책은 429/5xx/timeout 대상 3회 지수 백오프

- Decision: `429`/`5xx`/`ConnectTimeout`에 대해 최대 3회 재시도, 지수 백오프(0.5s/1s/2s)+jitter를 적용한다.
- Rationale: 일시적 장애에 대한 복원력을 확보하면서도 무제한 재시도를 방지한다.
- Alternatives considered:
  - 재시도 없음: 실패율 상승.
  - 사용자 플래그로 완전 노출: MVP 운영 복잡도 증가.

## Decision 6: async 도입 경계는 명령 핸들러 포함 end-to-end

- Decision: 네트워크/파일 레이어만이 아니라 command handler까지 async 경로로 전환한다.
- Rationale: 호출 경계에서 sync↔async 브리징 비용/복잡도를 줄이고 에러 처리/취소 제어를 단순화한다.
- Alternatives considered:
  - 내부 레이어만 async + `asyncio.run`: 점진 전환은 쉬우나 경계 복잡도와 중복 코드 증가.

## Decision 7: atomic 설치 보장은 async 전환 후에도 유지

- Decision: 모든 파일 다운로드 성공 후 반영하는 atomic staging 규칙을 유지한다.
- Rationale: 비동기 최적화와 무관하게 clean operation 핵심 불변조건이다.
- Alternatives considered:
  - 스트리밍 반영: 중간 실패 시 롤백 복잡도 증가.

## Decision 8: 프로그램 자체 업데이트는 패키지 매니저 경로 유지

- Decision: `multikit update`는 kit 업데이트 전용으로 유지하고, CLI 패키지 업그레이드는 `pip/uv/rye`로 처리한다.
- Rationale: 기능 경계가 명확해지고 배포/환경 정책 충돌을 피할 수 있다.
- Alternatives considered:
  - CLI self-update 명령 도입: MVP 범위 확장 및 배포 전략 복잡화.
