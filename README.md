# Code Health Toolkit

Small, deterministic code-health tooling for Python repositories.

This is a personal toolkit for turning routine maintenance signals into a
small, reviewable backlog. It runs common Python quality tools, stores their
output under `.audit/`, and ranks files that look worth inspecting first.

It is intentionally boring: shell scripts, a Python ranking script, templates,
and notes about keeping refactors narrow.

## Why this exists

Code-health work is easy to make vague. A repository might have unused code,
large modules, duplicated logic, type errors, weak coverage, or import-boundary
drift, but it is not always obvious where to start.

This project tries to make that first pass more concrete:

```text
run local checks
-> collect audit output
-> combine evidence by file
-> pick one bounded target
-> improve it with tests
```

The ranking is not meant to be authoritative. It is just a triage aid for
finding files that deserve a closer look.

## Repository contents

```text
tools/
  audit_codebase.sh       # Runs local checks and writes .audit/
  rank_hotspots.py        # Produces a ranked remediation backlog
  prepare_target_repo.sh  # Copies the toolkit baseline into another repo

templates/
  AGENTS.md                       # Assistant/coding-agent guardrails
  importlinter.ini                # Example architecture contracts
  pyproject-code-health.toml      # Tooling config snippet
  github-actions-code-health.yml  # Optional CI example

docs/
  adoption-playbook.md
  operating-model.md
  agent-refactor-prompt.md
  decision-record-template.md
```

## Quick start

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

Open `.audit/hotspots.md` and pick one small target. The audit output is local
working data and should normally stay out of commits.

## Tools it can use

The audit script does not install packages automatically. It uses tools already
available in the environment so that it is predictable when run against an
existing project.

Useful tools to install in the target project:

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

Checks that are not available will either fail into `.audit/status.tsv` or be
skipped when the script can detect that cleanly.

## Development

Run the test suite with the dev extra installed:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

The tests focus on the ranking script because that is where the repo-specific
logic lives. The shell scripts are deliberately thin wrappers around existing
tools.
