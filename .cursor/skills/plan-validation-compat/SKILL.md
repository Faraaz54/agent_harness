---
name: plan-validation-compat
description: Backward-compatible skill for validating legacy plans before converting them into IDSD Expectations and task contracts. Use when the handoff package contains a plan rather than an IDSD Intent.
---

# Plan Validation Compatibility

## Purpose

Audit legacy plans for clarity, boundedness, testability and contradictions before converting to IDSD artifacts.

## Checks

- Goal is singular and observable.
- Constraints are explicit.
- Failure conditions are present.
- Non-goals are present.
- Tasks are vertical slices, not layers.
- Tests and validation commands can prove outcomes.
- Dependencies are valid.
- Ambiguities are recorded for human decision.

## Output

A validation report should recommend one of:

- PASS_CONVERT_TO_IDSD
- PASS_WITH_WARNINGS
- FAIL_REPAIR_PLAN
