# Intent: Simulated Local Pipeline

## Goal

Build a local pipeline that reads fixture source rows and produces validated output records.

## Constraints

- Preserve source lineage.
- Support deterministic idempotent reruns.
- Keep implementation local; no cloud mutation.

## Failure Conditions

- Accepted output lacks source lineage.
- Duplicate rerun creates duplicate output.
- Invalid rows are silently dropped.
