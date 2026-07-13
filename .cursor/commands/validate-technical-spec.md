---
description: Validate the Technical Spec artifact before task decomposition.
---

Use `technical-specification` with `technical-spec-validation-agent`.

Inputs:

- `docs/technical-specs/<intent-id>.json`
- `docs/context/<intent-id>.json`
- `docs/expectations/<intent-id>.json`

Run:

```bash
python -B scripts/schema_validator.py --kind technical-spec --path docs/technical-specs/<intent-id>.json
python -B scripts/validate_technical_spec.py --spec docs/technical-specs/<intent-id>.json --output docs/validation-reports/<intent-id>-technical-spec-validation.json
python -B scripts/schema_validator.py --kind technical-spec-validation-result --path docs/validation-reports/<intent-id>-technical-spec-validation.json
```

Human checkpoint: review library choices, module boundaries, implementation rules, and deferred items before `/derive-tasks`.
