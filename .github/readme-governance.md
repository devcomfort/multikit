# README Governance

- Version: 1.1.0
- Last Updated: 2026-03-03
- Owner: Maintainer (`@devcomfort`)
- Scope: Repository-level README policy for change-driven maintenance

## 1) Purpose and Scope

이 문서는 `README.md` 관리 원칙을 정의한다.
목표는 다음과 같다.

- 프로젝트 변경사항으로 인해 필요한 README 갱신을 빠짐없이 식별한다.
- README 업데이트를 제안 중심(proposal-based)으로 운영한다.
- 규칙을 명시적으로 버전 관리하여 재사용 가능하게 유지한다.

적용 범위:

- 루트 `README.md`의 구조, 내용 정확성, 동기화 트리거, 변경 제안 절차
- `.github/agents/` 및 `kits/*`의 README 관련 에이전트 운영 방식

비적용 범위:

- 코드 구현 세부 설계
- README 외 문서(예: `REQUIREMENTS.md`)의 상세 편집 정책

## 2) Source of Truth Hierarchy

README 내용 충돌 시 아래 우선순위를 따른다 (상위가 우선).

1. `kits/*/manifest.json` (킷 이름/버전/agents/prompts 목록)
2. `kits/registry.json` (공개 킷 목록/버전/설명)
3. 실행 가능한 명령/스크립트 정의 (`pyproject.toml`, 실제 CLI 동작)
4. 저장소 실제 파일 구조 (`src/`, `tests/`, `.github/`)
5. `README.md` 설명 텍스트

규칙:

- README의 kit/tool/버전/개수 정보는 1~4와 불일치하면 안 된다.
- README 예시 텍스트는 “설명용 예시”여도 실제 규칙과 모순되면 수정 대상이다.

## 3) Required README Sections

`README.md`는 아래 핵심 섹션을 유지해야 한다.

- 프로젝트 소개/개요
- Kit 개념
- 제공 중인 킷(킷/버전/도구/역할)
- 핵심 기능(주요 CLI 명령)
- 설치
- Quick Start
- CLI 사용법
- 설정 파일 예시 (`multikit.toml`)
- 트러블슈팅
- 개발자 가이드(개발 명령/아키텍처/테스트 정책)
- 라이선스

허용:

- 제목/문장 스타일 변경
- 설명 보강

금지:

- 핵심 섹션 삭제(동등 정보가 다른 섹션으로 이동되어 검증 가능하게 대체된 경우 제외)

## 4) Style & Tone

README의 서식, 말투, 구조 기준을 정의한다.

### 언어 및 말투

- **언어**: 한국어 (코드/명령/경로/킷 이름은 영문 유지)
- **말투**: 기술 문서 격식체 (존댓말, ~합니다/~입니다)
- **명칭**: 킷 이름은 소문자, 도구 이름은 파일 stem 기준 (예: `testkit.design`)

### 서식 규칙

- **Badge**: 최상단, CI → Coverage → Python Support 순서
- **코드 블록**: bash 언어 태그 사용, 복사-실행 가능한 형태
- **테이블**: 킷 목록은 반드시 Markdown 테이블 사용, 좌측 정렬
- **섹션 구조**: H2 기준 평면 구조, H3은 H2 내부 세분화에만 사용
- **TOC**: 생략 (GitHub 자동 목차 활용)

## 5) Update Triggers from Project Changes

아래 변경이 발생하면 README 갱신 필요 여부를 반드시 평가한다.

### A. Kit Metadata Changes

- 대상 파일: `kits/registry.json`, `kits/*/manifest.json`
- 점검 항목:
  - 제공 킷 목록 추가/삭제/이름 변경
  - 킷 버전 변경
  - agent/prompt 파일 추가/삭제/이름 변경
- 예상 수정 섹션:
  - 제공 중인 킷 표
  - Quick Start 예시
  - `multikit.toml` 예시

### B. CLI/Command Behavior Changes

- 대상 파일: `src/multikit/cli.py`, `src/multikit/commands/*`
- 점검 항목:
  - 명령 추가/삭제
  - 옵션/인자/기본 동작 변경
- 예상 수정 섹션:
  - 핵심 기능
  - CLI 사용법
  - 트러블슈팅

### C. Dev Workflow Changes

- 대상 파일: `pyproject.toml`, `tox.ini`, 테스트/린트 실행 정책
- 예상 수정 섹션:
  - 개발 환경 준비
  - 테스트 정책

### D. Path/Structure Changes

- 대상 파일: `.github/agents/*`, `.github/prompts/*`, `src/`, `tests/`
- 예상 수정 섹션:
  - 설치 후 예시 구조
  - 프로젝트 구조

