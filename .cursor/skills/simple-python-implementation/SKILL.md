---
name: simple-python-implementation
description: Ponytail-style Python implementation discipline: smallest readable design, standard library first, explicit errors, no speculative abstraction.
---

# Simple Python Implementation

Prefer:

- functions before classes unless state or polymorphism is required;
- standard library before dependencies;
- clear names over comments explaining obscure code;
- typed boundaries for public functions;
- explicit exceptions and narrow `except` clauses;
- small modules and tests close to behaviour;
- deterministic logic and pure functions where practical.

Avoid:

- factories, registries, plugins, service classes, inheritance trees, or frameworks not required by the task;
- hidden global state;
- broad `except Exception`;
- adding dependencies for trivial logic;
- implementing future tasks early.
