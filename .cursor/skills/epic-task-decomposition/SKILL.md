---
name: epic-task-decomposition
description: Converts approved IDSD artifacts into dependency-aware vertical-slice task contracts with explicit testing hierarchy requirements.
---

# Task Decomposition

Tasks should deliver vertical behaviour, not architectural layers. Each task must include:

- objective;
- behavior;
- scope;
- non-goals;
- dependencies;
- acceptance criteria;
- negative cases;
- verification commands;
- required reviewers;
- risk level;
- stop conditions;
- `test_expectations`.

## Required `test_expectations`

Every task contract must state the required evidence for all four tiers:

- `unit`;
- `integration`;
- `local_e2e`;
- `cloud_e2e`.

Each tier entry must contain:

- `required`: boolean;
- `what_to_test`: list of behaviours or risks to prove;
- `evidence_required`: list of commands, files, queries, reports, or expected observations;
- `not_required_reason`: required when `required` is false.

Also include:

- `highest_required_tier`;
- `tier_rationale`;
- `coverage_map`, mapping acceptance criteria and negative cases to the test tier that proves them.

## Pipeline default

For data pipelines, ingestion, ETL/ELT, bronze/silver/gold transformations, orchestration entrypoints, and stateful processing, local E2E evidence is normally required before session closure. Cloud E2E is not run by `/build-auto` unless explicit environment authority exists.
