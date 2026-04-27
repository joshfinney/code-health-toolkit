# Security and Data Handling

## Scope

This repository should contain generic tooling only. It should not contain:

- company source code
- customer, trade, market, or portfolio data
- logs from production or controlled environments
- credentials, tokens, certificates, cookies, or SSH keys
- internal system names that are not already approved for the destination repo
- exported audit reports from proprietary repositories

## Local-first behaviour

The scripts in this repository are designed to run locally and write output
under `.audit/` in the target repository. They do not install dependencies and
do not intentionally send data to external services.

Some tools invoked by the audit script may access networks if configured by the
target environment. Review local policy and tool configuration before enabling
checks such as dependency vulnerability auditing.

## Corporate use

For work use, host this toolkit in an approved internal Git system. Do not clone
from personal infrastructure onto controlled workstations unless your company
policy explicitly allows that pattern.

## Reporting issues

Report security issues through the owning team's approved internal process.

