---
name: definition-of-done
description: Determines whether a task, run, or delivery stage is genuinely complete based on evidence rather than model confidence. Use before marking any task or run terminal.
---

# Definition of Done

## Task done

A task is done only when:

- it is within the approved manifest scope;
- every dependency is passed and committed;
- implementation changes are task-scoped;
- RED/GREEN evidence exists where applicable;
- task verification commands pass;
- postflight passes for the exact tree;
- required reviews pass;
- domain review passes when required by the project pack;
- validator accepts the evidence against the immutable task contract;
- the task is committed through the governed commit path;
- technical learning capture is updated.

## Run done

A run is engineering-complete only when:

- all approved tasks are `passed`, `blocked`, or `deferred` with evidence;
- all passed tasks have commit receipts;
- final gates pass;
- run closure report exists;
- session JSON/Markdown/HTML reports exist;
- offline PR package exists;
- final governance artifacts are committed;
- unresolved risks are explicit.

## Not done

- Tests passed but review is missing.
- Review passed but validator evidence is absent.
- Code works locally but task contract negative cases are unproven.
- Commit exists but is mixed with unrelated changes.
- Domain review found semantic issues.
- Reports are generated from chat memory rather than durable artifacts.

## Verification

- [ ] Status was derived from artifacts, not conversation claims.
- [ ] The current tree matches the evidence used.
- [ ] Human decisions are recorded where required.
