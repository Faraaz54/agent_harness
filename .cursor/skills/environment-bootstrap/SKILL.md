---
name: environment-bootstrap
description: Inventories the local development toolchain and writes a privacy-conscious capability snapshot for agents. Use before implementation and whenever the environment snapshot is missing or stale.
---

# Environment Bootstrap

## Purpose

Agents should operate from observed capabilities, not assumptions. The bootstrap snapshot records available tools, versions, canonical commands, and limitations without exposing credentials.

## Required outputs

```text
docs/bootstrap/environment.json
docs/bootstrap/environment.md
```

## Probe rules

- Inspect, do not install.
- Do not authenticate.
- Do not enumerate cloud resources.
- Do not print environment-variable values, tokens, subscriptions, tenants, or Databricks hosts.
- Treat the snapshot as evidence with a freshness window, not permanent truth.

## Tools to probe when available

Python, pip, pytest, ruff, mypy, make, git, GitHub CLI, Azure CLI, Azure Developer CLI, Bicep, Databricks CLI, Docker, Compose, PostgreSQL client, Java, Spark submit, jq, curl and PowerShell.

## Verification

- [ ] JSON and Markdown agree.
- [ ] Versions and availability are recorded.
- [ ] Canonical project commands are listed.
- [ ] Unavailable tools are explicit.
- [ ] No sensitive account or token material is captured.
