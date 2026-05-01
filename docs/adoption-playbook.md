# Usage Notes

## 1. Add the baseline to a repository

From this repo:

```bash
cd code-health-toolkit
./tools/prepare_target_repo.sh /path/to/target-repo
```

Then:

```bash
cd /path/to/target-repo
git switch -c refactor/code-health-baseline
./tools/audit_codebase.sh
python tools/rank_hotspots.py --audit-dir .audit --output-md .audit/hotspots.md
```

## 2. Keep the setup commit small

The first change in a target repo should ideally add only:

- audit script
- ranking script
- engineering rules
- minimal configuration
- `.audit/` ignore rule

Avoid mixing tooling setup with refactors. It makes review harder and blurs
whether the tool changed behaviour.

Suggested commit title:

```text
Add code-health audit baseline
```

Suggested summary:

```text
Adds local scripts for collecting linting, typing, complexity, dependency,
dead-code, duplication, test, and architecture evidence under .audit/. Audit
output is treated as local working data.
```

## 3. Remediate in small patches

Each follow-up change should have one bounded target:

- one file
- one module
- one duplicated concept
- one import-boundary violation class
- one dependency hygiene issue

Avoid broad "cleanup" PRs.

## 4. Convert repeated lessons into checks

When the same issue appears repeatedly, add a rule:

- Ruff rule
- import-linter contract
- test helper
- type annotation expectation
- docs guideline
- CI check
