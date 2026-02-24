# Tasks: Multikit CLI (MVP)

**Input**: Design documents from `/specs/001-multikit-cli/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/cli-commands.md

**Tests**: Spec requires ≥ 90% test coverage. Tests are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/multikit/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, pyproject.toml, package scaffold

- [x] T001 Create pyproject.toml with hatchling build, cyclopts/aiohttp/aiofiles/pydantic/tomli/tomli-w dependencies, and `[project.scripts] multikit = "multikit.cli:app"` entry point in `pyproject.toml`
- [x] T002 Create package scaffold: `src/multikit/__init__.py` (with `__version__ = "0.1.0"`), `src/multikit/commands/__init__.py`, `src/multikit/models/__init__.py`, `src/multikit/registry/__init__.py`, `src/multikit/utils/__init__.py`
- [x] T003 [P] Create root CLI app with cyclopts in `src/multikit/cli.py` — import and register all sub-command apps (init, install, uninstall, list, diff, update)
- [x] T004 [P] Create pytest conftest with tmp_path fixtures and httpx mock helpers in `tests/conftest.py`
- [x] T005 [P] Create sample kit data for testing: `kits/registry.json`, `kits/testkit/manifest.json`, `kits/testkit/agents/testkit.testdesign.agent.md`, `kits/testkit/agents/testkit.testcoverage.agent.md`, `kits/testkit/prompts/testkit.testdesign.prompt.md`, `kits/testkit/prompts/testkit.testcoverage.prompt.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, config I/O, registry client, file utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 [P] Implement Manifest and RegistryEntry Pydantic models in `src/multikit/models/kit.py` (per data-model.md)
- [x] T007 Implement Registry Pydantic model in `src/multikit/models/kit.py` (T006과 같은 파일이므로 T006 완료 후 순차 실행)
- [x] T008 [P] Implement InstalledKit and MultikitConfig Pydantic models in `src/multikit/models/config.py` (per data-model.md)
- [x] T009 [P] Implement TOML read/write utilities (tomli/tomli-w compat layer, load_config, save_config) in `src/multikit/utils/toml_io.py` (per research.md D-003). load_config에서 TOMLDecodeError 발생 시 `multikit.toml` → `multikit.toml.bak` 백업 생성 후 사용자 친화적 에러 메시지 출력 포함
- [x] T010 [P] Implement file utilities (atomic_install with tempdir, file delete, file move) in `src/multikit/utils/files.py` (per research.md D-004)
- [x] T011 [P] Implement diff utilities (show_diff with colored unified diff, prompt_overwrite interactive y/n/a/s) in `src/multikit/utils/diff.py` (per research.md D-005, D-006)
- [x] T012 Implement remote registry client (fetch_registry, fetch_manifest, fetch_file using aiohttp with timeout/retry and bounded concurrency controls) in `src/multikit/registry/remote.py` (per research.md D-002)
- [x] T013 [P] Write unit tests for Pydantic models (Manifest, Registry, MultikitConfig validation) in `tests/test_models.py`
- [x] T014 [P] Write unit tests for TOML I/O (read/write/update config) in `tests/test_toml_io.py`
- [x] T015 [P] Write unit tests for registry client (using respx mocks for httpx) in `tests/test_registry.py`
- [x] T015b [P] Write unit tests for file utilities (atomic_install, file move/delete) in `tests/test_files_utils.py`
- [x] T015c [P] Write unit tests for diff utilities (show_diff, prompt_overwrite) in `tests/test_diff_utils.py`

**Checkpoint**: Foundation ready — models validated, config I/O works, registry client tested with mocks

---

## Phase 3: User Story 1 - 프로젝트 초기화 (Priority: P1) 🎯 MVP

**Goal**: `multikit init`으로 `.github/agents/`, `.github/prompts/`, `multikit.toml`을 생성 (멱등)

**Independent Test**: 빈 디렉토리에서 `multikit init` → 3개 아티팩트 존재 확인

### Tests for User Story 1

- [x] T016 [P] [US1] Write tests for init command (empty dir, existing dir, idempotency) in `tests/test_init.py`

### Implementation for User Story 1

- [x] T017 [US1] Implement init command handler (create dirs + default multikit.toml) in `src/multikit/commands/init.py` (per contracts/cli-commands.md init spec)
- [x] T018 [US1] Register init sub-app in `src/multikit/cli.py` and verify `multikit init` works end-to-end

**Checkpoint**: `multikit init` works. Directories and config file are created idempotently.

---

## Phase 4: User Story 2 - 원격 킷 설치 (Priority: P1) 🎯 MVP

**Goal**: `multikit install testkit`으로 원격에서 에이전트/프롬프트를 다운로드하여 `.github/`에 배치하고 config에 기록

**Independent Test**: `multikit init && multikit install testkit` → `.github/agents/testkit.*.agent.md` 파일 존재 + config 업데이트 확인

### Tests for User Story 2

