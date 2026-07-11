---
name: red-green-vertical-slice
description: Implements one approved task through the smallest useful vertical slice with failing evidence before production code where practical, using the required testing hierarchy.
---

# Red-Green Vertical Slice

- Start from the task contract and acceptance criteria.
- Classify the required test tier: unit, integration, local E2E, or cloud E2E.
- Write or identify the smallest focused failing test first when the change is testable.
- Prefer unit RED/GREEN for isolated logic, integration RED/GREEN for boundaries, and local E2E as final proof for pipeline flow.
- Implement the minimum production code to pass the focused test.
- Run focused tests, then affected regression tests, then required higher-tier gates.
- Avoid unrelated refactors and broad architecture changes.
- Record RED evidence, GREEN evidence, highest tier run, files changed, and residual concerns.
- Do not use cloud E2E as a substitute for local unit/integration tests; cloud E2E proves deployment/runtime, not internal design correctness.
