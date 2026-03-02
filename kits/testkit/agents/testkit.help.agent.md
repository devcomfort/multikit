```chatagent
---
description: "testkit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## testkit — Test Design, Planning, Coverage & Analysis

### 이 킷은 무엇인가요?

**테스트를 설계하고, 계획하고, 커버리지를 분석**하는 킷입니다.
"무엇을 테스트할까" → "어떻게 테스트할까" → "빠진 테스트가 있나" → "설계대로 구현되었나"의 흐름을 제공합니다.

### 에이전트 구성

| 에이전트 | 역할 |
|---|---|
| `testkit.design` | 테스트 설계 문서 생성 (what/why/how) |
| `testkit.plan` | 테스트 전략 및 실행 계획 수립 |
| `testkit.coverage` | 테스트 커버리지 분석 및 누락된 테스트 보완 |
| `testkit.analyze` | 테스트 설계/계획 vs 실제 테스트 일관성 분석 |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 새 기능에 대한 테스트를 설계하고 싶다 | `testkit.design` |
| 테스트 전략(단위/통합/E2E 비율 등)을 세우고 싶다 | `testkit.plan` |
| 커버리지를 올리거나 누락된 테스트를 찾고 싶다 | `testkit.coverage` |
| 설계한 테스트가 실제로 구현되었는지 확인하고 싶다 | `testkit.analyze` |

### 워크플로우

```

신규 기능 테스트:
design → plan → 구현 → analyze (설계 vs 구현 비교)

커버리지 개선:
coverage → 누락 테스트 보완

정기 점검:
analyze (설계/계획과 실제 테스트의 일관성)

```

### 알아두면 좋은 점

- `design`은 **테스트 케이스**를, `plan`은 **실행 전략**을 다룹니다.
- `analyze`는 설계 산출물과 실제 테스트 코드의 **교차 일관성**을 검사합니다.
- 커버리지 하드닝(edge case 테스트 추가)은 `refactorkit.fix` + "coverage" 키워드로 함께 활용 가능합니다.
```
