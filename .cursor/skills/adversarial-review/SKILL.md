---
name: adversarial-review
description: Read-only adversarial review of a plan, expectation set, task contract, diff, report, or PR body. Assumes the artifact is incomplete or misleading until proven otherwise.
---

# Adversarial Review

## Purpose

Find omissions, contradictions, reward-hacking paths, missing constraints, false success claims, and unsafe assumptions.

## Method

1. Identify the artifact's claimed purpose.
2. Try to falsify each claim using source-of-truth precedence.
3. Look for missing edge cases, hidden dependencies, ambiguous ownership, hidden implementation choices, and untestable success criteria.
4. Self-refute each suspected issue; report only findings that survive.
5. Categorize findings by BLOCKER/MAJOR/MINOR/NIT.

## Special focus for IDSD

- Is the Intent actually one outcome, or several goals joined by “and”?
- Are constraints business qualities rather than implementation choices?
- Are failure conditions observable and binary?
- Are success scenarios in Expectations rather than Intent?
- Did Context become a dumping ground for new requirements?
- Are hidden/private evals protected from the builder?

## Output

Structured findings with exact artifact section, problem, impact, and required correction.
