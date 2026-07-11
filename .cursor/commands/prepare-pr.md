---
description: Prepare an offline pull-request package from closed-run evidence without pushing or creating a remote PR.
---

Invoke `pull-request-delivery`.

Run when engineering closure and session reports exist:

```bash
python -B scripts/prepare_pr.py
```

This command must not push, create, merge, or mark a PR ready. It writes reviewable PR evidence under `docs/pull-requests/`.
