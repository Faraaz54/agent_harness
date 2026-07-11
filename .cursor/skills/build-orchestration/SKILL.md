---
name: build-orchestration
description: Drives an approved IDSD run by delegating deterministic state transitions to the build orchestrator, routing actions to specialist agents/commands, and recording structured evidence.
---

# Build Orchestration

## Purpose

Coordinate the approved implementation loop. Do not implement, review, validate, or commit directly. The orchestrator owns state; specialist agents own lifecycle work.

## Required inputs

- `AGENTS.md`
- `harness.config.json`
- `docs/bootstrap/environment.md`
- approved Intent, Context, Expectations, and task contracts
- `tasks/run_manifest.json`
- `tasks/run_state.json`
- `tasks/feature_list.json`
- active project-pack README and public review criteria when configured

## Method

1. Run `python -B scripts/build_orchestrator.py status`.
2. If no approved run exists, stop.
3. If bootstrap is stale, route `REFRESH_BOOTSTRAP`.
4. Ask the deterministic controller for the next action.
5. Execute exactly that action with the specified agent/command.
6. Require a structured result artifact for every agent action.
7. Record the result using `record-result`.
8. Repeat until terminal.

## Action routing

| Action | Route |
|---|---|
| `REFRESH_BOOTSTRAP` | `/bootstrap-environment` |
| `RUN_PREFLIGHT` | `/start-run` |
| `IMPLEMENT_TASK` | `build-agent` |
| `REPAIR_TASK` | `build-agent` with repair packet |
| `RUN_POSTFLIGHT` | `/postflight` |
| `RUN_REVIEW:test-agent` | `test-agent` |
| `RUN_REVIEW:principal-engineer-agent` | `principal-engineer-agent` |
| `RUN_DOMAIN_REVIEW` | `domain-reviewer-agent` |
| `RUN_VALIDATOR` | `validator-agent` |
| `COMMIT_TASK` | `/commit-task` |
| `FINALIZE_SESSION` | `/finalize-session` |
| `COMPLETE` | stop and summarize |

## State discipline

- Conversation text is never durable state.
- Do not update task status manually unless a controller command explicitly asks for that artifact.
- Every action receives an action ID.
- Every action result must reference the same run ID, task ID, and attempt.
- Do not continue from an action whose result failed schema or consistency checks.

## Repair discipline

- Classify failure before repair.
- Consolidate findings across test/principal/domain/validator gates.
- After repair, previous postflight, review, and validator evidence is stale.
- Stop when the repair budget is exhausted.
- Update repair memory for repeated defects.

## Stop conditions

- missing required artifact;
- project-pack config cannot be loaded;
- required reviewer unavailable;
- manifest/source hash mismatch;
- task contract conflict;
- private eval requested by builder;
- repair budget exhausted;
- branch/worktree/preflight failure;
- command would require remote/prod authority not present.

## Verification

- [ ] Every action came from `build_orchestrator.py next`.
- [ ] Every agent used appropriate skills.
- [ ] Every result was recorded.
- [ ] No role self-approved.
- [ ] Build progressed only through durable evidence.


## Model routing

The orchestrator must select the model alias from `harness.config.json:model_routing` for every action. `/build-auto` itself should use `orchestration_large`. Implementation actions should use `execution_medium` unless risk/escalation policy says otherwise. Test and principal review should use `review_reasoning`; validator should use `validation_reasoning`; domain review should use `domain_reasoning`.

Every action packet must include `model_routing` with alias/provider/model/reasoning metadata. Every structured result should record the actual model used and any fallback.

Do not silently downgrade validation/review on high-risk tasks. Prefer independent model aliases for build, review and validation.
