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
  - `network.max_concurrency: int | None` (optional, default 8)

### 6) NetworkPolicy

- Purpose: 비동기 원격 호출 정책 정의
- Fields:
  - `max_concurrency: int` (default 8)
  - `retry_attempts: int` (=3)
  - `retry_backoff_seconds: list[float]` (`[0.5, 1.0, 2.0]`)
  - `retry_statuses: list[int]` (`429`, `5xx`)
  - `retry_exceptions: list[str]` (`ConnectTimeout`)

## Relationships

- `Registry` 1:N `RegistryEntry`
- `RegistryEntry(name)` 1:1 `Manifest(name)`
- `MultikitConfig` 1:N `InstalledKit`
- `MultikitConfig` 1:1 `NetworkPolicy` (effective runtime policy; config override optional)

## State Transitions

### Install

1. config 로드
2. manifest 조회
3. tempdir 전체 다운로드 (`aiohttp` bounded concurrency)
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

1. config/manifest/remote 파일 조회 (`aiohttp` bounded concurrency)
2. 로컬 파일과 unified diff 생성
3. 변경 없음이면 `No changes detected`

### Update

1. config 로드 + 설치된 킷 검증
2. install 재사용 경로로 원격 최신 파일 async 조회/반영
3. 성공 시 `kits.<name>` 버전/파일 목록 갱신
4. 다건 처리 중 일부 실패 시 exit code 1

## Example TOML

```toml
[multikit]
version = "0.1.0"
registry_url = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

[multikit.network]
max_concurrency = 8

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
