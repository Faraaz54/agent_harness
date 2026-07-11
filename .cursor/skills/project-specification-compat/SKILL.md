---
name: project-specification-compat
description: Backward-compatible skill for converting older plan/spec documents into IDSD Intent, Context seed, Expectations, and task contracts. Use when a project starts from a traditional specification instead of IDSD artifacts.
---

# Project Specification Compatibility

## Purpose

Do not discard useful existing plan/spec work. Convert it into the v0.5 IDSD artifact model.

## Conversion

- Goals and narrative become `docs/intents/<id>.md`.
- Architecture and repository facts become context seed material.
- Acceptance criteria and done conditions become expectations.
- Feature lists become task contracts.
- Risks and constraints are preserved explicitly.

## Rules

- Do not treat the old spec as implementation authority after conversion.
- Preserve non-goals and failure modes.
- Flag contradictions instead of resolving them silently.
- Require expectation validation before implementation.
