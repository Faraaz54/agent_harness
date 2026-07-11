# Teach-Me Design

`/teach-me` is the post-run understanding workflow. It is deliberately outside `/build-auto`.

The build loop proves engineering work. The teach-me loop proves human understanding.

## Goals

- Generate a visual HTML report explaining what happened in a run.
- Preserve a durable mental model of the run.
- Help the human explain the project status to others.
- Verify the human understands the problem, solution, decisions, edge cases, evidence, impact and current status.
- Maintain a Markdown checklist that records learning progress.

## Non-goals

- Do not implement code.
- Do not repair tasks.
- Do not validate task completion.
- Do not approve delivery.
- Do not change the run manifest, feature ledger or run state.

## Artifacts

`python -B scripts/teach_me_report.py` creates:

```text
docs/teach-me-reports/<run-id>/teach-me.json
docs/teach-me-reports/<run-id>/teach-me.md
docs/teach-me-reports/<run-id>/teach-me.html
docs/learning/<run-id>-teach-me-checklist.md
```

The JSON file is the canonical report model. Markdown and HTML are rendered views.

## Teaching model

The teacher starts by asking the human to restate their understanding. It then compares that restatement against the checklist and teaches one stage at a time:

1. Problem and intent
2. Context and constraints
3. Expectations
4. Task outcomes
5. Solution design
6. Edge cases
7. Validation and reviews
8. Current status and next steps

The teacher should not mark mastery from acknowledgement alone. Mastery requires restatement and quiz evidence.

## HTML report

The HTML report is self-contained and designed to answer:

- What was the run trying to achieve?
- Which tasks completed?
- Which tasks are blocked, deferred or pending?
- What evidence exists?
- What should the human understand?
- What is the current project status?

It is safe to share as a local artifact because it uses inline CSS and no remote JavaScript, fonts or images.

## Relationship to IDSD

IDSD keeps human-owned intent and expectations separate from harness-owned context and execution. Teach-me closes the loop by making sure the human still understands what the harness did with those artifacts.

## v0.5.6 testing hierarchy explanation

Teach-me reports now include testing hierarchy coverage. The teacher should help the human explain:

- which testing tiers were required for each task;
- why the highest required tier was selected;
- which evidence proved unit, integration, local E2E, and cloud E2E expectations;
- which tiers were explicitly not required and why;
- what remains unproven when a tier is missing, blocked, or deferred.
