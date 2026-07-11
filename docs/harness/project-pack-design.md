# Project Pack Design

Project packs contain domain-specific review agents, skills, invariants, examples and optional validators. The core harness is domain-neutral and loads a project pack only when configured.

A project pack may define:

- domain reviewer agent
- domain review skill
- domain invariants
- domain failure modes
- result schema
- public/private eval split
