# CLI Contracts: Multikit CLI (MVP)

## Command Surface

- `multikit init [path]`
- `multikit install <kit_name> [--force] [--registry <url>]`
- `multikit list`
- `multikit uninstall <kit_name>`
- `multikit diff <kit_name>`

## Common Rules

- Exit code `0`: 성공
- Exit code `1`: 에러(유효하지 않은 킷, 네트워크 실패, 설정 파싱 실패 등)
- 네트워크 오류는 crash 없이 사용자 친화 메시지로 반환

## `multikit init`

### Behavior

1. 대상 경로 확인(기본 `.`)
2. `.github/agents`, `.github/prompts` 생성(`exist_ok=True`)
3. `multikit.toml` 없으면 기본 템플릿 생성

### Guarantees

- 멱등 실행
- 기존 사용자 파일 보존

## `multikit install <kit_name>`

### Behavior

1. `multikit.toml` 로드(또는 기본값)
2. 원격 최신 기준으로 `manifest.json` 조회
3. manifest 선언 파일을 tempdir에 전부 다운로드
4. 전부 성공 시에만 `.github/` 반영(atomic)
5. 기존 파일과 차이 있으면 diff + `[y/n/a/s]` (또는 `--force`)
6. `multikit.toml`의 `kits.<kit_name>` 갱신

### Error Contracts

- manifest 404: `Kit not found`
- 파일 다운로드 실패: tempdir 정리 + 기존 파일 불변
- TOML 파싱 실패: 명확한 설정 오류 메시지

## `multikit list`

### Behavior

1. 로컬 config 로드
2. 원격 `registry.json` 조회
3. 원격 목록과 로컬 설치 상태 병합 출력(table)

### Degraded Mode

- 원격 조회 실패 시 로컬 설치 목록만 출력 + 경고

## `multikit uninstall <kit_name>`

### Behavior

1. `kits.<kit_name>` 존재 확인
2. `files[]` 기준 파일 삭제
3. `kits.<kit_name>` 섹션 제거 후 저장

### MVP Ownership Rule

- 단독 소유만 처리
- 공유 참조가 감지되는 예외 상황은 삭제하지 않고 경고

## `multikit diff <kit_name>`

### Behavior

1. 로컬 설치 확인
2. 원격 최신 manifest/files 조회
3. 로컬 파일과 unified diff 출력
4. 변경 없으면 `No changes detected`

## Prompt Contracts

### Install conflict prompt

- Options:
  - `y`: 현재 파일만 덮어쓰기
  - `n`: 현재 파일 건너뛰기
  - `a`: 이후 파일 전부 덮어쓰기
  - `s`: 이후 파일 전부 건너뛰기

### Uninstall shared-reference warning (MVP)

- 공유 감지 시:
  - 해당 파일 삭제 생략
  - ownership 모델은 Post-MVP 범위임을 경고
