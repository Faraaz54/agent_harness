# IDSD and Build-Auto

The harness uses Intent, Context and Expectations as separate artifacts. Intent and Expectations are human-owned. Context is assembled by the harness. Task contracts are executable vertical slices derived from those artifacts.

`/build-auto` should not act from chat memory. It asks `scripts/build_orchestrator.py next`, executes one returned action, records a structured result, and repeats.

## v0.5.6 testing expectations

IDSD artifact generation must now include hierarchical testing expectations before implementation starts. Expectations contain the human-readable Testing Expectations Matrix. Task contracts contain machine-readable `test_expectations` for unit, integration, local E2E, and cloud E2E.

`/build-auto` should treat missing `test_expectations` as a task-contract defect, not an implementation detail. The build agent may repair implementation and tests, but it must not silently invent a missing test hierarchy after the run has started without routing back through expectation/task-contract validation.
