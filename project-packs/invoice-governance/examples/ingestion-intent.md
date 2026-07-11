# Intent: Local Contractor Ingestion Pipeline

## Goal

Build a local ingestion pipeline that loads approved contractor activity source files into traceable bronze and silver tables.

## Constraints

- Preserve row-level source lineage for accepted and rejected records.
- Support deterministic reruns without duplicate canonical records.
- Keep implementation portable between local execution and cloud orchestration.
- Use simple, idiomatic Python with explicit data contracts.
- Ambiguous reconciliation must be classified, not guessed.

## Failure Conditions

- A silver row cannot be traced to a bronze/source row.
- A duplicate rerun creates duplicate canonical records.
- A required source type is silently skipped.
- An invalid source row is accepted without classification.
- A worker or work-order attribution is made without sufficient evidence.

## Explicit Non-Goals

- No Databricks job execution in this intent.
- No production Azure deployment.
- No invoice-estimation rule engine.
