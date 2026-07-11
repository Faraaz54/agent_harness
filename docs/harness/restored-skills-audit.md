# Restored Skills Audit — v0.5.1

v0.5 correctly introduced IDSD, build-auto, and project packs, but it was too lean compared with v0.4. v0.5.1 restores the important general engineering skills and keeps them domain-neutral.

## Restored / retained skill families

| Family | Status | Location |
|---|---|---|
| Skill routing | Restored | `.cursor/skills/using-agent-skills/` |
| Testing patterns | Restored | `.cursor/skills/testing-patterns/` |
| Definition of done | Restored | `.cursor/skills/definition-of-done/` |
| Simple Python / ponytail | Retained | `.cursor/skills/simple-python-implementation/` |
| Red-green vertical slice | Retained | `.cursor/skills/red-green-vertical-slice/` |
| Code review | Restored | `.cursor/skills/code-review/` |
| Sceptical review / Gilfoyle | Restored | `.cursor/skills/gilfoyle-code-review/` |
| Self-explanatory comments | Restored | `.cursor/skills/self-explanatory-code-comments/` |
| OOP design patterns | Restored | `.cursor/skills/oop-design-patterns/` |
| Docker/containerization | Restored | `.cursor/skills/docker-containerization/` |
| GitHub Actions CI/CD | Restored | `.cursor/skills/github-actions-ci-cd/` |
| Azure naming | Restored | `.cursor/skills/azure-naming/` |
| Bicep best practices | Restored | `.cursor/skills/bicep-best-practices/` |
| Environment bootstrap | Restored as skill | `.cursor/skills/environment-bootstrap/` |
| Verified commit | Retained | `.cursor/skills/verified-commit/` |
| Pull-request delivery | Restored | `.cursor/skills/pull-request-delivery/` |
| Run manifest preparation | Restored | `.cursor/skills/run-manifest-preparation/` |
| Legacy spec/plan compatibility | Restored | `.cursor/skills/project-specification-compat/`, `.cursor/skills/plan-validation-compat/` |
| Session reporting | Retained | `.cursor/skills/session-reporting/` |
| Teach-me | Retained | `.cursor/skills/teach-me/` |

## Source influence retained

- Addy Osmani-style thin commands, skill anatomy, atomic commits, staged delivery, and proof-of-work discipline.
- Awesome Copilot-style instruction families for testing, definition of done, Azure, Bicep, Docker, comments, review, GitHub Actions, and specialised agents.
- Karpathy-inspired human oversight/taste layer: simple code, explicit verification, and avoiding unreviewed “vibe-coded” complexity.
- Matt Pocock-inspired type/interface discipline is represented in the generic Python and future TypeScript project-pack pattern rather than hard-coding TypeScript into the core.

## Design decision

The restored skills remain in the reusable core only when they are domain-neutral. Invoice-specific review remains in the invoice-governance project pack.
