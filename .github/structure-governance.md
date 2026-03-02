# Project Directory Structure Governance

- Version: 1.0.0
- Last Updated: 2026-03-02
- Owner: devcomfort
- Scope: 프로젝트 디렉토리 구조, 네이밍 규칙, 배포 패턴

## 1) Purpose & Scope

이 문서는 프로젝트의 **디렉토리 구조 규칙**을 정의한다.

목표:

- 모든 디렉토리와 파일의 위치가 예측 가능하다
- 자동화 도구(CI, 코드 생성, 검증)가 구조에 의존할 수 있다
- 새 기여자가 설명 없이도 파일을 찾을 수 있다

적용 범위:

- 최상위 디렉토리 구성
- 킷(kit) 디렉토리 내부 구조
- 소스 코드 레이아웃
- 테스트 디렉토리 구조
- 스펙 디렉토리 구조
- 파일 네이밍 규칙
- 배포(deploy) 매핑 패턴

비적용 범위:

- 파일 내용 정책 (→ 각 거버넌스 문서)
- 버전 규칙 (→ versioning-governance.md)
- CI 정책 (→ ci-governance.md)

## 2) Top-Level Directory Map

| Directory   | Role                                                        | Required |
| ----------- | ----------------------------------------------------------- | :------: |
| `src/`      | Python 소스 패키지 루트                                     |   Yes    |
| `tests/`    | 테스트 코드 루트                                            |   Yes    |
| `kits/`     | 에이전트 킷 소스 (개발용 원본)                              |   Yes    |
| `specs/`    | 기능 스펙 문서                                              |   Yes    |
| `scripts/`  | 유틸리티 스크립트                                           |   Yes    |
| `.github/`  | GitHub 배포 대상 (에이전트, 프롬프트, 워크플로우, 거버넌스) |   Yes    |
| `.specify/` | 스펙 생성 도구 설정 (memory, templates)                     |   Yes    |

루트 레벨 설정 파일:

| File              | Purpose                          |
| ----------------- | -------------------------------- |
| `pyproject.toml`  | Python 프로젝트 메타데이터, 빌드 |
| `multikit.toml`   | multikit CLI 설정                |
| `tox.ini`         | 테스트 매트릭스 설정             |
| `coverage.xml`    | 테스트 커버리지 리포트           |
| `README.md`       | 프로젝트 소개 문서               |
| `REQUIREMENTS.md` | 요구사항 문서                    |
| `TODO.md`         | 작업 추적                        |

## 3) Kit Directory Structure

### 필수 구조

```
kits/{kit-name}/
├── manifest.json          # 킷 메타데이터 (필수)
├── agents/                # 에이전트 파일 (필수)
│   └── {kit}.{feature}.agent.md
├── prompts/               # 프롬프트 파일 (필수)
│   └── {kit}.{feature}.prompt.md
└── templates/             # 템플릿 파일 (선택)
    └── {template-name}/
        └── {name}.template.{ext}
```

### 규칙

- 모든 킷은 `agents/`, `prompts/`, `manifest.json`을 포함해야 한다.
- 모든 킷은 `{kit}.help.agent.md` + `{kit}.help.prompt.md`를 포함해야 한다.
- `templates/`는 거버넌스 문서나 설정 파일을 생성하는 에이전트에만 필요하다.
- `manifest.json`의 `agents` 배열은 실제 `agents/` 디렉토리의 파일과 1:1 매치해야 한다.
- `manifest.json`의 `prompts` 배열은 실제 `prompts/` 디렉토리의 파일과 1:1 매치해야 한다.

### 템플릿 규칙

- 템플릿 디렉토리명은 **template-name** (에이전트명이 아님)이다.
- 하나의 에이전트가 여러 템플릿을 사용할 수 있다.
- 템플릿은 킷 단위로 관리되며, 킷 간 템플릿 공유가 허용된다.
- 템플릿 파일명은 `{name}.template.{ext}` 패턴을 따른다.

