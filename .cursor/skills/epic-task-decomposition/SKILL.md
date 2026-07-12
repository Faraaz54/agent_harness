---
name: epic-task-decomposition
description: Converts approved IDSD artifacts into epic-organized, dependency-aware vertical-slice task contracts with explicit testing hierarchy requirements.
---

# Epic Task Decomposition

Do not produce a flat list of unrelated tasks. First create epics, then tasks inside epics.

## Epic requirements

Each epic must include:

- `epic_id`;
- `name`;
- `goal`;
- `sequencing_rationale`;
- dependencies on earlier epics, if any;
- risk level.

Epics group coherent outcomes. They are not layers like "models", "database", "tests". A pipeline epic might be "Source-to-bronze ingestion foundation" or "Bronze-to-silver normalization and lineage".

## Task requirements

Tasks should deliver vertical behaviour, not architectural layers. Each task must include:

- `task_id`;
- `epic_id` referencing a declared epic;
- objective;
- behavior;
- scope;
- allowed and forbidden paths where known;
- non-goals;
- dependencies;
- acceptance criteria;
- negative cases;
- verification commands or evidence paths;
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

After generating contracts, run:

```bash
python -B scripts/schema_validator.py --kind task-contracts --path docs/task-contracts/<intent-id>.json
python -B scripts/test_strategy.py validate-contracts --contracts docs/task-contracts/<intent-id>.json
python -B scripts/validate_tasks.py --tasks docs/task-contracts/<intent-id>.json --output docs/validation-reports/<intent-id>-task-contract-validation.json
```
