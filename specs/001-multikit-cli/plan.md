# Implementation Plan: Multikit CLI Async Optimization + Update Command

**Branch**: `001-multikit-cli` | **Date**: 2026-02-25 | **Spec**: `/specs/001-multikit-cli/spec.md`
**Input**: Feature specification from `/specs/001-multikit-cli/spec.md`

## Summary

`multikit` CLI에 `update` 명령을 도입하고, `install`/`diff`/`update` 경로를 end-to-end async(`aiohttp`, `aiofiles`)로 최적화한다. 동시성(기본 8 + `network.max_concurrency`), 재시도 정책(429/5xx/ConnectTimeout, 3회, 지수 백오프+jitter), atomic 설치 보장을 구현 기준으로 확정한다. 모든 원격 명령(`install`/`list`/`diff`/`update`)은 기본 레지스트리를 기본값으로 사용하고, 사용자가 `--registry`를 명시한 경우에만 오버라이드한다.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: cyclopts, aiohttp, aiofiles, pydantic, tomli/tomli-w, tabulate, questionary  
**Storage**: Local filesystem + `multikit.toml`  
**Testing**: pytest, pytest-cov, aioresponses(aiohttp 전용 HTTP 모킹)  
**Target Platform**: Linux/macOS/Windows CLI  
**Project Type**: Single Python project (CLI)  
**Performance Goals**: <3s remote install/update, <2s remote diff, <500ms local commands  
**Constraints**: Atomic install 유지, bounded concurrency(기본 8), retry budget 3회, VS Code Copilot `.github` 구조 준수  
**Scale/Scope**: 수십 개 파일 수준 kit 단위 동기화, 단일 프로젝트 로컬 실행

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Pre-Research Gate Check

- **I. Intuitive CLI Experience**: PASS — `update`는 기존 command surface와 동일 패턴(단건 + 인터랙티브 다건)을 따른다.
- **II. Standardized Configuration**: PASS — `multikit.toml` 중심 구성, `.github/agents|prompts` 경로 계약 유지.
- **III. Idempotent & Clean Operations**: PASS — atomic staging과 tracked files 기반 정리 전략 유지.
- **IV. Minimal & Modern Foundation**: PASS — Python 3.10+ 및 경량 async 라이브러리(`aiohttp`, `aiofiles`) 채택.
- **V. Extensibility via Kits**: PASS — manifest/registry 기반 kit 아키텍처 불변.

### Post-Design Gate Check

- **I** PASS — 계약/quickstart/tasks 모두 `update` UX를 동일한 사용성 패턴으로 문서화.
- **II** PASS — `network.max_concurrency`를 Config 엔티티에 명시해 스키마 일관성 확보.
- **III** PASS — retry/concurrency 정책이 실패 시 partial write 방지 조건과 함께 정의됨.
- **IV** PASS — async 최적화는 병목 구간에 한정하고 비기능 목표 수치 포함.
- **V** PASS — `update`도 install 재사용 경로로 kit 아키텍처 중심 확장.

## Project Structure

### Documentation (this feature)

```text
specs/001-multikit-cli/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-commands.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multikit/
├── cli.py
├── commands/
│   ├── init.py
│   ├── install.py
│   ├── list_cmd.py
│   ├── uninstall.py
│   ├── diff.py
│   └── update.py
├── models/
│   └── config.py
├── registry/
│   └── remote.py
└── utils/
    ├── files.py
    ├── diff.py
    └── toml_io.py

tests/
├── cli/
├── commands/
├── registry/
└── utils/
```

**Structure Decision**: 단일 Python CLI 프로젝트 구조를 유지하고, async 최적화는 `commands`/`registry`/`utils`의 기존 경계 내에서 점진 적용한다.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
