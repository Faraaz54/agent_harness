# Build-next / build-auto hardening — v0.6.5

## Problem fixed

Earlier command guidance required the operator to discover the next orchestrator action manually with:

```bash
python -B scripts/build_orchestrator.py next
```

That made `/build-next` and `/build-auto` too shallow. The command should own next-action discovery.

## New rule

Operators should start from:

```bash
python -B scripts/build_next.py
```

or:

```bash
python -B scripts/build_auto.py
```

These driver scripts call the orchestrator internally, validate the generated action packet, and return exact execution instructions.

## Build-next boundary

`/build-next` stops after the first durable boundary:

- one task committed and recorded;
- blocker;
- human decision required;
- no eligible task;
- finalization would be next;
- validation failure.

It must not start a second task.

## Build-auto boundary

`/build-auto` repeats driver discovery and action execution until terminal or blocking state.

## First-class deterministic result recording

`RUN_POSTFLIGHT` and `COMMIT_TASK` now have schemas and can be recorded by the orchestrator:

- `schemas/postflight-result.schema.json`
- `schemas/commit-result.schema.json`

Postflight now writes:

```text
docs/postflight/<task-id>.json
```

so it can be recorded with:

```bash
python -B scripts/build_orchestrator.py record-result \
  --action-id <ACTION-ID> \
  --result docs/postflight/<task-id>.json
```

## Operator impact

After preflight, do not run `build_orchestrator.py next` manually during normal operation. Use `/build-next` or `/build-auto`, which must call the driver first.
