---
description: Convert approved IDSD artifacts into epic-organized vertical-slice task contracts with explicit hierarchical test expectations.
---

Use these skills, in this order:

1. `epic-task-decomposition`
2. `technical-specification`
3. `test-hierarchy`
4. active project-pack domain review guidance

Use `task-decomposition-agent`.

Inputs:

- approved Intent;
- approved Context Pack, including `project_context.included_files`;
- approved Expectations, including the Testing Expectations Matrix;
- validated Technical Spec (`docs/technical-specs/<intent-id>.json`);
- technical spec validation result;
- expectation validation result;
- active project pack and harness testing strategy.

Write:

- `docs/task-contracts/<intent-id>.json`
- `docs/task-decomposition-results/<intent-id>.json`

Task contracts must contain top-level `epics` and `tasks`. Every task must include an `epic_id` referencing a declared epic. Every task must include `required_context` and `context_files` referencing the assembled project-pack context it depends on. Every task must include `technical_spec_refs` identifying the exact Technical Spec sections that govern implementation. Every task must include `test_expectations` with all four tiers:

- `unit`
- `integration`
- `local_e2e`
- `cloud_e2e`

After writing task contracts, run:

```bash
python -B scripts/schema_validator.py --kind context-pack --path docs/context/<intent-id>.json
python -B scripts/schema_validator.py --kind technical-spec --path docs/technical-specs/<intent-id>.json
python -B scripts/schema_validator.py --kind technical-spec-validation-result --path docs/validation-reports/<intent-id>-technical-spec-validation.json
python -B scripts/schema_validator.py --kind task-contracts --path docs/task-contracts/<intent-id>.json
python -B scripts/test_strategy.py validate-contracts --contracts docs/task-contracts/<intent-id>.json
python -B scripts/validate_tasks.py --tasks docs/task-contracts/<intent-id>.json --output docs/validation-reports/<intent-id>-task-contract-validation.json
python -B scripts/schema_validator.py --kind task-contract-validation-result --path docs/validation-reports/<intent-id>-task-contract-validation.json
```

Do not prepare a run unless these checks pass.
