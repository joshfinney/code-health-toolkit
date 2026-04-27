# Operating Model

## Thesis

Use deterministic tools to locate mechanical problems. Use coding assistants
only inside a narrow, test-backed remediation loop. Codify repeated lessons as
rules so the same problems do not quietly return.

## Loop

```text
1. Run audit.
2. Rank hotspots.
3. Select one bounded target.
4. Read behaviour and tests.
5. Add characterisation tests where needed.
6. Refactor conservatively.
7. Run checks.
8. Commit through normal review.
9. Promote repeated lessons into rules.
```

## Prioritisation

Prioritise files that combine several signals:

- high line count
- high cyclomatic complexity
- duplication
- lint findings
- type findings
- unused code
- weak coverage
- import-boundary violations

No single metric should drive refactoring. The goal is to find high-confidence,
high-ROI maintenance work.

## Good remediation targets

- duplicated validation logic
- duplicated parsing logic
- unused helper functions
- oversized orchestration functions
- functions with unclear side effects
- reverse imports across architecture layers
- modules with weak tests and high churn

## Bad remediation targets

- arbitrary line-count splits
- broad style-only rewrites
- new abstraction layers without deleted complexity
- behaviour changes bundled with cleanup
- changes that cannot be tested locally

## Definition of done

A remediation PR is done when:

- behaviour is preserved or intentionally changed in a separately reviewed PR
- tests cover the touched behaviour
- lint/type/test checks pass
- public imports remain compatible or migration is documented
- any remaining risks are stated in the PR

