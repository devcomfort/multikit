# multikit — Requirements

## 개요

**multikit**는 VS Code Copilot Chat에서 사용할 수 있는 커스텀 에이전트(`.github/agents/`, `.github/prompts/`)를
프로젝트에 설치·관리하는 CLI 도구입니다.

speckit이 spec/plan/tasks 워크플로우를 관리하듯, multikit은 **testkit**, **gitkit** 등
다양한 에이전트 킷(kit)을 프로젝트에 주입(inject)합니다.

---

## 기술 스택

| Component           | Choice                                                       | Rationale                                 |
| ------------------- | ------------------------------------------------------------ | ----------------------------------------- |
| **Language**        | Python ≥ 3.10                                                | cyclopts 최소 요구사항                    |
| **CLI Framework**   | [cyclopts](https://github.com/BrianPugh/cyclopts)            | 타입 힌트 기반, 직관적 API, Pydantic 지원 |
| **Build**           | hatchling                                                    | 경량 빌드 백엔드                          |
| **Package Manager** | rye 또는 uv                                                  | 빠른 의존성 관리                          |
| **Config Format**   | TOML (`multikit.toml` 또는 `pyproject.toml [tool.multikit]`) | Python 생태계 표준                        |
| **Template Engine** | Jinja2 (선택)                                                | 에이전트 파일 내 변수 치환이 필요한 경우  |

---

## 핵심 개념

### Kit (킷)

재사용 가능한 에이전트 + 프롬프트의 묶음입니다.

```
testkit/
├── agents/
│   ├── testkit.testdesign.agent.md
│   └── testkit.testcoverage.agent.md
└── prompts/
    ├── testkit.testdesign.prompt.md
    └── testkit.testcoverage.prompt.md
```

### Registry (레지스트리)

킷이 저장되는 중앙 저장소입니다:

- **로컬**: `~/.multikit/kits/` 디렉토리
- **원격** (향후): GitHub 리포지토리 또는 PyPI 패키지

---

## CLI 명령 설계

### `multikit init`

프로젝트에 multikit 설정을 초기화합니다.

```bash
multikit init
# → .github/agents/, .github/prompts/ 디렉토리 생성
# → multikit.toml 또는 pyproject.toml [tool.multikit] 섹션 생성
```

### `multikit install <kit>`

킷을 현재 프로젝트에 설치합니다.

```bash
multikit install testkit
# → .github/agents/testkit.*.agent.md 복사
# → .github/prompts/testkit.*.prompt.md 복사
# → multikit.toml에 설치 기록 추가

multikit install gitkit
# → .github/agents/gitkit.*.agent.md 복사
# → .github/prompts/gitkit.*.prompt.md 복사
```

### `multikit uninstall <kit>`

킷을 프로젝트에서 제거합니다.

```bash
multikit uninstall testkit
# → testkit.*.agent.md, testkit.*.prompt.md 삭제
# → multikit.toml에서 기록 제거
```

### `multikit list`

사용 가능한 킷과 설치 상태를 보여줍니다.

```bash
multikit list
# Kit          Installed  Version  Agents  Prompts
# testkit      ✅          1.0.0    2       2
# gitkit       ✅          1.0.0    1       1
# speckit      ❌          —        —       —
```

### `multikit update [kit]`

설치된 킷을 최신 버전으로 업데이트합니다.

```bash
multikit update           # 모든 킷 업데이트
multikit update testkit   # testkit만 업데이트
```

### `multikit create <kit>`

새 킷 스캐폴딩을 생성합니다.

```bash
multikit create mykit
# → ~/.multikit/kits/mykit/ 디렉토리 생성
# → 템플릿 agent.md, prompt.md 파일 생성
```

### `multikit sync`

`multikit.toml` 기반으로 프로젝트의 에이전트 파일들을 동기화합니다.
CI/CD나 팀 온보딩 시 유용합니다.

```bash
multikit sync
# → multikit.toml에 기록된 킷들을 모두 설치/업데이트
```

---

## 설정 파일 형식

### `multikit.toml`

```toml
[multikit]
version = "0.1.0"

[multikit.kits.testkit]
version = "1.0.0"
source = "local"  # "local" | "git" | "pypi"

[multikit.kits.gitkit]
version = "1.0.0"
source = "local"

# 향후 원격 소스 지원
# [multikit.kits.speckit]
# version = "^2.0"
# source = "git"
# repository = "https://github.com/user/speckit-agents"
```

### 또는 `pyproject.toml`

```toml
[tool.multikit]
kits = ["testkit", "gitkit"]

[tool.multikit.kits.testkit]
version = "1.0.0"
```

---

## 프로젝트 구조 (예상)

```
multikit/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── multikit/
│       ├── __init__.py
│       ├── cli.py              # cyclopts App 정의 (진입점)
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init.py         # multikit init
│       │   ├── install.py      # multikit install
│       │   ├── uninstall.py    # multikit uninstall
│       │   ├── list.py         # multikit list
│       │   ├── update.py       # multikit update
│       │   ├── create.py       # multikit create
│       │   └── sync.py         # multikit sync
│       ├── models/
│       │   ├── __init__.py
│       │   ├── kit.py          # Kit 데이터 모델 (Pydantic)
│       │   └── config.py       # 설정 파일 모델
│       ├── registry/
│       │   ├── __init__.py
│       │   ├── local.py        # 로컬 레지스트리 (~/.multikit/kits/)
│       │   └── remote.py       # 원격 레지스트리 (향후)
│       └── utils/
│           ├── __init__.py
│           ├── files.py        # 파일 복사/삭제 유틸리티
│           └── toml.py         # TOML 읽기/쓰기
├── kits/                       # 번들 킷 (패키지에 포함)
│   ├── testkit/
│   │   ├── agents/
│   │   └── prompts/
│   └── gitkit/
│       ├── agents/
│       └── prompts/
└── tests/
    ├── test_cli.py
    ├── test_install.py
    └── test_registry.py
```

---

## 우선순위

### P0 — MVP (v0.1.0)

- [ ] `multikit init` — 디렉토리 + 설정 파일 생성
- [ ] `multikit install <kit>` — 로컬 레지스트리에서 킷 설치
- [ ] `multikit uninstall <kit>` — 킷 제거
- [ ] `multikit list` — 설치된 킷 목록 출력
- [ ] 로컬 레지스트리 (`~/.multikit/kits/`) 지원
- [ ] testkit, gitkit 번들 킷 포함
- [ ] PyPI 배포 (`pip install multikit`)

### P1 — v0.2.0

- [ ] `multikit update` — 킷 업데이트
- [ ] `multikit create` — 새 킷 스캐폴딩
- [ ] `multikit sync` — 설정 기반 동기화
- [ ] 킷 버전 관리

### P2 — v0.3.0+

- [ ] 원격 레지스트리 (GitHub 리포지토리)
- [ ] 킷 의존성 관리 (킷 간 참조)
- [ ] Jinja2 템플릿 변수 치환
- [ ] 킷 검증 (`multikit validate`)

---

## 비기능 요구사항

| Requirement     | Target                                |
| --------------- | ------------------------------------- |
| Python 호환     | ≥ 3.10                                |
| 설치 크기       | < 5MB (의존성 제외)                   |
| 명령 응답 시간  | < 500ms (로컬 레지스트리)             |
| 테스트 커버리지 | ≥ 90%                                 |
| 에러 메시지     | 한국어/영어 지원 (사용자 locale 감지) |

---

## 참고

- [speckit](https://github.com/devcomfort/speckit) — spec/plan/tasks 워크플로우 관리 CLI (영감의 원천)
- [cyclopts](https://github.com/BrianPugh/cyclopts) — 타입 힌트 기반 CLI 프레임워크
- [VS Code Chat Agents](https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode) — `.github/agents/` 형식 참조
