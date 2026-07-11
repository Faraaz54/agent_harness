---
description: Show the current build orchestration state, active task, blockers, configured project pack, and next predicted action without making changes.
---

# /build-status

Run:

```bash
python -B scripts/build_orchestrator.py status
```

Then summarize:

- run ID and branch;
- current stage;
- current task;
- completed/passed/blocked/deferred counts;
- active project pack;
- bootstrap freshness;
- latest action receipt;
- next eligible action;
- blockers or human decisions required.

Do not edit files.
