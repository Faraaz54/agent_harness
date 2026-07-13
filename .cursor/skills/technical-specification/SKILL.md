# Technical Specification Skill

Use this skill when deriving or validating the IDSD Technical Spec.

## Purpose

Translate approved Intent, assembled Context, validated Expectations, and project-pack context into concrete technical requirements that can safely drive task decomposition and implementation.

## Technical Spec responsibilities

The Technical Spec captures **how** the project will be built. It must include:

- architecture style and runtime targets;
- dependency and library decisions;
- module boundaries;
- source/data flow;
- persistence and data contracts where relevant;
- configuration and secret-handling policy;
- error, rejection, retry, and idempotency behaviour;
- observability/logging expectations;
- testing implications for unit, integration, local E2E, and cloud E2E;
- explicit deferred items and non-decisions.

## Boundary

- Intent owns outcome and constraints.
- Expectations own done/fail criteria.
- Technical Spec owns implementation design decisions.
- Task contracts slice the Technical Spec into implementable vertical tasks.

## Validation standard

A Technical Spec is not ready if:

- required libraries are listed without rationale;
- module boundaries are vague;
- pipeline lineage/idempotency/rejection handling are missing;
- it conflicts with project-pack context;
- it authorizes cloud mutation without explicit authority;
- testing implications omit any hierarchy tier;
- deferred items are implicit.
