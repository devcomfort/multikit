# multikit

VS Code Copilot 에이전트/프롬프트를 프로젝트에 설치·관리하는 CLI 도구입니다.

`multikit install testkit` 한 줄로 `.github/agents/`와 `.github/prompts/`에 커스텀 에이전트를 설치하고, `multikit.toml`로 설치 상태를 추적합니다.

## 킷(Kit)이란?

**킷**은 특정 작업 영역에 특화된 에이전트(`.agent.md`)와 프롬프트(`.prompt.md`) 파일의 묶음입니다. VS Code GitHub Copilot은 `.github/agents/`와 `.github/prompts/` 디렉토리의 마크다운 파일을 인식하여 코드 어시스턴트의 동작을 커스터마이징합니다.

multikit은 이러한 킷을 **원격 레지스트리에서 다운로드하고, 설치 상태를 추적하며, 업데이트 여부를 확인**하는 과정을 자동화합니다. 수동으로 파일을 복사·관리하는 번거로움 없이, 한 줄의 명령으로 프로젝트에 원하는 에이전트를 추가할 수 있습니다.

### 사용 가능한 킷

| Kit         | Version | 설명                                                     |
| ----------- | ------- | -------------------------------------------------------- |
| **testkit** | 1.0.0   | 테스트 설계 및 커버리지 에이전트 (agents: 2, prompts: 2) |
| **gitkit**  | 1.0.0   | Git 커밋 에이전트 (agents: 1, prompts: 1)                |
| **lintkit** | 1.0.0   | 코드 분석 및 린팅 에이전트                               |

> `multikit list`로 최신 목록을 조회할 수 있습니다.

## 주요 기능

- **`multikit init`** — `.github/agents/`, `.github/prompts/`, `multikit.toml` 초기화 (멱등)
- **`multikit install [kit]`** — 원격 레지스트리에서 킷 다운로드 및 설치 (atomic, 충돌 시 interactive diff)
- **`multikit list`** — 원격 + 로컬 킷 상태 테이블 출력
- **`multikit diff [kit]`** — 로컬 vs 원격 파일별 colored diff 출력
- **`multikit uninstall [kit]`** — 킷 파일 삭제 및 config 정리

> `[kit]` 인자를 생략하면 인터랙티브 체크박스로 여러 킷을 한 번에 선택할 수 있습니다.

## 요구 사항

- **Python** ≥ 3.10 (3.10, 3.11, 3.12, 3.13 테스트 완료)
- **OS**: Linux, macOS, Windows

## 설치

```bash
pip install "git+https://github.com/devcomfort/multikit.git@main"                # pip
uv pip install "git+https://github.com/devcomfort/multikit.git@main"             # uv (가상환경에 설치)
uv tool install "git+https://github.com/devcomfort/multikit.git@main"            # uv (전역 tool 설치)
rye add multikit --git https://github.com/devcomfort/multikit --branch main      # rye 프로젝트 의존성
rye add --dev multikit --git https://github.com/devcomfort/multikit --branch main # rye dev 의존성
rye install --git https://github.com/devcomfort/multikit --branch main multikit  # rye 전역 tool 설치
```

## 빠른 시작 (Quick Start)

```bash
# 1. 프로젝트 초기화 — 디렉토리 구조와 설정 파일 생성
multikit init

# 2. 킷 설치
multikit install testkit

# 3. 설치 확인
multikit list
```

실행 후 프로젝트에 다음 파일이 생성됩니다:

```
your-project/
├── .github/
│   ├── agents/
│   │   ├── testkit.testdesign.agent.md
│   │   └── testkit.testcoverage.agent.md
│   └── prompts/
│       ├── testkit.testdesign.prompt.md
│       └── testkit.testcoverage.prompt.md
└── multikit.toml
```

## 사용법

### 프로젝트 초기화

```bash
multikit init
# .github/agents/, .github/prompts/, multikit.toml 생성
```

이미 존재하는 프로젝트에서 실행해도 기존 파일을 보존합니다 (멱등).

### 킷 설치

