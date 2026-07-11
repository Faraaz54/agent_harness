---
description: Show and validate role-based model routing for commands, agents, reviews and validation.
---

Run:

```bash
python -B scripts/model_router.py status
```

Use this before `/build-auto` when the IDE/provider model configuration changes. Treat configured model names as aliases that must resolve to models available in the active IDE or API workspace.
