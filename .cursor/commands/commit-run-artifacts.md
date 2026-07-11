---
description: Commit final governance/report artifacts after run closure, session reports, and offline PR preparation.
---

Invoke `pull-request-delivery` and `verified-commit`.

```bash
python -B scripts/commit_run_artifacts.py
```

This command stages only configured governance/report paths. It must not include production-code changes.
