---
description: Assemble a schema-valid Context Pack from repo/runtime/bootstrap plus active project-pack context files.
---

Use `context-assembly`.

Inputs:

- `docs/intents/<intent-id>.md`
- `docs/bootstrap/environment.json` and `.md`, when present
- active `project-packs/<project-name>/project-pack.json`
- active `project-packs/<project-name>/context/**`

Run:

```bash
python -B scripts/project_context.py validate --pack project-packs/<project-name>
python -B scripts/assemble_context.py --intent docs/intents/<intent-id>.md --output-json docs/context/<intent-id>.json --output-md docs/context/<intent-id>.md
python -B scripts/schema_validator.py --kind context-pack --path docs/context/<intent-id>.json
```

The generated Context Pack must include `project_context.included_files`. In v0.6.3 simple mode, every supported UTF-8 file under the active project pack `context/` folder is made available to later phases. Downstream artifacts must narrow which context files they used.

Do not proceed to `/derive-expectations` if the Context Pack is missing, invalid, or omits available project-pack context files.
