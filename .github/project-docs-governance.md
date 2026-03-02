# Project Documentation Governance

- Version: 1.0.0
- Last Updated: 2026-03-02
- Owner: Maintainer (`@devcomfort`)
- Scope: 사용자/기여자 대상 프로젝트 문서 사이트 정책

## 1) Purpose and Scope

이 문서는 multikit 프로젝트의 **사용자 대상 문서 사이트** 관리 원칙을 정의한다.

목표:

- 에이전트 사용자와 기여자 모두가 필요한 정보를 빠르게 찾을 수 있다
- 문서의 정확성·최신성을 코드 변경과 동기화하여 유지한다
- 문서 구조·스타일·배포 정책을 명시적으로 버전 관리하여 일관성을 보장한다

적용 범위:

- `docs/` 디렉토리 내 모든 Markdown 문서
- `zensical.toml` 문서 사이트 설정
- 문서 빌드·배포 파이프라인 (Cloudflare Pages)
- CLI 레퍼런스 자동 생성 (cyclopts MkDocs plugin)

비적용 범위:

- `README.md` (→ readme-governance.md)
- `kits/*/` 내부 에이전트·프롬프트 파일의 내용 (→ 각 킷 관리 정책)
- API/코드 수준 인라인 docstring 정책 — ⚠️ **별도 technical-docs-governance 불필요로 결정** (본 프로젝트는 라이브러리 API를 외부에 제공하지 않으며, CLI 레퍼런스는 cyclopts 자동 생성으로 충분)

## 2) Technology Stack

### Static Site Generator

| Item            | Value                                                          |
| --------------- | -------------------------------------------------------------- |
| SSG             | **Zensical** (v0.0.24+)                                        |
| Config          | `zensical.toml` (네이티브 TOML 형식)                           |
| Theme variant   | `modern` (기본)                                                |
| Package manager | rye (`rye add --dev zensical`)                                 |
| CLI autodoc     | `cyclopts[mkdocs]` 플러그인 — `multikit.cli:app`에서 자동 생성 |

### Plugin Compatibility Note

Zensical은 MkDocs 플러그인과의 호환 레이어를 제공한다. `cyclopts[mkdocs]` 플러그인의 설정은 다음 중 하나로 관리한다:

1. **Preferred**: Zensical의 네이티브 플러그인 설정이 지원되면 `zensical.toml`에 선언
2. **Fallback**: 네이티브 지원 전까지 `mkdocs.yml`에 `plugins:` 섹션만 별도 유지

### Core Dependencies

```toml
# pyproject.toml [project.optional-dependencies] 또는 rye dev-dependencies
[tool.rye]
dev-dependencies = [
    "zensical",
    "cyclopts[mkdocs]",
]
```

## 3) Information Architecture

### Site Structure (Tab-based Dual Structure)

문서 사이트는 **탭 기반 이중 구조**로 대상 독자별 영역을 분리한다.

```text
docs/
├── index.md                          # 🏠 Home: 프로젝트 소개 + 빠른 링크
│
├── getting-started/                  # 🚀 Getting Started (공통)
│   ├── index.md                      #   Installation & Setup
│   ├── quickstart.md                 #   5-minute Quickstart
│   └── concepts.md                   #   Core Concepts (kit, agent, prompt)
│
├── guide/                            # 📖 User Guide (탭 1)
│   ├── index.md                      #   Guide Overview
│   ├── cli-reference.md              #   CLI Reference (cyclopts 자동 생성)
│   ├── configuration.md              #   multikit.toml Configuration
│   └── kits/                         #   Kit-by-Kit Guides
│       ├── index.md                  #     Kit Overview & Catalog
│       ├── cikit.md                  #     cikit
│       ├── demokit.md                #     demokit
│       ├── dockit.md                 #     dockit
│       ├── gitkit.md                 #     gitkit
│       ├── multikit.md              #     multikit (self)
│       ├── promptkit.md              #     promptkit
│       ├── refactorkit.md            #     refactorkit
│       ├── speckit.md                #     speckit
│       └── testkit.md                #     testkit
│
├── contributing/                     # 🤝 Contributing Guide (탭 2)
│   ├── index.md                      #   Contributing Overview
│   ├── architecture.md               #   Project Architecture
│   ├── creating-kits.md              #   Creating New Kits
│   ├── creating-agents.md            #   Writing Agents & Prompts
│   ├── testing.md                    #   Testing Strategy
│   └── governance.md                 #   Governance Policies
│
└── changelog.md                      # 📝 Changelog
```

