# Contract: Badge Workflow

## Scope

- README 배지 2종(`coverage`, `python-support`)의 값 출처와 갱신 흐름 계약

## Contract A: Coverage Badge

### Preconditions

- CI에서 `pytest --cov`가 실행됨
- 커버리지 임계값 90% 설정 유지

### Postconditions

- 최신 CI 결과가 배지에 반영됨
- 90% 미만 시 실패 상태가 시각적으로 구분됨

### Failure Contract

- coverage 업로드 실패 시 배지 상태는 `unknown`/실패로 노출 가능
- 실패 원인은 CI 로그에서 확인 가능해야 함

## Contract B: Python Support Badge

### Preconditions

- tox envlist와 GitHub Actions matrix 정의 존재

### Postconditions

- README 배지의 버전 범위가 tox/CI 검증 범위와 일치

### Failure Contract

- tox/CI와 README 배지가 불일치하면 문서 검증 단계에서 경고 또는 리뷰 블로커로 취급

## Contract C: Trigger Coupling

### Rule

- 배지 갱신은 기존 테스트 실행 파이프라인의 결과에 결합되어야 함
- 별도 수동 배지 갱신 단계는 허용하지 않음

## Verification Checklist

- README 배지 2개 모두 렌더링됨
- 커버리지 배지 값이 테스트 출력과 ±1% 이내
- Python 지원 배지 값이 tox/CI 매트릭스와 일치
