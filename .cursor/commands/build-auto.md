---
description: Start or resume an approved run and execute every eligible task through implementation, review, validation, governed commit, and local finalization.
---

# /build-auto

Use the `build-orchestration` skill. The command is intentionally a thin orchestrator client, but it must not be shallow in behaviour: it delegates all state decisions to `scripts/build_orchestrator.py` and all work to the proper specialist agents/commands.

## Required startup

1. Read `AGENTS.md`, `harness.config.json`, `docs/bootstrap/environment.md`, `tasks/run_manifest.json`, `tasks/run_state.json`, `tasks/feature_list.json`, and the active project pack summary.
2. Apply `using-agent-skills` and record selected skills in each result artifact.
3. Run:

```bash
python -B scripts/build_orchestrator.py status
```

4. If status is not terminal, run:

```bash
python -B scripts/build_orchestrator.py next
```

## Execute the returned action exactly

Route actions as follows:

- `REFRESH_BOOTSTRAP` → `/bootstrap-environment`
- `RUN_PREFLIGHT` → `/start-run`
- `IMPLEMENT_TASK` → delegate context packet to `build-agent`
- `REPAIR_TASK` → delegate repair packet to `build-agent`
- `RUN_POSTFLIGHT` → `/postflight`
- `RUN_REVIEW` with `test-agent` → `test-agent`
- `RUN_REVIEW` with `principal-engineer-agent` → `principal-engineer-agent`
- `RUN_DOMAIN_REVIEW` → `domain-reviewer-agent`
- `RUN_VALIDATOR` → `validator-agent`
- `COMMIT_TASK` → `/commit-task`
- `FINALIZE_SESSION` → `/finalize-session`
- `COMPLETE` → report final artifacts and stop
- `BLOCKED` or `REQUIRES_HUMAN_DECISION` → checkpoint, report exact blocker, and stop

Do not invent a new action. Do not skip `record-result`.

## Record every result

After an agent or command writes its structured result:

```bash
python -B scripts/build_orchestrator.py record-result \
  --action-id <ACTION-ID> \
  --result <RESULT-PATH>
```

The conversation is not evidence. Only recorded artifacts are evidence.

## Repair policy

When reviews or validation require changes:

1. Consolidate findings into the orchestrator-provided repair context.
2. Do not fix one finding at a time when the repair packet contains several related findings.
3. After repair, prior postflight/reviews/validator results are stale.
4. Stop when repair budget is exhausted.

## Progress updates

Report only meaningful boundaries:

- run resumed/started;
- task selected;
- implementation completed;
- review requires repair;
- task committed;
- blocker/human decision required;
- local delivery complete.

## Completion

Normal unattended completion is:

```text
LOCAL_DELIVERY_COMPLETE
LEARNING_PENDING
```

Do not push, create PR, merge, deploy, or start `/teach-me` unless explicitly instructed and authorised.

## Model routing

Before starting, inspect `harness.config.json:model_routing`. This command should run under the `orchestration_large` alias. Every action returned by `scripts/build_orchestrator.py next` includes a `model_routing` block. Route the action to the configured alias/model and record any fallback in the result artifact.

Run when needed:

```bash
python -B scripts/model_router.py action --name <ACTION>
```
