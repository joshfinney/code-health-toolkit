# Security and Compliance Notes

## Intent

This toolkit is designed to support normal engineering quality work in
controlled environments. It should be boring, auditable, and easy to explain.

## Professional framing

Use neutral language:

- deterministic code-health audit
- maintainability baseline
- local engineering quality checks
- ranked remediation backlog
- architecture boundary checks

Avoid informal language in internal artefacts:

- AI slop
- cleanup bot
- autonomous rewrite
- stealth automation
- bypass

## Data handling

Do not commit `.audit/` output. Audit reports may contain file paths, code
symbols, dependency names, and error messages that should remain inside the
target repository's approved environment.

## Dependency policy

The audit script does not install packages. Install tools through the target
team's approved dependency process.

Avoid tools with licences that are not approved for corporate use. In
particular, do not add AGPL-licensed tools to work repositories without legal or
open-source-program approval.

## Assistant/tooling policy

Coding assistants should operate within normal review, test, and approval
controls. Avoid unapproved external services, random MCP servers, browser
extensions, or daemons that expand the tool surface on a controlled workstation.

## Recommended first PR

Title:

```text
Add deterministic code-health audit baseline
```

Description:

```text
Adds local-only scripts and repository guidance for collecting code-health
evidence. Reports are written under .audit/ and are not committed. This prepares
the repository for small, reviewable maintainability improvements.
```

