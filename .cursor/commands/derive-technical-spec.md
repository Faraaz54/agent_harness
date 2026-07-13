---
description: Derive a schema-valid Technical Spec from approved Intent, Context, and Expectations before task decomposition.
---

Use `technical-specification` with `technical-spec-agent`.

Inputs:

- `docs/intents/<intent-id>.md`
- `docs/context/<intent-id>.json`
- `docs/expectations/<intent-id>.json`
- `docs/validation-reports/<intent-id>-expectations-validation.json`
- active project pack, including `project-packs/<project-name>/context/**`

Write:

- `docs/technical-specs/<intent-id>.json`
- `docs/technical-specs/<intent-id>.md`
- `docs/technical-spec-results/<intent-id>.json`

The Technical Spec must capture concrete implementation decisions, including:

- architecture style and runtime targets;
- Python/library/dependency choices with rationale;
- module boundaries;
- source/data flow;
- configuration and secrets policy;
- error/rejection handling;
- lineage/idempotency strategy where relevant;
- testing implications by unit, integration, local E2E, and cloud E2E;
- explicit deferred items and non-decisions.

After writing the spec, run:

```bash
python -B scripts/schema_validator.py --kind technical-spec --path docs/technical-specs/<intent-id>.json
python -B scripts/validate_technical_spec.py --spec docs/technical-specs/<intent-id>.json --output docs/validation-reports/<intent-id>-technical-spec-validation.json
python -B scripts/schema_validator.py --kind technical-spec-validation-result --path docs/validation-reports/<intent-id>-technical-spec-validation.json
python -B scripts/schema_validator.py --kind technical-spec-derivation-result --path docs/technical-spec-results/<intent-id>.json
```

Do not proceed to `/derive-tasks` until the Technical Spec exists and validates.
