---
description: Prepare run manifest, run state, and feature ledger from approved IDSD artifacts and task contracts.
---

Invoke `run-manifest-preparation`.

```bash
python -B scripts/prepare_run.py \
  --run-id <run-id> \
  --intent docs/intents/<intent-id>.md \
  --context docs/context/<intent-id>.json \
  --expectations docs/expectations/<intent-id>.json \
  --tasks docs/task-contracts/<intent-id>.json \
  --expectation-validation docs/validation-reports/<intent-id>-expectations-validation.md \
  --output tasks/run_manifest.draft.json \
  --state-output tasks/run_state.json \
  --feature-output tasks/feature_list.json
```

The draft manifest is not implementation authority until approved.
