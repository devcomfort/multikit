# CI Automation Governance

- Version: TODO_VERSION (e.g., 1.0.0)
- Last Updated: TODO_DATE
- Owner: TODO_OWNER

## 1) Purpose & Scope

이 문서는 CI 자동 검수 환경에 대한 정책을 정의한다.
어떤 도구를 사용하여, 어떤 조건에서, 무엇을 검사하고, 실패 시 어떻게 처리하는지를 명시한다.

적용 범위:

- GitHub Actions 기반 자동 검사 워크플로우
- Copilot CLI / Ralph Wiggum 기반 AI 검사
- 거버넌스 준수 자동 검증 (README, 구조, 버전)

비적용 범위:

- 빌드/테스트 CI (pytest, ruff 등 — 별도 워크플로우)
- 배포 파이프라인

## 2) Tool Policy

| 항목                 | 정책                                                        | 근거                          |
| -------------------- | ----------------------------------------------------------- | ----------------------------- |
| 기본 실행 엔진       | TODO: Copilot 직접 / Ralph 루프 / 둘 다                     |                               |
| AI 에이전트          | GitHub Copilot CLI (`--agent copilot`)                      |                               |
| 모델 선택            | 환경변수 `COPILOT_MODEL`로 지정                             | 프로젝트마다 최적 모델이 다름 |
| Ralph max-iterations | TODO: 기본값 (환경변수 `RALPH_MAX_ITERATIONS`로 오버라이드) |                               |

## 3) Authentication Policy

| 항목                | 규칙                                                         |
| ------------------- | ------------------------------------------------------------ |
| PAT 종류            | Fine-grained PAT with **Copilot Requests** 권한              |
| GitHub Secrets 이름 | `PERSONAL_ACCESS_TOKEN`                                      |
| 워크플로우 환경변수 | `COPILOT_GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}` |
| 모델 설정           | GitHub Variables: `COPILOT_MODEL`                            |
| Ralph 반복 제한     | GitHub Variables: `RALPH_MAX_ITERATIONS`                     |

## 4) Trigger Policy

| 트리거   | 조건                    | 비고                                 |
| -------- | ----------------------- | ------------------------------------ |
| PR       | `pull_request` to main  | 전체 검사 수행                       |
| Push     | `push` to main          | merge commit 제외 (PR에서 이미 검증) |
| Manual   | `workflow_dispatch`     | 디버깅 및 수동 트리거                |
| Schedule | TODO: 필요 시 cron 추가 | 주기적 전체 검사 (선택)              |

**중복 검증 방지**:
PR 머지로 인한 push는 자동으로 스킵한다.

## 5) Failure & Reporting Policy

| 항목         | 정책                                          |
| ------------ | --------------------------------------------- |
| 실패 시 동작 | **리포트만 생성** — 자동 수정/PR 생성 없음    |
| 리포트 형식  | Workflow log 출력 (향후 PR comment 확장 가능) |
| 블로킹 여부  | Non-blocking (경고만, 머지 차단 없음)         |
| 리포트 보존  | `specs_ci/ci-check-report.md` (Ralph 모드)    |

## 6) Cost Control Policy

| 항목              | 규칙                                                   |
| ----------------- | ------------------------------------------------------ |
| Copilot 과금 모델 | 요청 횟수 기반                                         |
| Ralph 반복 상한   | `RALPH_MAX_ITERATIONS` 환경변수 (기본 TODO)            |
| 모델 등급         | 경제적 모델 우선, 필요 시 거버넌스 수정으로 업그레이드 |
| 실행 빈도         | PR 검사 + main 직접 push 검사                          |

## 7) Check Scope

CI에서 수행하는 검사 항목:

| 카테고리      | 검사 항목                                                | 거버넌스 근거            |
| ------------- | -------------------------------------------------------- | ------------------------ |
| README 준수   | 필수 섹션 존재, manifest 데이터 일치, 예시 유효성        | readme-governance.md     |
| 프로젝트 구조 | .help 에이전트, manifest 유효성, 네이밍, agent-prompt 쌍 | (구조 규칙)              |
| 버전 일관성   | manifest vs pyproject.toml, semver 유효성                | versioning-governance.md |

## 8) Version & Amendment Log

버전 규칙:

- MAJOR: 호환되지 않는 정책 변경
- MINOR: 새로운 규칙 추가 또는 확장
- PATCH: 문구 수정

### Amendment Log

- TODO_VERSION (TODO_DATE)
  - 초기 제정
