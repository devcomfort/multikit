```prompt
---
agent: lintkit.analyze.python
---

Run static analysis tools (ruff, mypy, Pylance) to collect issues,
classify each issue by root cause (AUTO-FIXABLE / MANUAL-FORMAT / TYPE-SIGNATURE / TEST-SPECIFIC / INTENTIONAL),
then create and execute a phased remediation plan.
After all fixes, verify there are no test regressions.

```
