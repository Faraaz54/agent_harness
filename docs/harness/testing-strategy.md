# Testing Strategy Hierarchy

The harness uses a layered test strategy. The goal is to prove behaviour at the cheapest reliable level first, then escalate only when the task crosses a boundary or changes an end-to-end pipeline outcome.

## Hierarchy

1. **Unit tests** prove isolated logic.
2. **Integration tests** prove local boundaries such as database, filesystem, schema, adapter, API, queue, or orchestration contracts.
3. **Local end-to-end tests** prove a complete local pipeline path using known fixtures or local test data.
4. **Cloud end-to-end tests** prove the deployed runtime in Azure, Databricks, or another remote environment. These are governed by goal/environment authority, not ordinary build-auto.

## Default gating model

- Per-task implementation must include unit tests where testable.
- Boundary-touching tasks must include integration evidence.
- Pipeline-affecting runs must include local E2E evidence before final closure.
- Cloud E2E is not automatically run by `/build-auto`; it belongs to the later goal loop or to explicitly authorised environment verification.

## Why this matters for pipelines

Pipelines often pass unit tests while failing where it matters: source parsing, schema drift, idempotency, stateful reruns, persistence, deployment configuration, or Databricks runtime differences. The hierarchy prevents false confidence by requiring each relevant boundary to be proven.

## Evidence expectations

| Tier | Required evidence |
|---|---|
| Unit | focused test command, RED/GREEN evidence, mapped acceptance criteria |
| Integration | boundary under test, fixture setup, command, local state/output assertion |
| Local E2E | source fixture identity, pipeline command, output validation, idempotency/failure-path checks |
| Cloud E2E | deployed artifact SHA, environment, job/run ID, logs, remote validation queries, cleanup/cost envelope |

## Relationship to build-auto and goal-auto

`/build-auto` is responsible for unit, integration, and local E2E evidence within the repository and local environment.

Cloud E2E requires external authority and should be handled by a goal loop because it mutates or consumes remote infrastructure. A successful Databricks job is not sufficient by itself; the verifier must also validate produced tables, invariants, lineage, and output reports.


## IDSD generation requirement

Starting in v0.5.6, testing hierarchy is not only a review-time concern. IDSD artifact generation must declare it up front.

Expectations must include a Testing Expectations Matrix. Task contracts must include machine-readable `test_expectations`. The test agent and validator should reject missing tiers.

A tier can be not required; a tier cannot be absent.
