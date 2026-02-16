# Data Model: Multikit CLI (MVP)

**Feature**: 001-multikit-cli
**Date**: 2026-02-12
**Source**: spec.md Key Entities + research.md

## Entity Relationship

```
Registry (registry.json)
  └─ 1:N ─→ RegistryEntry
                └─ 1:1 ─→ Manifest (manifest.json, per kit)
                              ├─ agents: [filename, ...]
                              └─ prompts: [filename, ...]

Config (multikit.toml)
  └─ 1:N ─→ InstalledKit
                └─ tracks installed version/source of a Kit
```

## Entities

### 1. Manifest (킷 매니페스트)

킷의 `manifest.json`에 대응. 원격에서 다운로드하여 어떤 파일을 설치할지 결정한다.

**Location**: `kits/{kit_name}/manifest.json`

```python
from pydantic import BaseModel, Field

class Manifest(BaseModel):
    """A kit's manifest.json — declares files to install."""
    name: str = Field(description="Kit name (e.g., 'testkit')")
    version: str = Field(description="Semantic version (e.g., '1.0.0')")
    description: str = Field(default="", description="Human-readable description")
    agents: list[str] = Field(default_factory=list, description="Agent filenames (e.g., ['testkit.testdesign.agent.md'])")
    prompts: list[str] = Field(default_factory=list, description="Prompt filenames (e.g., ['testkit.testdesign.prompt.md'])")
```

**Validation Rules**:

- `name`: non-empty, lowercase, alphanumeric + hyphens
- `version`: non-empty, semver format preferred
- `agents` + `prompts`: combined must have at least 1 entry (empty kit → warning)
- filenames must end with `.agent.md` or `.prompt.md` respectively

**Example**:

```json
{
  "name": "testkit",
  "version": "1.0.0",
  "description": "Test design and coverage agents",
  "agents": ["testkit.testdesign.agent.md", "testkit.testcoverage.agent.md"],
  "prompts": ["testkit.testdesign.prompt.md", "testkit.testcoverage.prompt.md"]
}
```

---

### 2. RegistryEntry (레지스트리 항목)

`registry.json`의 개별 킷 항목.

```python
class RegistryEntry(BaseModel):
    """A single kit entry in registry.json."""
    name: str = Field(description="Kit name")
    version: str = Field(description="Latest available version")
    description: str = Field(default="", description="Short description")
```

---

### 3. Registry (레지스트리)

원격 `registry.json`의 루트 객체. 사용 가능한 킷 전체 목록.

**Location**: `kits/registry.json`

```python
class Registry(BaseModel):
    """Remote registry.json — lists all available kits."""
    kits: list[RegistryEntry] = Field(default_factory=list, description="Available kits")
```

**Example**:

```json
{
  "kits": [
    {
      "name": "testkit",
      "version": "1.0.0",
      "description": "Test design and coverage agents"
    },
    {
      "name": "gitkit",
      "version": "1.0.0",
      "description": "Git commit agents"
    },
    {
      "name": "speckit",
      "version": "2.0.0",
      "description": "Spec/plan/tasks workflow agents"
    }
  ]
}
```

---

### 4. InstalledKit (설치된 킷 기록)

`multikit.toml`의 `[multikit.kits.<name>]` 섹션에 대응.

```python
class InstalledKit(BaseModel):
    """Tracks an installed kit in multikit.toml."""
    version: str = Field(description="Installed version")
    source: str = Field(default="remote", description="Installation source ('remote')")
    files: list[str] = Field(default_factory=list, description="List of installed file paths relative to .github/")
```

**Note**: `files` 필드는 uninstall 시 정확한 파일 삭제를 위해 설치된 파일 경로를 추적한다.

---

### 5. MultikitConfig (프로젝트 설정)

`multikit.toml`의 전체 구조에 대응.

```python
class MultikitConfig(BaseModel):
    """Root config model for multikit.toml."""
    version: str = Field(default="0.1.0", description="Multikit config version")
    registry_url: str = Field(
        default="https://raw.githubusercontent.com/devcomfort/multikit/main/kits",
        description="Base URL for the remote kit registry",
    )
    kits: dict[str, InstalledKit] = Field(default_factory=dict, description="Installed kits")
```

**TOML Representation**:

```toml
[multikit]
version = "0.1.0"
registry_url = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"

[multikit.kits.testkit]
version = "1.0.0"
source = "remote"
files = [
    "agents/testkit.testdesign.agent.md",
    "agents/testkit.testcoverage.agent.md",
    "prompts/testkit.testdesign.prompt.md",
    "prompts/testkit.testcoverage.prompt.md",
]

[multikit.kits.gitkit]
version = "1.0.0"
source = "remote"
files = [
    "agents/gitkit.commit.agent.md",
    "prompts/gitkit.commit.prompt.md",
]
```

---

## State Transitions

### Kit Lifecycle

```
                    multikit install
  [Not Installed] ─────────────────→ [Installed]
        ↑                                │
        │     multikit uninstall         │
        └────────────────────────────────┘

  [Installed] ──── multikit install (재실행) ───→ [Installed] (diff + 선택적 업데이트)
  [Installed] ──── multikit diff ───→ [Installed] (상태 변경 없음, 정보 출력만)
```

### Install Flow (Atomic)

```
  [Start]
    │
    ▼
  Fetch manifest.json from remote
    │
    ├─ 404 / network error → [Error: Kit not found] → [End]
    │
    ▼
  Download all files to tempdir
    │
    ├─ Any download fails → cleanup tempdir → [Error] → [End]
    │
    ▼
  Compare with existing local files (if any)
    │
    ├─ No local files → move all to .github/ → update config → [Success]
    │
    ├─ Has differences + --force → overwrite all → update config → [Success]
    │
    └─ Has differences + interactive →
         For each file:
           Show diff → prompt [y/n/a/s]
           y → overwrite this file
           n → skip this file
           a → overwrite all remaining
           s → skip all remaining
       → update config (with actually installed files) → [Success]
```
