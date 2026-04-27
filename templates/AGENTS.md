# Repository Engineering Rules

## Core rule

This codebase values maintainability, evidence, and behaviour preservation over
cleverness.

## Required workflow

Before editing:

- understand the target module and its tests
- inspect the latest local audit evidence where available
- work on one bounded target only

After editing:

- run Ruff for touched Python files
- run Pyright or the configured type checker when types are affected
- run relevant tests
- run import-linter if imports or architecture boundaries changed

## Refactoring rules

- Do not change behaviour during cleanup.
- Add characterisation tests before risky refactors.
- Prefer deletion, simplification, and extraction over new framework layers.
- Prefer pure functions for domain logic.
- Do not create vague `Manager`, `Handler`, `Processor`, or `Orchestrator`
  classes unless the responsibility is precise and documented.
- Do not move code across layers if it creates reverse imports.
- Keep compatibility wrappers when moving widely imported functions.

## Architecture

Use this direction unless the repository has a documented alternative:

```text
interfaces -> application -> domain
adapters   -> application/domain where needed
domain     -> imports nothing from adapters/interfaces
```

Definitions:

- `domain` contains pure business logic.
- `application` orchestrates use cases.
- `adapters` handle files, databases, APIs, LLMs, and external integrations.
- `interfaces` expose CLI, API, UI, or scheduled-job surfaces.

## Assistant constraints

- One session should produce one coherent patch.
- Do not run broad rewrites.
- Do not introduce unapproved dependencies.
- Do not send source code, audit output, logs, or credentials to external
  services.
- Stop and ask for review when a change could alter public behaviour.

