# Multikit CLI — Technology Research

> 조사일: 2026-02-12
> 대상 Python 버전: ≥ 3.10
> 핵심 라이브러리: cyclopts, httpx, Pydantic, tomli/tomli-w, difflib (stdlib)

---

## Topic 1: cyclopts CLI Framework Patterns

### 1.1 권장 라이브러리 버전

| 패키지   | 버전    | 비고                         |
| -------- | ------- | ---------------------------- |
| cyclopts | `>=3.6` | Python ≥3.10, Rich 기반 help |

### 1.2 기본 App 생성 + default 액션

```python
from cyclopts import App

app = App(
    name="multikit",
    help="A modular Python project scaffolding toolkit.",
    version="0.1.0",          # --version 자동 등록
)

@app.default
def default_action():
    """기본 액션 — 커맨드 없이 실행 시 help 출력."""
    app.help_print()

if __name__ == "__main__":
    app()
```

### 1.3 서브커맨드 등록 (별도 모듈)

cyclopts는 `App` 인스턴스를 `app.command()`로 등록하는 방식으로 서브커맨드를 분리한다.

**프로젝트 구조:**

```
multikit/
├── __main__.py
├── cli.py            # root App
├── commands/
│   ├── __init__.py
│   ├── init.py       # init sub-app
│   └── install.py    # install sub-app
```

**cli.py (root):**

```python
from cyclopts import App

app = App(
    name="multikit",
    help="A modular Python project scaffolding toolkit.",
    version="0.1.0",
)

# 서브커맨드 등록 — 별도 모듈에서 import
from multikit.commands.init import app as init_app
from multikit.commands.install import app as install_app

app.command(init_app)
app.command(install_app)
```

**commands/init.py:**

```python
from cyclopts import App

app = App(name="init", help="Initialize a new multikit project.")

@app.default
def handler(path: str = "."):
    """Initialize multikit in the given directory.

    Parameters
    ----------
    path
        Target directory for initialization.
    """
    print(f"Initializing multikit in {path}")
```

**commands/install.py:**

```python
from cyclopts import App, Parameter
from typing import Annotated

app = App(name="install", help="Install kits from a registry.")

@app.default
def handler(
    kit_name: str,
    *,
    force: Annotated[bool, Parameter(help="Overwrite existing files.")] = False,
    dry_run: Annotated[bool, Parameter(name=["--dry-run", "-n"], help="Preview without writing.")] = False,
):
    """Install a kit by name.

    Parameters
    ----------
    kit_name
        Name of the kit to install.
    """
    print(f"Installing {kit_name} (force={force}, dry_run={dry_run})")
```

### 1.4 타입 매개변수 + Annotated + 플래그

```python
from cyclopts import App, Parameter
from typing import Annotated
from pathlib import Path

app = App(name="install")

@app.default
def handler(
    kit_name: str,                                                    # positional 필수 인자
    *,                                                                 # 이후는 keyword-only
    force: bool = False,                                               # --force / --no-force 플래그 자동
    output: Annotated[Path, Parameter(help="Output directory.")] = Path("."),
    timeout: Annotated[int, Parameter(name=["--timeout", "-t"])] = 30,
    verbose: Annotated[int, Parameter(name=["-v"], help="Verbosity level.")] = 0,
):
    ...
```

**핵심 포인트:**

- `bool` 타입은 자동으로 `--flag` / `--no-flag` 쌍이 된다.
- `Annotated[T, Parameter(...)]`로 이름, help, validator 등을 세밀하게 제어한다.
- keyword-only (`*` 이후)로 선언하면 반드시 `--name` 형태로만 전달 가능하다.
- 이름 변환: 기본적으로 `snake_case` → `kebab-case` (예: `dry_run` → `--dry-run`).

### 1.5 주의사항 / Gotchas

| 항목               | 설명                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| 함수 시그니처 보존 | `@app.command`는 원본 함수를 수정하지 않으므로 단위 테스트에서 직접 호출 가능                  |
| Docstring 파싱     | Numpydoc, Google, ReST, Epydoc 스타일 모두 지원                                                |
| SubApp 이름        | `App(name="install")` — name이 CLI 커맨드 이름이 됨                                            |
| 순서               | positional 인자 뒤에 keyword를 쓸 수 있지만, keyword 뒤에 positional은 불가 (Python 규칙 동일) |
| `app()` 호출       | entrypoint에서 `app()` 호출 필수 — `pyproject.toml`의 `[project.scripts]`와 연동               |
| Lazy Loading       | 대규모 앱에서는 `app.command("module.path:app")` 문자열 기반 lazy import 지원                  |

