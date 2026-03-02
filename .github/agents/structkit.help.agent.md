---
description: "structkit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## structkit — Project Structure Governance & Architecture Analysis

### 이 킷은 무엇인가요?

**프로젝트 구조의 거버넌스, 분석, 수정**을 담당하는 킷입니다.
두 가지 관점에서 프로젝트 구조를 다룹니다:

1. **거버넌스 준수 검사** — 디렉토리 역할, 네이밍 규칙, 배포 패턴을 정의하고 위반을 감지
2. **아키텍처 분석** — 아키텍처 패턴, 설계 패턴, 컨벤션을 분석하고 개선 방향을 제안

### 에이전트 구성

| 에이전트               | 역할                                                                 |
| ---------------------- | -------------------------------------------------------------------- |
| `structkit.governance` | 디렉토리 구조 거버넌스 생성/갱신 — `.github/structure-governance.md` |
| `structkit.analyze`    | **두 가지 모드**: (A) 거버넌스 대비 구조 위반/변동 분석, (B) 아키텍처 패턴 분석·토론·제안 |
| `structkit.fix`        | 위반사항에 대한 수정 계획 제안 및 실행                               |

### 언제 사용하나요?

| 상황                                         | 추천 진입점                                                |
| -------------------------------------------- | ---------------------------------------------------------- |
| 프로젝트 구조 규칙을 처음 정의하고 싶다      | `structkit.governance`                                     |
| 기존 구조 규칙을 업데이트하고 싶다           | `structkit.governance`                                     |
| 구조가 거버넌스를 잘 따르는지 점검하고 싶다  | `structkit.analyze` (Mode A: Compliance)                   |
| 새 킷/모듈 추가 후 구조 검증이 필요하다      | `structkit.analyze` (Mode A: Compliance)                   |
| 기존 프로젝트의 아키텍처를 분석하고 싶다     | `structkit.analyze` (Mode B: Architecture)                 |
| 새 프로젝트의 아키텍처를 설계하고 싶다       | `structkit.analyze` (Mode B: Architecture)                 |
| 아키텍처 패턴이나 설계 구조를 추천받고 싶다  | `structkit.analyze` (Mode B: Architecture)                 |
| 분석에서 나온 위반을 수정하고 싶다           | `structkit.fix`                                            |
| CI에서 구조 검사를 자동화하고 싶다           | `structkit.analyze` (Ralph 프롬프트의 참조 대상)           |

### 워크플로우

```

최초 거버넌스 설정:
structkit.governance → 거버넌스 생성 → structkit.analyze (Mode A 검증)

정기 점검:
structkit.analyze (Mode A) → 리포트 → (위반 있으면) structkit.fix → 수정 → 재검증

구조 변경 시:
structkit.analyze (Mode A) → DRIFT 감지 → structkit.governance (거버넌스 갱신)

아키텍처 분석:
structkit.analyze (Mode B) → 패턴 식별 → 추천 리포트 → (구현 시) speckit.clarify

새 프로젝트 설계:
structkit.analyze (Mode B, 대화 모드) → 컨텍스트 수집 → 아키텍처 추천

CI 자동화:
cikit.ci.check → structkit 거버넌스 참조 → Ralph 루프 검사

```

### 다른 킷과의 연계

| 연계 킷               | 관계                                                  |
| --------------------- | ----------------------------------------------------- |
| `cikit`               | CI 검사 시 structure-governance.md를 규칙 소스로 참조 |
| `multikit.generation` | 새 킷 생성 후 구조 규칙 준수 여부 검증                |
| `multikit.validate`   | 킷 유효성 검증 시 구조 규칙 교차 확인                 |
| `speckit.clarify`     | 아키텍처 추천 후 스펙에 반영                          |
| `gitkit.commit`       | 구조 수정 후 커밋                                     |

### 알아두면 좋은 점

- `analyze`는 **모드 선택**으로 거버넌스 점검과 아키텍처 분석을 모두 수행합니다.
- `governance`는 **기존 패턴을 발견하고 명시화**합니다 — 새 규칙을 발명하지 않습니다.
- `analyze`는 READ-ONLY입니다 — 파일을 절대 수정하지 않습니다.
- `fix`는 proposal-based입니다 — 수정 계획을 보여주고 승인 후에만 실행합니다.
- 아키텍처 추천은 항상 **2-3개 옵션 + 근거 + 트레이드오프**를 함께 제시합니다.
