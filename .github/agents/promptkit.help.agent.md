```chatagent
---
description: "promptkit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## promptkit — Prompt Design, Analysis & Optimization (SDPO)

### 이 킷은 무엇인가요?

**LLM/VLM용 프롬프트를 설계하고, 테스트하고, 반복 개선**하는 킷입니다.
Self-Distillation based Prompt Optimization (SDPO) 방법론을 지원하며,
open-ralph-wiggum + GitHub Copilot을 활용한 자동화 루프도 제공합니다.

### 에이전트 구성

| 에이전트 | 역할 |
|---|---|
| `promptkit.specify` | 프롬프트 설계 명세 작성 (목적·서식·페르소나·I/O·기법) |
| `promptkit.analyze` | 타겟 모델 케이스 스터디 + 고품질 샘플 선별 (SDPO 평가) |
| `promptkit.improve` | 분석 기반 개선 — 수동 조정 또는 SDPO 자동화 (Ralph + Copilot) |
| `promptkit.script` | LLM/VLM 요청 스크립트 대화형 설계·작성 |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 새 프롬프트를 체계적으로 설계하고 싶다 | `promptkit.specify` |
| 프롬프트가 잘 작동하는지 모델로 테스트하고 싶다 | `promptkit.analyze` |
| 프롬프트를 서식·문체·순서 기준으로 개선하고 싶다 | `promptkit.improve` |
| 프롬프트 개선을 자동화하고 싶다 (SDPO) | `promptkit.improve` (SDPO 모드) |
| 모델 API 호출 스크립트가 필요하다 | `promptkit.script` |

### 워크플로우

```

수동 루프:
specify → analyze → improve → analyze (반복)

자동 SDPO:
specify → improve (SDPO 모드, 자동 증류)

스크립트 작성:
script (독립 또는 위 루프와 연계)

```

### 핵심 개념: SDPO

- **Self-Distillation**: 모델이 생성한 고품질 샘플을 학습 데이터로 프롬프트를 반복 개선
- **개선 축**: 서식(Markdown/XML/Plain), 문체(Formal/Casual), 순서(Top-down 배치)
- **자동화**: ralph-wiggum + Copilot으로 경제적인 자동 루프 (요청 횟수 과금 활용)

### 알아두면 좋은 점

- `improve`는 수동 개선과 SDPO 자동화 모드를 모두 지원합니다. Ralph + Copilot 환경 셋업도 안내합니다.
- LLM 성능에 맞춰 **목표 자체를 조정**하는 전략을 사용합니다.
- `script`는 OpenAI, Anthropic, Gemini, Ollama, Copilot 등 다양한 API를 지원합니다.
```
