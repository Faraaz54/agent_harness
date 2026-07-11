---
name: harness-doctor
description: Performs a read-only health check of harness installation, environment bootstrap, schemas, scripts, commands, skills, agents, project-pack configuration, and common setup mistakes.
---

# Harness Doctor

## Purpose

Detect install/configuration problems before `/build-auto` starts. This follows the ADLC-style idea that setup health should be diagnosed by one deterministic command with exact fixes.

## Checks

- required `.cursor` commands/agents/rules/skills exist;
- required scripts and schemas exist;
- Python syntax checks pass;
- harness unit tests pass;
- environment bootstrap exists and is fresh;
- project-pack path resolves when enabled;
- configured project pack has README, domain-review skill, and schema where required;
- task/run files exist when a run is active;
- git repository and identity are available;
- current branch is not protected for implementation;
- no missing command referenced by `harness.config.json` gates.

## Output

Return a table of checks with PASS/FAIL/WARN and exact remediation commands. Do not change files.
