# Agent Operating Contract — Harness v0.6.0

These instructions apply to all agents using this repository.

## Core rule

Do not rely on prose when deterministic scripts exist. Run the script, record the evidence, and update the run state.

## IDSD authority order

1. Approved run manifest.
2. Intent.
3. Expectations.
4. Context pack.
5. Task contracts.
6. Project-pack invariants.
7. Harness rules and skills.
8. Implementation choices.

## Required local build loop

```text
select task → implement → postflight → test review → principal review → domain review if required → validator → commit → evidence/report
```

## Safety requirements

- Read before writing.
- Touch only allowed paths.
- Do not edit approved Intent/Expectations/Task Contracts during implementation.
- Run scope guard and secret scan before commit.
- Validate structured result files against schemas.
- Surface uncertainty and stop on ambiguous contract issues.
- Use model routing from `harness.config.json`.
- Use the testing hierarchy declared in task contracts.

## Cloud boundary

Do not deploy, mutate Azure resources, submit Databricks jobs, or modify production systems from `/build-auto`. Use future `/goal-auto` or explicit environment authority.

## v0.6.3 context propagation rule

When a project pack has files under `project-packs/<project-name>/context/`, treat them as reusable project-specific context. `/assemble-context` must include them in `docs/context/<intent-id>.json`. `/derive-expectations` must carry them into `source_context`. `/derive-tasks` must assign relevant context IDs to each task through `required_context` and `context_files`. Implementation, review, domain review, and validation agents must consume the task context packet rather than re-discovering project context ad hoc.

## v0.6.4 Technical Spec rule

Major technical choices must be captured in `docs/technical-specs/<intent-id>.json` before task decomposition. `/derive-tasks` must use the validated Technical Spec and every task must include `technical_spec_refs`. Build, review, domain-review, and validation agents must treat referenced Technical Spec sections as binding context and must return structured findings if implementation would contradict them.
