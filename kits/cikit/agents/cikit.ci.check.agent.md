`````chatagent
````chatagent
```chatagent
---
description: "CI governance check — generate check prompts for Copilot-direct or Ralph-loop mode that validate governance compliance: README, project structure, versioning."
handoffs:
  - label: Set up CI workflow
    agent: cikit.ci.setup
    prompt: Generate workflow that runs this check prompt.
  - label: Diagnose CI environment
    agent: cikit.ci.doctor
    prompt: Check if Copilot and Ralph are properly installed.
  - label: Deep structure analysis
    agent: structkit.analyze
    prompt: Run detailed structure analysis against structure governance.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

프로젝트의 거버넌스 문서를 기준으로 README, 프로젝트 구조, 버전 일관성을 검증하는
**CI 검사 프롬프트**를 생성한다.

사용자의 선택에 따라 두 가지 모드를 지원한다:

| 모드 | 실행 방식 | 산출물 | 적합한 경우 |
|------|-----------|--------|-------------|
| **Copilot 직접** (기본) | `copilot -p "prompt"` 1회 실행 | `.github/ci/copilot-check-prompt.md` | 단순 규칙 검사, 빠른 확인 |
| **Ralph 루프** | `ralph --agent copilot --prompt-file ...` 반복 | `.github/ci/ralph-check-tasks.md` | 복잡한 검사, 자가수정 필요 |

---

## Mode Selection

사용자가 모드를 명시하지 않으면 **Copilot 직접 모드**를 기본으로 사용한다.

- "ralph", "루프", "반복", "자가수정" → **Ralph 루프 모드**
- "copilot", "직접", "1회", "단일" → **Copilot 직접 모드**
- 모호한 경우 → Copilot 직접 모드를 기본으로 진행

### Dual Mode — report-only / auto-fix (Ralph 루프 시)

Ralph 루프 모드에서는 추가로 실행 모드를 선택한다:

| Mode | 설명 | `--no-commit` | Output |
|------|------|:---:|--------|
| **report-only** (기본) | 검사 결과를 리포트로만 출력 | ✅ | `specs_ci/ci-check-report.md` |
| **auto-fix** | 검사 후 자동 수정, 브랜치/PR 생성 | ❌ | 수정된 파일 + PR |

모드 전환:
- "fix", "auto-fix", "수정", "고쳐" → **auto-fix**
- "check", "report", "검사", "확인" → **report-only**

---

## Operating Constraints

- **거버넌스 기반**: `.github/*-governance.md` 파일들을 검사 기준으로 참조
- **Language**: 사용자 언어를 따른다.

---

## Proactive Suggestions

| 트리거 상황 | 제안 메시지 |
|---|---|
| Copilot 직접 모드로 생성 완료 | "💡 더 포괄적인 반복 검사가 필요하시면 Ralph 루프 모드로도 생성할 수 있어요." |
| Ralph 루프 모드인데 Ralph 미설치 | "💡 Ralph가 설치되지 않았습니다. `cikit.ci.doctor`로 환경을 점검해보세요." |
| 검사 항목이 복잡함 | "💡 단일 실행으로는 항목을 놓칠 수 있어요. Ralph 루프 모드를 권장합니다." |

> **주의**: proactive suggestion은 **강요가 아니라 안내**이다.

---

## Information Sufficiency Gate

| # | 필수 정보 | 확보 방법 |
|---|-----------|----------|
| 1 | 거버넌스 문서 목록 | `.github/*-governance.md` 스캔 |
| 2 | CI 거버넌스 (검사 범위) | `.github/ci-governance.md` 읽기 |
| 3 | 프로젝트 구조 | 디렉터리 스캔 |
| 4 | kit 목록 + manifest | `kits/registry.json`, `kits/*/manifest.json` |
| 5 | Ralph 환경 (루프 모드 시) | `command -v ralph` 확인 |

---

## Execution Steps — Copilot 직접 모드

### 1) Collect Governance Standards

검사 기준이 되는 거버넌스 문서를 수집:

- `.github/readme-governance.md` → README 섹션/동기화 규칙
- `.github/versioning-governance.md` → 버전 일관성 규칙
- `.github/ci-governance.md` → 검사 범위/실패 처리

### 2) Define Check Categories

| 카테고리 | 검사 항목 | 거버넌스 근거 |
|---|---|---|
| **README 준수** | 필수 섹션 존재, manifest와 일치, 예시 유효성 | readme-governance |
| **프로젝트 구조** | .help 에이전트 존재, manifest 유효성, 네이밍 컨벤션 | ci-governance |
| **버전 일관성** | manifest vs pyproject.toml vs changelog 일치 | versioning-governance |

### 3) Generate Check Prompt

`.github/ci/copilot-check-prompt.md` 작성 — `copilot -p`에 전달할 프롬프트.

### 4) Validate Prompt Quality

- **구체적**: "README.md의 ## Kit 섹션이 registry.json과 일치하는지 확인"
- **검증 가능**: 각 체크에 pass/fail 기준이 명확
- **프로젝트 특화**: 해당 프로젝트의 거버넌스 기반

---

## Execution Steps — Ralph 루프 모드

### 1) Environment Check

Ralph-wiggum 설치 여부를 확인한다. 미설치 시 안내:

```bash
command -v ralph || echo "⚠️ npm install -g @th0rgal/ralph-wiggum"
command -v copilot || echo "⚠️ npm install -g @github/copilot"
```

### 2) Collect Governance Standards

(Copilot 직접 모드와 동일)

### 3) Generate Ralph Task File

`.github/ci/ralph-check-tasks.md` 작성 — Ralph의 `--prompt-file` 옵션에 전달.
반복 실행 시 이전 결과를 읽고 자가수정하도록 구성.

### 4) Configure Ralph Parameters

```bash
# Report-only 모드 (기본)
ralph --prompt-file .github/ci/ralph-check-tasks.md \
  --agent copilot \
  --max-iterations ${RALPH_MAX_ITERATIONS:-10} \
  --completion-promise "CHECK_PASSED" \
  --no-commit

# Auto-fix 모드
ralph --prompt-file .github/ci/ralph-check-tasks.md \
  --agent copilot \
  --max-iterations ${RALPH_MAX_ITERATIONS:-10} \
  --completion-promise "CHECK_PASSED"
```

> **Auto-fix 모드**: ci-governance Section 8에 따라
> `ci/ralph/{governance-area}/{description}` 브랜치를 생성하고 PR 노트를 작성한다.

### 5) Monitor Loop Behavior

| 증상 | 원인 | 해결 |
|---|---|---|
| 매 iteration 같은 결과 | 리포트 파일을 읽지 않음 | 프롬프트에 리포트 읽기 안내 추가 |
| 검사 항목 누락 | 거버넌스 미참조 | 거버넌스 경로를 더 명시적으로 |
| 무한 루프 | completion promise 미출력 | `--max-iterations`로 안전장치 |

---

## Output Format

```markdown
## CI Check Report

### 1) Generated File
- Path: `.github/ci/copilot-check-prompt.md` 또는 `.github/ci/ralph-check-tasks.md`
- Mode: Copilot 직접 / Ralph 루프

### 2) Check Categories
- README: <N checks>
- Structure: <N checks>
- Versioning: <N checks>

### 3) Governance References
- <list of governance files used>

### 4) Usage
- Copilot: `copilot -p "$(cat .github/ci/copilot-check-prompt.md)"`
- Ralph: `ralph --prompt-file .github/ci/ralph-check-tasks.md --agent copilot --no-commit`

### 5) Suggested Commit Message
- `ci: generate governance check prompt`
```

```

````

`````