---

## Topic 2: httpx Sync Client Best Practices

### 2.1 권장 라이브러리 버전

| 패키지 | 버전       | 비고                                           |
| ------ | ---------- | ---------------------------------------------- |
| httpx  | `>=0.28.0` | 최신 안정 버전, `follow_redirects` 기본 비활성 |

### 2.2 httpx.Client 컨텍스트 매니저 + 커넥션 풀링

```python
import httpx

TIMEOUT = httpx.Timeout(
    connect=10.0,   # 연결 수립 최대 10초
    read=30.0,      # 데이터 수신 최대 30초
    write=10.0,     # 데이터 송신 최대 10초
    pool=5.0,       # 풀에서 커넥션 획득 최대 5초
)

def download_file(url: str) -> str:
    """URL에서 텍스트 파일을 다운로드하여 문자열로 반환."""
    with httpx.Client(
        timeout=TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": "multikit/0.1.0"},
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
```

**왜 Client를 사용하는가:**

- 커넥션 풀링: 동일 호스트 반복 요청 시 TCP 핸드셰이크 절감
- 설정 공유: timeout, headers 등 일괄 적용
- 컨텍스트 매니저(`with`)로 연결 자동 정리

### 2.3 raw.githubusercontent.com에서 파일 다운로드

```python
import httpx

BASE_URL = "https://raw.githubusercontent.com"

def fetch_kit_file(org: str, repo: str, ref: str, path: str) -> str:
    """GitHub raw 콘텐츠에서 단일 파일 다운로드."""
    url = f"{BASE_URL}/{org}/{repo}/{ref}/{path}"
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text
```

### 2.4 에러 핸들링 패턴

```python
import httpx
import sys

def safe_download(url: str) -> str | None:
    """안전한 다운로드 — 네트워크/HTTP 에러를 사용자 친화적으로 처리."""
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text

    except httpx.ConnectError:
        print(f"Error: Could not connect to {url}", file=sys.stderr)
        print("  Check your internet connection.", file=sys.stderr)
        return None

    except httpx.TimeoutException:
        print(f"Error: Request timed out for {url}", file=sys.stderr)
        return None

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 404:
            print(f"Error: Resource not found — {url}", file=sys.stderr)
        else:
            print(f"Error: HTTP {status} for {url}", file=sys.stderr)
        return None

    except httpx.RequestError as exc:
        # 모든 네트워크/프로토콜 에러의 베이스 클래스
        print(f"Error: Request failed for {exc.request.url} — {exc}", file=sys.stderr)
        return None
```

**예외 계층 구조 (중요 부분):**

```
HTTPError
├── RequestError              ← 요청 자체가 실패
│   ├── TransportError
│   │   ├── TimeoutException
│   │   │   ├── ConnectTimeout
│   │   │   ├── ReadTimeout
│   │   │   └── PoolTimeout
│   │   └── NetworkError
│   │       └── ConnectError  ← DNS/연결 불가
│   └── TooManyRedirects
└── HTTPStatusError           ← 4xx/5xx 응답 (raise_for_status)
```

### 2.5 주의사항 / Gotchas

| 항목                 | 설명                                                                     |
| -------------------- | ------------------------------------------------------------------------ |
| `follow_redirects`   | 기본값 `False` — GitHub raw URL은 리다이렉트 가능하므로 `True` 설정 필요 |
| `raise_for_status()` | 호출하지 않으면 4xx/5xx도 정상 Response로 반환됨                         |
| 바이너리 vs 텍스트   | `.text`는 인코딩 자동 감지, `.content`는 raw bytes                       |
| Client 재사용        | 여러 파일을 연속 다운로드할 때는 단일 Client 인스턴스에서 반복 호출      |
| 기본 timeout         | 명시하지 않으면 5초 — 대용량 파일에는 부족할 수 있음                     |

---

## Topic 3: TOML Read/Write in Python

### 3.1 권장 라이브러리 버전

| 패키지  | 버전      | 비고                                               |
| ------- | --------- | -------------------------------------------------- |
| tomli   | `>=2.0.0` | Python <3.11 호환용 (3.11+에서는 stdlib `tomllib`) |
| tomli-w | `>=1.0.0` | TOML 쓰기 전용 (tomli의 write 카운터파트)          |

