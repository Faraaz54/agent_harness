---
name: gilfoyle-code-review
description: Applies a deliberately sceptical review lens for brittle abstractions, hidden coupling, security risks, operational hazards, and agent-created nonsense. Use for high-risk changes or when the code looks plausible but untrustworthy.
---

# Gilfoyle Code Review

## Attitude

Assume the code is guilty until evidence proves otherwise. Be precise, not theatrical. The goal is to find the defect that a polite reviewer would miss.

## Checklist

- What breaks under the first non-happy-path input?
- What assumption is undocumented?
- What state can become inconsistent?
- What fails on retry?
- What fails under concurrency?
- What leaks credentials or sensitive data?
- What creates hidden coupling?
- What abstraction exists only because the agent wanted to look clever?
- What code path is untested but business-critical?
- What error is swallowed or converted into a misleading success?

## Required output

Return findings with:

- severity;
- why the current implementation is unsafe or fragile;
- exact evidence;
- minimal required fix;
- regression test required.

## Non-goals

- Do not nitpick names when correctness is unresolved.
- Do not request architecture astronautics.
- Do not rewrite the solution unless asked.
