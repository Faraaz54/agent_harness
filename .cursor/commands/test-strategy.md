---
description: Inspect, classify, and validate the hierarchical testing strategy for the current harness or task contracts.
---

Use `test-hierarchy` and `testing-patterns`.

Common commands:

```bash
python -B scripts/test_strategy.py status
python -B scripts/test_strategy.py validate
python -B scripts/test_strategy.py classify --task-id <TASK_ID> --contracts docs/task-contracts/<intent-id>.json
python -B scripts/test_strategy.py validate-contracts --contracts docs/task-contracts/<intent-id>.json
```

`validate-contracts` is required after `/derive-tasks` in v0.5.6. It verifies that every task declares `test_expectations` for unit, integration, local E2E, and cloud E2E. A non-required tier must include a reason.
