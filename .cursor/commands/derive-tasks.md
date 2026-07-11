---
description: Convert approved IDSD artifacts into vertical-slice task contracts with explicit hierarchical test expectations.
---

Use `epic-task-decomposition` and `test-hierarchy`.

Inputs:

- approved Intent;
- approved Context Pack;
- approved Expectations, including the Testing Expectations Matrix;
- active project pack and harness testing strategy.

Write `docs/task-contracts/<intent-id>.json`.

Every task must include `test_expectations` with all four tiers:

- `unit`;
- `integration`;
- `local_e2e`;
- `cloud_e2e`.

A tier may be `{ "required": false }`, but it must include `not_required_reason`. Required tiers must include `what_to_test`, `evidence_required`, and verification commands or expected evidence paths. Do not silently omit a tier.

After writing the task contracts, run:

```bash
python -B scripts/test_strategy.py validate-contracts --contracts docs/task-contracts/<intent-id>.json
```
