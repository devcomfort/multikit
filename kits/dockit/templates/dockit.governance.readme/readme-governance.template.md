# README Governance

- Version: 0.1.0
- Last Updated: <!-- TODO: fill date -->
- Owner: <!-- TODO: fill owner -->
- Scope: Repository-level README policy for change-driven maintenance

## 1) Purpose and Scope

이 문서는 `README.md` 관리 원칙을 정의한다.

목표:

- 프로젝트 변경사항으로 인해 필요한 README 갱신을 빠짐없이 식별한다.
- README 업데이트를 제안 중심(proposal-based)으로 운영한다.
- 규칙을 명시적으로 버전 관리하여 재사용 가능하게 유지한다.

적용 범위:

- 루트 `README.md`의 구조, 내용 정확성, 동기화 트리거, 변경 제안 절차

비적용 범위:

- 코드 구현 세부 설계
- README 외 문서의 상세 편집 정책

## 2) Source of Truth Hierarchy

README 내용 충돌 시 아래 우선순위를 따른다 (상위가 우선).

1. 소스 코드 / 설정 파일 (`pyproject.toml`, CLI 동작 등)
2. 실제 파일 구조
3. `README.md` 설명 텍스트

## 3) Required README Sections

<!-- TODO: 프로젝트에 맞게 필수 섹션을 정의하세요. 예시: -->

- 프로젝트 소개
- 설치
- Quick Start
- 사용법
- 개발자 가이드
- 라이선스

## 4) Update Triggers

아래 변경이 발생하면 README 갱신 필요 여부를 평가한다.

<!-- TODO: 프로젝트에 맞게 트리거를 정의하세요. 예시: -->

- 새 기능/명령 추가
- CLI 옵션/인자 변경
- 의존성 변경
- 구조 변경

## 5) Consistency Rules

<!-- TODO: 프로젝트에 맞게 정의하세요. -->

- 예시 명령은 실행 가능해야 한다.
- 버전 정보는 실제와 일치해야 한다.

## 6) Proposal and Approval Workflow

1. 분석 → 2. 제안 → 3. 승인 → 4. 적용 → 5. 보고

금지: 승인 전 README 자동 수정

## 7) Amendment Log

- 0.1.0: 초기 템플릿 설치
