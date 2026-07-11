# Testing Expectations in IDSD

v0.5.6 requires hierarchical testing expectations to be generated as part of IDSD artifact creation.

## Why

Pipeline projects can pass unit tests while failing at schema, persistence, orchestration, idempotency, or deployed runtime boundaries. Testing tiers must therefore be declared before implementation and reviewed after implementation.

## Artifact placement

| Artifact | Responsibility |
|---|---|
| Intent | Outcome, constraints, and failure conditions. It may mention testable failure conditions, but should not become a test plan. |
| Context | Available tools, local/cloud environment, repo conventions, fixtures, databases, project-pack rules. |
| Expectations | Human-readable Testing Expectations Matrix. |
| Task Contracts | Machine-readable `test_expectations` per task. |
| Test Agent Review | Verifies whether the implementation produced evidence for the required tiers. |
| Teach-Me Report | Explains which tiers were required, which were satisfied, and what remains unproven. |

## Required matrix

Every Expectations document should include:

| Behaviour / Risk | Unit | Integration | Local E2E | Cloud E2E |
|---|---|---|---|---|
| Behaviour or risk to prove | What to test, or not required reason | What to test, or not required reason | What to test, or not required reason | What to test, or not required reason |

## Required task-contract object

Each task must include:

```json
{
  "test_expectations": {
    "highest_required_tier": "local_e2e",
    "tier_rationale": "This task changes stateful pipeline persistence and must be proven from fixture input to validated output.",
    "unit": {
      "required": true,
      "what_to_test": ["parser validation", "lineage key construction"],
      "evidence_required": ["focused RED/GREEN unit tests"]
    },
    "integration": {
      "required": true,
      "what_to_test": ["bronze insert into local database"],
      "evidence_required": ["local DB integration test output"]
    },
    "local_e2e": {
      "required": true,
      "what_to_test": ["fixture landing directory to validated bronze/silver outputs"],
      "evidence_required": ["local E2E command output", "row-count and lineage assertions"]
    },
    "cloud_e2e": {
      "required": false,
      "what_to_test": [],
      "evidence_required": [],
      "not_required_reason": "Cloud verification is reserved for goal-auto or explicit environment authority."
    },
    "coverage_map": [
      {
        "criterion": "Silver rows retain source lineage.",
        "tiers": ["unit", "integration", "local_e2e"]
      }
    ]
  }
}
```

## Validation rule

A tier may be explicitly not required. A tier may not be omitted silently.

Run:

```bash
python -B scripts/test_strategy.py validate-contracts --contracts docs/task-contracts/<intent-id>.json
```
