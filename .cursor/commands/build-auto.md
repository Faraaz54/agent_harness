---
description: Start or resume an approved run and execute every eligible task through implementation, review, validation, governed commit, and local finalization.
---

# /build-auto

Use the `build-orchestration` skill. This command is an unattended orchestrator client, but it must still delegate all state decisions to scripts.

## Non-negotiable startup

Do **not** ask the operator to run `python -B scripts/build_orchestrator.py next` manually.

Start by running:

```bash
python -B scripts/build_auto.py
```

`build_auto.py` calls `build_orchestrator.py next` internally, creates the next action packet, validates it, and prints the exact action plus next steps. Treat that output as authoritative.

## Auto loop

Repeat this loop:

1. Run `python -B scripts/build_auto.py`.
2. Execute the returned action exactly.
3. If the action writes a structured result, record it:

```bash
python -B scripts/build_orchestrator.py record-result \
  --action-id <ACTION-ID> \
  --result <RESULT-PATH>
```

4. Continue until `FINALIZE_SESSION`, `COMPLETE`, `BLOCKED`, `REQUIRES_HUMAN_DECISION`, or a result validation failure.

The operator should not need to call `build_orchestrator.py next` directly during normal `/build-auto` execution.

## Action routing

- `RUN_PREFLIGHT` → `/start-run`; stop if it fails.
- `IMPLEMENT_TASK` → delegate context packet to `build-agent`.
- `REPAIR_TASK` → delegate repair/context packet to `build-agent`.
- `RUN_POSTFLIGHT` → `/postflight`; record `docs/postflight/<task-id>.json`.
- `RUN_REVIEW` with `test-agent` → `test-agent`.
- `RUN_REVIEW` with `principal-engineer-agent` → `principal-engineer-agent`.
- `RUN_DOMAIN_REVIEW` → `domain-reviewer-agent`.
- `RUN_VALIDATOR` → `validator-agent`.
- `COMMIT_TASK` → `/commit-task`; record `docs/commit-results/<task-id>.json`.
- `FINALIZE_SESSION` → `/finalize-session` only if local delivery should be completed now.
- `COMPLETE` → report final artifacts and stop.
- `BLOCKED` or `REQUIRES_HUMAN_DECISION` → checkpoint, report exact blocker, and stop.

Do not invent a new action. Do not skip `record-result` for actions that produce a result artifact.

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

Before starting, inspect `harness.config.json:model_routing`. This command should run under the `orchestration_large` alias. Every action returned by `scripts/build_auto.py` includes a `model_routing` block. Route the action to the configured alias/model and record any fallback in the result artifact.