### 3.2 호환 레이어 (Python 3.10 + 3.11+)

```python
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "Python <3.11 requires 'tomli'. Install with: pip install tomli"
        )

import tomli_w
```

**pyproject.toml 의존성 선언:**

```toml
[project]
dependencies = [
    "tomli>=2.0.0; python_version < '3.11'",
    "tomli-w>=1.0.0",
]
```

### 3.3 TOML 읽기

```python
from pathlib import Path

def read_toml(path: Path) -> dict:
    """TOML 파일을 읽어서 dict로 반환."""
    with open(path, "rb") as f:  # 반드시 바이너리 모드!
        return tomllib.load(f)
```

> **중요:** `tomllib.load()`는 파일을 **바이너리 모드(`"rb"`)** 로 열어야 한다. 텍스트 모드로 열면 `TypeError` 발생.

### 3.4 TOML 쓰기

```python
from pathlib import Path

def write_toml(path: Path, data: dict) -> None:
    """dict를 TOML 파일로 쓰기."""
    with open(path, "wb") as f:  # 바이너리 모드!
        tomli_w.dump(data, f)
```

### 3.5 중첩 섹션 Read-Modify-Write 패턴

`pyproject.toml` 예시:

```toml
[project]
name = "my-app"

[tool.multikit]
registry = "https://example.com/kits"

[tool.multikit.kits.testkit]
version = "1.0.0"
files = ["conftest.py", "pytest.ini"]
```

**증분 업데이트 (read-modify-write):**

```python
from pathlib import Path

def add_kit_to_config(
    config_path: Path,
    kit_name: str,
    kit_info: dict,
) -> None:
    """기존 TOML에 kit 정보를 추가/갱신."""
    # 1. READ
    if config_path.exists():
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    else:
        data = {}

    # 2. MODIFY — 중첩 dict를 안전하게 탐색/생성
    tool = data.setdefault("tool", {})
    multikit = tool.setdefault("multikit", {})
    kits = multikit.setdefault("kits", {})
    kits[kit_name] = kit_info

    # 3. WRITE
    with open(config_path, "wb") as f:
        tomli_w.dump(data, f)
```

### 3.6 주의사항 / Gotchas

| 항목              | 설명                                                                                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| 바이너리 모드     | `tomllib.load()` → `"rb"`, `tomli_w.dump()` → `"wb"` — 필수                                              |
| 코멘트 미보존     | tomli/tomli-w는 라운드트립 시 TOML 주석이 삭제됨 (코멘트 보존 필요 시 `tomlkit` 사용)                    |
| 정렬              | tomli-w는 입력 dict의 삽입 순서를 유지함 (자동 정렬 없음)                                                |
| 유효성 검증       | `tomli_w.dumps()` 출력이 항상 유효 TOML인 것은 보장되지 않음 — 입력 타입이 올바를 때만 보장              |
| multiline_strings | 기본적으로 개행이 포함된 문자열도 한 줄로 쓰임 — `tomli_w.dumps(data, multiline_strings=True)` 옵션 존재 |

---

## Topic 4: Atomic File Operations in Python

### 4.1 사용 라이브러리

표준 라이브러리만 사용: `tempfile`, `shutil`, `os`, `pathlib`

### 4.2 TemporaryDirectory로 스테이징

```python
import tempfile
from pathlib import Path

def staged_download(files_to_download: dict[str, str], target_dir: Path) -> None:
    """
    파일을 임시 디렉토리에 먼저 다운로드한 뒤,
    모두 성공하면 최종 위치로 이동.

    Parameters
    ----------
    files_to_download
        {상대경로: 콘텐츠} 매핑
    target_dir
        최종 설치 디렉토리
    """
    with tempfile.TemporaryDirectory(prefix="multikit_") as tmp_str:
        tmp_dir = Path(tmp_str)

        # Phase 1: 임시 디렉토리에 모든 파일 쓰기
        for rel_path, content in files_to_download.items():
            dest = tmp_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")

        # Phase 2: 검증 (선택)
        # ... 파일 무결성 체크 등

        # Phase 3: 최종 위치로 이동
        for rel_path in files_to_download:
            src = tmp_dir / rel_path
            dst = target_dir / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
```

> `tempfile.TemporaryDirectory`는 `with` 블록 종료 시 자동 정리된다.
> 예외 발생 시에도 임시 파일이 남지 않는다.