### Navigation Features

`zensical.toml`에서 활성화할 네비게이션 기능:

```toml
[project.theme]
features = [
    "navigation.tabs",
    "navigation.tabs.sticky",
    "navigation.sections",
    "navigation.indexes",
    "navigation.top",
    "navigation.path",
    "navigation.instant",
    "navigation.instant.prefetch",
    "search.highlight",
    "content.action.edit",
    "content.action.view",
    "toc.follow",
]
```

### Kit Page Template (권장 구조)

각 키트 전용 페이지(`docs/guide/kits/{name}.md`)는 아래 구조를 **권장**한다.
단, 해당 키트에 불필요하거나 반복 서술이 되는 섹션은 생략할 수 있다.

```markdown
# 🔧 {KitName}

> {한 줄 설명 — manifest.json description 기반}

## Overview

{키트의 목적, 해결하는 문제, 대상 사용자}

## Installation

{설치 명령 + 출력 예시}

## Agents

{에이전트 목록 — 이름, 역할, 주요 입출력}

## Usage Examples

{대표적인 사용 시나리오 + 명령 + 출력}

## Configuration

{키트별 설정이 있는 경우}

## Related Kits

{연관 키트 핸드오프 안내}
```

## 4) Writing Style

### Tone & Voice

| Item     | Policy                                   |
| -------- | ---------------------------------------- |
| 톤       | **Friendly-professional**                |
| 인칭     | **you** (2인칭) 중심                     |
| 언어     | **영어** 기본, 한국어 i18n은 추후 도입   |
| 이모지   | 섹션 제목에 사용 (🚀 Getting Started 등) |
| 페이지량 | 제한 없음 — 필요한 만큼 작성             |

### Code Examples

| Item        | Policy                                          |
| ----------- | ----------------------------------------------- |
| CLI 예시    | 명령 + 출력을 함께 표시                         |
| 코드 블록   | 제목 + 복사 버튼 (줄 번호 없음)                 |
| Admonitions | 적극 활용 (note, tip, warning, danger, example) |
| 다이어그램  | Mermaid (Zensical 내장 지원)                    |

### Style Example

````markdown
## 🚀 Getting Started with speckit

First, install speckit into your project:

```bash title="Install speckit"
multikit install speckit
```
````

```
✓ speckit installed successfully
```

You can then generate a spec for your new feature:

```bash title="Run speckit.clarify"
multikit run speckit.clarify
```

!!! tip
If you're unsure which agent to start with, `speckit.clarify` is
a great first step — it helps you identify gaps in your requirements.

````

## 5) Content Policies

### Update Triggers

문서 업데이트는 **코드 PR과 분리된 별도 PR**을 허용한다 (D14=b).

두 가지 운영 모드를 지원한다:

| Mode              | Flow                                                                     |
| ----------------- | ------------------------------------------------------------------------ |
| **Automated**     | CI가 코드 변경 감지 → 에이전트가 문서 업데이트 PR 자동 생성             |
| **Manual**        | CI가 진단 리포트만 생성 → 사용자가 에이전트 실행 → 검수 후 push         |

양쪽 모드 모두 최종적으로 문서 품질 검증 게이트를 통과해야 머지 가능하다.

### CLI Reference Generation

CLI 레퍼런스(`docs/guide/cli-reference.md`)는 cyclopts MkDocs 플러그인으로 **빌드 시 자동 생성**한다:

