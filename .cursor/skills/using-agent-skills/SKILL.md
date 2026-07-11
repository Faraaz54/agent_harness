---
name: using-agent-skills
description: Selects and applies the smallest relevant set of skills for a task, preventing generic prompting and unused specialist guidance. Use at the start of every command, task, review, or repair cycle.
---

# Using Agent Skills

## Purpose

Ensure the agent deliberately activates the right skills instead of relying on a single broad instruction. The harness should be skill-routed, not vibes-routed.

## Required workflow

1. Identify the lifecycle stage: intent, context, expectations, task derivation, implementation, review, validation, commit, reporting, delivery, teaching.
2. Select only the skills that materially affect the next action.
3. Read each selected skill's trigger, constraints, red flags, and verification checklist.
4. State the selected skills in the action record or result artifact.
5. Do not invoke project-pack skills unless the configured project pack is active.
6. Do not use a domain skill as a substitute for generic test, engineering, or validator review.

## Skill routing baseline

| Stage | Required skills |
|---|---|
| Intent | `intent-capture` |
| Context | `context-assembly`, `environment-bootstrap` |
| Expectations | `expectation-derivation`, `expectation-validation` |
| Task derivation | `epic-task-decomposition` |
| Build | `red-green-vertical-slice`, `simple-python-implementation`, `testing-patterns` |
| Review | `code-review`, `gilfoyle-code-review` when high scepticism is needed |
| Python design | `simple-python-implementation`, `oop-design-patterns` only when OO is justified |
| Comments/docs | `self-explanatory-code-comments` |
| Containers | `docker-containerization` |
| CI/CD | `github-actions-ci-cd` |
| Azure IaC | `azure-naming`, `bicep-best-practices` |
| Commit | `verified-commit` |
| PR | `pull-request-delivery` |
| Session report | `session-reporting` |
| Teaching | `teach-me` |

## Red flags

- A command proceeds without naming any active skill.
- The agent uses every skill, creating context noise.
- A specialised skill is used outside its domain.
- A reviewer uses implementation skills to modify code.
- The builder sees validator-only hidden checks.

## Verification

- [ ] Skill selection is recorded.
- [ ] Selected skills match the lifecycle stage.
- [ ] Domain skills match the active project pack.
- [ ] No irrelevant high-token skill was loaded.
