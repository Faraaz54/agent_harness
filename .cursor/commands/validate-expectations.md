---
description: Validate generated Expectations with schema and semantic checks before implementation authority exists.
---

Use `expectation-validation` with `expectation-validation-agent`.

Run deterministic validation:

```bash
python -B scripts/schema_validator.py --kind expectations --path docs/expectations/<intent-id>.json
python -B scripts/validate_expectations.py --expectations docs/expectations/<intent-id>.json --output docs/validation-reports/<intent-id>-expectations-validation.json
python -B scripts/schema_validator.py --kind expectation-validation-result --path docs/validation-reports/<intent-id>-expectations-validation.json
```

Also write a human-readable Markdown summary:

```text
docs/validation-reports/<intent-id>-expectations-validation.md
```

Return `PASS` only when the Expectations JSON is schema-valid, references the assembled Context Pack and project-pack context files through `source_context`, has success/failure scenarios, and declares all testing hierarchy tiers.