- [x] T019 [P] [US2] Write tests for install command (fresh install, already installed + force, invalid kit, network error, atomic rollback, permission denied) in `tests/test_install.py`

### Implementation for User Story 2

- [x] T020 [US2] Implement install command handler — fetch manifest, atomic download to tempdir, compare local, resolve conflicts (interactive/force), move files, update config — in `src/multikit/commands/install.py` (per contracts/cli-commands.md install spec). 다운로드된 파일이 1MB 초과 시 경고 출력 포함 (spec edge case: 대용량 파일). 매니페스트 조회 후 agents + prompts가 모두 비어있으면 `⚠ Kit '{name}' has no agent or prompt files` 경고 출력
- [x] T021 [US2] Register install sub-app in `src/multikit/cli.py` and verify `multikit install testkit` works end-to-end with mocked HTTP

**Checkpoint**: `multikit install <kit>` works. Atomic download, interactive diff on conflicts, config tracking.

---

## Phase 5: User Story 3 - 설치된 킷 목록 조회 (Priority: P2)

**Goal**: `multikit list`로 원격 레지스트리 + 로컬 설치 상태를 테이블로 출력

**Independent Test**: 킷 설치 후 `multikit list` → 테이블에 Installed 상태 표시 확인

### Tests for User Story 3

- [x] T022 [P] [US3] Write tests for list command (with kits, empty, network error fallback) in `tests/test_list.py`

### Implementation for User Story 3

- [x] T023 [US3] Implement list command handler — load config, fetch registry (graceful), merge + format table — in `src/multikit/commands/list_cmd.py` (per contracts/cli-commands.md list spec)
- [x] T024 [US3] Register list sub-app in `src/multikit/cli.py` and verify `multikit list` works end-to-end

**Checkpoint**: `multikit list` works. Shows remote + local kits, degrades gracefully on network error.

---

## Phase 6: User Story 4 - 킷 제거 (Priority: P2)

**Goal**: `multikit uninstall testkit`으로 킷 파일 삭제 + config에서 제거

**Independent Test**: install 후 `multikit uninstall testkit` → 파일 삭제 + config clean 확인

### Tests for User Story 4

- [x] T025 [P] [US4] Write tests for uninstall command (installed kit, not installed kit, file already deleted) in `tests/test_uninstall.py`

### Implementation for User Story 4

- [x] T026 [US4] Implement uninstall command handler — load config, verify installed, delete tracked files, update config — in `src/multikit/commands/uninstall.py` (per contracts/cli-commands.md uninstall spec)
- [x] T027 [US4] Register uninstall sub-app in `src/multikit/cli.py` and verify `multikit uninstall testkit` works end-to-end

**Checkpoint**: `multikit uninstall <kit>` works. Files removed, config cleaned, error on unknown kit.

---

## Phase 7: User Story 5 - 킷 변경 사항 확인 (Priority: P2)

**Goal**: `multikit diff testkit`으로 로컬 설치 vs 원격 최신 간 파일별 diff 출력

**Independent Test**: 킷 설치 후 로컬 파일 수정 → `multikit diff testkit` → diff 출력 확인

### Tests for User Story 5

- [x] T028 [P] [US5] Write tests for diff command (has changes, no changes, kit not installed) in `tests/test_diff.py`

### Implementation for User Story 5

- [x] T029 [US5] Implement diff command handler — load config, verify installed, fetch remote files, compare with local, output colored diff — in `src/multikit/commands/diff.py` (per contracts/cli-commands.md diff spec)
- [x] T030 [US5] Register diff sub-app in `src/multikit/cli.py` and verify `multikit diff testkit` works end-to-end

**Checkpoint**: `multikit diff <kit>` works. Shows colored per-file diff or "No changes detected".

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T031 [P] Verify/update gitkit bundle: `kits/gitkit/manifest.json` 스키마가 data-model.md와 일치하는지 확인, 필요 시 업데이트
- [ ] T032 [P] Verify/update `kits/registry.json` — testkit과 gitkit 항목이 모두 포함되어 있는지 확인
- [x] T033 [P] Verify `src/multikit/__main__.py`가 `python -m multikit` 실행을 올바르게 지원하는지 확인
- [ ] T034 [P] Verify/update README.md — 설치, 사용법, 개발 가이드가 현재 CLI 동작과 일치하는지 확인
- [ ] T034a [P] Clarify docs that `multikit update` updates installed kits only, and multikit program upgrades are handled via package managers (`pip`/`uv`/`rye`)
- [ ] T035 Run quickstart.md validation — verify `pip install -e .`, `multikit init`, `multikit install testkit`, `multikit list`, `multikit diff testkit`, `multikit update testkit`, `multikit uninstall testkit` all work. 각 명령 실행 시 `time` 명령으로 응답 시간 확인: `time multikit init` < 500ms, `time multikit list` < 500ms (로컬), `time multikit install testkit` < 3s (원격)
- [ ] T036 Run full test suite and verify ≥ 90% coverage with `pytest --cov=multikit`

