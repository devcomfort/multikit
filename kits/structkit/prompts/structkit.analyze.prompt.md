---
agent: structkit.analyze
---

Analyze the project structure. Supports two modes:
- **Compliance**: Check directory structure against governance rules — detect violations, drift, and warnings.
- **Architecture**: Analyze architecture patterns, design patterns, conventions, and recommend improvements with rationale and trade-offs.

Mode is determined from context: governance-related keywords → Compliance; architecture/design keywords → Architecture.
