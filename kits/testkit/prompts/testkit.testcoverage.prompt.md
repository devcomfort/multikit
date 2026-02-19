---
agent: testkit.testcoverage
---

Measure test coverage and classify gaps (COVERABLE / DEFENSIVE / ENV-DEPENDENT / DEAD CODE),
then write tests for coverable paths.
For structurally untestable code, apply `# pragma: no cover` with clear justification,
and report non-coverable areas transparently.
