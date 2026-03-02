```chatagent
---
description: "cikit 워크플로우 안내 — 에이전트 역할, 사용 시나리오, 추천 흐름을 설명합니다."
---

## cikit — CI/CD Pipeline Automation

### 이 킷은 무엇인가요?

**CI/CD 파이프라인** 내에서 사용할 자동화 도구와 정책을 생성하고, 파이프라인 내에서 에이전트가 실행되는 환경을 구성하는 킷입니다.
버전 정책 수립, 변경 분석(CI 트리거 맥락), CI 자동 검수(Copilot CLI / Ralph Wiggum) 워크플로우를 제공합니다.

> 문서 거버넌스·생성·업데이트는 **dockit**의 영역입니다.

### 에이전트 구성

| 그룹 | 에이전트 | 역할 |
|---|---|---|
| **거버넌스** | `cikit.governance.versioning` | 버전 정책 수립 (SemVer/CalVer 등) |
| **분석** | `cikit.analyze.change` | CI 트리거 맥락에서 커밋 변경사항 분석 |
| | `cikit.analyze.versioning` | 버전 범프 레벨 분석 |
| | `cikit.analyze.versioning.update` | 버전 업데이트 실행 |
| **CI 자동화** | `cikit.ci.governance` | CI 자동화 정책 수립 (도구·인증·트리거·비용) |
| | `cikit.ci.setup` | GitHub Actions 워크플로우 + 설치 스크립트 생성 |
| | `cikit.ci.check` | 거버넌스 검사 프롬프트 생성 (Copilot 직접 / Ralph 루프 모드 선택) |
| | `cikit.ci.doctor` | CI 환경 진단 (도구·인증·변수·거버넌스 확인) |

### 언제 사용하나요?

| 상황 | 추천 진입점 |
|---|---|
| 버전 정책을 세우고 싶다 | `cikit.governance.versioning` |
| CI 파이프라인 내에서 변경 분석이 필요하다 | `cikit.analyze.change` |
| 버전을 올려야 하는지 판단하고 싶다 | `cikit.analyze.versioning` |
| 버전 업데이트를 실행하고 싶다 | `cikit.analyze.versioning.update` |
| CI에서 자동 검사를 세우고 싶다 | `cikit.ci.governance` → `cikit.ci.setup` |
| CI에서 거버넌스 검사를 하고 싶다 (Copilot/Ralph) | `cikit.ci.check` |
| CI 환경이 잘 구성됐는지 확인하고 싶다 | `cikit.ci.doctor` |

### 워크플로우

```

초기 설정 (설치 시 템플릿 자동 배포):
multikit install cikit
→ .github/versioning-governance.md (버전 거버넌스 템플릿)
→ .github/ci-governance.md (CI 자동화 거버넌스)
→ .github/workflows/ci-check-copilot.yml (Copilot 워크플로우)
→ .github/workflows/ci-check-ralph.yml (Ralph 워크플로우)
→ .github/scripts/setup-copilot-ralph.sh (도구 설치 스크립트)
→ .github/scripts/populate-governance.sh (데이터 채우기 스크립트)
→ .github/ci/copilot-check-prompt.md (Copilot 검사 프롬프트)
→ .github/ci/ralph-check-tasks.md (Ralph 태스크 파일)

버전 정책 수립:
governance.versioning 에이전트가 템플릿을 프로젝트에 맞게 수정

변경 분석 (CI 트리거):
analyze.change → analyze.versioning → analyze.versioning.update

CI 자동화 설정:
ci.governance → ci.setup → ci.check (Copilot 직접 또는 Ralph 루프 모드)
문제 진단: ci.doctor

```

### 템플릿

cikit은 설치 시 아래 **템플릿 파일**을 함께 배포합니다.
이미 파일이 있으면 건드리지 않으므로, 커스터마이징한 내용은 보존됩니다.

| 템플릿 | 배포 위치 | 용도 |
|---|---|---|
| `versioning-governance.template.md` | `.github/versioning-governance.md` | 버전 거버넌스 시작점 |
| `populate-governance.sh` | `.github/scripts/populate-governance.sh` | 템플릿 플레이스홀더 채우기 |
| `ci-governance.template.md` | `.github/ci-governance.md` | CI 자동화 거버넌스 정책 |
| `ci-check-copilot.template.yml` | `.github/workflows/ci-check-copilot.yml` | Copilot 직접 모드 워크플로우 |
| `ci-check-ralph.template.yml` | `.github/workflows/ci-check-ralph.yml` | Ralph 루프 모드 워크플로우 |
| `setup-copilot-ralph.template.sh` | `.github/scripts/setup-copilot-ralph.sh` | Copilot + Ralph 설치 스크립트 |
| `copilot-check-prompt.template.md` | `.github/ci/copilot-check-prompt.md` | Copilot 검사 프롬프트 |
| `ralph-check-tasks.template.md` | `.github/ci/ralph-check-tasks.md` | Ralph 태스크 파일 |

### 알아두면 좋은 점

- **문서 관련은 dockit으로**: README, API 문서, 프로젝트 문서의 정책·생성·업데이트는 dockit이 담당합니다.
- **버전 정책이 먼저**: 정책이 있어야 분석 에이전트가 범프 레벨을 결정할 수 있습니다.
- `analyze.change`가 CI 맥락의 분석 시작점 — 변경 문서를 기반으로 버전 분석이 수행됩니다.
- **CI 자동화**: `ci.governance`로 정책 수립 → `ci.setup`으로 워크플로우 생성 → `ci.check`으로 검사 프롬프트 생성
- **듀얼 모드**: `ci.check`이 Copilot 직접 모드와 Ralph 루프 모드 모두 지원
- **환경 진단**: CI 구성 후 `ci.doctor`로 도구·인증·환경 변수 상태 확인
```
