---
name: docker-containerization
description: Designs and reviews Dockerfiles and Compose files for small, secure, reproducible, cache-friendly builds. Use when adding or modifying containerization.
---

# Docker Containerization

## Build principles

- Use a minimal, explicit base image.
- Pin major/runtime versions intentionally.
- Separate dependency installation from source copy for cache efficiency.
- Use multi-stage builds when build tools are not needed at runtime.
- Run as a non-root user unless explicitly justified.
- Do not bake secrets into images.
- Keep runtime image small and single-purpose.
- Use `.dockerignore` aggressively.

## Python containers

- Copy lockfiles before source.
- Avoid global editable installs in runtime images unless intentional.
- Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1` when appropriate.
- Prefer deterministic dependency installation.
- Expose only required ports.

## Compose

- Use named services and healthchecks.
- Avoid binding production credentials.
- Use volumes deliberately.
- Keep dev/test compose separate from production deployment definitions.

## Review checks

- [ ] Cache layers are ordered correctly.
- [ ] No secrets are copied.
- [ ] Runtime user is non-root or justified.
- [ ] Image has only needed tools.
- [ ] Healthcheck or readiness strategy exists when used by integration tests.
