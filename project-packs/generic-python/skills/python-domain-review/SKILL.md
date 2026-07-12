---
name: python-domain-review
description: Reviews generic Python implementation against task intent, API expectations, simplicity and maintainability.
---

# Generic Python Review

Check:

- public API matches expectation;
- implementation is simple and idiomatic;
- no speculative abstraction;
- no unnecessary dependency;
- errors are explicit;
- tests cover acceptance and negative cases;
- type boundaries are clear where useful.

## Required structured output

The domain reviewer must write `docs/reviews/<task-id>/domain-review.json` and the file must validate against:

```text
project-packs/generic-python/schemas/domain-review-result.schema.json
```

Never return prose-only review. Findings must be structured with severity, evidence, required outcome and completion impact.
