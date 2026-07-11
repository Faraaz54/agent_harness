---
name: pull-request-delivery
description: Prepares and optionally creates a traceable draft pull request from closed-run evidence. Use after engineering closure and final report generation.
---

# Pull Request Delivery

## Purpose

Create a reviewable PR package that explains what changed, why, what was validated, what risks remain, and how to roll back.

## Required PR body sections

1. Summary
2. Why
3. Scope
4. Task and commit traceability
5. Validation
6. Review outcomes
7. Residual risks and deferred work
8. Rollback
9. Operational notes
10. Learning and audit evidence
11. Explicit non-goals

## Rules

- Prepare PR evidence offline before remote mutation.
- Draft by default.
- No merge, auto-merge, deployment, or CI-success claim.
- Push and PR creation require explicit delivery authority.
- Update an existing PR for the same head branch instead of creating duplicates.

## Verification

- [ ] PR metadata matches current branch and run.
- [ ] Task-to-commit traceability is complete.
- [ ] Reports are linked.
- [ ] Risks and rollback are explicit.
- [ ] Remote action is authorized.
