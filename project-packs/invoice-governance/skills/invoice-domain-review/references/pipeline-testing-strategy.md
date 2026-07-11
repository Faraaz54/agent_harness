# Invoice Governance Pipeline Testing Strategy

Use this project-pack testing layer for ingestion, rule extraction, reconciliation, invoice estimation, and validation pipelines.

## Required tiers

- Unit tests for parsers, normalizers, rule functions, validation functions, matching functions, and amount calculations.
- Integration tests for filesystem inputs, database writes, schema contracts, batch metadata, lineage joins, and rejection tables.
- Local E2E tests for source-to-bronze-to-silver/gold pipeline paths using synthetic fixtures.
- Cloud E2E tests for Databricks/Azure only under explicit environment authority.

## Domain-specific pipeline checks

- Source row count reconciliation.
- Bronze-to-silver/gold lineage preservation.
- Idempotent rerun behaviour.
- Vendor reconciliation ambiguity handling.
- Attendance attribution safety.
- Late-arriving source handling.
- Rejection classification for malformed/invalid rows.
- Truth/evaluation files excluded from production runtime paths.

## Cloud E2E minimum evidence

- Git SHA or artifact digest deployed.
- Databricks job ID and run ID.
- Cluster/runtime identifier.
- Input dataset identity.
- Job terminal status.
- Output table/schema checks.
- Validation query results.
- Logs or log artifact references.
- Cleanup/retention decision.


## IDSD testing expectations

Invoice-governance IDSD Expectations must include a Testing Expectations Matrix. Each generated task contract must include `test_expectations` for unit, integration, local E2E, and cloud E2E.

For ingestion/reconciliation tasks, local E2E is normally required before closure unless the task is deliberately isolated and the exception is justified. Cloud E2E should be marked not required unless an approved Azure/Databricks environment-verification authority exists.
