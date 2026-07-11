# Production Hardening — v0.6.0

v0.6.0 consolidates the planned v0.5.7, v0.5.9 and v0.6.0 work into a single release-candidate package.

## Included hardening

- JSON schema validation utility for structured results.
- Strict postflight checks: configured gates, scope guard and secret scan.
- Scope guard for allowed/forbidden paths.
- Secret scanner for common credential patterns.
- Evidence ledger for normalized run evidence.
- Project-pack manifests and validation/activation commands.
- Installer and installation verifier.
- Recovery commands: abort, resume, defer, unblock, rollback.
- CI parity checker.
- Operator manual with flowcharts and step-by-step instructions.
- Tiny Python pipeline fixture for harness self-testing and demonstrations.

## Still intentionally deferred

- Cloud job submission.
- Azure/Databricks mutation.
- Remote table verification.
- Production deployment and release promotion.

Those belong in the future goal loop.
