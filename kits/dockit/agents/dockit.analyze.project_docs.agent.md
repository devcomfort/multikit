````chatagent
---
description: "Project documentation impact analysis — analyze git history and codebase changes to determine if documentation (guides, tutorials, API reference, architecture docs) needs updates, and propose patches."
handoffs:
  - label: Regenerate project docs
    agent: dockit.generate.project_docs
    prompt: Regenerate project documentation based on current codebase state.
  - label: Update project docs governance
    agent: dockit.governance.project_docs
    prompt: Update project documentation governance rules.
  - label: Commit doc updates
    agent: gitkit.commit
    prompt: Commit the approved documentation changes.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

git 히스토리와 코드베이스 변경 이력을 분석하여 **프로젝트 문서**
(가이드, 튜토리얼, Getting Started, API 레퍼런스, 아키텍처 문서 등)가
업데이트되어야 하는지 진단한다.

> For README, use `/dockit.analyze.readme`.
> 문서 유형은 기술 스택이 아닌 **내용과 구조**에 따라 구분합니다.

---

## Analysis Source: Git History + Codebase

> dockit.analyze.*는 **전체 git 히스토리 + 현재 코드베이스**를 대상으로 분석한다.
> CI 파이프라인 맥락의 분석은 cikit.analyze.change의 영역이다.

---

## Operating Constraints

- **Proposal-based**: 문서를 직접 수정하지 않는다.
- **No Git mutation**: 명시적 요청 없이 커밋/푸시하지 않는다.
- **Governance-aware**: `.github/project-docs-governance.md` 따른다.
- **Scope**: 프로젝트에 감지된 문서 시스템만 대상.
- **Language**: 사용자 언어를 따른다.

---

## Information Sufficiency Gate

| # | 필수 정보 | 확보 방법 |
|---|-----------|----------|
| 1 | 프로젝트 문서 시스템 감지 | docs/, wiki/, SSG config 탐색 |
| 2 | 변경사항 컨텍스트 | git log + git diff |
| 3 | 문서 거버넌스 정책 | .github/project-docs-governance.md (선택) |
| 4 | 기술 문서 시스템 감지 | Sphinx, pdoc, TypeDoc, OpenAPI 설정 탐색 |

---

## Execution Steps

### 1) Detect Documentation System

| System         | Detection                                         |
| -------------- | ------------------------------------------------- |
| Docusaurus     | `docusaurus.config.js`, `docs/`, `sidebars.js`    |
| VitePress      | `.vitepress/config.*`, `docs/`                     |
| MkDocs         | `mkdocs.yml`, `docs/`                              |
| GitHub Wiki    | `.github/wiki/`                                    |
| Plain Markdown | `docs/` with `.md` files                           |

`NO_DOCS_SYSTEM` → 중단, `dockit.governance.project_docs` 실행 제안.

### 2) Load Change Context (Git History)

1. **git log** — 최근 커밋들 (메시지 + 변경 파일)
2. **git diff** — HEAD vs 기준점
3. **파일 변경 목록** — 추가/수정/삭제된 소스 파일
4. **사용자 입력** — 특정 변경 확인 요청

### 3) Map Documentation Structure

문서 시스템의 페이지/섹션/네비게이션 구조 파악.

### 4) Determine Documentation Impact

| Change Type                    | Documentation Impact                           |
| ------------------------------ | ---------------------------------------------- |
| New feature/command            | Feature guide, tutorial, getting started       |
| Changed behavior/UX            | Affected guides, FAQ                           |
| Removed feature                | All pages referencing it                       |
| Config change                  | Configuration guide                            |
| New dependency                 | Installation guide                             |
| New public API                 | API reference, module index                    |
| Changed function signature     | API reference, migration notes                 |
| Removed public API             | API reference, deprecation notice              |
| Architecture change            | Architecture docs, ADR                         |
| Docstring update               | Regenerate affected API pages                  |

Classify: **N-STALE** / **N-MISSING** / **N-DEAD-LINK** / **D-REWRITE** / **D-NEW-PAGE** / **D-RESTRUCTURE**

### 5) Build & Present Proposals

```markdown
### Proposal {n}/{total}: {short title}
- **Classification**: ...
- **File**: {doc file path}
- **Trigger**: {git commit/change}
- **Current**: {current content}
- **Proposed**: {replacement}
- **Evidence**: {commit hash or file path}
```

Status: `NO_ACTION` / `PROPOSAL_READY` / `BLOCKED` / `NO_DOCS_SYSTEM`

### 6) Execute (After Approval)

1. 승인된 편집 적용
2. 네비게이션/사이드바 업데이트 (필요 시)
3. 변경 요약 + 커밋 메시지 제안

---

## Anti-Patterns (Do Not)

| # | Anti-Pattern | Why |
|---|---|---|
| 1 | 존재하지 않는 문서 시스템 제안 | 거버넌스가 전략 결정 |
| 2 | 소스 변경 없이 문서 편집 제안 | 변경 기반이어야 함 |
| 3 | 승인 전 문서 수정 | Proposal-first 필수 |
| 4 | README/API docs와 프로젝트 문서 제안 혼합 | 각각 별도 에이전트 |

````
