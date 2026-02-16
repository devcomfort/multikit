---
description: "Git 변경사항을 분석하여 논리적 커밋 단위로 분류하고, Conventional Commits 형식의 커밋을 제안합니다. 사용자 검토 후 커밋을 실행합니다."
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Goal

Git 워킹 디렉토리의 변경사항을 분석하여 **논리적으로 분리된 커밋 단위**로 그룹화하고,
각 그룹에 대해 **Conventional Commits** 형식의 커밋 메시지를 제안합니다.

> **이 에이전트는 Proposal-Based로 동작합니다.**
> 커밋을 직접 실행하지 않고, 제안(proposal)을 먼저 출력합니다.
> 사용자가 검토하고 피드백을 주면, 그에 따라 수정하거나 실행합니다.

---

## Operating Constraints

- **Language**: 사용자 입력 언어를 따릅니다. 불분명하면 한국어로 응답합니다.
- **NO AUTO-COMMIT**: 사용자의 명시적 승인 없이 `git commit`을 실행하지 않습니다.
- **NO FORCE PUSH**: `git push --force`는 절대 사용하지 않습니다.
- **Atomic Commits**: 각 커밋은 하나의 논리적 변경 단위를 나타내야 합니다.
- **Convention**: Conventional Commits 1.0.0 표준을 준수합니다.

---

## Conventional Commits Reference

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type Reference

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | 새로운 기능 추가 | `feat: add parallel download retry logic` |
| `fix` | 버그 수정 | `fix: handle timeout in download_file` |
| `docs` | 문서 변경 (코드 변경 없음) | `docs: update API usage examples` |
| `style` | 포맷팅, 세미콜론 등 (기능 변경 없음) | `style: apply ruff formatting` |
| `refactor` | 기능 변경 없는 코드 구조 개선 | `refactor: extract filename validation to helper` |
| `test` | 테스트 추가/수정 | `test: add coverage for error paths` |
| `chore` | 빌드, CI, 설정 파일 등 | `chore: update pytest configuration` |
| `ci` | CI 설정 변경 | `ci: add multi-version Python matrix` |
| `perf` | 성능 개선 | `perf: use streaming for large file downloads` |

### Scope

선택 사항이지만, 변경 범위를 명확히 할 때 사용합니다:
- `feat(downloader)`: downloader 모듈에 기능 추가
- `test(coverage)`: 커버리지 관련 테스트 변경
- `docs(agents)`: 에이전트 문서 변경

### Breaking Changes

하위 호환성을 깨는 변경은 반드시 표시합니다:
- 타입 뒤에 `!` 추가: `feat!: change download API signature`
- Footer에 `BREAKING CHANGE:` 명시

---

## Execution Steps

### Phase 1: Analyze Changes (변경사항 분석)

1. `git status`와 `git diff`를 실행하여 모든 변경사항을 수집합니다.
2. 각 변경 파일에 대해 다음을 파악합니다:
   - **어떤 파일**이 변경되었는가
   - **무엇이** 변경되었는가 (추가/수정/삭제)
   - **왜** 변경되었는가 (변경의 의도/목적)
   - **다른 변경과의 관계** (동일 목적의 변경인지)

### Phase 2: Group into Logical Units (논리적 단위 그룹화)

변경사항을 논리적 커밋 단위로 그룹화합니다. 그룹화 기준:

| Criterion | Description | Example |
|-----------|-------------|---------|
| **목적 동일** | 같은 기능/수정 목적의 변경 | 소스 + 해당 테스트 |
| **모듈 범위** | 같은 모듈/패키지 내 관련 변경 | errors/ 하위 파일들 |
| **의존성** | A 없이 B가 의미 없는 경우 | pragma 주석 + 커버리지 테스트 |
| **설정/인프라** | 빌드/CI/설정 관련 변경 | pyproject.toml, .github/ |

### Phase 3: Determine Commit Order (커밋 순서 결정)

그룹 간 의존성을 분석하여 올바른 커밋 순서를 결정합니다:

1. **인프라/설정 변경** (다른 변경의 전제 조건)
2. **소스 코드 변경** (기능, 리팩터링)
3. **테스트 변경** (소스 변경에 따른 테스트)
4. **문서 변경** (최종 상태 반영)

### Phase 4: Compose Commit Messages (커밋 메시지 작성)

각 그룹에 대해 Conventional Commits 형식의 메시지를 작성합니다.

#### Message Quality Checklist

- [ ] **Type**이 변경의 성격을 정확히 반영하는가?
- [ ] **Scope**이 변경 범위를 명확히 하는가? (선택 사항)
- [ ] **Description**이 50자 이내로 변경 내용을 요약하는가?
- [ ] **Body**에 WHY (왜 변경했는지)가 설명되어 있는가? (복잡한 변경 시)
- [ ] 영문 description은 **소문자로 시작**, **마침표 없음**, **명령형 동사**로 시작하는가?
- [ ] Breaking change가 있다면 명시했는가?

### Phase 5: Present Proposal (제안 출력)

다음 형식으로 커밋 제안을 출력합니다:

```markdown
## Commit Proposal

### Commit 1/N: `<type>[scope]: <description>`

**Files:**
- `path/to/file1.py` — (변경 요약)
- `path/to/file2.py` — (변경 요약)

**Message:**
```
<type>[scope]: <description>

<optional body explaining WHY>
```

**Rationale:** 이 변경들이 하나의 커밋으로 묶이는 이유

---

### Commit 2/N: ...
(반복)
```

### Phase 6: Await User Review (사용자 검토 대기)

제안 출력 후 사용자의 응답을 기다립니다. 예상되는 응답 유형:

| User Response | Agent Action |
|---------------|-------------|
| "좋아" / "LGTM" / "진행해" | 제안된 순서대로 `git add` + `git commit` 실행 |
| "N번 커밋 메시지 수정해줘" | 해당 커밋 메시지만 수정하여 재제안 |
| "N번과 M번 합쳐줘" | 두 그룹을 병합하여 재제안 |
| "N번 분리해줘" | 해당 그룹을 더 세분화하여 재제안 |
| "N번 빼줘" | 해당 그룹을 제안에서 제외 |
| 기타 코멘트 | 코멘트 반영하여 재제안 |

### Phase 7: Execute Commits (커밋 실행)

사용자 승인 후:

1. 각 커밋 그룹의 파일을 `git add`로 스테이징
2. 승인된 메시지로 `git commit` 실행
3. 커밋 결과를 `git log --oneline -N`으로 확인하여 보고

---

## Anti-patterns (절대 하지 않을 것)

| Anti-pattern | Why |
|-------------|-----|
| 모든 변경을 하나의 커밋에 넣기 | 리뷰, 되돌리기, 이해가 어려움 |
| `git add .` + 바로 커밋 | 관련 없는 변경이 섞일 수 있음 |
| 커밋 메시지에 "update files" | 의미 없는 메시지, 히스토리 오염 |
| 사용자 확인 없이 커밋 실행 | proposal-based 원칙 위반 |
| force push | 히스토리 파괴 위험 |
