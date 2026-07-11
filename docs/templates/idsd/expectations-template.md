# Expectations: <intent-id>

## Success Scenarios

## Failure Scenarios

## Acceptance Criteria

## Validation Strategy

## Review Requirements

## Hidden/Private Eval Boundary

Do not expose validator-only exact checks to the builder.


## Testing Expectations Matrix

Every row should describe a behaviour, risk, or acceptance criterion and the expected proof at each tier. A tier may be marked `Not required`, but the reason must be explicit.

| Behaviour / Risk | Unit | Integration | Local E2E | Cloud E2E |
|---|---|---|---|---|
| <behaviour-or-risk> | <what to test, or not required because...> | <what to test, or not required because...> | <what to test, or not required because...> | <what to test, or not required because...> |

## Required Testing Tiers

State the minimum required evidence for this intent.

- Unit: required / not required; reason.
- Integration: required / not required; reason.
- Local E2E: required / not required; reason.
- Cloud E2E / environment verification: required / not required; reason.

Cloud E2E should only be marked required when this intent, a linked goal, or an approved environment contract explicitly authorises remote execution.

## Testing Evidence Expectations

- Unit evidence path or command:
- Integration evidence path or command:
- Local E2E evidence path or command:
- Cloud E2E evidence path, job/run ID, or not-required reason:
