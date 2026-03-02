```chatagent
---
description: "multikit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## multikit — Meta-Kit for Agent Ecosystem Management

### 이 킷은 무엇인가요?

**multikit 에이전트 에코시스템 자체를 관리**하는 메타 킷입니다.
새 에이전트 생성, 기존 에이전트 개선, 에코시스템 등록, 일관성 검증을 담당합니다.

### 에이전트 구성

| 에이전트 | 역할 |
|---|---|
| `multikit.generation` | 새로운 에이전트 및 프롬프트 템플릿 생성 |
| `multikit.improve` | 기존 에이전트 선언 분석·개선 (구조/품질/패턴 감사) |
| `multikit.register` | 에이전트 에코시스템 등록 (manifest/registry/README/배포) |
| `multikit.validate` | 킷 일관성 감사 (매니페스트/배포/상호참조 검증) |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 새 에이전트를 만들고 싶다 | `multikit.generation` |
| 기존 에이전트의 품질을 개선하고 싶다 | `multikit.improve` |
| 새 킷을 에코시스템에 등록하고 싶다 | `multikit.register` |
| 매니페스트·배포 파일·상호참조가 일관적인지 확인하고 싶다 | `multikit.validate` |

### 워크플로우

```

새 에이전트:
generation → register → validate

기존 에이전트 개선:
improve → validate

정기 점검:
validate (단독 실행)

```

### 알아두면 좋은 점

- `generation`은 네이밍 규칙, frontmatter 형식, 섹션 구조 등 multikit 패턴을 자동 적용합니다.
- `validate`는 매니페스트, registry.json, .github/ 배포, handoff 참조의 **4중 일관성**을 검사합니다.
- 이 킷은 "킷을 만드는 킷" — 다른 모든 킷의 관리를 담당합니다.
```
