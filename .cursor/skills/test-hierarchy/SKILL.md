---
name: test-hierarchy
description: Classifies and enforces the required unit, integration, local E2E, and cloud E2E test tier for a task or run.
---

# Test Hierarchy

## Purpose

Select the minimum adequate verification level and prevent false confidence from only running low-level tests on high-risk pipeline changes.

## Tier selection rules

- Use **unit** for deterministic logic with no external boundary.
- Add **integration** when the task touches database, filesystem, network adapter, schema, queue, API, or runtime configuration boundaries.
- Add **local E2E** when the task changes a pipeline stage, CLI/job entry point, orchestration path, or multi-stage data flow.
- Require **cloud E2E** only when the approved goal/environment contract asks for deployed verification in Azure, Databricks, or another remote platform.

## Pipeline default

For pipeline projects, assume local E2E is required before final session closure when any approved task touches ingestion, transformation, loading, scheduling, reconciliation, schema evolution, or data quality checks.

## Builder obligations

- Do not jump straight to E2E when a focused unit/integration test can expose the defect faster.
- Do not claim implementation complete if the highest required tier was skipped.
- For skipped tiers, record why the tier was not applicable or not runnable.

## Reviewer obligations

- Verify that test tier selection is justified.
- Require higher-tier evidence when the task crosses a boundary.
- Reject test evidence that only proves a helper function when the task changed the pipeline outcome.

## Validator obligations

- Compare evidence against expected test tiers from task contract, expectations, project pack, and `harness.config.json`.
- Mark validation as blocked or rejected when required test tiers are missing without a valid exception.


## IDSD generation obligations

When generating Expectations or Task Contracts, include a full testing hierarchy declaration. Do not leave tier selection implicit.

For Expectations, create a Testing Expectations Matrix with columns: Behaviour/Risk, Unit, Integration, Local E2E, Cloud E2E.

For Task Contracts, include `test_expectations` with all four tiers. Required tiers must specify what to test and what evidence is required. Non-required tiers must specify why.

The reviewer and validator must reject a task contract that omits a tier or claims a tier is not required without a reason.