### 4.3 shutil.move vs os.rename

```python
import shutil
import os

# os.rename — 같은 파일시스템에서만 원자적 (cross-device 시 OSError)
os.rename("/tmp/file.txt", "/home/user/project/file.txt")  # 실패할 수 있음!

# shutil.move — cross-filesystem 안전 (내부적으로 copy + delete)
shutil.move("/tmp/file.txt", "/home/user/project/file.txt")  # 항상 동작
```

| 함수            | 같은 FS              | 다른 FS          | 원자성                 |
| --------------- | -------------------- | ---------------- | ---------------------- |
| `os.rename()`   | ✅ 원자적            | ❌ `OSError`     | 같은 FS에서만          |
| `os.replace()`  | ✅ 원자적 (덮어쓰기) | ❌ `OSError`     | 같은 FS에서만          |
| `shutil.move()` | ✅ (내부 rename)     | ✅ (copy→delete) | 다른 FS에서는 비원자적 |

**권장:** `shutil.move()` — cross-filesystem 안전성이 중요하므로.

### 4.4 실패 시 정리 패턴 (try/finally)

```python
import shutil
import tempfile
from pathlib import Path

def safe_install(files: dict[str, str], target_dir: Path, force: bool = False) -> None:
    """실패 시 아무것도 변경되지 않도록 보장하는 설치."""
    installed: list[Path] = []
    backup_dir = None

    try:
        # 기존 파일 백업 (force 모드 시)
        if force:
            backup_dir = Path(tempfile.mkdtemp(prefix="multikit_backup_"))
            for rel_path in files:
                existing = target_dir / rel_path
                if existing.exists():
                    backup_path = backup_dir / rel_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(existing), str(backup_path))

        # 파일 설치
        for rel_path, content in files.items():
            dest = target_dir / rel_path
            if dest.exists() and not force:
                raise FileExistsError(f"File already exists: {dest}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            installed.append(dest)

    except Exception:
        # 롤백: 설치된 파일 삭제
        for path in installed:
            path.unlink(missing_ok=True)

        # 백업 복원
        if backup_dir and backup_dir.exists():
            for rel_path in files:
                backup_path = backup_dir / rel_path
                if backup_path.exists():
                    original = target_dir / rel_path
                    shutil.copy2(str(backup_path), str(original))
        raise

    finally:
        # 백업 디렉토리 정리
        if backup_dir and backup_dir.exists():
            shutil.rmtree(backup_dir)
```

### 4.5 주의사항 / Gotchas

| 항목               | 설명                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| `/tmp` vs 프로젝트 | `tempfile.TemporaryDirectory()`는 시스템 temp 디렉토리 사용 — 다른 파티션일 수 있음            |
| `dir` 파라미터     | `tempfile.TemporaryDirectory(dir=target_dir)` 하면 같은 FS 보장 → `os.rename` 원자적 사용 가능 |
| Windows 호환       | Windows에서 열린 파일은 이동 불가 — 파일 핸들을 반드시 닫은 후 이동                            |
| 권한               | `shutil.copy2`는 메타데이터(권한, 타임스탬프) 보존                                             |
| `missing_ok`       | Python 3.8+ `Path.unlink(missing_ok=True)`                                                     |

---

## Topic 5: Python difflib for File Comparison

### 5.1 사용 라이브러리

표준 라이브러리: `difflib` (추가 설치 없음)

### 5.2 unified_diff로 통합 diff 생성

```python
import difflib

def generate_diff(
    old_content: str,
    new_content: str,
    filename: str = "file",
) -> str:
    """두 문자열 간 unified diff를 생성."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=3,  # 컨텍스트 라인 수
    )
    return "".join(diff)
```

### 5.3 터미널에서 컬러 diff 출력

```python
import difflib
import sys

# ANSI 색상 코드
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_colored_diff(
    old_content: str,
    new_content: str,
    filename: str = "file",
) -> bool:
    """컬러 unified diff를 터미널에 출력. 변경사항이 있으면 True 반환."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff_lines = list(difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"local/{filename}",
        tofile=f"remote/{filename}",
        n=3,
    ))

    if not diff_lines:
        return False  # 변경사항 없음

    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++"):
            sys.stdout.write(f"{BOLD}{line}{RESET}")
        elif line.startswith("@@"):
            sys.stdout.write(f"{CYAN}{line}{RESET}")
        elif line.startswith("-"):
            sys.stdout.write(f"{RED}{line}{RESET}")
        elif line.startswith("+"):
            sys.stdout.write(f"{GREEN}{line}{RESET}")
        else:
            sys.stdout.write(line)

    return True
```

