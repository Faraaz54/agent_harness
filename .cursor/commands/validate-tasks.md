---
description: Validate epic-organized task contracts before run preparation.
---

Use `task-contract-validation-agent` and deterministic validation scripts.

Run:

```bash
python -B scripts/schema_validator.py --kind technical-spec --path docs/technical-specs/<intent-id>.json
python -B scripts/schema_validator.py --kind technical-spec-validation-result --path docs/validation-reports/<intent-id>-technical-spec-validation.json
python -B scripts/schema_validator.py --kind task-contracts --path docs/task-contracts/<intent-id>.json
python -B scripts/test_strategy.py validate-contracts --contracts docs/task-contracts/<intent-id>.json
python -B scripts/validate_tasks.py --tasks docs/task-contracts/<intent-id>.json --output docs/validation-reports/<intent-id>-task-contract-validation.json
python -B scripts/schema_validator.py --kind task-contract-validation-result --path docs/validation-reports/<intent-id>-task-contract-validation.json
```

Validation must fail when:

- top-level `epics` are missing;
- a task lacks `epic_id`;
- a task references an unknown epic;
- dependencies reference unknown tasks;
- `test_expectations` is missing or omits any test tier;
- a required test tier lacks `what_to_test` or `evidence_required`;
- a non-required tier lacks `not_required_reason`.

- top-level `technical_spec` is missing;
- a task lacks `technical_spec_refs`;
- a technical spec reference lacks `section` or `reason`;
