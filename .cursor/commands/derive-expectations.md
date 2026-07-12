---
description: Derive schema-valid Expectations from approved Intent and Context.
---

Use `expectation-derivation` with `expectation-derivation-agent`.

Inputs:

- `docs/intents/<intent-id>.md`
- `docs/context/<intent-id>.json`
- active project pack
- `docs/bootstrap/environment.json`

Write:

- `docs/expectations/<intent-id>.md`
- `docs/expectations/<intent-id>.json`
- `docs/expectation-derivation-results/<intent-id>.json`

The JSON expectations artifact must validate against:

```bash
python -B scripts/schema_validator.py --kind expectations --path docs/expectations/<intent-id>.json
python -B scripts/validate_expectations.py --expectations docs/expectations/<intent-id>.json --output docs/validation-reports/<intent-id>-expectations-validation.json
```

The derivation result must validate against:

```bash
python -B scripts/schema_validator.py --kind expectation-derivation-result --path docs/expectation-derivation-results/<intent-id>.json
```

Do not proceed to task derivation until expectations schema validation and semantic validation pass.