### 5.4 로컬 파일 vs 원격 콘텐츠 비교

```python
from pathlib import Path

def compare_local_vs_remote(
    local_path: Path,
    remote_content: str,
) -> str | None:
    """로컬 파일과 원격 콘텐츠를 비교하여 diff 문자열 반환.
    차이가 없으면 None 반환.
    """
    if not local_path.exists():
        # 로컬 파일이 없음 — 전체가 "추가"
        return generate_diff("", remote_content, filename=str(local_path.name))

    local_content = local_path.read_text(encoding="utf-8")

    if local_content == remote_content:
        return None  # 동일

    return generate_diff(
        local_content,
        remote_content,
        filename=str(local_path.name),
    )
```

### 5.5 dry-run 모드에서 활용 예시

```python
def install_with_preview(
    files: dict[str, str],    # {상대경로: 원격콘텐츠}
    target_dir: Path,
    dry_run: bool = False,
) -> None:
    """dry_run=True일 때 diff만 출력하고 실제 설치하지 않음."""
    for rel_path, remote_content in files.items():
        local_path = target_dir / rel_path

        if local_path.exists():
            local_content = local_path.read_text(encoding="utf-8")
            has_diff = print_colored_diff(
                local_content, remote_content, filename=rel_path
            )
            if not has_diff:
                print(f"  ✓ {rel_path} (unchanged)")
                continue
            if dry_run:
                print(f"  ~ {rel_path} (would be updated)")
                continue
        else:
            if dry_run:
                print(f"  + {rel_path} (would be created)")
                continue

        # 실제 쓰기
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(remote_content, encoding="utf-8")
        print(f"  ✓ {rel_path} (installed)")
```

### 5.6 주의사항 / Gotchas

| 항목                        | 설명                                                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------ |
| `splitlines(keepends=True)` | **필수** — 줄 끝 문자를 유지해야 diff가 올바르게 동작                                                  |
| `lineterm` 파라미터         | trailing newline이 없는 입력에는 `lineterm=""` 설정 필요                                               |
| 빈 파일 비교                | 빈 문자열과 비교 시에도 정상 동작                                                                      |
| 성능                        | difflib는 대용량 파일(수만 줄)에서 느릴 수 있음 — CLI 도구 수준에서는 문제 없음                        |
| ANSI 색상                   | Windows에서는 `colorama` 또는 Rich 라이브러리를 사용하는 것이 안전                                     |
| Rich 통합                   | cyclopts가 이미 Rich에 의존하므로, `rich.syntax.Syntax` 또는 `rich.console.Console`로 diff 출력도 가능 |

---

## 종합 의존성 요약

```toml
[project]
requires-python = ">=3.10"
dependencies = [
    "cyclopts>=3.6",
    "httpx>=0.28.0",
    "pydantic>=2.0",
    "tomli>=2.0.0; python_version < '3.11'",
    "tomli-w>=1.0.0",
]
```

**표준 라이브러리 (추가 설치 불필요):**

- `difflib` — diff 비교
- `tempfile` — 임시 디렉토리/파일
- `shutil` — 파일 이동/복사
- `pathlib` — 경로 처리
- `tomllib` — TOML 읽기 (Python 3.11+)

---

## 참고 자료

| 자료                | URL                                                       |
| ------------------- | --------------------------------------------------------- |
| cyclopts 공식 문서  | https://cyclopts.readthedocs.io/en/latest/                |
| cyclopts Commands   | https://cyclopts.readthedocs.io/en/latest/commands.html   |
| cyclopts Parameters | https://cyclopts.readthedocs.io/en/latest/parameters.html |
| httpx 공식 문서     | https://www.python-httpx.org/                             |
| httpx Clients       | https://www.python-httpx.org/advanced/clients/            |
| httpx Timeouts      | https://www.python-httpx.org/advanced/timeouts/           |
| httpx Exceptions    | https://www.python-httpx.org/exceptions/                  |
| tomli (PyPI)        | https://pypi.org/project/tomli/                           |
| tomli-w (PyPI)      | https://pypi.org/project/tomli-w/                         |
| difflib 공식 문서   | https://docs.python.org/3/library/difflib.html            |
