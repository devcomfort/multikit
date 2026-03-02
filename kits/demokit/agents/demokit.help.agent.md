```chatagent
---
description: "demokit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## demokit — Demo Design & Implementation

### 이 킷은 무엇인가요?

프로젝트의 **데모를 설계하고 구현**하는 킷입니다.
`__main__` 블록의 간단한 CLI 데모부터 TUI, GUI 앱까지 다양한 형태의 데모를 만듭니다.

### 에이전트 구성

| 에이전트 | 역할 |
|---|---|
| `demokit.design` | 데모 전략 수립 — 형태(CLI/TUI/GUI) 및 범위 결정 |
| `demokit.build` | 데모 구현 — 실제 코드 작성 |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 프로젝트에 데모를 추가하고 싶다 | `demokit.design` |
| 어떤 형태의 데모가 적합한지 모르겠다 | `demokit.design` |
| 데모 전략이 이미 있고 구현만 필요하다 | `demokit.build` |

### 워크플로우

```

design → build

```

### 알아두면 좋은 점

- `design`이 먼저 — 형태와 범위를 정한 뒤 `build`로 구현합니다.
- 프로젝트의 핵심 기능을 효과적으로 보여주는 것이 데모의 목표입니다.
```
