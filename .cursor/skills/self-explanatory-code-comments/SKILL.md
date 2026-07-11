---
name: self-explanatory-code-comments
description: Guides when to write comments, docstrings, and explanatory notes so code remains readable without noise. Use when adding or reviewing comments and public APIs.
---

# Self-Explanatory Code Comments

## Principle

Prefer clear names and simple structure over comments that restate code. Use comments to explain why, invariants, trade-offs, domain meaning, and non-obvious constraints.

## Write comments for

- public APIs and expected contracts;
- business/domain rules not obvious from code;
- safety constraints;
- concurrency or retry assumptions;
- non-obvious performance trade-offs;
- workaround rationale with a removal condition;
- validation logic that mirrors external contracts.

## Avoid comments that

- repeat the next line;
- describe syntax;
- excuse confusing code;
- become stale because they narrate implementation details;
- include secrets, customer data, or environment-specific values.

## Python docstrings

Use docstrings for public modules, classes, and functions when the name and type hints are insufficient. Include parameters/returns only when they add meaning beyond type annotations.

## Verification

- [ ] Names and structure are clear without excessive comments.
- [ ] Comments explain why, not what.
- [ ] Public contracts are documented where useful.
- [ ] Comments are updated when behaviour changes.
