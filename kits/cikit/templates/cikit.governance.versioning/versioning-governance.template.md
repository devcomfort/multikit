# Versioning Governance

- Version: 0.1.0
- Last Updated: <!-- TODO: fill date -->
- Owner: <!-- TODO: fill owner -->
- Scope: 프로젝트 전체 버전 관리 정책

## 1) Purpose and Scope

이 문서는 프로젝트의 **버전 관리 원칙**을 정의한다.

목표:

- 모든 버전 번호가 명확한 의미를 전달한다
- 버전 증분이 예측 가능하고 일관성 있다

## 2) Versioning Scheme

**Semantic Versioning (SemVer) 2.0.0** — `MAJOR.MINOR.PATCH`

| Component | Meaning                            |
| --------- | ---------------------------------- |
| MAJOR     | 하위 호환성이 깨지는 변경          |
| MINOR     | 하위 호환되는 기능 추가            |
| PATCH     | 하위 호환되는 버그 수정, 문구 개선 |

## 3) Version Locations

<!-- TODO: 프로젝트에 맞게 버전이 위치하는 파일을 정의하세요. -->

- `pyproject.toml`
- `package.json`
- 기타

## 4) Bump Rules

<!-- TODO: 프로젝트에 맞게 범프 기준을 정의하세요. -->

| Bump  | Trigger        |
| ----- | -------------- |
| MAJOR | 호환 불가 변경 |
| MINOR | 새 기능 추가   |
| PATCH | 버그 수정      |

## 5) Consistency Policy

버전 변경 시 모든 위치를 동기화한다.

## 6) Amendment Log

- 0.1.0: 초기 템플릿 설치