### 레지스트리

- 모든 킷은 `kits/registry.json`에 등록해야 한다.
- 레지스트리의 `version`과 `manifest.json`의 `version`은 동기화해야 한다.
- 레지스트리 항목: `name`, `version`, `description` (필수).

## 4) Source Code Structure

```
src/multikit/
├── __init__.py            # 패키지 초기화
├── __main__.py            # python -m multikit 진입점
├── cli.py                 # cyclopts CLI 정의
├── commands/              # CLI 서브커맨드
├── models/                # pydantic 데이터 모델
├── registry/              # 레지스트리 로직
└── utils/                 # 유틸리티 함수
```

### 규칙

- `src/` 레이아웃을 사용한다 (`src/{package-name}/`).
- 진입점 파일 3개는 패키지 루트에 위치한다: `__init__.py`, `__main__.py`, `cli.py`.
- 기능별 서브모듈은 디렉토리로 분리한다.
- 현재 표준 서브모듈: `commands/`, `models/`, `registry/`, `utils/`.
- 새 서브모듈 추가 시 이 거버넌스를 업데이트한다.

## 5) Test Structure

```
tests/
├── conftest.py            # 공유 픽스처
├── {module}/              # src/ 모듈별 미러링
│   └── test_{feature}.py
├── {test-only}/           # 테스트 전용 디렉토리 (허용)
│   └── test_{feature}.py
└── integration/           # 통합 테스트 (선택)
    ├── conftest.py
    └── test_{scenario}.py
```

### 규칙

- `src/multikit/`의 각 서브모듈에 대응하는 테스트 디렉토리를 필수로 둔다.
  - 현재 미러링: `commands/`, `models/`, `registry/`, `utils/`.
- 소스에 대응하지 않는 테스트 전용 디렉토리를 허용한다.
  - 현재 테스트 전용: `badges/`, `cli/`, `entrypoints/`, `integration/`.
- 공유 픽스처 파일 `conftest.py`는 `tests/` 루트에 배치한다.
- 통합 테스트는 `tests/integration/` 하위에 별도로 둔다.
- 테스트 파일명은 `test_{feature}.py` 패턴을 따른다.

## 6) Spec Structure

```
specs/{NNN-feature-name}/
├── spec.md                # 기능 명세
├── plan.md                # 기술 계획
├── tasks.md               # 태스크 분해
├── data-model.md          # 데이터 모델 (선택)
├── research.md            # 리서치 노트 (선택)
├── quickstart.md          # 빠른 시작 가이드 (선택)
├── contracts/             # 계약/인터페이스 정의 (선택)
└── checklists/            # 체크리스트 (선택)
```

### 규칙

- 디렉토리 이름은 `NNN-kebab-case-name` 패턴 (예: `001-multikit-cli`, `002-readme-badges`).
- `NNN`은 0-padding 3자리 일련번호이다.
- 필수 파일: `spec.md`, `plan.md`, `tasks.md`.
- 선택 파일: `data-model.md`, `research.md`, `quickstart.md`.
- 선택 하위 디렉토리: `contracts/`, `checklists/`.

## 7) File Naming Conventions

### 에이전트/프롬프트

| Type        | Pattern                     | Example                    |
| ----------- | --------------------------- | -------------------------- |
| Agent       | `{kit}.{feature}.agent.md`  | `cikit.ci.check.agent.md`  |
| Prompt      | `{kit}.{feature}.prompt.md` | `cikit.ci.check.prompt.md` |
| Help agent  | `{kit}.help.agent.md`       | `gitkit.help.agent.md`     |
| Help prompt | `{kit}.help.prompt.md`      | `gitkit.help.prompt.md`    |

### 템플릿

| Type     | Pattern                            | Example                                     |
| -------- | ---------------------------------- | ------------------------------------------- |
| Template | `{name}.template.{ext}`            | `ci-governance.template.md`                 |
| Dir      | `kits/{kit}/templates/{tpl-name}/` | `kits/cikit/templates/cikit.ci.governance/` |

