# Project Directory Structure Governance

- Version: 1.0.0
- Last Updated: {DATE}
- Owner: {OWNER}
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

| Directory | Role   | Required |
| --------- | ------ | :------: |
| {DIR}     | {ROLE} | {YES/NO} |

루트 레벨 설정 파일:

| File   | Purpose   |
| ------ | --------- |
| {FILE} | {PURPOSE} |

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
    └── {agent-name}/
        └── {template-file}
```

### 규칙

- 모든 킷은 `agents/`, `prompts/`, `manifest.json`을 포함해야 한다.
- 모든 킷은 `{kit}.help.agent.md` + `{kit}.help.prompt.md`를 포함해야 한다.
- `templates/`는 거버넌스 문서나 설정 파일을 생성하는 에이전트에만 필요하다.
- `manifest.json`의 `agents` 배열은 실제 `agents/` 디렉토리의 파일과 1:1 매치해야 한다.
- `manifest.json`의 `prompts` 배열은 실제 `prompts/` 디렉토리의 파일과 1:1 매치해야 한다.

## 4) Source Code Structure

```
src/{package-name}/
├── __init__.py
├── __main__.py           # CLI 진입점 (해당 시)
├── cli.py                # CLI 정의 (해당 시)
├── commands/             # CLI 서브커맨드
├── models/               # 데이터 모델
├── registry/             # 레지스트리 로직
└── utils/                # 유틸리티
```

### 규칙

{SOURCE_RULES}

## 5) Test Structure

```
tests/
├── conftest.py           # 공유 픽스처
├── {module}/             # src/ 모듈별 미러링
│   └── test_{feature}.py
└── integration/          # 통합 테스트 (선택)
    ├── conftest.py
    └── test_{scenario}.py
```

### 규칙

{TEST_RULES}

## 6) Spec Structure

```
specs/{NNN-feature-name}/
├── spec.md               # 기능 명세
├── plan.md               # 기술 계획
├── tasks.md              # 태스크 분해
├── data-model.md         # 데이터 모델 (선택)
├── research.md           # 리서치 노트 (선택)
├── quickstart.md         # 빠른 시작 가이드 (선택)
├── contracts/            # 계약/인터페이스 정의 (선택)
└── checklists/           # 체크리스트 (선택)
```

### 규칙

{SPEC_RULES}

## 7) File Naming Conventions

### 에이전트/프롬프트

| Type        | Pattern                     | Example                   |
| ----------- | --------------------------- | ------------------------- |
| Agent       | `{kit}.{feature}.agent.md`  | `gitkit.commit.agent.md`  |
| Prompt      | `{kit}.{feature}.prompt.md` | `gitkit.commit.prompt.md` |
| Help agent  | `{kit}.help.agent.md`       | `gitkit.help.agent.md`    |
| Help prompt | `{kit}.help.prompt.md`      | `gitkit.help.prompt.md`   |

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

- 배포는 flat copy이다 — 킷 디렉토리 구조가 사라지고 파일만 복사된다.
- 배포 후 `.github/agents/`와 `.github/prompts/`의 파일은 모든 킷의 파일을 합친 것이다.
- 파일 이름에 킷 접두사가 있으므로 충돌하지 않는다.
- `multikit install` / `multikit uninstall`이 이 매핑을 관리한다.

## 9) CI Verification Checklist

Ralph 자동 검사 시 아래 항목을 검증한다:

| #   | Check                  | Rule                                        |
| --- | ---------------------- | ------------------------------------------- |
| 1   | 킷 help 에이전트 존재  | 모든 `kits/*/`에 `{kit}.help.agent.md` 존재 |
| 2   | Manifest ↔ 파일 매치   | `manifest.json` 배열과 실제 파일 1:1        |
| 3   | 에이전트 네이밍        | `{kit}.{feature}.agent.md` 패턴 준수        |
| 4   | 프롬프트 네이밍        | `{kit}.{feature}.prompt.md` 패턴 준수       |
| 5   | 에이전트 ↔ 프롬프트 쌍 | 모든 에이전트에 대응하는 프롬프트 존재      |
| 6   | 배포 동기화            | kits/ 파일과 .github/ 파일 내용 일치        |
| 7   | 템플릿 존재            | manifest templates 배열의 src 파일 존재     |

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

| Version | Date   | Change                  |
| ------- | ------ | ----------------------- |
| 1.0.0   | {DATE} | 초기 구조 거버넌스 수립 |
