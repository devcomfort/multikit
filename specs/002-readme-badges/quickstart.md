# Quickstart: README Badge Generation

## 1) Baseline 확인

```bash
rye run tox -av
rye run test:cov
```

확인 포인트:

- tox 환경: `py310`, `py311`, `py312`, `py313`
- coverage 결과 출력 가능

## 2) README 배지 추가

README 상단에 다음 배지를 배치한다.

- Coverage badge (CI 결과 기반)
- Python support badge (3.10–3.13)

## 3) CI 연동 검증

```bash
rye run test:cov
rye run test:tox
```

확인 포인트:

- 커버리지 임계치(90%) 준수
- 지원 버전 매트릭스와 문서 표기가 일치

## 3-1) 로컬 배지값 사전 확인

```bash
rye run badge:preview
```

확인 포인트:

- 테스트 종료 후 커버리지 퍼센트가 출력됨
- `coverage.xml` 아티팩트가 생성됨 (배지 소스와 동일한 기반 데이터)

## 4) 렌더링 확인

- GitHub README 화면에서 배지 2개가 정상 렌더링되는지 확인
- 커버리지 값/색상이 최근 실행 결과와 부합하는지 확인

## 5) 회귀 체크

- 기존 CLI 테스트 스위트가 유지되는지 확인
- 문서 변경 외 코드 경로에 영향이 없는지 확인