```bash
multikit install testkit          # 이름으로 직접 설치
multikit install                  # 인자 없이 실행 → 인터랙티브 선택 (복수 선택 가능)
multikit install testkit --force  # 충돌 확인 없이 강제 덮어쓰기
```

커스텀 레지스트리를 사용하려면 `--registry` 옵션을 지정합니다:

```bash
multikit install testkit --registry https://example.com/my-kits
```

### 킷 목록 조회

```bash
multikit list
# Kit      Status     Version    Agents    Prompts
# -------  ---------  ---------  --------  ---------
# testkit  Installed  1.0.0      2         2
# gitkit   Available  1.0.0      —         —
# lintkit  Available  1.0.0      —         —
```

### 변경 사항 확인

```bash
multikit diff testkit             # 이름으로 직접 비교
multikit diff                     # 인자 없이 실행 → 인터랙티브 선택
```

### 킷 제거

```bash
multikit uninstall testkit        # 이름으로 직접 제거
multikit uninstall                # 인자 없이 실행 → 인터랙티브 선택
```

### 모듈 실행

```bash
python -m multikit --help
```

## 설정 파일 (`multikit.toml`)

`multikit init`으로 생성되는 설정 파일의 구조:

```toml
[multikit]
version = "0.1.0"
registry_url = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

[multikit.kits.testkit]          # multikit install 후 자동 생성
version = "1.0.0"
source = "remote"
files = [
    "agents/testkit.testdesign.agent.md",
    "agents/testkit.testcoverage.agent.md",
    "prompts/testkit.testdesign.prompt.md",
    "prompts/testkit.testcoverage.prompt.md",
]
```

- `registry_url` — 킷을 가져올 원격 레지스트리 URL. 변경하면 커스텀 레지스트리를 기본으로 사용합니다.
- `kits.*` — 설치된 킷의 버전, 소스, 파일 목록을 기록합니다. 수동 수정 불필요.

## 트러블슈팅

| 증상                                | 해결                                                                      |
| ----------------------------------- | ------------------------------------------------------------------------- |
| `Kit 'xxx' not found`               | `multikit list`로 사용 가능한 킷 이름을 확인하세요.                       |
| `multikit.toml not found`           | `multikit init`을 먼저 실행하세요.                                        |
| 네트워크 오류                       | 인터넷 연결과 GitHub 접근 가능 여부를 확인하세요.                         |
| 이미 설치된 킷을 재설치하고 싶을 때 | `--force` 플래그를 사용하거나, diff로 차이를 확인 후 파일별로 덮어쓰세요. |

---

## 개발자 가이드

이 섹션은 multikit에 기여하거나 커스텀 킷을 만들려는 개발자를 위한 내용입니다.

### 개발 환경 설정

```bash
# 리포지토리 클론
git clone https://github.com/devcomfort/multikit.git
cd multikit

# rye로 의존성 설치
rye sync

# 테스트 실행
rye run pytest tests/ -v

# 커버리지 확인 (fail_under=90%)
rye run pytest tests/ --cov=multikit --cov-report=term-missing

# tox로 다중 Python 버전 테스트 (3.10, 3.11, 3.12, 3.13)
rye run tox

# 린트
rye run ruff check src/ tests/

# 포맷팅
rye run ruff format src/ tests/
```

### 아키텍처

```
CLI (cyclopts)
  ↓ 커맨드 디스패치
commands/*        ← 각 서브커맨드 로직
  ↓ 데이터 접근
models/*          ← Pydantic 모델 (Manifest, Config)
registry/remote   ← httpx로 GitHub raw 파일 fetch
utils/*           ← TOML I/O, atomic file ops, diff, interactive prompt
```

**데이터 흐름** (install 기준):

1. `registry.json` fetch → `Registry` 모델 파싱
2. 킷의 `manifest.json` fetch → `Manifest` 모델 파싱
3. 에이전트/프롬프트 파일을 임시 디렉토리에 다운로드 (atomic staging)
4. 충돌 검사 → 사용자 확인 또는 `--force`
5. 임시 파일을 `.github/`으로 이동, `multikit.toml` 업데이트

### 기술 스택

