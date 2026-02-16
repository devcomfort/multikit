# Feature Specification: Multikit CLI (MVP)

**Feature Branch**: `001-multikit-cli`
**Created**: 2026-02-11
**Status**: Draft
**Input**: User description: "cyclopts 기반 CLI 도구. multikit install로 .github에 agents/prompts를 VS Code Copilot 환경에 맞게 설치. raw.githubusercontent.com에서 다운로드. Claude Code/Cursor 등 타 IDE 미지원."

## Clarifications

### Session 2026-02-11

- Q: 킷 파일 목록은 어떻게 탐색(discovery)해야 하는가? → A: manifest.json — 각 킷 폴더에 `manifest.json`을 두고 에이전트/프롬프트 파일 이름을 명시적으로 선언한다.
- Q: 이미 설치된 킷 파일이 로컬 수정되었거나 원격이 업데이트된 경우 어떻게 처리하는가? → A: 대화식 확인 + 선택적 덮어쓰기. 파일별 diff를 보여주고 개별 확인 후 덮어쓸지 결정. 별도 `multikit diff` 명령으로 사전 확인 가능.
- Q: HTTP 클라이언트 라이브러리는 무엇을 사용하는가? → A: httpx — sync/async 모두 지원하며 경량. 향후 async 확장 가능.
- Q: `multikit list`가 보여주는 "사용 가능한 킷" 목록의 소스는? → A: registry.json — 원격 리포지토리 루트에 `registry.json`(킷 이름/버전 목록)을 두고, `list` 시 이를 GET하여 전체 목록 표시.
- Q: `multikit install` 도중 네트워크 오류로 일부 파일만 다운로드된 경우 롤백 전략은? → A: Atomic (임시 디렉토리) — 모든 파일을 임시 디렉토리에 먼저 다운로드하고, 전부 성공 시에만 `.github/`로 이동. 실패 시 임시 파일 삭제.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - 프로젝트 초기화 (Priority: P1)

개발자가 새 프로젝트에서 `multikit init`을 실행하여 VS Code Copilot 에이전트를 설치할 수 있는 기반 구조(`.github/agents/`, `.github/prompts/`, `multikit.toml`)를 생성한다.

**Why this priority**: 모든 후속 명령의 전제 조건. 이것 없이는 install/list/uninstall이 동작하지 않음.

**Independent Test**: 빈 디렉토리에서 `multikit init`을 실행하고, `.github/agents/`, `.github/prompts/` 디렉토리와 `multikit.toml` 파일이 존재하는지 확인.

**Acceptance Scenarios**:

1. **Given** 빈 프로젝트 디렉토리, **When** `multikit init` 실행, **Then** `.github/agents/`와 `.github/prompts/` 디렉토리가 생성됨.
2. **Given** 빈 프로젝트 디렉토리, **When** `multikit init` 실행, **Then** `multikit.toml`이 기본 템플릿으로 생성됨.
3. **Given** 이미 `.github/` 폴더가 존재하는 프로젝트, **When** `multikit init` 실행, **Then** 기존 파일을 보존하고 누락된 구조만 추가함 (멱등성).

---

### User Story 2 - 원격 킷 설치 (Priority: P1)

개발자가 `multikit install testkit`을 실행하면 `raw.githubusercontent.com`에서 킷의 에이전트/프롬프트 파일을 다운로드하여 `.github/agents/`와 `.github/prompts/`에 설치하고, `multikit.toml`에 설치 기록을 남긴다.

**Why this priority**: 도구의 핵심 가치 — 에이전트를 프로젝트에 주입하는 것.

**Independent Test**: `multikit init` 후 `multikit install testkit`을 실행하고, `.github/agents/testkit.*.agent.md`와 `.github/prompts/testkit.*.prompt.md` 파일이 다운로드되었는지 확인.

**Acceptance Scenarios**:

1. **Given** 초기화된 프로젝트, **When** `multikit install testkit` 실행, **Then** 원격 레지스트리에서 킷 매니페스트를 조회하고, 에이전트/프롬프트 파일을 `.github/` 하위에 다운로드함.
2. **Given** 초기화된 프로젝트, **When** `multikit install testkit` 실행, **Then** `multikit.toml`의 `[multikit.kits.testkit]` 섹션이 생성되어 버전과 소스 정보가 기록됨.
3. **Given** 이미 testkit이 설치된 프로젝트, **When** `multikit install testkit` 실행, **Then** 로컬과 원격 파일의 차이를 파일별로 diff 형식으로 표시하고, 각 파일에 대해 덮어쓰기 여부를 개별 확인한다. `--force` 플래그 시 확인 없이 모두 덮어쓴다.
4. **Given** 존재하지 않는 킷 이름, **When** `multikit install invalidkit` 실행, **Then** 명확한 에러 메시지를 출력하고 파일 시스템을 변경하지 않음.
5. _(이 시나리오는 User Story 5 — 킷 변경 사항 확인에서 다룹니다. US5-AS2 참조.)_

---

### User Story 3 - 설치된 킷 목록 조회 (Priority: P2)

개발자가 `multikit list`를 실행하여 현재 프로젝트에 설치된 킷과 레지스트리에서 사용 가능한 킷을 확인한다.

**Why this priority**: 설치 상태의 가시성 제공. install/uninstall 없이도 독립적으로 가치가 있음.

**Independent Test**: 킷을 설치한 후 `multikit list`를 실행하고, 테이블 형식 출력에서 설치된 킷이 표시되는지 확인.

**Acceptance Scenarios**:

1. **Given** testkit이 설치된 프로젝트, **When** `multikit list` 실행, **Then** 원격 `registry.json`에서 전체 킷 목록을 조회하고, testkit이 "Installed" 상태로 표시됨.
2. **Given** 킷이 없는 프로젝트, **When** `multikit list` 실행, **Then** 사용 가능한 킷 목록이 모두 "Not installed" 상태로 표시됨.
3. **Given** 네트워크 오류 상황, **When** `multikit list` 실행, **Then** `multikit.toml`에 기록된 로컬 설치 킷만 표시하고, 원격 조회 실패를 경고로 알림.

---

### User Story 4 - 킷 제거 (Priority: P2)

개발자가 `multikit uninstall testkit`을 실행하여 설치된 에이전트/프롬프트 파일을 삭제하고 설정에서 기록을 제거한다.

**Why this priority**: 가역성(reversibility) 보장. install의 역연산.

**Independent Test**: 킷을 설치한 후 uninstall을 실행하고, 관련 파일이 삭제되었는지 및 `multikit.toml`에서 제거되었는지 확인.

**Acceptance Scenarios**:

1. **Given** testkit이 설치된 프로젝트, **When** `multikit uninstall testkit` 실행, **Then** `.github/agents/testkit.*.agent.md`와 `.github/prompts/testkit.*.prompt.md` 파일이 삭제됨.
2. **Given** testkit이 설치된 프로젝트, **When** `multikit uninstall testkit` 실행, **Then** `multikit.toml`에서 `[multikit.kits.testkit]` 섹션이 제거됨.
3. **Given** 설치되지 않은 킷, **When** `multikit uninstall unknownkit` 실행, **Then** 에러 메시지 출력, 파일 시스템 변경 없음.

---

### User Story 5 - 킷 변경 사항 확인 (Priority: P2)

개발자가 `multikit diff <kit>`를 실행하여 로컬에 설치된 킷 파일과 원격 최신 버전 사이의 차이를 확인한다. 로컬 수정과 원격 업데이트 양쪽 모두에 대응한다.

**Why this priority**: install 전에 변경 사항을 안전하게 미리 확인할 수 있어 사용자 실수를 방지함.