## 6) Consistency Rules

README 제안/수정 시 아래 규칙을 만족해야 한다.

- Naming
  - 도구 이름은 파일 stem 기준으로 표기한다.
  - 예: `testkit.design` ← `testkit.design.agent.md`
- Version
  - 킷 버전은 각 manifest의 `version`과 동일해야 한다.
- Count
  - agent/prompt 개수 표기는 manifest 배열 길이와 동일해야 한다.
- Path examples
  - 예시 경로는 실제 파일명 패턴(`<kit>.<feature>.agent|prompt.md`)을 따라야 한다.
- Command examples
  - README 명령은 실행 가능한 형식이어야 하며, 현재 CLI와 모순되면 안 된다.
- Templates
  - 템플릿은 반드시 **킷 단위**로 관리한다: `kits/{name}/templates/{agent_name}/`
  - 공유(cross-kit) 템플릿 디렉터리(`kits/templates/`)를 만들지 않는다.
  - 공유 템플릿이 필요하다고 느끼면, 그것은 **책임 분리가 잘못된 신호**이다 — 해당 템플릿을 사용하는 에이전트가 속한 킷에 귀속시킨다.

검증 기준(테스트 가능성):

- 최소한 변경 제안 시 `kits/registry.json` + 관련 `manifest.json` 파일을 근거로 제시한다.
- 근거 없는 추측성 수정 제안은 금지한다.

## 7) Quality Standards

README 수정 제안 시 아래 품질 기준을 만족해야 한다.

### 정확성

- 모든 킷 이름/버전/에이전트 수는 `manifest.json`으로 검증 가능해야 한다.
- CLI 명령 예시는 실제 실행 가능해야 한다.
- 파일 경로 예시는 실제 프로젝트 구조와 일치해야 한다.

### 완전성

- 핵심 섹션(§3 정의)이 모두 존재해야 한다.
- 설치 가능한 모든 킷이 표에 포함되어야 한다.
- 삭제된 킷은 즉시 표에서 제거해야 한다.

### 예시 품질

- 설치/사용법 예시는 초보자가 복사-실행으로 동작 확인 가능해야 한다.
- `multikit.toml` 예시는 현재 스키마와 일치해야 한다.
- CLI 출력 예시는 실제 출력 형식을 반영해야 한다.

### 최신성

- 킷 생태계 변경(추가/삭제/통합) 후 README 업데이트 리드타임: 동일 커밋 또는 즉시 후속 커밋
- 버전 불일치 허용 기간: 없음 (예외 조항 §9 적용 시 제외)

## 8) Proposal and Approval Workflow

README 수정은 기본적으로 proposal-based로 진행한다.

1. 분석
   - 프로젝트 변경점을 수집하고 README 영향도를 판정한다.
2. 제안
   - 원자적 단위로 수정안(섹션/이유/현재/기대값/근거)을 제시한다.
3. 승인
   - 사용자 명시 승인 전에는 README를 수정하지 않는다.
4. 적용
   - 승인된 항목만 최소 변경으로 적용한다.
5. 보고
   - 적용 결과와 근거 파일을 요약한다.

금지 사항:

- 승인 전 `README.md` 자동 수정
- 승인 전 자동 커밋/푸시
- 근거 없는 스타일-only 대량 변경

## 9) Exception Handling and Ownership

예외 허용 조건:

- 릴리스 임박 등으로 임시 불일치가 불가피한 경우
- 외부 의존성 변경으로 즉시 반영이 어려운 경우

예외 처리 규칙:

- README 또는 PR 설명에 예외 사유/범위/만료 조건을 명시한다.
- 예외는 임시 조치이며, 후속 정합화 작업을 TODO로 남긴다.

책임 주체:

- 기본 오너: Maintainer (`@devcomfort`)
- README 관련 에이전트는 오너의 승인 규칙을 따라야 한다.

## 10) Versioning and Amendment Log

버전 규칙:

- MAJOR: 호환되지 않는 거버넌스 변경
- MINOR: 새로운 규칙 범주 추가 또는 실질적 확장
- PATCH: 문구 명확화/오탈자 수정

### Amendment Log

- 1.1.0 (2026-03-03)
  - Style & Tone 섹션 신설 (한국어/격식체/서식 규칙)
  - Quality Standards 섹션 신설 (정확성/완전성/예시 품질/최신성)
  - 10개 킷 생태계 반영 (lintkit/archkit 삭제, structkit/dockit 추가, refactorkit 통합)
- 1.0.0 (2026-02-23)
  - 초기 제정
  - Source of Truth/업데이트 트리거/Proposal-based 워크플로우 정의
  - 프로젝트 변경 기반 README 관리 원칙 확정
