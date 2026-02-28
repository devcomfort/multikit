# Docker Integration Tests

이 디렉토리에는 **격리된 Docker 환경**에서 `multikit` CLI의 전체 기능을 테스트하는 통합 테스트가 포함되어 있습니다.

## 아키텍처

```
┌──────────────────────────────┐     HTTP     ┌──────────────────────┐
│        test-runner           │ ◄──────────► │    mock-registry     │
│  (python:3.10 + multikit)    │              │  (nginx static files)│
│  pytest → subprocess multikit│              │  registry.json       │
│                              │              │  demokit/…           │
│                              │              │  alphakit/…          │
└──────────────────────────────┘              └──────────────────────┘
```

- **mock-registry**: nginx 컨테이너가 `fixtures/registry/` 디렉토리의 정적 파일을 서빙합니다.
- **test-runner**: `multikit`이 pip으로 설치된 Python 컨테이너에서 pytest가 실제 CLI 명령을 subprocess로 실행합니다.

## 실행 방법

### 스크립트 사용 (권장)

```bash
# 빌드 & 실행
./scripts/integration-test.sh

# 강제 리빌드
./scripts/integration-test.sh --build

# 컨테이너 정리
./scripts/integration-test.sh --down
```

### 직접 실행

```bash
docker compose -f tests/integration/docker-compose.yml up \
  --build \
  --abort-on-container-exit \
  --exit-code-from test-runner
```

## 테스트 시나리오

| 명령              | 테스트 내용                                                         |
| ----------------- | ------------------------------------------------------------------- |
| `init`            | 프로젝트 구조 생성 (multikit.toml, .github/agents, .github/prompts) |
| `install`         | 단일 킷 설치, 파일 생성 확인, config 업데이트, 존재하지 않는 킷     |
| `list`            | 사용 가능한 킷 목록, 설치 상태 표시                                 |
| `diff`            | 변경 없음 감지, 로컬 수정 후 diff 감지                              |
| `update`          | 재설치, 수정된 파일 복원, 미설치 킷 업데이트 시도                   |
| `uninstall`       | 파일 삭제, config에서 제거, 미설치 킷 삭제 시도                     |
| **Full Workflow** | init → install → list → diff → modify → diff → update → uninstall   |

## 파일 구조

```
tests/integration/
├── README.md                 ← 이 파일
├── docker-compose.yml        ← 서비스 오케스트레이션
├── Dockerfile.registry       ← nginx mock registry 이미지
├── Dockerfile.test           ← multikit + pytest 테스트 러너 이미지
├── nginx.conf                ← nginx 설정
├── conftest.py               ← pytest fixtures (workspace, run_cli 등)
├── test_cli_e2e.py           ← 통합 테스트 22개
└── fixtures/
    └── registry/             ← mock registry 정적 파일
        ├── registry.json
        ├── demokit/
        │   ├── manifest.json
        │   ├── agents/demokit.demo.agent.md
        │   └── prompts/demokit.demo.prompt.md
        └── alphakit/
            ├── manifest.json
            ├── agents/alphakit.alpha.agent.md
            └── prompts/alphakit.alpha.prompt.md
```

## 요구 사항

- Docker ≥ 20.10
- Docker Compose v2 (`docker compose` 명령)
