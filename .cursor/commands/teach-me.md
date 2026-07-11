---
description: Generate a post-run teaching report and run an interactive mastery session from the run evidence.
---

# /teach-me

Use the `teach-me` skill and `teacher-agent`.

This command is intentionally separate from `/build-auto`. Build automation must not pause for interactive teaching. `/teach-me` runs after a session, after `/finalize-session`, or whenever the human wants to understand the current project state.

## Start

1. Read:
   - `AGENTS.md`
   - `harness.config.json`
   - `tasks/run_state.json`
   - `tasks/feature_list.json`
   - latest `docs/session-reports/<run-id>/final.json` if present
   - latest `docs/run-reports/<run-id>.md` if present
   - `docs/intents/**`, `docs/context/**`, `docs/expectations/**`, and `docs/task-contracts/**` referenced by the run manifest
   - implementation results, reviews, validation results, project-pack domain reviews, and commit receipts available for the run

2. Generate or refresh the teaching report:

```bash
python -B scripts/teach_me_report.py
```

3. Open the generated artifacts:
   - `docs/teach-me-reports/<run-id>/teach-me.md`
   - `docs/teach-me-reports/<run-id>/teach-me.html`
   - `docs/learning/<run-id>-teach-me-checklist.md`

## Teaching protocol

Follow the `teach-me` skill exactly:

1. Ask the human to restate their understanding first.
2. Compare the restatement against the checklist.
3. Teach incrementally by stage:
   - problem and intent
   - context and constraints
   - expectations and success/failure boundaries
   - tasks completed
   - implementation approach
   - key design decisions
   - edge cases and failure modes
   - validation/review evidence
   - current project status and next steps
4. Do not move to the next stage until the human can explain the current stage.
5. Use code snippets, diagrams, debugger walkthroughs, or file navigation when useful.
6. Quiz with open-ended and multiple-choice questions. Do not reveal multiple-choice answers before submission.
7. Update the teach-me checklist with demonstrated mastery, partial gaps, and follow-up explanations.
8. Regenerate the teaching report after the interactive session if the checklist changed.

## Completion criteria

Do not mark learning complete from acknowledgement alone.

Learning may be marked complete only when the human demonstrates mastery across all configured dimensions in `harness.config.json`:

- problem
- solution
- design decisions
- edge cases
- validation
- impact
- current status

If the human stops early, record `LEARNING_IN_PROGRESS` and preserve the checklist.

## Output

End by giving the human the key report paths:

- Markdown teaching report
- HTML teaching report
- teach-me checklist

Do not claim the build is complete unless the run evidence says engineering closure is complete.
