---
name: lesson-memory
description: Maintains relevance-ranked lessons and repair memory so agents do not repeat mistakes across tasks or sessions.
---

# Lesson Memory

## Purpose

Convert repeated defects into durable prevention rules without bloating global prompts.

## Read policy

Before implementation, repair, or review, load lessons relevant to touched components. Prefer component/domain/tag matches over recency. Cap loaded lessons to avoid context bloat.

## Write policy

Create or update a lesson when:

- the same finding appears more than once;
- a repair was non-obvious;
- a hidden assumption caused failure;
- a domain invariant was missed;
- an environment/tooling issue changed the correct command.

## Lesson format

Each lesson should include:

- id;
- domain/component/tags;
- symptom;
- root cause;
- prevention rule;
- example task;
- date observed.
