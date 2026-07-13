---
name: context-assembly
description: Assembles a schema-valid Context Pack from repository, runtime, bootstrap evidence, active project pack, and project-pack context folder files.
---

# Context Assembly

Context is harness-owned. It is the bridge between the human Intent and the build loop.

## Required inputs

- `docs/intents/<intent-id>.md`
- `docs/bootstrap/environment.json`, if available
- `docs/bootstrap/environment.md`, if available
- active project pack from `harness.config.json`
- active project-pack `context/` folder

## Project-pack context folder

In v0.6.3 simple mode, project-specific context can be placed in:

```text
project-packs/<project-name>/context/
```

Supported file types:

- Markdown: `.md`
- JSON: `.json`
- YAML: `.yaml`, `.yml`
- Text: `.txt`

The folder may start with only:

```text
context/README.md
context/<one-small-context-file>.md
```

That is enough. The harness will scan the folder and include those files in the assembled Context Pack.

## Required Context Pack shape

The generated `docs/context/<intent-id>.json` must validate against `schemas/context-pack.schema.json` and include:

- `intent_id`
- `runtime`
- `repository`
- `project_pack`
- `project_context.context_folder`
- `project_context.included_files[]`

Each included context file must expose:

- `context_id`
- `path`
- `kind`
- `title`
- `sha256`
- `size_bytes`
- `summary`
- `content_excerpt`
- phases where it is available

## Downstream requirement

Later phases must not merely assume the context exists. They must reference it:

- Expectations: `source_context.project_context_files[]`
- Task contracts: `required_context[]` and `context_files[]`
- Implementation/review/validation: action packets and review artifacts should cite relevant task `context_files` as evidence.

## Deterministic commands

Run:

```bash
python -B scripts/project_context.py validate --pack project-packs/<project-name>
python -B scripts/assemble_context.py --intent docs/intents/<intent-id>.md --output-json docs/context/<intent-id>.json --output-md docs/context/<intent-id>.md
python -B scripts/schema_validator.py --kind context-pack --path docs/context/<intent-id>.json
```
