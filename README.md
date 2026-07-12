# Cursor Engineering Harness v0.6.0

Reusable IDSD-first engineering harness for agentic development in Cursor/VS Code-style repositories.

This package includes:

- IDSD artifacts: Intent, Context, Expectations and Task Contracts.
- Build-auto orchestration.
- Model routing.
- Test hierarchy: unit, integration, local E2E, cloud E2E declaration.
- Domain-review project packs.
- Teach-me HTML/Markdown/JSON reports.
- v0.6.0 hardening: schema validation, scope guard, secret scan, evidence ledger, recovery commands, project-pack validation, install verification and operator manual.

## Start here

Read the operator manual:

```text
docs/operator-manual/README.md
```

Then run:

```bash
python -B scripts/verify_installation.py
python -B scripts/validate_harness.py .
python -B scripts/harness_doctor.py
python -B scripts/model_router.py validate
python -B scripts/test_strategy.py validate
```

## Important boundaries

`/build-auto` is for local implementation quality, tests, review, validation and commits. It does not deploy to Azure or submit Databricks jobs. Cloud execution belongs to the future `/goal-auto` loop.

## Project packs

Included:

- `project-packs/generic-python`
- `project-packs/invoice-governance`

Validate or activate:

```bash
python -B scripts/project_pack.py validate --pack project-packs/invoice-governance
python -B scripts/project_pack.py activate --name invoice-governance
```

## v0.6.1 structured agent outputs

v0.6.1 requires implementation, review, domain review and validation agents to emit structured JSON. These files are validated before orchestrator state transitions.

See:

- `docs/harness/agent-output-contracts.md`
- `schemas/implementation-result.schema.json`
- `schemas/review-result.schema.json`
- `schemas/domain-review-result.schema.json`
- `schemas/task-validation.schema.json`
- `scripts/agent_result_contracts.py`


## v0.6.2 planning enforcement

Adds schema-enforced expectation derivation/validation, epic-based task decomposition, task-contract validation, and a simulated pipeline planning workflow.
