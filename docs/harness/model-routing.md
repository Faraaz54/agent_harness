# Model Routing

## Purpose

The harness separates orchestration, execution, review, validation, delivery and teaching roles. These roles do not require the same model. High-intelligence models should handle orchestration, ambiguity, hard trade-offs and final proof decisions. Cheaper or faster models can handle bounded implementation and deterministic delivery tasks.

The routing layer is provider-agnostic. `harness.config.json:model_routing` contains aliases such as `orchestration_large`, `execution_medium`, `review_reasoning`, `validation_reasoning` and `domain_reasoning`. Each alias maps to the concrete model identifier available in the active IDE or API workspace.

## Default routing

| Role | Default alias | Rationale |
|---|---|---|
| `/build-auto` | `orchestration_large` | Owns sequencing, ambiguity, repair classification and state transitions. |
| `/build-next` | `orchestration_large` | Same orchestration logic, smaller run scope. |
| `/build-status` | `execution_fast` | Deterministic status summarisation. |
| `build-agent` | `execution_medium` | Bounded coding inside one task. |
| `test-agent` | `review_reasoning` | Independent test and evidence critique. |
| `principal-engineer-agent` | `review_reasoning` | Architecture, maintainability and risk review. |
| `domain-reviewer-agent` | `domain_reasoning` | Project-pack semantic review. |
| `validator-agent` | `validation_reasoning` | Contract proof and evidence mapping. |
| `delivery-agent` | `execution_fast` | Governed commits and reports through deterministic scripts. |
| `teacher-agent` | `orchestration_large` | Human explanation and synthesis. |

## Independence policy

Implementation, review and validation should use independent model aliases when possible. This is not a guarantee of correctness, but it reduces correlated failure modes where the same model builds a flawed solution and then rationalises it as correct.

Configured independence checks warn when:

- builder and validator share an alias;
- builder and principal reviewer share an alias;
- builder and test reviewer share an alias.

For critical tasks, the harness can be configured to block non-independent review/validation rather than warn.

## Escalation policy

Escalate to `orchestration_large` for:

- critical-risk tasks;
- ambiguous or blocked states;
- second and later repair attempts;
- schema, data-loss, security or irreversible-state risk;
- human-decision synthesis.

## Fallback policy

Model names in `harness.config.json` are aliases, not universal truth. An IDE workspace may not expose every configured model. Fallback must be explicit:

- low-risk deterministic actions may warn and use IDE default;
- review/validation fallback should be surfaced in evidence;
- high-risk fallback requires human confirmation;
- production-impacting workflows must stop if a required model is unavailable.

## Commands

```bash
python -B scripts/model_router.py status
python -B scripts/model_router.py validate
python -B scripts/model_router.py role --name validator-agent
python -B scripts/model_router.py action --name RUN_VALIDATOR
```

Or use:

```text
/model-status
```

## Action packets

Every orchestrator action now includes a `model_routing` block. Example:

```json
{
  "action": "RUN_VALIDATOR",
  "task_id": "ING-014",
  "model_routing": {
    "alias": "validation_reasoning",
    "provider": "openai-or-ide-default",
    "model": "codex-or-equivalent-validation-model",
    "reasoning_effort": "high"
  }
}
```

The IDE or operator is responsible for mapping that alias to the actual model it can run.
