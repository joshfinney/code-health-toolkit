# Security

## Scope

This repository should contain generic tooling only. Please do not commit:

- source code from another project
- application logs or exported audit reports
- credentials, tokens, certificates, cookies, or SSH keys
- private system names or URLs

## Local-first behaviour

The scripts in this repository are designed to run locally and write output
under `.audit/` in the target repository. They do not install dependencies or
intentionally send project data to external services.

Some invoked tools may perform network access depending on their own
configuration. Review those tools before enabling checks such as dependency
vulnerability auditing.

## Audit output

Audit reports can contain file paths, symbols, dependency names, and error
messages. Keep `.audit/` out of version control unless you have deliberately
reviewed the contents.

## Reporting issues

Please open a private issue or contact the repository owner if you find a
security problem in the toolkit itself.
