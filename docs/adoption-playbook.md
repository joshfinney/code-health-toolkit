# Adoption Playbook

## 1. Create an internal toolkit repository

Use a company-approved Git host.

Recommended name:

```text
engineering/code-health-toolkit
```

The repository should contain generic tooling and documentation only.

## 2. Clone on the work laptop

Clone from the approved internal host:

```bash
git clone git@approved-host:engineering/code-health-toolkit.git
```

Do not clone from personal infrastructure onto a controlled workstation unless
that pattern is explicitly approved.

## 3. Add the baseline to a target repository

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

## 4. Open the first PR

The first PR should add only:

- audit script
- ranking script
- engineering rules
- minimal configuration
- `.audit/` ignore rule

Do not include refactors in the baseline PR.

Suggested PR title:

```text
Add deterministic code-health audit baseline
```

Suggested PR summary:

```text
This change adds a local deterministic code-health audit workflow. The workflow
collects linting, typing, complexity, dependency, dead-code, duplication, test,
and architecture evidence under .audit/ for local triage. No audit output is
committed.
```

## 5. Remediate in small PRs

Each follow-up PR should have one bounded target:

- one file
- one module
- one duplicated concept
- one import-boundary violation class
- one dependency hygiene issue

Avoid broad "cleanup" PRs.

## 6. Convert lessons into checks

When the same issue appears repeatedly, add a rule:

- Ruff rule
- import-linter contract
- test helper
- type annotation expectation
- docs guideline
- CI check

