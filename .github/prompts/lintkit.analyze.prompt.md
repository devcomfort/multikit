```prompt
---
agent: lintkit.analyze
---

정적 분석 도구(ruff, mypy, Pylance)를 실행하여 오류를 수집하고,
각 오류를 원인별로 분류(AUTO-FIXABLE / MANUAL-FORMAT / TYPE-SIGNATURE / TEST-SPECIFIC / INTENTIONAL)한 뒤,
단계적 수정 계획을 수립하여 실행합니다.
모든 수정 후 테스트 회귀가 없는지 검증합니다.

```
