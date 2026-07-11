# Directory Layout

```text
cursor_engineering_harness_v0_5_2/
├── .cursor/
│   ├── agents/              # reusable agents
│   ├── commands/            # slash commands
│   ├── rules/               # always-on project rules
│   └── skills/              # reusable core skills
├── docs/
│   ├── harness/             # harness design and audit docs
│   └── templates/idsd/      # Intent, Context, Expectations templates
├── harness_tests/           # harness self-tests
├── project-packs/
│   ├── generic-python/      # reusable Python project-pack
│   └── invoice-governance/  # AGL/invoice project-pack
├── schemas/                 # machine-readable artifact schemas
├── scripts/                 # deterministic harness scripts
├── AGENTS.md
├── README.md
└── harness.config.json
```

Copy the whole directory contents into a project repository, or install selectively by copying `.cursor/`, `scripts/`, `schemas/`, `harness.config.json`, `AGENTS.md`, and the desired `project-packs/`.
