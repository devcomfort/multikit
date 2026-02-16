# multikit

VS Code Copilot 에이전트/프롬프트를 프로젝트에 설치·관리하는 CLI 도구입니다.

`multikit install testkit` 한 줄로 `.github/agents/`와 `.github/prompts/`에 커스텀 에이전트를 설치하고, `multikit.toml`로 설치 상태를 추적합니다.

## 주요 기능

- **`multikit init`** — `.github/agents/`, `.github/prompts/`, `multikit.toml` 초기화 (멱등)
- **`multikit install <kit>`** — 원격 레지스트리에서 킷 다운로드 및 설치 (atomic, 충돌 시 interactive diff)
- **`multikit list`** — 원격 + 로컬 킷 상태 테이블 출력
- **`multikit diff <kit>`** — 로컬 vs 원격 파일별 colored diff 출력
- **`multikit uninstall <kit>`** — 킷 파일 삭제 및 config 정리

## 설치

### rye (권장)

```bash
rye add multikit
rye sync
```

### pip

```bash
pip install multikit
```

### 개발 환경

```bash
git clone https://github.com/devcomfort/multikit.git
cd multikit
rye sync          # 의존성 설치 + editable install
rye run multikit --version
```

## 사용법

### 프로젝트 초기화

```bash
multikit init
# .github/agents/, .github/prompts/, multikit.toml 생성
```

### 킷 설치

```bash
multikit install testkit
# 원격에서 에이전트/프롬프트 파일 다운로드 → .github/ 에 배치

multikit install testkit --force
# 충돌 확인 없이 강제 덮어쓰기
```

### 킷 목록 조회

```bash
multikit list
# Kit        Status        Version  Agents  Prompts
# ─────────  ────────────  ───────  ──────  ───────
# testkit    ✅ Installed   1.0.0    2       2
# gitkit     ❌ Available   1.0.0    —       —
```

### 변경 사항 확인

```bash
multikit diff testkit
# 로컬 설치 파일 vs 원격 최신 파일의 colored unified diff
```

### 킷 제거

```bash
multikit uninstall testkit
# 파일 삭제 + multikit.toml 에서 제거
```

### 모듈 실행

```bash
python -m multikit --help
```

## 기술 스택

| Component       | Choice                                            |
| --------------- | ------------------------------------------------- |
| Language        | Python ≥ 3.10                                     |
| CLI Framework   | [cyclopts](https://github.com/BrianPugh/cyclopts) |
| HTTP Client     | [httpx](https://www.python-httpx.org/) (sync)     |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) v2         |
| Config Format   | TOML (tomli + tomli-w)                            |
| Build System    | hatchling                                         |
| Package Manager | [rye](https://rye.astral.sh/)                     |

## 프로젝트 구조

```
src/multikit/
├── __init__.py          # __version__
├── __main__.py          # python -m multikit
├── cli.py               # 루트 cyclopts App + 서브커맨드 등록
├── commands/
│   ├── init.py          # multikit init
│   ├── install.py       # multikit install
│   ├── list_cmd.py      # multikit list
│   ├── uninstall.py     # multikit uninstall
│   └── diff.py          # multikit diff
├── models/
│   ├── kit.py           # Manifest, RegistryEntry, Registry
│   └── config.py        # InstalledKit, MultikitConfig
├── registry/
│   └── remote.py        # httpx 기반 원격 레지스트리 클라이언트
└── utils/
    ├── toml_io.py       # TOML 읽기/쓰기 (Python 3.10/3.11 호환)
    ├── files.py          # atomic staging, 파일 삭제/이동
    └── diff.py           # colored unified diff, interactive prompt
```

## 개발

```bash
# 테스트 실행
rye run pytest tests/ -v

# 커버리지 확인
rye run pytest tests/ --cov=multikit --cov-report=term-missing

# 린트
rye run ruff check src/ tests/
```

## 라이선스

MIT
