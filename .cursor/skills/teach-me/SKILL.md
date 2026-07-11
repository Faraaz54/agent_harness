---
name: teach-me
description: Post-run learning workflow that generates a visual teaching report, builds a human mental model of the session, and verifies mastery through restatement, explanation, and quizzes.
---

# Teach Me

Use this skill after an implementation session, successful run, or partial run when the human wants to understand what happened and be able to explain the project status to others.

This skill is not part of `/build-auto`. It runs after the build loop or at an explicit learning checkpoint.

## Purpose

Convert run evidence into human understanding.

The human should leave able to explain:

- what problem was being solved;
- why the problem existed;
- what branches or alternatives existed;
- what was implemented;
- why it was implemented that way;
- how it works end to end;
- what edge cases and failure modes matter;
- what evidence proves the work;
- what the current project status is;
- what remains to be done.

## Required evidence

Before teaching, gather:

- `tasks/run_manifest.json`
- `tasks/run_state.json`
- `tasks/feature_list.json`
- IDSD artifacts referenced by the manifest:
  - intent
  - context
  - expectations
  - task contracts
- `docs/session-reports/<run-id>/final.json`, if present
- `docs/run-reports/<run-id>.md`, if present
- `docs/implementation-results/**`
- `docs/reviews/**`
- `docs/validation-results/**`
- `docs/pull-requests/**`, if present
- project-pack review evidence, if present
- `docs/learning/<run-id>-teach-me-checklist.md`, if present

Then generate or refresh the teaching report:

```bash
python -B scripts/teach_me_report.py
```

## Teaching sequence

### Stage 1 — Restatement first

Ask the human to restate their current understanding before explaining.

Use prompts such as:

- “Explain what you think happened in this run.”
- “What goal was the session trying to satisfy?”
- “Which tasks do you think were completed?”
- “What part still feels unclear?”

Do not start with a lecture unless the human explicitly asks for one.

### Stage 2 — Gap diagnosis

Compare the human restatement against the checklist.

Classify each area as:

- `mastered`
- `partial`
- `missing`
- `incorrect`
- `not_covered_yet`

Use the checklist file as the durable source:

```text
docs/learning/<run-id>-teach-me-checklist.md
```

### Stage 3 — Incremental teaching

Teach one stage at a time.

Recommended order:

1. Problem and intent
2. Context and constraints
3. Expectations and boundaries of done
4. Task-by-task execution
5. Solution design and key decisions
6. Code path / data path / workflow walkthrough
7. Edge cases and failure modes
8. Test, review, validation, and domain-review evidence
9. Current status, risks, blockers, deferred work, and next steps

Do not move to the next stage until the human can explain the current stage.

### Stage 4 — Drill-down

For each important point, ask why at least once.

Examples:

- “Why did this problem exist?”
- “Why was this design chosen?”
- “Why does this edge case matter?”
- “Why does this test prove the behaviour?”
- “Why would an alternative have been riskier?”

Support different explanation levels when requested:

- ELI5: non-technical, analogy-first
- ELI14: simple technical model
- ELII: explain like an intern joining the project
- Senior engineer: architecture/trade-off level
- Stakeholder: business outcome and risk level

### Stage 5 — Use evidence, not memory

Ground explanations in files and reports.

Show relevant snippets when useful:

- task contract excerpts;
- code changed;
- test added;
- validation result;
- review finding;
- domain invariant;
- run report section.

Use the debugger or file navigation when it would improve understanding.

### Stage 6 — Quiz

Ask open-ended or multiple-choice questions.

Rules:

- Do not reveal multiple-choice answers before submission.
- Rotate the correct answer position.
- Ask at least one “why” question.
- Ask at least one edge-case question.
- Ask at least one current-status question.

Examples:

Open-ended:

- “Explain the end-to-end flow from intent to completed task commit.”
- “What evidence proves task X is complete?”
- “What would fail if the domain invariant were violated?”

Multiple-choice:

- “Which artifact is the implementation authority: A) intent, B) run manifest, C) HTML report, D) README?”
- “Which role validates proof against the task contract: A) build-agent, B) validator-agent, C) delivery-agent, D) teacher-agent?”

Only mark mastery after the human answers correctly or self-corrects after explanation.

### Stage 7 — Report update

At the end, regenerate the report if the checklist changed:

```bash
python -B scripts/teach_me_report.py
```

The HTML report must make the mental model visually clear.

## Checklist requirements

The checklist must cover:

- Problem
- Intent and constraints
- Expectations
- Context
- Completed tasks
- Implementation flow
- Design decisions
- Edge cases
- Tests and validation
- Reviews and repairs
- Current status
- Remaining risks and next steps

## Completion statuses

Use these statuses:

- `LEARNING_COMPLETE`: human demonstrated mastery across all configured dimensions.
- `LEARNING_IN_PROGRESS`: human made progress but some checklist items remain partial/missing.
- `LEARNING_BLOCKED`: evidence is missing or the run state is too incomplete to teach reliably.

Never mark `LEARNING_COMPLETE` just because the human says “got it.”

## Output

End with:

- learning status;
- mastered topics;
- remaining gaps;
- generated HTML report path;
- generated Markdown report path;
- checklist path;
- recommended next teaching session, if needed.