| Component       | Choice                                                 | 선택 이유                                        |
| --------------- | ------------------------------------------------------ | ------------------------------------------------ |
| Language        | Python ≥ 3.10                                          | `match` 문, `X \| Y` 타입 힌트 등 모던 문법 활용 |
| CLI Framework   | [cyclopts](https://github.com/BrianPugh/cyclopts)      | 타입 힌트 기반 인자 파싱, 서브커맨드 앱 패턴     |
| HTTP Client     | [httpx](https://www.python-httpx.org/) (sync)          | 경량, `requests` 호환 API, 향후 async 확장 가능  |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) v2              | JSON/TOML ↔ 모델 자동 변환, 풍부한 검증          |
| Config Format   | TOML (tomli + tomli-w)                                 | Python 표준 설정 형식, 가독성                    |
| Interactive UX  | [questionary](https://github.com/tmbo/questionary)     | 체크박스 다중 선택, 터미널 UX                    |
| Table Output    | [tabulate](https://github.com/astanin/python-tabulate) | 간결한 테이블 포맷팅                             |
| Build System    | hatchling                                              | 표준 PEP 517 빌드                                |
| Testing         | pytest + tox                                           | 다중 Python 버전 테스트 지원                     |

### 프로젝트 구조

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
    ├── diff.py           # colored unified diff, overwrite prompt
    └── prompt.py         # questionary 기반 인터랙티브 킷 선택

specs/                   # 기능 명세 및 설계 문서
kits/                    # 원격 레지스트리용 킷 원본 (registry.json, manifest.json, *.md)
tests/                   # pytest 테스트 (test_*.py, conftest.py fixtures)
```

### 테스트

- **테스트 프레임워크**: pytest
- **커버리지 기준**: 90% 이상 (`fail_under=90`)
- **네트워크 모킹**: [respx](https://github.com/lundberg/respx) (httpx용 mock)
- **다중 버전**: [tox](https://tox.wiki/) (Python 3.10–3.13)
- **파일 명명**: `test_<모듈명>.py` (예: `test_install.py`, `test_models.py`)
- **Fixtures**: `tests/conftest.py`에 공용 fixture 정의 (`project_dir`, `initialized_project`, `sample_manifest` 등)

```bash
rye run pytest tests/ -v            # 전체 테스트
rye run pytest tests/ -x            # 첫 실패 시 중단
rye run tox                         # 다중 Python 버전 테스트
rye run tox -e coverage             # 커버리지 리포트
```

### 커스텀 킷 만들기

새로운 킷을 만들어 레지스트리에 등록하는 방법:

1. `kits/<킷이름>/` 디렉토리 생성
2. `manifest.json` 작성:

```json
{
  "name": "mykit",
  "version": "1.0.0",
  "description": "My custom agents",
  "agents": ["mykit.example.agent.md"],
  "prompts": ["mykit.example.prompt.md"]
}
```

3. `agents/`와 `prompts/` 하위에 마크다운 파일 생성
4. `kits/registry.json`의 `kits` 배열에 항목 추가:

```json
{
  "name": "mykit",
  "version": "1.0.0",
  "description": "My custom agents"
}
```

**파일 명명 규칙**:

- 에이전트: `<킷이름>.<기능>.agent.md`
- 프롬프트: `<킷이름>.<기능>.prompt.md`
- 킷 이름: 소문자 영숫자 + 하이픈 (`^[a-z0-9][a-z0-9-]*$`)

### 기여 가이드

1. 이슈를 열거나, 기존 이슈에 코멘트
2. feature 브랜치에서 작업 (`feature/<설명>`)
3. 테스트 작성 및 통과 확인 (`rye run pytest tests/ -v`)
4. 린트 통과 확인 (`rye run ruff check src/ tests/`)
5. PR 생성

### 버전 관리

- 프로젝트 버전: [SemVer](https://semver.org/) (`pyproject.toml`의 `version`)
- 킷 버전: 각 `manifest.json`의 `version` 필드
- 설정 파일 버전: `multikit.toml`의 `[multikit].version`

## 라이선스

MIT
