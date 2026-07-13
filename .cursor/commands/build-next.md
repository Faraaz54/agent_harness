---
description: Execute at most one eligible task through implementation, review, validation, and governed commit, then stop at a durable checkpoint.
---

# /build-next

Use `build-orchestration`. This is the proving mode for a new project or newly installed harness.

## Non-negotiable startup

Do **not** ask the operator to run `python -B scripts/build_orchestrator.py next` manually.

Start by running:

```bash
python -B scripts/build_next.py
```

`build_next.py` calls the orchestrator internally, creates the next action packet, validates it, and prints the exact action plus next steps. Treat that output as authoritative.

## Boundary policy

`/build-next` executes until the first durable boundary:

- one `COMMIT_TASK` action records successfully;
- `BLOCKED`;
- `REQUIRES_HUMAN_DECISION`;
- no eligible task exists;
- `FINALIZE_SESSION` would be next;
- a command/agent result fails validation.

Do not start a second task in the same `/build-next` invocation.

## Execution loop inside one task

After `python -B scripts/build_next.py` returns an action:

1. Execute the returned action exactly.
2. If the action writes a structured result, record it:

```bash
python -B scripts/build_orchestrator.py record-result \
  --action-id <ACTION-ID> \
  --result <RESULT-PATH>
```

3. Run `python -B scripts/build_next.py` again to discover the next action for the same task.
4. Continue only until the durable boundary above.

The operator should not need to call `build_orchestrator.py next` directly.

## Action routing

- `RUN_PREFLIGHT` → run the command shown by the action, then stop.
- `IMPLEMENT_TASK` → delegate context packet to `build-agent`.
- `REPAIR_TASK` → delegate repair/context packet to `build-agent`.
- `RUN_POSTFLIGHT` → run the command shown by the action; it writes `docs/postflight/<task-id>.json`; record that result.
- `RUN_REVIEW` with `test-agent` → delegate to `test-agent`.
- `RUN_REVIEW` with `principal-engineer-agent` → delegate to `principal-engineer-agent`.
- `RUN_DOMAIN_REVIEW` → delegate to `domain-reviewer-agent`.
- `RUN_VALIDATOR` → delegate to `validator-agent`.
- `COMMIT_TASK` → run the command shown by the action; record `docs/commit-results/<task-id>.json`; then stop.
- `FINALIZE_SESSION` → report that no task remains and stop. Do not finalize unless explicitly instructed.
- `BLOCKED` / `REQUIRES_HUMAN_DECISION` → report exact blocker and stop.

## Status summary

Always end with:

```bash
python -B scripts/build_orchestrator.py status
```

Summarize:

- run ID;
- task handled;
- actions completed;
- evidence/result files;
- current next action or blocker;
- whether it is safe to run `/build-next` again.
