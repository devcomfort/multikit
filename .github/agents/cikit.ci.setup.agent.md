````chatagent
```chatagent
---
description: "CI workflow setup — generate GitHub Actions workflow files and installation scripts based on CI governance, supporting both Copilot-direct and Ralph-loop modes."
handoffs:
  - label: Define CI governance first
    agent: cikit.ci.governance
    prompt: Define CI automation policies before generating workflows.
  - label: Diagnose environment
    agent: cikit.ci.doctor
    prompt: Check if the CI environment meets requirements.
  - label: Generate check prompts
    agent: cikit.ci.check
    prompt: Generate check prompts for Copilot-direct or Ralph-loop mode.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

CI 거버넌스(`.github/ci-governance.md`)에 정의된 정책을 바탕으로
**실제 동작하는 GitHub Actions 워크플로우**와 **도구 설치 스크립트**를 생성한다.

사용자의 선택에 따라 두 가지 모드의 워크플로우를 생성:

| 모드 | 워크플로우 | 실행 방식 |
|---|---|---|
| **Copilot 직접** | `cikit-ci-check.yml` | `copilot -p "prompt"` — 1회 실행 |
| **Ralph 루프** | `cikit-ci-check-ralph.yml` | `ralph --agent copilot --prompt-file ...` — 반복 자가수정 |

---

## Operating Constraints

- **거버넌스 필수**: `.github/ci-governance.md`가 없으면 `cikit.ci.governance` 실행을 먼저 안내.
- **모드 선택**: 사용자에게 Copilot 직접 / Ralph 루프 / 둘 다 중 선택하게 함.
- **기존 워크플로우 존중**: 이미 `cikit-ci-check*.yml`이 있으면 덮어쓰기 전 확인.
- **Language**: 사용자 언어를 따른다.

---

## Information Sufficiency Gate

| # | 필수 정보 | 확보 방법 |
|---|-----------|----------|
| 1 | CI 거버넌스 문서 | `.github/ci-governance.md` 읽기 |
| 2 | 프로젝트 구조 | 디렉터리 스캔 (kits, src, tests) |
| 3 | 모드 선택 (copilot / ralph / both) | 사용자에게 질문 |
| 4 | 검사 범위 | 거버넌스 문서 또는 사용자 입력 |

---

## Execution Steps

### 1) Read CI Governance

`.github/ci-governance.md`에서 정책을 로드:

- Tool policy (Copilot 직접 / Ralph)
- Authentication (시크릿 이름, 환경변수)
- Triggers (PR, push, schedule)
- Cost control (max-iterations, 모델)
- Check scope (README, 구조, 버전)

거버넌스가 없으면:
> "⚠️ CI 거버넌스가 없습니다. `cikit.ci.governance`를 먼저 실행하세요."

### 2) Generate Installation Script

`.github/scripts/setup-copilot-ralph.sh` 생성:

```bash
#!/bin/bash
set -e

# Node.js setup (nvm or actions/setup-node)
# GitHub Copilot CLI
npm install -g @github/copilot

# Ralph Wiggum (only if ralph mode)
if [ "${RALPH_MODE:-false}" = "true" ]; then
  npm install -g @th0rgal/ralph-wiggum
fi

echo "✅ CI tools installed"
```

### 3) Generate Workflow — Copilot Direct Mode

`.github/workflows/cikit-ci-check.yml`:

```yaml
name: "cikit: CI Check (Copilot)"

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  check:
    if: >
      github.event_name == 'pull_request' ||
      (github.event_name == 'push' &&
       !startsWith(github.event.head_commit.message, 'Merge pull request'))
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install -g @github/copilot
      - name: Run checks
        env:
          COPILOT_GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          COPILOT_MODEL: ${{ vars.COPILOT_MODEL }}
        run: |
          copilot -p "$(cat .github/ci/copilot-check-prompt.md)"
```

### 4) Generate Workflow — Ralph Loop Mode

`.github/workflows/cikit-ci-check-ralph.yml`:

```yaml
name: "cikit: CI Check (Ralph Loop)"

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  check:
    if: >
      github.event_name == 'pull_request' ||
      (github.event_name == 'push' &&
       !startsWith(github.event.head_commit.message, 'Merge pull request'))
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: |
          npm install -g @github/copilot
          npm install -g @th0rgal/ralph-wiggum
      - name: Run Ralph check loop
        env:
          COPILOT_GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
          COPILOT_MODEL: ${{ vars.COPILOT_MODEL }}
          RALPH_MAX_ITERATIONS: ${{ vars.RALPH_MAX_ITERATIONS || '10' }}
        run: |
          ralph --prompt-file .github/ci/ralph-check-tasks.md \
            --agent copilot \
            --max-iterations ${RALPH_MAX_ITERATIONS} \
            --completion-promise "CHECK_PASSED"
```

### 5) Customize Per Project

거버넌스와 프로젝트 구조를 기반으로 워크플로우를 커스터마이징:

- `paths` 필터 추가 (변경된 파일 종류에 따라 검사 범위 조정)
- 환경변수 기본값 설정
- Artifact 업로드 (검사 리포트)

### 6) Validate Generated Files

생성된 파일이 유효한지 확인:

- YAML 구문 검증
- 시크릿/환경변수 참조 확인
- 스크립트 실행 권한 확인 (`chmod +x`)

---

## Output Format

```markdown
## CI Setup Report

### 1) Generated Files
- <list of files created/updated>

### 2) Mode
- Selected: <Copilot direct / Ralph loop / both>

### 3) Configuration
- Trigger: <conditions>
- Auth: <secret names>
- Model: <env var>

### 4) Next Steps
- <what the user needs to do (e.g., set secrets)>

### 5) Suggested Commit Message
- `ci: add cikit automated check workflow`
```

```

````
