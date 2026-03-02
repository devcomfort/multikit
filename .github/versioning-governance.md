# Versioning Governance

- Version: 1.0.0
- Last Updated: 2026-03-01
- Owner: Maintainer (`@devcomfort`)
- Scope: 프로젝트 전체 버전 관리 정책

## 1) Purpose and Scope

이 문서는 multikit 프로젝트의 **버전 관리 원칙**을 정의한다.

목표:

- 모든 버전 번호가 명확한 의미를 전달한다 (SemVer)
- 버전 증분이 예측 가능하고 일관성 있다
- 버전 인플레이션(session 내 누적 증분)을 방지한다
- 모든 버전 위치가 동기화된 상태를 유지한다

적용 범위:

- `kits/*/manifest.json` 킷 버전
- `kits/registry.json` 레지스트리 버전
- `pyproject.toml` 패키지 버전
- `README.md` 킷 테이블 버전
- Git 태그

비적용 범위:

- 소비자(consumer) 프로젝트의 `multikit.toml` 버전 (로컬 설치 기록)

## 2) Versioning Scheme

**Semantic Versioning (SemVer) 2.0.0** — `MAJOR.MINOR.PATCH`

| Component | Meaning                            |
| --------- | ---------------------------------- |
| MAJOR     | 하위 호환성이 깨지는 변경          |
| MINOR     | 하위 호환되는 기능 추가            |
| PATCH     | 하위 호환되는 버그 수정, 문구 개선 |

신규 아티팩트(새 킷 등)는 `1.0.0`부터 시작한다.

## 3) Version Locations (Source of Truth)

버전 충돌 시 아래 우선순위를 따른다 (상위가 우선):

1. `kits/{name}/manifest.json` — **킷 버전의 단일 진실 원천**
2. `kits/registry.json` — manifest에서 파생
3. `README.md` 킷 테이블 — registry에서 파생
4. `pyproject.toml` — 패키지 자체 버전 (킷 버전과 독립)

규칙:

- registry와 README의 킷 버전은 반드시 manifest와 일치해야 한다
- 불일치 발견 시 manifest 기준으로 동기화한다

## 4) Bump Rules — Kit Versioning

### SemVer 범프 기준

| Bump      | Trigger                                                                                 |
| --------- | --------------------------------------------------------------------------------------- |
| **MAJOR** | 에이전트 ID 변경/제거, 에이전트 핵심 목적 변경, 기존 에이전트 삭제, 호환 불가 구조 변경 |
| **MINOR** | 새 에이전트 추가, 새 핸드오프 추가, 기존 에이전트에 새 기능/섹션 추가 (하위 호환)       |
| **PATCH** | 핸드오프 대상 수정, 문구 개선, 테이블 정렬, Proactive Suggestions 추가, 오타 수정       |

### Git-Diff-Based Single Increment Rule (핵심 규칙)

**작업 세션 내 버전은 커밋된 기준에서 정확히 한 번만 증분한다.**

| Rule                 | Description                                                          |
| -------------------- | -------------------------------------------------------------------- |
| **Base = HEAD**      | 범프 계산 시 `git show HEAD:<path>` 에서 읽은 커밋된 버전이 기준이다 |
| **Single Increment** | 세션 중 아무리 많은 변경이 있어도 커밋된 기준에서 **한 번만** 증분   |
| **Highest Wins**     | 모든 변경을 MAJOR/MINOR/PATCH로 분류 후, **최고 레벨** 하나만 적용   |
| **New = 1.0.0**      | HEAD에 존재하지 않는 신규 아티팩트는 `1.0.0`                         |

**예시**:

```
HEAD version: 1.0.1
작업 세션 변경: 에이전트 3개 추가(MAJOR) + 오타 수정(PATCH) + 핸드오프 추가(MINOR)
→ 최고 레벨: MAJOR
→ 올바른 버전: 2.0.0

❌ 틀린 예: 1.0.1 → 1.0.2 → 1.1.0 → 2.0.0 → 3.0.0 (누적 증분)
✅ 올바른 예: 1.0.1 → 2.0.0 (단일 증분)
```

## 5) Consistency Policy

버전 변경 시 **반드시** 아래 파일을 동기화한다:

1. `kits/{name}/manifest.json` — 킷 버전 변경
2. `kits/registry.json` — 해당 킷 항목 버전 업데이트
3. `README.md` — 킷 테이블 버전 업데이트
4. `.github/agents/`, `.github/prompts/` — 에이전트/프롬프트 파일 재배포

검증 방법:

```bash
# manifest ↔ registry 일치 확인
python3 -c "import json; r=json.load(open('kits/registry.json')); [print(f\"{k['name']:12s} {k['version']}\") for k in r['kits']]"

# kits/ ↔ .github/ 동일성 확인
for kit in kits/*/; do for type in agents prompts; do
  if [ -d "$kit/$type" ]; then for f in "$kit/$type/"*; do
    diff -q "$f" ".github/$type/$(basename $f)" 2>/dev/null || echo "DIFF: $f"
  done; fi
done; done
```

## 6) Pre-release Convention

현재 적용하지 않음. 필요 시 아래 형식을 사용:

- Alpha: `X.Y.Z-alpha.N`
- Beta: `X.Y.Z-beta.N`
- RC: `X.Y.Z-rc.N`

## 7) Release Workflow

1. 작업 세션에서 변경 수행
2. `cikit.analyze.versioning`으로 범프 레벨 분석
3. `cikit.analyze.versioning.update`로 전체 파일 동기화
4. 또는 `multikit.register`로 등록 + 배포
5. 커밋 메시지: `chore: bump {kit} v{old} → v{new}`

## 8) Exception Handling

| 상황                    | 처리                                         |
| ----------------------- | -------------------------------------------- |
| 실수로 과대 범프된 버전 | 커밋 전이면 HEAD 기준으로 재계산하여 수정    |
| 여러 킷이 동시에 변경됨 | 각 킷 독립적으로 범프 (킷 간 버전 연동 없음) |
| 거버넌스 문서 자체 변경 | 이 문서의 버전도 SemVer로 관리 (아래 참조)   |

## 9) Governance Self-Versioning

| Bump  | Trigger                                        |
| ----- | ---------------------------------------------- |
| MAJOR | 호환 불가 정책 변경 (예: SemVer → CalVer 전환) |
| MINOR | 새 규칙 카테고리 추가, 정책 확장               |
| PATCH | 문구 명확화, 예시 추가/수정                    |

## Amendment Log

| Version | Date       | Change                                                                         |
| ------- | ---------- | ------------------------------------------------------------------------------ |
| 1.0.0   | 2026-03-01 | 초기 거버넌스 수립 — SemVer, Git-Diff-Based Single Increment Rule, 동기화 정책 |
