# Context Pack: simulated-local-pipeline

Created: `2026-07-13T02:59:20.129420+00:00`

## Active project pack

- Name: `invoice-governance`
- Path: `project-packs/invoice-governance`

## Project-pack context files

### CTX-INVOICE-GOVERNANCE-README — Invoice Governance Project Context

- Path: `project-packs/invoice-governance/context/README.md`
- Kind: `markdown`
- SHA-256: `b302c8d976ee2255e17fea18ecca1eff428d0bf5f3d54f2dcac6cb653b7aa324`

```
# Invoice Governance Project Context

This folder contains project-specific context for the invoice-governance harness pack. Files here are included in assembled Context Packs and should influence expectation derivation, epic/task decomposition, implementation, review, validation, and teach-me reporting.

```

### CTX-INVOICE-GOVERNANCE-INGESTION-CONTEXT — Ingestion Pipeline Project Context

- Path: `project-packs/invoice-governance/context/ingestion-context.md`
- Kind: `markdown`
- SHA-256: `7b6f9622919b5586cceb133106507e12e1a2130696d1a2150fe595b833bc3baf`

```
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

```
