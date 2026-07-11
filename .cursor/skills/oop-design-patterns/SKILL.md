---
name: oop-design-patterns
description: Evaluates whether object-oriented design or a design pattern is justified. Use when introducing classes, inheritance, factories, registries, strategies, adapters, or dependency injection.
---

# OOP Design Patterns

## Default

Do not introduce OOP patterns by default. Start with functions and small data structures. Add classes only when state, lifecycle, polymorphism, or dependency boundaries justify them.

## Justified uses

- Adapter around external systems.
- Repository/gateway around persistence or APIs.
- Strategy when multiple interchangeable algorithms already exist.
- Value object/dataclass for structured immutable data.
- Service object when a workflow coordinates multiple dependencies.

## Avoid

- Abstract base classes for one implementation.
- Factories without multiple products.
- Registries before extension points exist.
- Inheritance where composition is simpler.
- Dependency injection containers in small Python modules.
- Pattern names used as design justification.

## Review questions

- What concrete future change does this abstraction make easier?
- Is that change approved scope or speculation?
- Can a function/dataclass solve it more clearly?
- Is the public API smaller after this abstraction?
- Is testing easier or harder?

## Verification

- [ ] Every class has a reason beyond grouping functions.
- [ ] Pattern choice is tied to an actual requirement.
- [ ] Simpler alternatives were considered.
