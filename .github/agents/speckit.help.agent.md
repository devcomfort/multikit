```chatagent
---
description: "speckit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## speckit — Specification Analysis & Clarification

### 이 킷은 무엇인가요?

**기능 명세(Spec) 문서를 분석하고 명확화**하는 킷입니다.
spec.md, plan.md, tasks.md 등 설계 산출물의 일관성과 품질을 검사하고,
모호한 요구사항을 구조화된 질문으로 구체화합니다.

### 에이전트 구성

| 에이전트 | 역할 |
|---|---|
| `speckit.analyze` | 사양 문서·설계 산출물의 일관성·품질 분석 |
| `speckit.clarify` | 모호한 요구사항 식별 → 구조화된 질문으로 명확화 |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 작성된 스펙의 품질을 점검하고 싶다 | `speckit.analyze` |
| spec.md와 plan.md가 일관적인지 확인하고 싶다 | `speckit.analyze` |
| 요구사항이 모호해서 구체화가 필요하다 | `speckit.clarify` |
| 의사결정이 필요한 부분을 식별하고 싶다 | `speckit.clarify` |

### 워크플로우

```

스펙 점검:
analyze → 리포트 출력

모호한 부분 해소:
clarify → 질문 → 답변 반영 → analyze (재검증)

교차 킷 연계:
clarify/analyze → testkit.design (테스트 설계)
clarify → structkit.analyze (아키텍처 분석)

```

### 알아두면 좋은 점

- `analyze`는 spec, plan, tasks 간의 **교차 일관성**을 검사합니다.
- `clarify`는 "결정 불필요(합리적 기본값)" vs "결정 필요(옵션 제시)" 를 구분합니다.
- 명세 확정 후 `testkit.design`으로 테스트를 설계하거나, `structkit.analyze`로 아키텍처를 점검할 수 있습니다.
```
