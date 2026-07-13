# Ingestion Pipeline Project Context

The ingestion pipeline ingests contractor governance sources into traceable bronze/silver outputs. Runtime implementation must preserve source lineage, classify invalid or ambiguous records, support deterministic reruns, and keep build-auto local unless explicit cloud authority is granted.

Important source concepts:

- SAP work orders provide work-order and approval context.
- Vendor invoices and rate cards may use vendor IDs.
- Work orders may use vendor names, requiring vendor-master reconciliation.
- DSX gate events support attendance evidence but must not be attributed to the wrong work order.

Implementation implications:

- Raw/source metadata must be retained before normalization.
- Accepted and rejected rows both need source lineage.
- Ambiguous reconciliation must be classified, not guessed.
- Local tests should use fixtures/mocks rather than live Azure or Databricks calls.
