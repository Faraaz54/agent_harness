---
description: Create or update a draft pull request only after explicit remote-delivery authority exists.
---

Invoke `pull-request-delivery`.

Run only after `/prepare-pr`, final governance commit, clean tree, and explicit delivery approval:

```bash
python -B scripts/create_pr.py --draft
```

Do not force push, merge, enable auto-merge, deploy, or claim remote CI success.