```markdown
# 🖥️ CLI Reference

::: cyclopts
    module: multikit.cli:app
    recursive: true
    heading_level: 2
````

수동 CLI 문서 작성은 금지한다 — 코드가 단일 진실 원천이다.

### Ownership

| Policy      | Value                            |
| ----------- | -------------------------------- |
| 소유권 모델 | **공동 소유** — 누구나 수정 가능 |
| 리뷰 요건   | 최소 **1명** 승인 필수           |
| 기본 오너   | Maintainer (`@devcomfort`)       |

### Quality Gates (CI)

아래 검증을 CI 파이프라인에서 실행한다:

| Check            | Tool / Method                  | Blocking |
| ---------------- | ------------------------------ | -------- |
| 깨진 링크        | CI link checker (e.g., lychee) | ✅ Yes   |
| 코드 블록 정확성 | doctest-style 검증             | ✅ Yes   |
| Markdown 린팅    | markdownlint                   | ✅ Yes   |
| 스펠체크         | cspell                         | ✅ Yes   |
| 빌드 성공        | `zensical build`               | ✅ Yes   |

## 6) Deployment

### Hosting & Trigger

| Item          | Value                               |
| ------------- | ----------------------------------- |
| 호스팅        | **Cloudflare Pages**                |
| 배포 트리거   | `main` 브랜치 머지 시 **자동 배포** |
| 빌드 명령     | `zensical build`                    |
| 출력 디렉토리 | `site/`                             |
| 커스텀 도메인 | 추후 설정                           |

### Versioned Documentation

| Item           | Value                                            |
| -------------- | ------------------------------------------------ |
| 버전 관리      | **다중 버전** (mike 또는 Zensical 네이티브 지원) |
| 최신 버전 라벨 | `latest`                                         |
| 보관 정책      | 최근 MAJOR 릴리스 + 현재 개발 버전               |

초기에는 단일 버전으로 시작하고, 프로젝트가 v2+ 릴리스에 도달하면 다중 버전을 활성화한다.

## 7) Source of Truth Hierarchy

문서 내용 충돌 시 아래 우선순위를 따른다 (상위가 우선):

1. **소스 코드** (`src/multikit/`) — CLI 동작, API 시그니처
2. **`kits/*/manifest.json`** — 킷 이름, 버전, 에이전트/프롬프트 목록
3. **`kits/registry.json`** — 공개 킷 카탈로그
4. **`pyproject.toml`** — 패키지 메타데이터, 의존성
5. **`docs/` 내 문서** — 설명 텍스트

규칙:

- 문서의 CLI 명령 예시는 실제 코드와 일치해야 한다 (cyclopts 자동 생성으로 보장)
- 문서의 킷 목록/버전/에이전트 수는 manifest와 일치해야 한다
- 불일치 발견 시 상위 소스 기준으로 문서를 수정한다

## 8) Exception Handling

예외 허용 조건:

- Zensical 또는 cyclopts 플러그인의 업스트림 변경으로 일시적 빌드 실패가 발생한 경우
- 대규모 킷 리팩토링 중 문서 동기화가 점진적으로 진행되는 경우

예외 처리 규칙:

- PR 설명 또는 `docs/` 내에 예외 사유/범위/만료 조건을 명시한다
- 예외는 임시 조치이며, 후속 정합화 작업을 TODO 또는 이슈로 남긴다

## 9) Governance Self-Versioning

| Bump  | Trigger                                               |
| ----- | ----------------------------------------------------- |
| MAJOR | 호환 불가 정책 변경 (예: SSG 교체, 구조 전면 재설계)  |
| MINOR | 새 규칙 카테고리 추가, 정책 확장 (예: i18n 정책 추가) |
| PATCH | 문구 명확화, 예시 추가/수정                           |

## Amendment Log

| Version | Date       | Change                                                                                       |
| ------- | ---------- | -------------------------------------------------------------------------------------------- |
| 1.0.0   | 2026-03-02 | 초기 거버넌스 수립 — Zensical 기반 문서 사이트 정책, IA, 스타일, 품질 게이트, 배포 정책 확정 |
