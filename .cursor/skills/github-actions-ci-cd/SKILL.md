---
name: github-actions-ci-cd
description: Designs and reviews GitHub Actions workflows for safe, cached, least-privilege CI/CD. Use when adding or changing `.github/workflows`.
---

# GitHub Actions CI/CD

## Principles

- Keep CI deterministic and fast.
- Use least-privilege `permissions`.
- Pin action versions to major or SHA according to project policy.
- Separate pull-request validation from deployment.
- Cache dependencies using lockfile keys.
- Avoid secrets in pull-request workflows from forks.
- Upload useful test artifacts and reports.
- Make deployment manual or environment-gated unless explicitly approved.

## Python CI baseline

- install dependencies from lockfile;
- run formatting/lint where configured;
- run type checks where configured;
- run tests;
- generate coverage only when meaningful;
- test supported Python versions deliberately.

## Anti-patterns

- `permissions: write-all` by default.
- Deploying on every branch push.
- Reinstalling all dependencies without cache.
- Running untrusted code with secrets.
- Hiding failures behind `continue-on-error`.
- Long monolithic workflows that cannot be debugged.

## Verification

- [ ] Trigger policy matches risk.
- [ ] Permissions are minimal.
- [ ] Secrets are scoped.
- [ ] Build/test/deploy are separated.
- [ ] Cache keys are deterministic.
