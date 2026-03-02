```chatagent
---
description: "refactorkit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## refactorkit — Code Quality Diagnosis & Remediation

### 이 킷은 무엇인가요?

**코드 품질을 진단하고 수정**하는 킷입니다.
린터 에러, deprecation, 논리 오류, 테스트 경고, 커버리지 갭, 테스트 누수를
체계적으로 진단하고 수정합니다.

### 에이전트 구성

| 에이전트 | 역할 |
|---|---|
| `refactorkit.diagnose` | 포괄적 코드 건강 진단 — 린트, deprecation, 논리 오류, 경고, 커버리지, 누수를 한번에 분석 |
| `refactorkit.fix` | 진단 결과 기반 통합 수정 — 린트 수정, import 정리, 마이그레이션, 리팩토링, 경고 해소, 커버리지 강화 |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 코드 전반의 건강 상태를 점검하고 싶다 | `refactorkit.diagnose` |
| 린트 에러만 집중 진단하고 싶다 | `refactorkit.diagnose` + "lint" 키워드 |
| 테스트 경고를 없애고 싶다 | `refactorkit.diagnose` + "warning" → `refactorkit.fix` + "warning" |
| 커버리지를 올리고 싶다 | `refactorkit.diagnose` + "coverage" → `refactorkit.fix` + "coverage" |
| 코드 스멜을 정리하고 싶다 | `refactorkit.diagnose` + "smell" → `refactorkit.fix` + "smell" |
| 진단 결과를 바탕으로 수정하고 싶다 | `refactorkit.fix` (진단 리포트 전달) |

### 워크플로우

```
포괄 진단 + 수정:
diagnose (전체) → fix (우선순위별 수정)

특정 영역 집중:
diagnose + "키워드" → fix + "키워드"

예시 키워드: lint, deprecation, logical/smell, warning, coverage, leakage/skip
```

### 알아두면 좋은 점

- **항상 진단 먼저**: `fix`는 `diagnose`의 리포트를 전제조건으로 요구합니다.
- `diagnose`에 키워드를 주면 특정 영역만 선택적으로 진단할 수 있습니다.
- `fix`도 마찬가지로 키워드를 사용하여 특정 카테고리만 수정할 수 있습니다.
- 리팩토링, 마이그레이션, skip 해제는 **Proposal-based** — 사용자 승인 후 실행됩니다.
- 커버리지 하드닝은 `testkit.coverage`와 함께 활용할 수 있습니다.

```