# Bounded Remediation Prompt

Use this prompt only after deterministic audit reports have been generated.

```text
You are working on a Python codebase with an existing code-health audit.

Goal:
Improve maintainability without changing public behaviour.

Read:
- .audit/ruff.json
- .audit/pyright.json
- .audit/vulture.txt
- .audit/radon-cc.json
- .audit/radon-raw.json
- .audit/jscpd/jscpd-report.json if present
- .audit/coverage.txt
- the target source file
- relevant tests

Rules:
- Work on one file or one tightly coupled module group only.
- Do not redesign the whole project.
- Do not change public behaviour.
- Do not introduce new abstractions unless they remove real duplication or
  complexity.
- Prefer deletion, simplification, and extraction over new framework layers.
- Add or strengthen characterisation tests before risky refactors.
- Keep compatibility wrappers if external imports may rely on old locations.
- Run the relevant checks after changes.
- Stop after one coherent patch.

Deliver:
1. Diagnosis.
2. Refactor plan.
3. Tests added or updated.
4. Files changed.
5. Remaining risks.
```

