---
description: Prepare run manifest, run state, and feature ledger from approved IDSD artifacts, Technical Spec, and task contracts.
---

Invoke `run-manifest-preparation` only after Intent, Context, Expectations, Technical Spec, and Task Contracts are all validated.

```bash
python -B scripts/prepare_run.py \
  --run-id <run-id> \
  --intent docs/intents/<intent-id>.md \
  --context docs/context/<intent-id>.json \
  --expectations docs/expectations/<intent-id>.json \
  --technical-spec docs/technical-specs/<intent-id>.json \
  --technical-spec-validation docs/validation-reports/<intent-id>-technical-spec-validation.json \
  --tasks docs/task-contracts/<intent-id>.json \
  --expectation-validation docs/validation-reports/<intent-id>-expectations-validation.json \
  --task-validation docs/validation-reports/<intent-id>-task-contract-validation.json \
  --output tasks/run_manifest.json \
  --state-output tasks/run_state.json \
  --feature-output tasks/feature_list.json
```

The draft manifest is not implementation authority until approved.