**Independent Test**: 킷을 설치 후 로컬 파일을 수정하거나 원격이 업데이트된 상황에서 `multikit diff testkit`을 실행하고, diff 출력이 표시되는지 확인.

**Acceptance Scenarios**:

1. **Given** testkit 설치 후 로컬 파일이 수정된 상태, **When** `multikit diff testkit` 실행, **Then** 수정된 파일에 대해 로컬↔원격 diff가 표시됨.
2. **Given** testkit 설치 후 원격에 새 버전이 배포된 상태, **When** `multikit diff testkit` 실행, **Then** 버전 차이와 변경된 파일의 diff가 표시됨.
3. **Given** 로컬과 원격이 동일한 상태, **When** `multikit diff testkit` 실행, **Then** "No changes detected" 메시지가 출력됨.

---

### Edge Cases

- **네트워크 오류**: `install`은 모든 파일을 임시 디렉토리에 먼저 다운로드(atomic). 중간에 네트워크가 끊기면 임시 파일을 삭제하고 `.github/`는 변경하지 않음. 에러 메시지와 함께 실패한 파일을 보고.
- **권한 오류**: `.github/` 디렉토리에 쓰기 권한이 없는 경우 명확한 에러 메시지 출력.
- **동시 실행**: MVP 범위에서 명시적으로 제외. 동시 실행 시 `multikit.toml` 레이스 컨디션이 발생할 수 있으나, MVP에서는 이를 감지하거나 방지하지 않음. Post-MVP에서 락 파일 기반 동시성 제어를 도입 예정.
- **로컬 수정 충돌**: `install` 시 로컬 파일이 수정되어 원격과 다를 경우, 파일별 diff를 보여주고 `[y/n/a(all)/s(skip all)]` 선택지를 제공해야 함.
- **빈 킷**: 에이전트/프롬프트 파일이 하나도 없는 킷을 install하면 경고를 출력.
- **대용량 파일**: 에이전트 파일이 비정상적으로 클 경우 (>1MB) 경고를 출력.
- **multikit.toml 손상**: TOML 파싱 실패 시 백업 후 명확한 에러 메시지 출력.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: `multikit init` 명령은 `.github/agents/`, `.github/prompts/` 디렉토리와 `multikit.toml` 파일을 생성해야 한다 (멱등).
- **FR-002**: `multikit install <kit>` 명령은 `httpx` 라이브러리를 사용하여 `raw.githubusercontent.com`에서 킷의 매니페스트를 조회하고 파일을 다운로드해야 한다.
- **FR-003**: `multikit install <kit>` 명령은 다운로드한 에이전트 파일을 `.github/agents/`에, 프롬프트 파일을 `.github/prompts/`에 배치해야 한다.
- **FR-004**: `multikit install <kit>` 명령은 설치 기록을 `multikit.toml`에 기록해야 한다 (킷 이름, 버전, 소스).
- **FR-005**: `multikit uninstall <kit>` 명령은 해당 킷의 파일만 정확히 삭제하고 설정에서 제거해야 한다.
- **FR-006**: `multikit list` 명령은 원격 `registry.json`(`https://raw.githubusercontent.com/{owner}/{repo}/{branch}/kits/registry.json`)을 GET하여 사용 가능한 전체 킷 목록을 조회하고, `multikit.toml`과 대조하여 설치 상태를 테이블로 출력해야 한다. 네트워크 오류 시 로컬 설치 킷만 표시하고 경고를 출력해야 한다.
- **FR-007**: CLI는 `cyclopts` 프레임워크를 사용하여 타입 힌트 기반으로 정의해야 한다.
- **FR-008**: 모든 네트워크 오류는 비정상 종료 없이 사용자 친화적 에러 메시지로 처리해야 한다.
- **FR-009**: 킷의 원격 소스 URL 패턴: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/kits/{kit_name}/` (기본값: `devcomfort/multikit/main`).
- **FR-010**: 각 킷은 `manifest.json`을 포함해야 하며, 최소 필드: `{"name": string, "version": string, "agents": [filename, ...], "prompts": [filename, ...]}`를 선언해야 한다. `multikit install`은 이 매니페스트를 먼저 다운로드한 후, 선언된 파일만 개별 다운로드한다.
- **FR-011**: `multikit diff <kit>` 명령은 설치된 킷의 로컬 파일과 원격 최신 버전을 비교하여 파일별 diff를 출력해야 한다. 로컬 수정(사용자 편집)과 원격 업데이트(레포지토리 변경) 양쪽을 모두 감지해야 한다.
- **FR-012**: `multikit install` 시 로컬 파일이 원격과 다를 경우, 파일별로 diff를 표시하고 `[y(덮어쓰기)/n(건너뛰기)/a(모두 덮어쓰기)/s(모두 건너뛰기)]` 대화식 확인을 수행해야 한다. `--force` 플래그로 확인 없이 전체 덮어쓰기가 가능해야 한다.
- **FR-013**: `multikit install`은 원자적(atomic) 설치를 수행해야 한다. 모든 킷 파일을 임시 디렉토리에 먼저 다운로드한 후, 전부 성공 시에만 `.github/agents/`와 `.github/prompts/`로 이동한다. 다운로드 실패 시 임시 파일을 삭제하고 기존 프로젝트 파일을 변경하지 않는다.

### Key Entities

- **Kit**: 재사용 가능한 에이전트+프롬프트 번들. 속성: name, version, files (agents[], prompts[]), source.
- **Registry**: 킷이 호스팅되는 원격 저장소. MVP에서는 단일 GitHub 리포지토리. 루트에 `registry.json`을 두어 사용 가능한 킷 목록을 선언. 스키마: `{kits: [{name: string, version: string, description?: string}, ...]}`.
- **Config (multikit.toml)**: 프로젝트별 설치 상태를 추적하는 설정 파일. 설치된 킷 목록과 버전 정보 포함.
- **Manifest (manifest.json)**: 킷 루트에 위치하는 메타데이터 파일. 스키마: `{name: string, version: string, description?: string, agents: string[], prompts: string[]}`. `install` 시 `raw.githubusercontent.com/.../kits/{kit}/manifest.json`을 먼저 GET하여 파일 목록을 확인한 후 개별 파일을 다운로드한다.

## Non-Functional Requirements

| Requirement     | Target                                                                                   |
| --------------- | ---------------------------------------------------------------------------------------- |
| Python 호환     | ≥ 3.10                                                                                   |
| 설치 크기       | `src/multikit/` 소스 코드 < 5MB (third-party 패키지 제외, `du -sh src/multikit/`로 측정) |
| 명령 응답 시간  | < 3초 (원격 install), < 500ms (로컬 명령)                                                |
| 테스트 커버리지 | ≥ 90%                                                                                    |
| 에러 메시지     | 영어 기본 (한국어 지원은 P1으로 연기)                                                    |
| 대상 IDE        | VS Code Copilot Chat 전용 (타 IDE 미지원)                                                |
| HTTP 클라이언트 | httpx (sync 모드, 향후 async 확장 가능)                                                  |

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 신규 사용자가 `pip install multikit && multikit init && multikit install testkit` 3개 명령으로 에이전트를 설치할 수 있다.
- **SC-002**: `multikit install`로 설치된 `.github/agents/*.agent.md` 파일이 VS Code Copilot Chat에서 에이전트로 인식된다.
- **SC-003**: `multikit uninstall` 후 해당 킷의 파일이 완전히 제거되고 `multikit.toml`에 흔적이 남지 않는다.
- **SC-004**: 네트워크 오류 시 `multikit install`이 비정상 종료(crash) 없이 에러 메시지를 출력하고 exit code 1을 반환한다.
- **SC-005**: MVP 범위의 모든 CLI 명령에 대해 테스트 커버리지 ≥ 90%를 달성한다.
