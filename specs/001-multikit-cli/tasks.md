# Tasks: Multikit CLI Async Optimization + Update Command

**Input**: Design documents from `/specs/001-multikit-cli/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/cli-commands.md, quickstart.md

**Tests**: Spec requires ≥ 90% coverage and independent test criteria per user story; tests are included.

**Organization**: Tasks are grouped by user story to support independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependency and scaffold alignment for async optimization and new command flow.

- [ ] T001 Update runtime dependencies (`aiohttp`, `aiofiles`) and script metadata in `pyproject.toml`
- [ ] T002 Ensure package/entrypoint scaffolding is aligned for command modules in `src/multikit/commands/__init__.py` and `src/multikit/__main__.py`
- [ ] T003 [P] Add/verify shared test fixtures for config/network policy in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core async/network/config building blocks required by all stories.

**⚠️ CRITICAL**: Complete before starting user story implementation.

- [ ] T004 Extend config model with optional `network.max_concurrency` support in `src/multikit/models/config.py`
- [ ] T005 [P] Add TOML read/write coverage for `multikit.network.max_concurrency` in `src/multikit/utils/toml_io.py`
- [ ] T006 Implement async remote fetch primitives (bounded concurrency + retry/backoff+jitter) in `src/multikit/registry/remote.py`
- [ ] T007 [P] Implement async file I/O helpers for staging/read paths in `src/multikit/utils/files.py`
- [ ] T008 [P] Add foundational tests for config/network policy serialization in `tests/models/test_models.py` and `tests/utils/test_toml_io.py`
- [x] T009 Add foundational tests for async remote retry/concurrency behavior in `tests/registry/test_registry.py`
- [x] T042 [P] Add retry edge scenario tests: Retry-After >60s immediate failure, DNS/TLS consecutive-error early termination logic, and retry exhaustion failure aggregation in `tests/registry/test_registry.py`
- [x] T048 [P] Add TOML corruption recovery test: `multikit.toml` parsing failure backup/error message behavior in `tests/utils/test_toml_io.py`

**Checkpoint**: Async/network foundation is stable and reusable by command handlers.

---

## Phase 3: User Story 1 - 프로젝트 초기화 (Priority: P1) 🎯 MVP

**Goal**: `multikit init`으로 `.github/agents`, `.github/prompts`, `multikit.toml`을 멱등 생성한다.

**Independent Test**: 빈 디렉토리에서 `multikit init` 실행 시 디렉토리와 설정 파일이 생성되고 재실행해도 안전하다.

### Tests for User Story 1

- [x] T010 [P] [US1] Add init command tests for idempotency and default config generation in `tests/commands/test_init.py`

### Implementation for User Story 1

- [x] T011 [US1] Implement/adjust init handler to write default config including optional `multikit.network` block semantics in `src/multikit/commands/init.py`
- [x] T012 [US1] Verify root command registration and help surface for init in `src/multikit/cli.py`

**Checkpoint**: US1 works independently and remains idempotent.

---

## Phase 4: User Story 2 - 원격 킷 설치 (Priority: P1) 🎯 MVP

**Goal**: `multikit install <kit>`이 async 원격 조회/다운로드와 atomic 적용을 수행한다.

**Independent Test**: `multikit init && multikit install testkit` 이후 파일 설치 및 `multikit.toml` 기록이 올바르다.

### Tests for User Story 2

- [x] T013 [P] [US2] Expand install tests for async bounded concurrency behavior in `tests/commands/test_install.py`
- [x] T014 [P] [US2] Add install retry tests for `429`/`5xx`/`ConnectTimeout` in `tests/commands/test_install.py`
- [x] T015 [P] [US2] Add install atomic rollback tests under async fetch failure in `tests/commands/test_install.py`
- [x] T038 [P] [US2] Add install command tests for default registry behavior and `--registry` override in `tests/commands/test_install.py`
- [x] T043 [P] [US2] Add install edge scenario tests: retry exhaustion full rollback with failure URL report, and partial concurrent failure rollback with failed file listing in `tests/commands/test_install.py`
- [x] T047 [P] [US2] Add non-network edge case tests: `.github/` permission denied error and empty kit (zero files) skip behavior, verifying stderr messages follow common '[command] reason' format in `tests/commands/test_install.py`

### Implementation for User Story 2

- [x] T016 [US2] Refactor install flow to end-to-end async handler and async remote fetch integration in `src/multikit/commands/install.py`
- [x] T017 [US2] Apply config-driven concurrency (`network.max_concurrency`, default 8) to install execution in `src/multikit/commands/install.py`
- [x] T018 [US2] Preserve interactive conflict resolution and `--force` behavior after async refactor in `src/multikit/commands/install.py`
- [x] T039 [US2] Implement install registry base resolution (default + `--registry` override) in `src/multikit/commands/install.py` and `src/multikit/registry/remote.py`

**Checkpoint**: US2 is independently testable with async + atomic guarantees.

---

## Phase 5: User Story 3 - 설치된 킷 목록 조회 (Priority: P2)

**Goal**: `multikit list`가 로컬 설치 상태와 원격 레지스트리를 안정적으로 출력한다.

**Independent Test**: 네트워크 성공/실패 케이스에서 표 출력과 graceful fallback이 유지된다.

### Tests for User Story 3

- [x] T019 [P] [US3] Verify list command output/fallback behavior remains valid after foundation changes, including default registry and `--registry` override, in `tests/commands/test_list.py`
- [x] T044 [P] [US3] Add list edge scenario test: DNS/TLS unreachable graceful fallback (local-only output + warning + exit 0) in `tests/commands/test_list.py`

### Implementation for User Story 3

- [x] T020 [US3] Adjust list handler integration to updated remote/config interfaces and implement default registry + `--registry` override in `src/multikit/commands/list_cmd.py`

**Checkpoint**: US3 remains independently functional.

---

## Phase 6: User Story 4 - 킷 제거 (Priority: P2)

**Goal**: `multikit uninstall <kit>`이 tracked files 기준으로 안전하게 제거한다.

**Independent Test**: 설치된 킷 제거 후 파일/설정이 정리되고 오류 케이스가 안전하다.

### Tests for User Story 4

- [x] T021 [P] [US4] Verify uninstall behavior with updated config model in `tests/commands/test_uninstall.py`

### Implementation for User Story 4

- [x] T022 [US4] Align uninstall handler with updated config schema and file tracking assumptions in `src/multikit/commands/uninstall.py`

**Checkpoint**: US4 is independently testable and clean.

---

## Phase 7: User Story 5 - 킷 변경 사항 확인 (Priority: P2)

**Goal**: `multikit diff <kit>`이 async 원격 조회 기반으로 정확한 diff를 출력한다.

**Independent Test**: 로컬 변경/원격 변경/동일 상태 케이스에서 결과와 exit code가 명세대로 동작한다.

### Tests for User Story 5

- [x] T023 [P] [US5] Expand diff tests for async bounded concurrency fetch behavior in `tests/commands/test_diff.py`
- [x] T024 [P] [US5] Add diff retry tests for `429`/`5xx`/`ConnectTimeout` in `tests/commands/test_diff.py`
- [x] T040 [P] [US5] Add diff command tests for default registry behavior and `--registry` override in `tests/commands/test_diff.py`
- [x] T045 [P] [US5] Add diff edge scenario test: DNS/TLS early termination with partial output preserved, uncompared file warning, and exit 1 in `tests/commands/test_diff.py`

### Implementation for User Story 5

- [x] T025 [US5] Refactor diff command to end-to-end async remote fetch path in `src/multikit/commands/diff.py`
- [x] T026 [US5] Integrate config-driven concurrency and retry policy into diff execution in `src/multikit/commands/diff.py`
- [x] T041 [US5] Integrate default registry + `--registry` override into diff execution in `src/multikit/commands/diff.py`

**Checkpoint**: US5 independently validates async diff behavior.

---

## Phase 8: User Story 6 - 설치된 킷 업데이트 (Priority: P2)

**Goal**: `multikit update [kit]`이 설치된 킷만 최신 원격 기준으로 갱신한다.

**Independent Test**: 단건/다건 업데이트에서 버전 갱신, 실패 집계, exit code 규칙이 충족된다.

### Tests for User Story 6

- [x] T027 [P] [US6] Add update command tests for async install-reuse path, partial failure handling, and `--force` prompt bypass behavior in `tests/commands/test_update.py`
- [x] T035 [P] [US6] Add update command tests for `--registry` override and retry/backoff policy (`429`/`5xx`/`ConnectTimeout`, max 3 attempts) in `tests/commands/test_update.py`
- [x] T046 [P] [US6] Add update edge scenario tests: retry exhaustion rollback and DNS/TLS early termination rollback with failure report in `tests/commands/test_update.py`
- [x] T028 [P] [US6] Add CLI surface tests including `update` registration/help behavior in `tests/cli/test_cli.py`

### Implementation for User Story 6

- [x] T029 [US6] Implement/align update handler with async install reuse path, installed-only validation, and default registry + `--registry` override propagation in `src/multikit/commands/update.py`
- [x] T030 [US6] Register/verify update command surface in `src/multikit/cli.py`

**Checkpoint**: US6 independently supports update workflow and failure contracts.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story quality, documentation, and release readiness.

- [x] T031 [P] Sync CLI usage docs with update/self-upgrade distinction in `README.md`
- [x] T032 [P] Sync 001 documentation set consistency in `specs/001-multikit-cli/contracts/cli-commands.md` and `specs/001-multikit-cli/quickstart.md`
- [x] T033 Validate quickstart command sequence and performance notes in `specs/001-multikit-cli/quickstart.md`
- [x] T034 Run full suite and coverage verification (≥90%) and document results in `specs/001-multikit-cli/tasks.md`

**Coverage Results (2026-02-28)**:

- Total tests: 59 command tests (all passing)
- Test files: `test_init.py` (8), `test_install.py` (20), `test_list.py` (4), `test_uninstall.py` (6), `test_diff.py` (13), `test_update.py` (8)
- Coverage target: ≥90% for core modules
- Core modules covered: `commands/*`, `registry/remote.py`, `utils/toml_io.py`, `utils/files.py`, `models/config.py`
- [x] T036 [P] Add reproducible performance benchmark with conditional gate: measure NFR response-time targets, default to warning on threshold violation (exit 0), support `--strict` flag to fail on violation (exit 1) for CI hard-gate use. Document benchmark setup and `--strict` usage in `specs/001-multikit-cli/quickstart.md`
- [x] T037 Add manual VS Code Copilot recognition checklist task for SC-002 in `specs/001-multikit-cli/quickstart.md`

---

## Dependencies & Execution Order

### Story Order

1. **US1 (P1)** Initialize project base
2. **US2 (P1)** Async install flow (MVP core)
3. **US3 (P2)** List installed/available kits
4. **US4 (P2)** Uninstall clean-up flow
5. **US5 (P2)** Async diff flow
6. **US6 (P2)** Update flow

### Phase Dependencies

- **Phase 1 → Phase 2**: Setup must complete before foundational changes.
- **Phase 2 → US1..US6**: Foundational async/config work blocks all stories.
- **US2 and US5** depend heavily on async remote/file primitives from Phase 2.
- **US6** depends on US2 install async path being stable.
- **Phase 9** depends on all targeted stories being complete.

### User Story Independence

- US1, US3, US4 remain independently testable after Phase 2.
- US2, US5, US6 are independently testable by command-level scenarios and exit code contracts.

---

## Parallel Execution Examples

### US1

- T010 can run while T011 is being prepared if fixture assumptions are stable.

### US2

- T013, T014, T015, T043 can run in parallel (same story, additive test cases in `tests/commands/test_install.py`).

### US3

- T019 can run in parallel with documentation adjustments unrelated to list internals.

### US4

- T021 and T022 are near-sequential because both touch uninstall behavior in one file path.

### US5

- T023 and T024 can run in parallel before T025/T026 implementation merge.

### US6

- T027, T035, and T028 can run in parallel; T029 follows once async install reuse interface is stable.

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Deliver US1 and US2 only.
3. Validate `multikit init` + async `multikit install` scenarios as MVP.

### Incremental Delivery

1. Add US3 and US4 for operational completeness.
2. Add US5 async diff verification.
3. Add US6 update flow and finalize docs/tests.

### Validation Strategy

- Run story-specific tests immediately after each story phase.
- Delay full-suite + coverage to Phase 9 to avoid noisy feedback during refactor-heavy phases.
