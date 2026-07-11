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
