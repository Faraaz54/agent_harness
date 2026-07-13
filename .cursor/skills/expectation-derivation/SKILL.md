---
name: expectation-derivation
description: Derives done/fail boundary and hierarchical testing expectations from Intent and Context as human-reviewable Expectations.
---

# Expectation Derivation

Generate Expectations from approved Intent and assembled Context.

Expectations must cite the assembled Context Pack and project-pack context files used to derive the expectations. Use `source_context.context_pack_path` and `source_context.project_context_files[]`.

Expectations must include:

- success scenarios;
- failure scenarios;
- acceptance criteria;
- validation strategy;
- review requirements;
- explicit non-goals and stop conditions;
- hidden/private eval boundary;
- **Testing Expectations Matrix** covering unit, integration, local E2E, and cloud E2E.

## Testing Expectations Matrix rules

For every meaningful behaviour, risk, or acceptance criterion, state what must be proven at each tier:

- `unit`: isolated logic such as parsing, mapping, validation, normalization, business rules.
- `integration`: local boundaries such as database, filesystem, schema, adapters, queues, APIs, local orchestration.
- `local_e2e`: full local pipeline or workflow from realistic fixture input to validated output.
- `cloud_e2e`: deployed Azure/Databricks/cloud runtime proof; only required under explicit environment or goal authority.

A tier may be marked not required, but it must include a reason. Do not silently omit a tier.

## Builder/validator separation

Keep private validator-only checks separate from builder-visible summaries. The builder may receive the testing intent and required tiers, but exact hidden eval queries can remain validator-only.
