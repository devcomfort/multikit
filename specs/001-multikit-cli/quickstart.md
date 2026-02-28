# Quickstart: Multikit CLI (MVP)

## Prerequisites

- Python 3.10+
- 네트워크 접근 가능(`raw.githubusercontent.com`)

Optional tuning:

- `multikit.toml`에 `network.max_concurrency` 설정 가능 (기본 8)

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

## 6) Update installed kits

```bash
multikit update testkit
```

Expected:

- 설치된 킷을 원격 최신 기준으로 갱신
- `multikit.toml` 버전/파일 목록 갱신
- `install`과 동일한 async concurrency/retry 정책 적용

Interactive multi-update:

```bash
multikit update
```

Expected:

- 설치된 킷 선택 UI 표시
- 선택한 킷만 순차 업데이트

## 7) Uninstall

```bash
multikit uninstall testkit
```

Expected:

- `multikit.toml`의 `files[]` 기준 파일 삭제
- `kits.testkit` 섹션 제거
- 공유 참조 예외 감지 시 파일 보존 + warning

## 8) Upgrade multikit program (package)

`multikit update`는 설치된 kit 업데이트용이다. CLI 프로그램 자체를 올릴 때는 패키지 매니저를 사용한다.

```bash
pip install -U "git+https://github.com/devcomfort/multikit.git@main"
uv pip install -U "git+https://github.com/devcomfort/multikit.git@main"
rye sync
```

## 성능 및 참고 사항

### 응답 시간 목표 (NFR)

- `init`: < 100ms (로컬 작업)
- `list`: < 2s (원격 레지스트리 조회 포함)
- `install`: < 5s (소규모 킷 기준, 네트워크 상태에 따라 변동)
- `diff`: < 2s (소규모 킷 기준)
- `update`: < 5s (소규모 킷 기준)
- `uninstall`: < 100ms (로컬 작업)

### 병렬 처리

- 기본 병렬도: 8 (configurable via `multikit.toml` → `network.max_concurrency`)
- DNS/TLS 오류 발생 시 조기 종료 로직 적용
- Retry: 최대 3 회, 지수 백오프 + jitter

### `--registry` 오버라이드

커스텀 레지스트리 사용:

```bash
multikit install testkit --registry https://example.com/kits
multikit list --registry https://example.com/kits
multikit diff testkit --registry https://example.com/kits
multikit update testkit --registry https://example.com/kits
```

### Benchmark (T036)

성능 벤치마크는 `tests/perf/` 에서 실행 가능합니다:

```bash
python -m pytest tests/perf/test_performance.py -v
```

`--strict` 플래그를 사용하면 임계값 위반 시 exit 1 을 반환하여 CI hard-gate 로 사용할 수 있습니다:

```bash
python -m pytest tests/perf/test_performance.py --strict -v
```

## VS Code Copilot 인식 체크리스트 (SC-002)

- [ ] `.github/agents/` 디렉토리가 프로젝트 루트에 존재
- [ ] `.github/prompts/` 디렉토리가 프로젝트 루트에 존재
- [ ] 각 킷이 `.agent.md` 와 `.prompt.md` 파일 쌍으로 제공됨
- [ ] `multikit.toml` 에 설치된 킷 목록과 버전이 기록됨
- [ ] Copilot 이 `.github/` 하위 파일을 자동으로 인식하는지 확인

## Validation Commands

```bash
pytest
pytest --cov=src/multikit --cov-report=term-missing
tox
```

### Suggested perf checks

```bash
time multikit install testkit
time multikit diff testkit
time multikit update testkit
```
