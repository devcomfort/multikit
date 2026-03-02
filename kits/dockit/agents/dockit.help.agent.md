````chatagent
---
description: "dockit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## dockit — Documentation Governance, Generation & Analysis

### 이 킷은 무엇인가요?

프로젝트의 **문서화 거버넌스(정책 수립), 초기 문서 생성, 문서 업데이트 진단**을 담당하는 킷입니다.
대상: README, 프로젝트 문서(가이드/튜토리얼/API 레퍼런스/아키텍처 문서)

> 문서 유형은 기술 스택이 아닌 **내용과 구조**에 따라 구분합니다.
> **dockit은 "문서가 무엇이어야 하는가(What)"를 소유합니다.**
> CI/CD 파이프라인 자동화는 cikit의 영역입니다.

### 에이전트 구성

| 그룹 | 에이전트 | 역할 |
|---|---|---|
| **거버넌스** | `dockit.governance.readme` | README 필수 섹션·서식·말투·업데이트 정책 수립 |
| | `dockit.governance.project_docs` | 프로젝트 문서 거버넌스 (가이드, API 레퍼런스, 아키텍처 문서 포함) |
| **생성** | `dockit.generate.readme` | 코드베이스 → 초기 README 생성 |
| | `dockit.generate.project_docs` | 코드베이스 → 초기 프로젝트 문서 생성 (가이드 + API + 아키텍처) |
| **분석** | `dockit.analyze.readme` | git 히스토리 기반 README 업데이트 필요성 진단 |
| | `dockit.analyze.project_docs` | git 히스토리 기반 프로젝트 문서 업데이트 진단 |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 문서 정책을 처음 세우고 싶다 | `dockit.governance.*` (해당 영역) |
| 코드는 있는데 README가 없다 | `dockit.generate.readme` |
| 프로젝트 문서를 처음 만들고 싶다 | `dockit.generate.project_docs` |
| API 문서와 docstring을 정비하고 싶다 | `dockit.generate.project_docs` |
| README가 최신인지 확인하고 싶다 | `dockit.analyze.readme` |
| 프로젝트 문서가 코드와 맞는지 확인 | `dockit.analyze.project_docs` |
| 문서의 서식·말투·구조를 바꾸고 싶다 | `dockit.governance.*` (해당 영역) |

### 워크플로우

```

초기 설정:
multikit install dockit
→ .github/readme-governance.md (거버넌스 템플릿)

1단계: 거버넌스 (정책 수립)
governance.* → 대화를 통해 문서 정책 결정
  - 서식, 말투, 구조, 필수 섹션, 업데이트 트리거
  - 프로젝트 유형(개발/연구/교육)에 따른 전략

2단계: 초기 생성
generate.* → 코드를 읽고 거버넌스에 맞는 문서 생성

3단계: 유지보수 (반복)
analyze.* → git 히스토리 기반으로 문서 업데이트 필요성 진단

```

### cikit과의 관계

| dockit | cikit |
|---|---|
| 문서 **정책과 내용**을 소유 | CI/CD **자동화 파이프라인**을 소유 |
| "문서가 무엇이어야 하는가" (What) | "그것을 언제/어떻게 자동화할 것인가" (How) |
| git 히스토리 + 코드 전체 대상 분석 | CI 트리거 맥락 분석 |
| `.github/*-governance.md` 생성 | `.github/workflows/*.yml` 생성 |

### 템플릿

| 템플릿 | 배포 위치 | 용도 |
|---|---|---|
| `readme-governance.template.md` | `.github/readme-governance.md` | README 거버넌스 시작점 |

### 핵심 특징

- **Proposal-First**: 모든 거버넌스 결정과 문서 변경은 사용자 승인 후 적용
- **Proactive Suggestions**: 대화 중 필요를 감지하면 선제적으로 제안
- **서식/말투/구조 커스터마이징**: 사용자가 직접 제안/수정 가능
- **프로젝트 유형 인식**: 개발/연구/교육 프로젝트에 따라 문서 전략이 달라짐
- **Git 히스토리 기반 분석**: analyze 에이전트는 전체 git 이력을 분석 소스로 사용

```
````
