---
name: reflection
description: Performs post-implementation self-reflection before formal review, capturing assumptions, changed files, tests, risks, and potential issues without approving the task.
---

# Reflection

## Purpose

Force the builder to slow down before review and expose weak spots early.

## Required questions

- What was changed and why?
- What task contract criteria are covered?
- What RED/GREEN evidence exists?
- What files were read before write?
- What assumptions were made?
- What code might still be wrong?
- What tests are missing or weaker than ideal?
- What scope was deliberately not touched?
- What should reviewers inspect first?

## Output

Append the reflection to the implementation result or write `docs/reflections/<task-id>-attempt-<n>.json`.
