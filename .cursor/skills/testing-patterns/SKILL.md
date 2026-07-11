---
name: testing-patterns
description: Designs focused, hierarchical, regression, boundary, integration, and end-to-end tests for vertical-slice implementation. Use before and after implementation, and during test review.
---

# Testing Patterns

## Purpose

Create tests that prove behaviour, fail for the right reason before implementation, and protect against regressions without excessive brittleness.

Use the testing hierarchy deliberately: unit first, integration when boundaries are touched, local E2E for pipeline flow, cloud E2E only under explicit environment authority.

## Hierarchy

| Tier | Purpose | Use when | Typical evidence |
|---|---|---|---|
| Unit | Prove isolated logic | Pure functions, parsing, validation, mapping, business rules | RED/GREEN focused tests |
| Integration | Prove local boundaries | DB, filesystem, schema, adapters, services, orchestration boundary | Fixture setup, command, state/output assertion |
| Local E2E | Prove full local pipeline flow | Multi-stage pipelines, ingest/transform/publish, CLI entry point | Input dataset, run command, output validation, idempotency evidence |
| Cloud E2E | Prove deployed environment behaviour | Azure, Databricks, cloud jobs, remote permissions, deployed runtime | artifact SHA, job/run ID, logs, remote validation queries |

## Workflow

1. Read the task contract, expectations, and testing strategy config.
2. Classify the highest required tier for the task.
3. Map every acceptance criterion to at least one focused test or evidence item.
4. Map every negative case to a failure-path test.
5. Start with the smallest RED unit or integration test that demonstrates missing behaviour.
6. Implement the minimum code to pass.
7. Run the focused tier first, then lower-cost regressions, then required higher tiers.
8. Record evidence by tier.
9. Add regression tests for every bug fixed during a repair cycle.

## Pipeline-specific test guidance

For data/ETL/ELT pipelines, include at least these checks when applicable:

- Parser unit tests for each source format.
- Contract tests for required columns, data types, nullability, and rejected rows.
- Integration tests using local filesystem and local database or in-memory equivalent.
- Local E2E test that runs the pipeline from input fixtures to persisted/output tables.
- Idempotency test: rerun the same input without duplicate canonical records.
- Failure-path test: invalid input is rejected/classified rather than silently skipped.
- Late-arrival/retry test when the task concerns incremental processing.
- Cloud E2E only through `/goal-auto` or approved environment verification, not ordinary `/build-auto`.

## Anti-patterns

- Overbroad E2E tests as the only proof.
- Tests that simply assert implementation structure.
- Tests that mock the unit under test.
- Tests that pass if no assertion runs.
- Hidden dependency on test ordering.
- Integration tests that mutate shared developer or cloud resources without isolation.
- Cloud tests smuggled into ordinary unit-test gates.
- Marking a cloud run successful without validating outputs.

## Verification checklist

- [ ] Highest required tier is classified.
- [ ] Each acceptance criterion has evidence.
- [ ] Each negative case has evidence or a documented exception.
- [ ] At least one test would fail against the prior behaviour.
- [ ] Tests are deterministic and can be run from the recorded environment bootstrap.
- [ ] Boundary-touching tasks include integration evidence.
- [ ] Pipeline tasks include local E2E evidence before closure.
- [ ] Remote/cloud E2E is gated by explicit environment authority.
- [ ] Repair fixes include regression tests.


## IDSD testing artifact requirements

When contributing to IDSD artifact generation, do not stop at a generic validation strategy. Produce explicit testing expectations by hierarchy.

Expectations must include a human-readable Testing Expectations Matrix. Task contracts must include machine-readable `test_expectations`.

Every tier must be accounted for, including cloud E2E. Mark cloud E2E as not required unless an approved environment authority exists, and state that reason explicitly.
