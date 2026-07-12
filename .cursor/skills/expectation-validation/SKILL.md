---
name: expectation-validation
description: Validates Expectations for schema correctness, ambiguity, implementation neutrality, testing hierarchy completeness, and validator/builder separation.
---

# Expectation Validation

Validate that expectations are observable, bounded, not over-specified, and not leaking private eval details to the builder.

Required deterministic checks:

```bash
python -B scripts/schema_validator.py --kind expectations --path docs/expectations/<intent-id>.json
python -B scripts/validate_expectations.py --expectations docs/expectations/<intent-id>.json --output docs/validation-reports/<intent-id>-expectations-validation.json
```

Review dimensions:

- success scenarios are observable;
- failure scenarios are binary or evaluable;
- acceptance criteria map to tests;
- testing expectations matrix includes unit, integration, local_e2e, and cloud_e2e;
- each non-required tier has an explicit reason;
- expectations do not smuggle implementation choices that belong in Context;
- private eval details are not leaked to the builder-facing sections.
