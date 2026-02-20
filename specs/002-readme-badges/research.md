# Research: README Badge Generation

## Decision 1: 커버리지 배지는 Codecov 기반 자동화

- Decision: CI에서 생성한 커버리지 결과를 Codecov에 업로드하고 README는 Codecov 배지를 참조한다.
- Rationale: 테스트 완료 후 자동 갱신 요구(FR-003, FR-004, FR-007)를 충족한다.
- Alternatives considered:
  - 정적 Shields 배지: 자동 갱신 불가
  - 로컬 배지 파일 생성/커밋: 유지보수 비용과 stale 위험 증가

## Decision 2: Python 버전 배지는 tox/CI 매트릭스 기준

- Decision: 배지에 표시되는 지원 버전은 `tox.ini` envlist 및 `.github/workflows/ci.yml` matrix와 일치시킨다.
- Rationale: “검증된 버전”은 실제 테스트 매트릭스가 단일 사실원이다.
- Alternatives considered:
  - pyproject classifier 기반: 실제 CI 검증 범위와 불일치 가능

## Decision 3: 배지 갱신은 기존 테스트 파이프라인에 결합

- Decision: 별도 배지 생성 파이프라인을 두지 않고 기존 테스트 실행 단계에 연동한다.
- Rationale: 운영 복잡도 최소화 + FR-007 준수.
- Alternatives considered:
  - 별도 workflow: 실패 원인 분산, 유지보수 비용 증가

## Decision 4: 임계치 실패 상태를 배지에 반영

- Decision: 커버리지 90% 미만 시 배지 상태가 통과 상태와 명확히 구분되도록 구성한다.
- Rationale: FR-006, SC-005 충족.
- Alternatives considered:
  - 실패 시 마지막 성공값 유지: 상태 오도 가능

## Decision 5: 로컬 사전 확인은 기존 테스트 명령 재사용

- Decision: `rye run test:cov` 출력으로 로컬에서 배지 예상값을 사전 확인한다.
- Rationale: 새로운 도구 없이 사용자 스토리 3을 충족한다.
- Alternatives considered:
  - 별도 로컬 배지 스크립트 추가: MVP 범위 대비 과도한 구현
