---
name: bicep-best-practices
description: Designs and reviews Azure Bicep modules for safe, parameterized, reusable infrastructure. Use when adding or changing `.bicep` files.
---

# Bicep Best Practices

## Principles

- Use modules for reusable resource groups of responsibility.
- Parameterize environment-specific values.
- Use explicit allowed values for environment and SKU where practical.
- Keep secrets in Key Vault or deployment-time secure parameters.
- Avoid hard-coded subscription/resource identifiers.
- Use outputs only for non-secret values needed by later stages.
- Add diagnostics, identity, network and RBAC deliberately.
- Prefer least privilege.

## Structure

- `main.bicep` composes modules.
- `modules/` contains focused modules.
- `parameters/` or `.bicepparam` files hold environment inputs.
- Naming and tags should use the `azure-naming` skill.

## Review checks

- [ ] No secrets in source.
- [ ] Parameters are typed and constrained.
- [ ] Modules are cohesive.
- [ ] Existing resources are referenced explicitly.
- [ ] RBAC/network changes are intentional and documented.
- [ ] Deployment is safe for the target environment.
