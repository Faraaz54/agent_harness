---
description: Run a read-only harness health check inspired by ADLC doctor: verifies install layout, required files, schemas, Python syntax, core tests, bootstrap, and project-pack configuration.
---

# /doctor

Apply `using-agent-skills` and `harness-doctor`.

Run:

```bash
python -B scripts/harness_doctor.py
```

Report every failed check with an exact copy-pasteable fix where possible. Do not mutate the repository.
