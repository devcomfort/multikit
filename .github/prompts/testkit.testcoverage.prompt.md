---
agent: testkit.testcoverage
---

테스트 커버리지를 측정하고 갭을 분류(COVERABLE / DEFENSIVE / ENV-DEPENDENT / DEAD CODE)하여,
커버 가능한 경로에 대해 테스트를 작성합니다.
구조적으로 커버 불가한 코드에는 사유가 포함된 `# pragma: no cover`를 적용하고,
불가능성을 투명하게 보고합니다.
