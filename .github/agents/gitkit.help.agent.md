```chatagent
---
description: "gitkit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## gitkit — Git Commit, Changelog & PR Notes

### 이 킷은 무엇인가요?

**Git 커밋 메시지 작성, CHANGELOG 생성, PR 노트 작성**을 도와주는 킷입니다.
Conventional Commits 규약을 따르며, CI 거버넌스 정책에 맞는 PR 설명을 생성합니다.

### 에이전트 구성

| 에이전트 | 역할 |
|---|---|
| `gitkit.commit` | Git 변경사항 분석 → 논리적 커밋 단위 그룹핑 → Conventional Commits 메시지 작성 |
| `gitkit.changelog` | Conventional Commits 기반 CHANGELOG.md 생성 |
| `gitkit.pr` | CI 거버넌스 PR Note Policy 기반 구조화된 PR 설명 생성 |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 여러 변경사항을 논리적 커밋으로 나누고 싶다 | `gitkit.commit` |
| 커밋 메시지를 잘 쓰고 싶다 | `gitkit.commit` |
| CHANGELOG를 생성하거나 업데이트하고 싶다 | `gitkit.changelog` |
| PR 설명을 체계적으로 작성하고 싶다 | `gitkit.pr` |
| 거버넌스 레퍼런스가 필요한 PR을 작성하고 싶다 | `gitkit.pr` |

### 워크플로우

```

코드 변경 → gitkit.commit → 커밋 완료 → gitkit.pr → PR 설명 생성

릴리스 시:
gitkit.changelog → CHANGELOG.md 생성/업데이트

```

### 알아두면 좋은 점

- `commit`은 사용자 리뷰 후에만 실제 커밋을 수행합니다 — 자동 커밋하지 않습니다.
- `pr`은 `.github/ci-governance.md` Section 9의 PR Note Policy를 따릅니다.
- Conventional Commits (feat, fix, refactor, docs 등) 규약을 따릅니다.
- 거버넌스 영역에 해당하는 변경이 포함되면 Governance Reference 섹션이 자동으로 추가됩니다.
```
