# Implementation Plan: Multikit CLI (MVP)

**Branch**: `001-multikit-cli` | **Date**: 2026-02-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-multikit-cli/spec.md`

## Summary

Multikit는 VS Code Copilot Chat용 커스텀 에이전트/프롬프트를 프로젝트에 설치·관리하는 cyclopts 기반 CLI 도구이다. `raw.githubusercontent.com`에서 킷(에이전트+프롬프트 번들)의 `manifest.json`을 조회하여 파일 목록을 확인하고, `httpx`로 개별 파일을 atomic하게 다운로드하여 `.github/agents/`와 `.github/prompts/`에 배치한다. 핵심 명령: `init`, `install`, `uninstall`, `list`, `diff`.

## Technical Context

**Language/Version**: Python ≥ 3.10
**Primary Dependencies**: cyclopts (CLI), httpx (HTTP), pydantic (models), tomli/tomli-w (TOML read/write)
**Storage**: File system only — `multikit.toml` (config), `.github/agents/` + `.github/prompts/` (kit files)
**Testing**: pytest + pytest-tmp-files (filesystem fixtures), respx (httpx mocking)
**Target Platform**: Linux, macOS, Windows (cross-platform CLI)
**Project Type**: single
**Performance Goals**: < 3초 (원격 install), < 500ms (로컬 명령)
**Constraints**: < 5MB 설치 크기 (의존성 제외), 네트워크 오류 시 graceful degradation
**Scale/Scope**: MVP — 5개 CLI 명령 (init, install, uninstall, list, diff)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| #   | Principle                     | Status  | Evidence                                                             |
| --- | ----------------------------- | ------- | -------------------------------------------------------------------- |
| I   | Intuitive CLI Experience      | ✅ PASS | cyclopts 사용, 표준 CLI 패턴 (init/install/uninstall/list/diff)      |
| II  | Standardized Configuration    | ✅ PASS | TOML 형식, `.github/agents` + `.github/prompts` VS Code 표준 구조    |
| III | Idempotent & Clean Operations | ✅ PASS | init 멱등, install 대화식 확인, uninstall 정확 삭제, atomic rollback |
| IV  | Minimal & Modern Foundation   | ✅ PASS | Python 3.10+, hatchling, httpx (경량), 최소 의존성                   |
| V   | Extensibility via Kits        | ✅ PASS | Kit 아키텍처 중심 설계, manifest.json + registry.json                |

**Gate Result**: ✅ ALL PASS — Phase 0 진행 가능.

### Post-Design Re-check (Phase 1 완료 후)

| #   | Principle                     | Status  | Evidence                                                               |
| --- | ----------------------------- | ------- | ---------------------------------------------------------------------- |
| I   | Intuitive CLI Experience      | ✅ PASS | contracts/cli-commands.md: 5개 명령 표준 CLI 패턴, 명확한 출력 포맷    |
| II  | Standardized Configuration    | ✅ PASS | data-model.md: MultikitConfig TOML 표준, `.github/` VS Code 구조 준수  |
| III | Idempotent & Clean Operations | ✅ PASS | atomic install (tempdir→move), uninstall files 트래킹, init exist_ok   |
| IV  | Minimal & Modern Foundation   | ✅ PASS | 의존성 5개 (cyclopts, httpx, pydantic, tomli, tomli-w), stdlib difflib |
| V   | Extensibility via Kits        | ✅ PASS | Manifest + Registry 모델로 킷 독립 배포 가능                           |

**Post-Design Gate Result**: ✅ ALL PASS — 위반 사항 없음.

## Project Structure

### Documentation (this feature)

```text
specs/001-multikit-cli/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-commands.md  # CLI command signatures
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
└── multikit/
    ├── __init__.py          # Package version
    ├── cli.py               # cyclopts App 진입점
    ├── commands/
    │   ├── __init__.py
    │   ├── init.py          # multikit init
    │   ├── install.py       # multikit install
    │   ├── uninstall.py     # multikit uninstall
    │   ├── list_cmd.py      # multikit list (list는 Python 예약어 회피)
    │   └── diff.py          # multikit diff
    ├── models/
    │   ├── __init__.py
    │   ├── kit.py           # Kit, Manifest Pydantic 모델
    │   └── config.py        # MultikitConfig Pydantic 모델
    ├── registry/
    │   ├── __init__.py
    │   └── remote.py        # 원격 레지스트리 (raw.githubusercontent.com)
    └── utils/
        ├── __init__.py
        ├── files.py         # 파일 복사/삭제/atomic 유틸리티
        ├── toml_io.py       # TOML 읽기/쓰기
        └── diff.py          # 파일 diff 유틸리티

kits/                        # 번들 킷 데이터 (registry.json 포함)
├── registry.json
├── testkit/
│   ├── manifest.json
│   ├── agents/
│   └── prompts/
└── gitkit/
    ├── manifest.json
    ├── agents/
    └── prompts/

tests/
├── conftest.py              # 공통 fixtures
├── test_cli.py              # CLI 진입점 테스트
├── test_diff.py             # diff 명령 테스트
├── test_diff_utils.py       # diff 유틸리티 단위 테스트
├── test_files_utils.py      # 파일 유틸리티 단위 테스트
├── test_init.py             # init 명령 테스트
├── test_install.py          # install 명령 테스트
├── test_list.py             # list 명령 테스트
├── test_models.py           # Pydantic 모델 테스트
├── test_registry.py         # 레지스트리 클라이언트 테스트
├── test_toml_io.py          # TOML I/O 테스트
└── test_uninstall.py        # uninstall 명령 테스트
```

**Structure Decision**: Single project 구조 선택. `src/multikit/` 하위에 commands/models/registry/utils로 분리. CLI 프레임워크 패턴에 맞게 commands를 독립 모듈로 분리하여 테스트 용이성 확보.

## Complexity Tracking

> No constitution violations detected. All five principles pass.