### 거버넌스

| Type       | Pattern                         | Example                    |
| ---------- | ------------------------------- | -------------------------- |
| Governance | `.github/{topic}-governance.md` | `.github/ci-governance.md` |

> **필수**: 모든 거버넌스 문서는 `.github/{topic}-governance.md` 네이밍을 따른다.

### 일반 규칙

- 킷 이름: 소문자, `kit` 접미사 (예: `gitkit`, `cikit`)
- 기능 이름: 소문자, `.`으로 계층 구분 (예: `ci.check`, `analyze.versioning`)
- 밑줄(`_`)은 단어 구분에 사용 (예: `project_docs`, `linter_errors`)
- 하이픈(`-`)은 스펙 디렉토리 이름에 사용 (예: `001-multikit-cli`)

## 8) Deployment Pattern

```
kits/{kit}/agents/{file}   →   .github/agents/{file}
kits/{kit}/prompts/{file}  →   .github/prompts/{file}
```

### 규칙

- 배포는 **flat copy**이다 — 킷 디렉토리 구조가 사라지고 파일만 복사된다.
- 배포 후 `.github/agents/`와 `.github/prompts/`의 파일은 모든 킷의 파일을 합친 것이다.
- 파일 이름에 킷 접두사가 있으므로 충돌하지 않는다.
- `multikit install` / `multikit uninstall`이 이 매핑을 관리한다.
- **배포 후 diff 0 유지 의무**: `kits/` 원본과 `.github/` 배포본은 내용이 동일해야 한다.

### .github/ 디렉토리 구조

```
.github/
├── agents/                # 배포된 에이전트 (flat)
├── prompts/               # 배포된 프롬프트 (flat)
├── workflows/             # GitHub Actions 워크플로우
├── copilot-instructions.md
└── {topic}-governance.md  # 거버넌스 문서
```

## 9) CI Verification Checklist

자동 검사 시 아래 항목을 검증한다:

| #   | Check                  | Rule                                                         |
| --- | ---------------------- | ------------------------------------------------------------ |
| 1   | 킷 필수 구조           | 모든 `kits/*/`에 `agents/`, `prompts/`, `manifest.json` 존재 |
| 2   | help 에이전트 존재     | 모든 `kits/*/`에 `{kit}.help.agent.md` 존재                  |
| 3   | Manifest ↔ 파일 매치   | `manifest.json` 배열과 실제 파일 1:1                         |
| 4   | 에이전트 네이밍        | `{kit}.{feature}.agent.md` 패턴 준수                         |
| 5   | 프롬프트 네이밍        | `{kit}.{feature}.prompt.md` 패턴 준수                        |
| 6   | 에이전트 ↔ 프롬프트 쌍 | 모든 에이전트에 대응하는 프롬프트 존재                       |
| 7   | 배포 동기화            | kits/ 파일과 .github/ 파일 내용 일치 (diff 0)                |
| 8   | 레지스트리 등록        | 모든 킷이 `kits/registry.json`에 등록                        |
| 9   | 네이밍 규칙            | 에이전트/프롬프트 파일명이 킷 접두사로 시작                  |

## 10) Exception Registry

거버넌스 규칙의 공식 예외를 기록한다.

| #   | Exception | Rule | Reason | Added |
| --- | --------- | ---- | ------ | ----- |
| —   | (없음)    | —    | —      | —     |

## 11) Governance Self-Versioning

| Bump  | Trigger                                                |
| ----- | ------------------------------------------------------ |
| MAJOR | 디렉토리 구조 호환 불가 변경 (필수 디렉토리 추가/제거) |
| MINOR | 새 규칙 추가, 새 디렉토리 역할 정의                    |
| PATCH | 문구 수정, 예시 추가                                   |

## Amendment Log

| Version | Date       | Change                  |
| ------- | ---------- | ----------------------- |
| 1.0.0   | 2026-03-02 | 초기 구조 거버넌스 수립 |
