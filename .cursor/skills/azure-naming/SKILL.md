---
name: azure-naming
description: Applies consistent Azure resource naming and tagging conventions. Use when creating or reviewing Azure resources, Bicep modules, Terraform, or deployment scripts.
---

# Azure Naming

## Naming template

Use a deterministic convention such as:

```text
<workload>-<component>-<environment>-<region>-<instance>
```

Example:

```text
invoice-ingest-dev-aue-001
```

Adjust for Azure service-specific length and character restrictions.

## Required dimensions

- workload/application;
- component/service role;
- environment: `dev`, `test`, `uat`, `prod`;
- Azure region abbreviation;
- instance or sequence when needed.

## Tags

At minimum:

- `workload`
- `environment`
- `owner`
- `costCenter` or billing equivalent
- `managedBy`
- `dataClassification` when data is involved

## Review checks

- [ ] Names are deterministic and human-readable.
- [ ] Names comply with service restrictions.
- [ ] Environment is explicit.
- [ ] Tags support ownership and cost governance.
- [ ] Production names cannot be confused with non-production names.
