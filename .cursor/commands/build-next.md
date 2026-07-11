---
description: Execute at most one eligible task through implementation, review, validation, and governed commit, then stop.
---

# /build-next

Use `build-orchestration`. This is the proving mode for a new project or newly installed harness.

Follow `/build-auto` routing, but stop after one of these boundaries:

- one `COMMIT_TASK` action records successfully;
- `BLOCKED`;
- `REQUIRES_HUMAN_DECISION`;
- no eligible task exists;
- `FINALIZE_SESSION` would be next.

Always produce a status summary:

- run ID;
- selected task;
- actions completed;
- evidence files;
- current next action;
- whether it is safe to run `/build-next` again.
