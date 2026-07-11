# Invoice Governance Domain Invariants

- Row-level lineage is mandatory for accepted and rejected records.
- Vendor name/ID reconciliation must be deterministic and explainable.
- Gate/attendance data must not be attributed across workers or work orders without explicit evidence.
- Ambiguity is quarantined, not guessed.
- Reruns must be idempotent.
- Evaluation truth files must never become runtime dependencies.
