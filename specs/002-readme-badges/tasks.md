# Tasks: README Badge Generation

**Input**: Design documents from `/specs/002-readme-badges/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/badge-workflow.md, quickstart.md

**Tests**: 명세에서 배지 노출/자동 갱신/로컬 검증을 요구하므로 테스트 작업을 포함한다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 배지 기능 구현 전 공통 검증/도구 기반 정리

- [x] T001 Create badge test module scaffold in tests/test_readme_badges.py
- [x] T002 [P] Create CI workflow assertion test scaffold in tests/test_badge_ci_workflow.py
- [x] T003 [P] Create local badge-preview assertion test scaffold in tests/test_badge_local_preview.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 사용자 스토리가 의존하는 커버리지/매트릭스 단일 사실원 확립

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Update coverage command to emit machine-readable artifact in tox.ini
- [x] T005 Update pytest coverage script for local preview in pyproject.toml
- [x] T006 Align Python version matrix between tox and CI in .github/workflows/ci.yml
- [x] T007 Add coverage upload step coupled to test pipeline in .github/workflows/ci.yml

**Checkpoint**: Coverage artifact + CI matrix + upload flow are aligned.

---

## Phase 3: User Story 1 - README에서 배지 즉시 가시화 (Priority: P1) 🎯 MVP

**Goal**: README 상단에서 커버리지/버전 지원 배지를 즉시 확인 가능하게 한다.

**Independent Test**: README 렌더링 기준으로 배지 2종(coverage, python support)이 상단에 노출되고 링크/라벨이 유효한지 검증.

### Tests for User Story 1

- [x] T008 [P] [US1] Add README badge presence/format tests in tests/test_readme_badges.py

### Implementation for User Story 1

- [x] T009 [US1] Add coverage badge and python support badge near top section in README.md
- [x] T010 [US1] Ensure badge links reference canonical CI/coverage sources in README.md

**Checkpoint**: README 배지 2종이 표시되고 포맷 검증 테스트 통과.

---

## Phase 4: User Story 2 - 테스트 완료 후 배지 자동 갱신 (Priority: P2)

**Goal**: 기존 테스트 파이프라인 결과에 결합되어 배지 값이 자동 갱신되게 한다.

**Independent Test**: CI workflow 정의에서 테스트→커버리지 산출→업로드가 단일 실행 흐름으로 연결되었는지 검증.

### Tests for User Story 2

- [x] T011 [P] [US2] Add CI workflow contract tests for coverage/upload coupling in tests/test_badge_ci_workflow.py

### Implementation for User Story 2

- [x] T012 [US2] Implement coverage upload integration in .github/workflows/ci.yml
- [x] T013 [US2] Ensure coverage threshold semantics remain consistent with badge failure state in tox.ini
- [x] T014 [US2] Add/adjust coverage service configuration for stable badge resolution in .codecov.yml

**Checkpoint**: CI 변경 계약 테스트 통과, 파이프라인 내 자동 갱신 경로 확정.

---

## Phase 5: User Story 3 - 로컬에서 배지값 사전 확인 (Priority: P3)

**Goal**: 개발자가 푸시 전 로컬에서 배지에 반영될 커버리지 값을 확인할 수 있게 한다.

**Independent Test**: 로컬 preview 명령으로 coverage 퍼센트 및 artifact 생성이 확인되고 문서화된 경로가 동작.

### Tests for User Story 3

- [x] T015 [P] [US3] Add local preview command/coverage artifact tests in tests/test_badge_local_preview.py

### Implementation for User Story 3

- [x] T016 [US3] Add dedicated local badge preview script in pyproject.toml
- [x] T017 [US3] Document local preview workflow in README.md
- [x] T018 [US3] Keep quickstart instructions aligned with preview flow in specs/002-readme-badges/quickstart.md

**Checkpoint**: 로컬 preview 경로와 문서가 일치하고 검증 테스트 통과.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 전 스토리 관통 검증 및 정합성 마무리

- [x] T019 [P] Validate badge workflow contract document consistency in specs/002-readme-badges/contracts/badge-workflow.md
- [x] T020 [P] Validate plan/research/data-model alignment in specs/002-readme-badges/plan.md
- [x] T021 Run focused badge test suite in tests/test_readme_badges.py
- [x] T022 Run full test and coverage verification commands from specs/002-readme-badges/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): start immediately
- Foundational (Phase 2): depends on Setup, blocks all user stories
- User Story phases (Phase 3–5): depend on Foundational completion
- Polish (Phase 6): depends on all selected user stories

### User Story Dependencies

- US1 (P1): starts after Foundational
- US2 (P2): starts after Foundational, independent from US1 implementation details
- US3 (P3): starts after Foundational, can proceed independently

### Within Each User Story

- Tests first → implementation → story checkpoint validation

### Parallel Opportunities

- T002 and T003 parallel (different test files)
- T004, T005, T006 parallelizable (different files) before T007
- T008 parallel with T009 preparation
- T011 parallel with T012 preparation
- T015 parallel with T016 preparation
- T019 and T020 parallel in Polish

---

## Parallel Example: User Story 2

```bash
# In parallel
T011 -> tests/test_badge_ci_workflow.py
T012 -> .github/workflows/ci.yml

# Then sequentially
T013 -> tox.ini
T014 -> .codecov.yml
```

## Parallel Example: User Story 1

```bash
# In parallel
T008 -> tests/test_readme_badges.py
T009 -> README.md

# Then sequentially
T010 -> README.md
```

## Parallel Example: User Story 3

```bash
# In parallel
T015 -> tests/test_badge_local_preview.py
T016 -> pyproject.toml

# Then sequentially
T017 -> README.md
T018 -> specs/002-readme-badges/quickstart.md
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1–2
2. Complete US1 (T008–T010)
3. Validate README badge visibility and format tests

### Incremental Delivery

1. US1: 배지 노출
2. US2: 자동 갱신 파이프라인 결합
3. US3: 로컬 preview 경험 완성
4. Polish: 계약/문서/전체 테스트 검증
