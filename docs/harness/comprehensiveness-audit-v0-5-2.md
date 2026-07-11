# Harness Comprehensiveness Audit — v0.5.2

## Audit finding

v0.5.1 had the right architecture but not enough operational detail in several high-leverage surfaces. The largest gaps were shallow agent instructions, thin build commands, weak always-on rules, and incomplete absorption of the 8-rule Karpathy-style contract and ADLC-style review/doctor/lesson patterns.

## Corrections made

| Area | v0.5.1 issue | v0.5.2 correction |
|---|---|---|
| Principal engineer agent | One-line review instruction | Full role, skills, inputs, review dimensions, stop conditions, structured output |
| Build agent | Minimal instruction | Full RED/GREEN, read-before-write, scope, evidence, output contract |
| Test agent | Minimal instruction | Criteria matrix, negative cases, false-positive risks, evidence contract |
| Validator agent | Minimal instruction | Proof-only validation gate with artifact identity checks |
| Domain reviewer | Generic placeholder | Project-pack loading and domain invariant workflow |
| Build-auto command | Thin but underspecified | Thin by design but now with complete routing, result recording, repair policy, progress policy |
| Rules | Too small | Full 8-rule contract: think, simplicity, surgical, goal-driven, budgets, read-before-write, checkpoint, fail-loud |
| Review approach | Basic review | Multi-dimensional ADLC-inspired review policy: correctness, tests, architecture, quality, security, operability, domain |
| Memory | Missing | Added lesson-memory and repair-memory expectations |
| Doctor | Missing | Added `/doctor` and read-only `harness_doctor.py` |
| Reflection/adversary | Missing | Added reflection and adversarial-review skills |

## Design position

Commands should stay thin, but not vague. A command should route to deterministic scripts, skills, and agents; the detailed behaviour belongs in skills, agents, schemas, and scripts. v0.5.2 keeps thin commands but expands the contracts they invoke.

## Remaining hardening

- Enforce every structured result against JSON Schema.
- Build richer examples for project packs.
- Add a real multi-agent review fan-out executor where the IDE supports it.
- Add relevance-ranked lesson loading by touched component.
- Add stronger token/context budget counters when the IDE exposes usage metadata.
