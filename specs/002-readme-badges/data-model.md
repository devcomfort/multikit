# Data Model: README Badge Generation

## Entity 1: BadgeDefinition

- Purpose: README에 표시되는 배지 정의
- Fields:
  - `id`: `coverage` | `python-support`
  - `label`: 사용자 표시 라벨
  - `source`: 값 출처(`coverage-report`, `tox-matrix`)
  - `url`: 클릭 시 이동 URL
  - `image_url`: 배지 이미지 URL
  - `state`: `pass` | `fail` | `unknown`

## Entity 2: CoverageSnapshot

- Purpose: 특정 CI 실행의 커버리지 측정 결과
- Fields:
  - `run_id`: GitHub Actions run identifier
  - `coverage_percent`: float
  - `threshold`: float (90.0)
  - `status`: `pass` | `fail`
  - `uploaded_at`: timestamp

## Entity 3: PythonSupportMatrix

- Purpose: 검증된 Python 버전 집합
- Fields:
  - `versions`: list[str] (예: `3.10`, `3.11`, `3.12`, `3.13`)
  - `tox_envs`: list[str] (예: `py310`, `py311`, `py312`, `py313`)
  - `ci_matrix`: list[str]
  - `last_verified_run`: run id

## Relationships

- `CoverageSnapshot` → `BadgeDefinition(coverage)` 값을 갱신
- `PythonSupportMatrix` → `BadgeDefinition(python-support)` 표시 범위를 결정

## Validation Rules

- `coverage_percent`는 0~100 범위
- `threshold`는 프로젝트 설정(`fail_under`)과 일치
- `versions`, `tox_envs`, `ci_matrix`는 의미적으로 동일 집합이어야 함
- README 배지 URL은 실제 소스(Codecov/Actions/Shields)와 일치해야 함

## State Transitions

1. CI 테스트 완료
2. coverage 산출
3. coverage 업로드 성공 시 `BadgeDefinition(coverage).state` 갱신
4. tox/ci 매트릭스 변경 시 `BadgeDefinition(python-support)` 값 재검증
