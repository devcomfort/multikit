# multikit

![CI](https://github.com/devcomfort/multikit/actions/workflows/ci.yml/badge.svg)
[![Coverage](https://codecov.io/gh/devcomfort/multikit/branch/main/graph/badge.svg)](https://codecov.io/gh/devcomfort/multikit)
[![Python Support](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/devcomfort/multikit/actions/workflows/ci.yml)

multikit은 VS Code GitHub Copilot용 에이전트/프롬프트 자산을 프로젝트 단위로 설치·관리하기 위한 CLI입니다.
`multikit install testkit` 한 줄로 필요한 파일을 `.github/agents/`, `.github/prompts/`에 배치하고,
설치 상태를 `multikit.toml`에 일관되게 기록합니다.

## 개요

Copilot은 프로젝트 루트의 `.github/agents/` 및 `.github/prompts/` 디렉토리에서 마크다운 기반 정의 파일을 인식합니다.
multikit은 다음 과정을 자동화합니다.

- 원격 레지스트리에서 킷(Kit) 메타데이터 조회
- 에이전트/프롬프트 파일 다운로드 및 배치
- 설치 상태 버전 추적
- 로컬과 원격 간 변경(diff) 확인

수동 복사·동기화 없이, 표준화된 명령으로 팀 단위 운영이 가능합니다.

## Kit 개념

Kit은 특정 목적에 맞춘 에이전트(`*.agent.md`)와 프롬프트(`*.prompt.md`)의 배포 단위입니다.

- 에이전트: 작업 절차, 실행 정책, 제약 조건 정의
- 프롬프트: 목표 작업에 맞는 지시문 템플릿 정의

## 제공 중인 킷

| Kit          | Version | 도구 이름 (Agent / Prompt)    | 역할                                              |
| :----------- | :------ | :---------------------------- | :------------------------------------------------ |
| **gitkit**   | 1.0.0   | `gitkit.commit`               | Git 커밋 메시지 자동 작성 및 커밋 수행            |
| **lintkit**  | 1.0.0   | `lintkit.analyze.python`      | Python 코드 정적 분석, 린팅 및 개선점 제안        |
| **multikit** | 1.0.0   | `multikit.generation`         | 새로운 multikit 에이전트 및 프롬프트 템플릿 생성  |
|              |         | `multikit.readme.governance`  | README 관리 규칙 생성/개정                        |
|              |         | `multikit.readme.proposal`    | 프로젝트 변경 기반 README 수정안 제안             |
| **speckit**  | 1.0.0   | `speckit.analyze`             | 요구사항(Spec) 문서 분석 및 리뷰                  |
|              |         | `speckit.clarify`             | 모호한 요구사항 구체화 및 명확화                  |
| **testkit**  | 1.0.0   | `testkit.python.testdesign`   | Python 코드 기반 테스트 케이스 설계               |
|              |         | `testkit.python.testcoverage` | Python 테스트 커버리지 분석 및 누락된 테스트 보완 |
|              |         | `testkit.python.demobuilder`  | Python 데모 및 예제 코드 작성                     |

_※ 각 도구는 `.agent.md`와 `.prompt.md` 파일 쌍으로 제공됩니다._

최신 목록은 `multikit list`로 확인할 수 있습니다.

## 핵심 기능

- `multikit init`: `.github/agents/`, `.github/prompts/`, `multikit.toml` 초기화 (멱등)
- `multikit install [kit]`: 원격 레지스트리에서 킷 설치 (atomic 처리, 충돌 시 interactive diff)
- `multikit list`: 원격/로컬 상태를 테이블로 출력
- `multikit diff [kit]`: 로컬과 원격 파일 간 컬러 diff 출력
- `multikit uninstall [kit]`: 킷 파일 제거 및 설정 정리

`[kit]` 인자를 생략하면 인터랙티브 체크박스로 다중 선택이 가능합니다.

## 요구 사항

- Python 3.10 이상 (3.10, 3.11, 3.12, 3.13 검증)
- Linux, macOS, Windows

## 설치

```bash
pip install "git+https://github.com/devcomfort/multikit.git@main"
uv pip install "git+https://github.com/devcomfort/multikit.git@main"
uv tool install "git+https://github.com/devcomfort/multikit.git@main"
rye add multikit --git https://github.com/devcomfort/multikit --branch main
rye add --dev multikit --git https://github.com/devcomfort/multikit --branch main
rye install --git https://github.com/devcomfort/multikit --branch main multikit
```

## Quick Start

```bash
# 1) 프로젝트 초기화
multikit init

# 2) 킷 설치
multikit install testkit

# 3) 설치 상태 확인
multikit list
```

설치 후 예시 구조:

```text
your-project/
├── .github/
│   ├── agents/
│   │   ├── testkit.python.demobuilder.agent.md
│   │   ├── testkit.python.testcoverage.agent.md
│   │   └── testkit.python.testdesign.agent.md
│   └── prompts/
│       ├── testkit.python.demobuilder.prompt.md
│       ├── testkit.python.testcoverage.prompt.md
│       └── testkit.python.testdesign.prompt.md
└── multikit.toml
```

## CLI 사용법

### 1) 초기화

```bash
multikit init
```

기존 파일은 보존하며, 필요한 디렉토리/설정만 생성합니다.

### 2) 설치

```bash
multikit install testkit
multikit install
multikit install testkit --force
```

커스텀 레지스트리 사용:

```bash
multikit install testkit --registry https://example.com/my-kits
```

### 3) 목록 확인

```bash
multikit list
```

출력 예시:

```text
Kit       Status     Version    Agents    Prompts
--------  ---------  ---------  --------  ---------
testkit   Installed  1.0.0      3         3
gitkit    Available  1.0.0      —         —
lintkit   Available  1.0.0      —         —
multikit  Available  1.0.0      —         —
speckit   Available  1.0.0      —         —
```

### 4) 변경 비교

```bash
multikit diff testkit
multikit diff
```

### 5) 제거

```bash
multikit uninstall testkit
multikit uninstall
```

### 6) 모듈 실행

```bash
python -m multikit --help
```

## 설정 파일 (`multikit.toml`)

`multikit init` 실행 시 생성되는 기본 구조:

```toml
[multikit]
version = "0.1.0"
registry_url = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

[multikit.kits.testkit]
version = "1.0.0"
source = "remote"
files = [
    "agents/testkit.python.demobuilder.agent.md",
    "agents/testkit.python.testcoverage.agent.md",
    "agents/testkit.python.testdesign.agent.md",
    "prompts/testkit.python.demobuilder.prompt.md",
    "prompts/testkit.python.testcoverage.prompt.md",
    "prompts/testkit.python.testdesign.prompt.md",
]
```

- `registry_url`: 기본 원격 레지스트리 URL
- `kits.*`: 설치된 킷의 버전, 소스, 파일 목록

일반적으로 수동 편집은 권장하지 않습니다.

## 트러블슈팅

| 증상                      | 조치                                                      |
| ------------------------- | --------------------------------------------------------- |
| `Kit 'xxx' not found`     | `multikit list`로 사용 가능한 킷 이름 확인                |
| `multikit.toml not found` | `multikit init` 선행 실행                                 |
| 네트워크 오류             | 인터넷 연결 및 GitHub 접근 가능 여부 확인                 |
| 재설치 필요               | `--force` 사용 또는 `multikit diff`로 차이 확인 후 재적용 |

---

## 개발자 가이드

### 개발 환경 준비

```bash
git clone https://github.com/devcomfort/multikit.git
cd multikit

rye sync
rye run test
rye run test:cov
rye run test:tox
rye run badge:preview
rye run lint
rye run format
```

`rye run badge:preview`는 로컬에서 커버리지 퍼센트와 `coverage.xml` 아티팩트를 생성하여
README 커버리지 배지에 반영될 값을 푸시 전에 확인할 수 있게 해줍니다.

### 아키텍처 개요

```text
CLI (cyclopts)
  ↓
commands/*        # 서브커맨드 로직
  ↓
models/*          # Pydantic 모델
registry/remote   # httpx 기반 원격 fetch
utils/*           # TOML I/O, atomic 파일 처리, diff, interactive prompt
```

Install 흐름:

1. `registry.json` 조회 및 `Registry` 파싱
2. 대상 킷의 `manifest.json` 조회 및 `Manifest` 파싱
3. 파일 임시 다운로드(atomic staging)
4. 충돌 검사 후 사용자 확인 또는 `--force`
5. `.github/` 반영 및 `multikit.toml` 갱신

### 기술 스택

| Component       | Choice                                                 | 선택 이유                                 |
| --------------- | ------------------------------------------------------ | ----------------------------------------- |
| Language        | Python ≥ 3.10                                          | 모던 문법 및 타입 힌트 지원               |
| CLI Framework   | [cyclopts](https://github.com/BrianPugh/cyclopts)      | 타입 힌트 기반 인자 파싱, 서브커맨드 패턴 |
| HTTP Client     | [httpx](https://www.python-httpx.org/)                 | 경량, requests 유사 API, 확장성           |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) v2              | JSON/TOML ↔ 모델 변환, 검증               |
| Config Format   | TOML (`tomli`, `tomli-w`)                              | 가독성, Python 생태계 친화성              |
| Interactive UX  | [questionary](https://github.com/tmbo/questionary)     | 다중 선택 기반 터미널 UX                  |
| Table Output    | [tabulate](https://github.com/astanin/python-tabulate) | 간결한 표 출력                            |
| Build System    | hatchling                                              | 표준 PEP 517 빌드                         |
| Testing         | pytest + tox                                           | 다중 Python 버전 테스트                   |

### 프로젝트 구조

```text
src/multikit/
├── __init__.py
├── __main__.py
├── cli.py
├── commands/
│   ├── init.py
│   ├── install.py
│   ├── list_cmd.py
│   ├── uninstall.py
│   └── diff.py
├── models/
│   ├── kit.py
│   └── config.py
├── registry/
│   └── remote.py
└── utils/
    ├── toml_io.py
    ├── files.py
    ├── diff.py
    └── prompt.py

specs/
kits/
tests/
```

### 테스트 정책

- 프레임워크: pytest
- 커버리지 기준: 90% 이상 (`fail_under=90`)
- 네트워크 모킹: respx
- 멀티 버전 검증: tox (Python 3.10–3.13)

```bash
rye run test
rye run test:cov
rye run test:tox
```

### 커스텀 킷 제작

1. `kits/<kit-name>/` 디렉토리 생성
2. `manifest.json` 작성
3. `agents/`, `prompts/` 하위 파일 작성
4. `kits/registry.json`의 `kits` 배열에 항목 등록

`manifest.json` 예시:

```json
{
  "name": "mykit",
  "version": "1.0.0",
  "description": "My custom agents",
  "agents": ["mykit.example.agent.md"],
  "prompts": ["mykit.example.prompt.md"]
}
```

파일 명명 규칙:

- 에이전트: `<kit>.<feature>.agent.md`
- 프롬프트: `<kit>.<feature>.prompt.md`
- 킷 이름: `^[a-z0-9][a-z0-9-]*$`

### 기여 절차

기여와 개선 제안은 언제든 환영합니다. 다만 본 프로젝트는 개인 목적의 라이브러리이므로,
기능 우선순위·설계 방향·반영 일정은 메인테이너의 개인 사용 맥락을 기준으로 결정될 수 있습니다.

1. 이슈 생성 또는 기존 이슈 논의
2. feature 브랜치에서 개발 (`feature/<description>`)
3. 테스트/린트 통과 확인
4. Pull Request 생성

### 버전 정책

- 프로젝트 버전: SemVer (`pyproject.toml`)
- 킷 버전: 각 `manifest.json`
- 설정 파일 버전: `multikit.toml`의 `[multikit].version`

## 라이선스

MIT
