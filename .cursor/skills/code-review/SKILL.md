---
name: code-review
description: Performs structured engineering review for correctness, maintainability, security, operability, and contract fit. Use for principal-engineer review and pre-commit review.
---

# Code Review

## Purpose

Find defects and design risks that tests alone may miss. This is a review skill, not an implementation skill.

## Review procedure

1. Reconstruct the task contract and intended behaviour.
2. Inspect the diff, call sites, tests, and public interfaces.
3. Check correctness before style.
4. Check negative paths, error handling, idempotency, and edge cases.
5. Check maintainability and simplicity.
6. Check observability and operational failure modes where relevant.
7. Check security, dependency, and secret-handling risks.
8. Return structured findings with severity and required outcome.

## Severity

- BLOCKER: must not proceed.
- MAJOR: task not acceptable until fixed.
- MINOR: should fix if low-risk.
- NIT: optional polish, should not block.

## Review output

Each finding must include:

- location;
- severity;
- violated expectation or risk;
- concrete problem;
- required outcome;
- suggested test when applicable.

## Red flags

- Review comments focus only on style.
- Reviewer rewrites code instead of producing findings.
- Reviewer approves without checking tests.
- Reviewer ignores task non-goals.
- Reviewer suggests broad refactors unrelated to the task.
