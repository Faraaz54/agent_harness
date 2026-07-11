---
description: Human-only command to authorize time-limited remote push and draft pull-request creation.
---

This is a human approval boundary. Agents must not invoke it for themselves.

```bash
python -B scripts/approve_delivery.py --approved-by <HUMAN-NAME>
```

The approval is bound to the current run, branch, and manifest hash and should be stored outside normal implementation commits.