---

## Phase 9: User Story 6 - 설치된 킷 업데이트 (Priority: P2)

**Goal**: `multikit update [kit]`로 설치된 킷을 원격 최신으로 갱신

**Independent Test**: 설치된 킷 대상으로 `multikit update testkit` 실행 시 파일/버전 갱신 확인

### Tests for User Story 6

- [x] T037 [P] [US6] Write tests for update command (single update, non-installed kit, interactive no selection, interactive partial failure) in `tests/commands/test_update.py`

### Implementation for User Story 6

- [x] T038 [US6] Implement update command handler in `src/multikit/commands/update.py` using latest-remote reinstall flow for installed kits only
- [x] T039 [US6] Register update sub-app in `src/multikit/cli.py` and verify `multikit update` appears in command surface tests

---

## Phase 10: Async Performance Optimization (Priority: P2)

**Goal**: `install`/`diff`의 네트워크·파일 I/O를 비동기 처리로 최적화

**Independent Test**: 다중 파일 킷에서 `install`/`diff` 실행 시 제한 동시성 비동기 처리 경로가 동작하고 기존 기능 계약을 유지하는지 확인

### Tests for Phase 10

- [ ] T040 [P] Add async optimization tests for install/diff (bounded concurrency, retry on transient failure/429, atomic safety 유지) in `tests/commands/test_install.py`, `tests/commands/test_diff.py`

### Implementation for Phase 10

- [ ] T041 Implement aiohttp-based concurrent remote fetch path for install/diff in `src/multikit/registry/remote.py`, `src/multikit/commands/install.py`, `src/multikit/commands/diff.py`
- [ ] T042 Implement aiofiles-based async file read/write path for staging and diff comparison in `src/multikit/utils/files.py` and related call sites

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001, T002 (package scaffold exists) — BLOCKS all user stories
- **US1 init (Phase 3)**: Depends on Phase 2 (toml_io for config creation)
- **US2 install (Phase 4)**: Depends on Phase 2 (registry client, file utils, diff utils, models)
- **US3 list (Phase 5)**: Depends on Phase 2 (registry client, config I/O). Can proceed in parallel with US2.
- **US4 uninstall (Phase 6)**: Depends on Phase 2 (config I/O, file utils). Can proceed in parallel with US2/US3.
- **US5 diff (Phase 7)**: Depends on Phase 2 (registry client, diff utils, config I/O). Can proceed in parallel with US2/US3/US4.
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Depends only on Phase 2 — can start first
- **US2 (P1)**: Depends only on Phase 2 — can start in parallel with US1
- **US3 (P2)**: Depends only on Phase 2 — can start in parallel with US1/US2
- **US4 (P2)**: Depends only on Phase 2 — can start in parallel with US1/US2/US3
- **US5 (P2)**: Depends only on Phase 2 — can start in parallel with US1/US2/US3/US4

### Within Each User Story

- Tests FIRST → then implementation → then CLI registration + E2E validation

### Parallel Opportunities

**Phase 1**: T003, T004, T005 can all run in parallel (after T001, T002)
**Phase 2**: T006–T011 (models + utils) all in parallel, T013–T015 (tests) all in parallel
**Phase 3–7**: All user stories can run in parallel once Phase 2 is complete
**Phase 8**: T031, T032, T033, T034 all in parallel

---

## Parallel Example: Phase 2 (Foundational)

```
# All models (T006 → T007 sequential, same file):
T006: Manifest + RegistryEntry models   → src/multikit/models/kit.py
T007: Registry model                    → src/multikit/models/kit.py (same file, sequential after T006)
T008: InstalledKit + MultikitConfig     → src/multikit/models/config.py

# All utils in parallel (different files):
T009: TOML I/O     → src/multikit/utils/toml_io.py
T010: File utils    → src/multikit/utils/files.py
T011: Diff utils    → src/multikit/utils/diff.py

# After models + utils:
T012: Registry client → src/multikit/registry/remote.py

# All tests in parallel (after implementations):
T013: Model tests       → tests/test_models.py
T014: TOML I/O tests    → tests/test_toml_io.py
T015: Registry tests    → tests/test_registry.py
T015b: File util tests  → tests/test_files_utils.py
T015c: Diff util tests  → tests/test_diff_utils.py
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (T001–T005)
2. Complete Phase 2: Foundational (T006–T015)
3. Complete Phase 3: US1 init (T016–T018)
4. Complete Phase 4: US2 install (T019–T021)
5. **STOP and VALIDATE**: `multikit init && multikit install testkit` works
6. Deploy/demo if ready — this is the MVP!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (init) → `multikit init` works
3. US2 (install) → `multikit install testkit` works → **MVP complete!**
4. US3 (list) → `multikit list` works
5. US4 (uninstall) → `multikit uninstall testkit` works
6. US5 (diff) → `multikit diff testkit` works
7. Polish → README, extra kits, coverage validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
