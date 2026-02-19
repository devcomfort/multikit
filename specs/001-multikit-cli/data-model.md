# Data Model: Multikit CLI (MVP)

## Entities

### 1) Manifest

- Purpose: 킷 설치 파일 계약(원격 `kits/{kit}/manifest.json`)
- Fields:
  - `name: str`
  - `version: str`
  - `description: str | None`
  - `agents: list[str]`
  - `prompts: list[str]`
- Validation:
  - `name` non-empty, slug 형식 권장
  - `agents/prompts` 항목은 각각 `.agent.md`/`.prompt.md` suffix
  - `agents + prompts` 모두 비어 있으면 경고(설치는 가능)

### 2) RegistryEntry

- Purpose: 사용 가능한 킷 요약 정보
- Fields:
  - `name: str`
  - `version: str`
  - `description: str | None`

### 3) Registry

- Purpose: 원격 레지스트리 루트 객체(`registry.json`)
- Fields:
  - `kits: list[RegistryEntry]`

### 4) InstalledKit

- Purpose: 프로젝트에 설치된 킷 상태 추적(`multikit.toml`)
- Fields:
  - `version: str`
  - `source: str` (기본 `remote`)
  - `files: list[str]` (`agents/...`, `prompts/...` 상대 경로)
- Rule:
  - MVP는 단독 소유 모델. `files` 기준으로 uninstall 대상 계산

### 5) MultikitConfig

- Purpose: 로컬 설정 루트
- Fields:
  - `version: str`
  - `registry_url: str`
  - `kits: dict[str, InstalledKit]`

## Relationships

- `Registry` 1:N `RegistryEntry`
- `RegistryEntry(name)` 1:1 `Manifest(name)`
- `MultikitConfig` 1:N `InstalledKit`

## State Transitions

### Install

1. config 로드
2. manifest 조회
3. tempdir 전체 다운로드
4. 충돌 시 diff + `[y/n/a/s]` 또는 `--force`
5. 반영 성공 시 `kits.<name>` 갱신
6. 실패 시 tempdir 삭제, 로컬 파일 불변

### Uninstall

1. config 로드
2. `kits.<name>.files` 조회
3. 파일 삭제 시도
4. 공유 참조 감지 예외 시 파일 보존 + 경고
5. `kits.<name>` 섹션 제거

### Diff

1. config/manifest/remote 파일 조회
2. 로컬 파일과 unified diff 생성
3. 변경 없음이면 `No changes detected`

## Example TOML

```toml
[multikit]
version = "0.1.0"
registry_url = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

[multikit.kits.testkit]
version = "1.0.0"
source = "remote"
files = [
  "agents/testkit.testdesign.agent.md",
  "agents/testkit.testcoverage.agent.md",
  "prompts/testkit.testdesign.prompt.md",
  "prompts/testkit.testcoverage.prompt.md",
]
```
