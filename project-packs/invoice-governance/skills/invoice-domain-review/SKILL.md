---
name: invoice-domain-review
description: Domain review for contractor invoice governance, ingestion, reconciliation, attendance attribution and billing evidence.
---

# Invoice Domain Review

## Purpose

Determine whether the implementation preserves invoice-governance domain meaning. This does not replace tests, principal engineering review, or validator proof.

## Invariants

- Accepted canonical records retain source lineage.
- Rejected records retain source lineage and reason codes.
- Ambiguous vendor, worker, work order, contract or site matches are not silently accepted.
- Attendance attribution is not based only on timestamp overlap.
- Idempotent reruns do not duplicate canonical records.
- Late-arriving source files do not corrupt previously accepted outputs.
- Manual overrides are auditable.
- Truth/evaluation files are not production dependencies.
- Monetary calculations use explicit decimal/rounding semantics.

## Procedure

1. Reconstruct the domain behaviour requested by the task.
2. Identify affected domain entities.
3. Inspect code paths that parse, validate, reconcile, persist, calculate or publish those entities.
4. Compare against Intent, Expectations, task contract and project-pack invariants.
5. Check failure paths and ambiguity handling.
6. Produce structured review result.

## Verdicts

- PASS
- CHANGES_REQUIRED
- BLOCKED_BY_AMBIGUITY
- BLOCKED_BY_MISSING_CONTEXT

## Required structured output

The domain reviewer must write `docs/reviews/<task-id>/domain-review.json` and the file must validate against:

```text
project-packs/invoice-governance/schemas/domain-review-result.schema.json
```

The result must include:

- `schema_version`
- `review_type`
- `reviewer`
- `project_pack`
- `domain_skill`
- `task_id`
- `attempt`
- `verdict`
- `domain_entities_reviewed`
- `invariants`
- `findings`
- `repair_guidance`
- `model_routing`

Never return prose-only domain review. Findings must include severity, evidence, required outcome and whether they block completion.
