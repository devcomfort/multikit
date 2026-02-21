# Implementation Plan: README Badge Generation

**Branch**: `002-readme-badges` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-readme-badges/spec.md`

## Summary

README 상단에 커버리지 배지와 Python 버전 지원 배지를 추가하고, 테스트/CI 결과가 배지에 자동 반영되도록 파이프라인을 정렬한다. 커버리지는 CI 테스트 실행 결과에서 자동 산출되어 외부 배지 서비스에 반영되고, Python 버전 배지는 tox/CI 매트릭스와 일치하도록 관리한다. 구현은 README, CI 워크플로우, 테스트 커버리지 리포트 설정, 문서 검증 경로를 포함한다.

## Technical Context

**Language/Version**: Python ≥ 3.10  
**Primary Dependencies**: pytest, pytest-cov, tox, tox-gh-actions, GitHub Actions, (badge provider) Codecov/Shields.io  
**Storage**: N/A (설정/문서 파일 기반)  
**Testing**: pytest, pytest-cov, tox  
**Target Platform**: GitHub repository (README renderer + GitHub Actions CI)  
**Project Type**: Single Python CLI project  
**Performance Goals**: 기존 테스트 시간 증가 최소화(배지 연동으로 인한 테스트 단계 변경 없음), CI 단계 안정적 완료  
**Constraints**: 헌법 원칙상 표준 구조 준수, 기존 명령/동작 무변경, 배지 링크/라벨의 유지보수 단순성  
**Scale/Scope**: README 1개, CI workflow 1개, 테스트 설정 파일(필요 시) 1~2개

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Pre-Research Gate Check

- **I. Intuitive CLI Experience**: PASS — CLI 명령 UX 자체를 변경하지 않음
- **II. Standardized Configuration**: PASS — README/CI/tox 설정은 기존 표준 파일 내에서 수정
- **III. Idempotent & Clean Operations**: PASS — 파일 설치/삭제 로직 변경 없음
- **IV. Minimal & Modern Foundation**: PASS — 새 런타임 의존성 최소화
- **V. Extensibility via Kits**: PASS — kit 아키텍처와 충돌 없음

결론: Gate 통과, Phase 0 진행 가능.

### Post-Design Gate Re-Check

- **I** PASS — 사용자 가시성(README) 강화, CLI 동작 영향 없음
- **II** PASS — tox/CI/README 간 단일 사실원 유지 전략 반영
- **III** PASS — 테스트/설정 중심 변경으로 운영 안정성 유지
- **IV** PASS — 기존 도구체인 재사용(추가 복잡도 낮음)
- **V** PASS — 기능 범위가 kit 배포 모델과 독립적

결론: 위반 없음.

## Project Structure

### Documentation (this feature)

```text
specs/002-readme-badges/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── badge-workflow.md
└── tasks.md
```

### Source Code (repository root)

```text
README.md
tox.ini
pyproject.toml
.github/
└── workflows/
    └── ci.yml

tests/
└── (existing pytest suite, no new feature module required)
```

**Structure Decision**: 코드 로직 변경 없이 문서/CI/설정 중심으로 구현한다. 배지 값의 출처는 테스트 실행 결과와 버전 매트릭스로 제한한다.

## Complexity Tracking

해당 없음.
