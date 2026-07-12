# Agent Output Contracts

The harness treats agent outputs as machine-consumed evidence, not prose. Any agent result that feeds later automation must be emitted as structured JSON and validated before it can change run state.

## Contracted outputs

| Agent/action | Output path | Schema |
|---|---|---|
| build-agent / IMPLEMENT_TASK | `docs/implementation-results/<task-id>-attempt-<n>.json` | `schemas/implementation-result.schema.json` |
| build-agent / REPAIR_TASK | `docs/implementation-results/<task-id>-repair-<n>.json` | `schemas/implementation-result.schema.json` |
| test-agent / RUN_REVIEW | `docs/reviews/<task-id>/test-agent.json` | `schemas/review-result.schema.json` |
| principal-engineer-agent / RUN_REVIEW | `docs/reviews/<task-id>/principal-engineer-agent.json` | `schemas/review-result.schema.json` |
| domain-reviewer-agent / RUN_DOMAIN_REVIEW | `docs/reviews/<task-id>/domain-review.json` | `schemas/domain-review-result.schema.json` or active project-pack schema |
| validator-agent / RUN_VALIDATOR | `docs/validation-results/<task-id>-validator.json` | `schemas/task-validation.schema.json` |

## Validation commands

Validate a result directly:

```bash
python -B scripts/agent_result_contracts.py validate \
  --kind review \
  --path docs/reviews/TASK-001/test-agent.json \
  --task-id TASK-001 \
  --agent test-agent
```

Validate a result against an orchestrator action:

```bash
python -B scripts/agent_result_contracts.py validate-action \
  --action .git/agent-harness/runs/<run-id>/actions/<action-id>.json \
  --result docs/reviews/TASK-001/test-agent.json
```

The orchestrator also validates contracted outputs during `record-result`. Malformed results are rejected before task state changes.

## Non-negotiable rules

- Do not use prose-only result files for implementation, review, domain review or validation.
- Do not omit empty arrays. Use `[]`.
- Do not invent verdict values.
- Every finding must have an ID, severity, evidence and required outcome.
- The result `task_id` must match the orchestrator action `task_id`.
- The result agent field must match the action `required_agent` when provided.

## Why this exists

Later agents rely on upstream evidence. If the test reviewer, domain reviewer or validator emits unstructured prose, the orchestrator cannot safely distinguish pass, repair, block, missing evidence or ambiguity. Structured outputs make the handoff deterministic.
