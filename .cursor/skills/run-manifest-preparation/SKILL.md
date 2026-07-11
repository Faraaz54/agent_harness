---
name: run-manifest-preparation
description: Freezes approved IDSD inputs and task contracts into a run manifest, state ledger, and feature ledger. Use before build-auto starts.
---

# Run Manifest Preparation

## Purpose

Convert approved Intent, Context, Expectations and task contracts into immutable run authority. The manifest decides what the build loop may implement.

## Inputs

- approved intent;
- context pack;
- approved expectations;
- task contracts;
- expectation validation report;
- harness configuration.

## Outputs

```text
tasks/run_manifest.draft.json
tasks/run_manifest.json
tasks/run_state.json
tasks/feature_list.json
```

## Rules

- Draft manifests are not implementation authority.
- Approved manifests must hash source artifacts.
- Build-auto must not implement outside the approved task IDs.
- Manifest changes require a new approval or amendment.

## Verification

- [ ] Source hashes exist.
- [ ] Task IDs are unique.
- [ ] Dependencies are valid.
- [ ] Retry and delivery policy are explicit.
- [ ] Human approval is recorded.
