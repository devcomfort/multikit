# Quickstart: Multikit CLI (MVP)

## Prerequisites

- Python 3.10+
- 네트워크 접근 가능(`raw.githubusercontent.com`)

## 1) Initialize

```bash
multikit init
```

Expected:

- `.github/agents/`
- `.github/prompts/`
- `multikit.toml`

## 2) Install a kit (latest remote)

```bash
multikit install testkit
```

Expected:

- 원격 최신 manifest/files 조회
- `.github/agents/*.agent.md`, `.github/prompts/*.prompt.md` 반영
- `multikit.toml`에 `kits.testkit` 기록

## 3) Reinstall with local changes

```bash
multikit install testkit
```

Expected:

- 파일별 diff 출력
- `[y/n/a/s]`로 덮어쓰기 선택

Force overwrite:

```bash
multikit install testkit --force
```

## 4) List kits

```bash
multikit list
```

Expected:

- 원격 전체 킷 + 로컬 설치 상태 table 출력
- 원격 실패 시 로컬만 출력 + warning

## 5) Diff local vs remote

```bash
multikit diff testkit
```

Expected:

- 변경 파일별 unified diff
- 변경 없음: `No changes detected`

## 6) Uninstall

```bash
multikit uninstall testkit
```

Expected:

- `multikit.toml`의 `files[]` 기준 파일 삭제
- `kits.testkit` 섹션 제거
- 공유 참조 예외 감지 시 파일 보존 + warning

## Validation Commands

```bash
pytest
pytest --cov=src/multikit --cov-report=term-missing
tox
```
