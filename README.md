# Code Health Toolkit

Deterministic code-health tooling for Python repositories.

This repository is a reusable engineering-quality baseline. It provides local
audit scripts, ranking logic, project templates, and operating guidance for
small, test-backed remediation work.

## Positioning

This is not an autonomous rewrite system. It is not a place for company source
code, production logs, customer data, credentials, or proprietary architecture
notes.

The operating model is:

```text
Scan deterministically
-> rank evidence
-> remediate one narrow target
-> prove behaviour with tests and checks
-> commit through normal review
-> convert repeated lessons into rules
```

## Why this exists

Fast iteration creates code-health debt: unused code, oversized modules,
duplicated logic, weak type guarantees, low branch coverage, and unclear import
boundaries. Those problems are best found by deterministic tools and fixed in
small reviewed changes.

The toolkit helps teams make quality work:

- measurable
- repeatable
- local-first
- reviewable
- compatible with normal SDLC controls
- safe to use in restricted corporate environments

## Repository contents

```text
tools/
  audit_codebase.sh       # Runs local checks and writes .audit/
  rank_hotspots.py        # Produces a ranked remediation backlog
  prepare_target_repo.sh  # Copies approved baseline files into a project

templates/
  AGENTS.md                       # Assistant/coding-agent guardrails
  importlinter.ini                # Example architecture contracts
  pyproject-code-health.toml      # Tooling config snippet
  github-actions-code-health.yml  # Optional CI example

docs/
  adoption-playbook.md
  operating-model.md
  security-and-compliance.md
  work-laptop-handoff.md
  agent-refactor-prompt.md
  decision-record-template.md
```

## Safe setup

Use an approved internal Git host if this will be cloned onto a work laptop.
Examples include GitHub Enterprise, GitLab, Bitbucket, or Azure DevOps if those
are approved by your organisation.

Recommended internal repository name:

```text
engineering/code-health-toolkit
```

Avoid storing this in a personal public GitHub account for work use. Keep the
repo generic and free of company code.

## Adopt in a target repository

From this toolkit repo:

```bash
./tools/prepare_target_repo.sh /path/to/target-repo
```

Then in the target repository:

```bash
git switch -c refactor/code-health-baseline
./tools/audit_codebase.sh
python tools/rank_hotspots.py --audit-dir .audit --output-md .audit/hotspots.md
git status
```

Open a baseline PR that adds the audit workflow and guidance only. Do not mix
tooling setup with refactoring.

## Tooling expectations

The audit script never installs packages automatically. It uses tools already
available in the target environment. This avoids unexpected network access and
keeps adoption compatible with controlled workstations.

Suggested project-level development tools:

```text
ruff
pyright or basedpyright
pytest
pytest-cov
coverage
vulture
deptry
radon
import-linter
bandit
pip-audit
jscpd
```

## Governance rules

- Use company-approved repositories and package sources on work devices.
- Do not move proprietary source code to personal machines or personal repos.
- Do not upload `.audit/` output outside approved systems.
- Do not add unapproved MCP servers or external automation services.
- Do not run blind overnight remediation loops.
- Do not use this toolkit to bypass policy, monitoring, approval, or review.

The professional story is simple: this is a deterministic engineering-quality
toolkit for local audit evidence and normal code review.

Before publishing or cloning this onto a controlled work device, read
`docs/work-laptop-handoff.md`.

