#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from harnesslib import load_config, repository_root

REQUIRED_ROLES = [
    'build-auto', 'build-next', 'build-status', 'doctor',
    'build-agent', 'test-agent', 'principal-engineer-agent',
    'validator-agent', 'domain-reviewer-agent', 'delivery-agent', 'teacher-agent'
]
REQUIRED_ACTIONS = [
    'RUN_PREFLIGHT', 'IMPLEMENT_TASK', 'REPAIR_TASK', 'RUN_POSTFLIGHT',
    'RUN_REVIEW', 'RUN_DOMAIN_REVIEW', 'RUN_VALIDATOR', 'COMMIT_TASK',
    'FINALIZE_SESSION', 'COMPLETE', 'BLOCKED', 'REQUIRES_HUMAN_DECISION'
]


def routing(config: dict[str, Any]) -> dict[str, Any]:
    return config.get('model_routing', {})


def alias_config(config: dict[str, Any], alias: str) -> dict[str, Any]:
    aliases = routing(config).get('aliases', {})
    return aliases.get(alias, {})


def role_alias(config: dict[str, Any], role: str) -> str | None:
    r = routing(config)
    return r.get('role_bindings', {}).get(role)


def action_alias(config: dict[str, Any], action: str, *, task: dict[str, Any] | None = None, repair_attempt: int = 0) -> str | None:
    r = routing(config)
    alias = r.get('action_bindings', {}).get(action)
    risk = str((task or {}).get('risk_level', '')).lower()
    esc = r.get('escalation_policy', {})
    if risk == 'critical' and esc.get('critical_risk_tasks_use'):
        return esc['critical_risk_tasks_use']
    if repair_attempt >= 2 and esc.get('repair_attempt_2_or_more_use'):
        return esc['repair_attempt_2_or_more_use']
    return alias


def action_model(config: dict[str, Any], action: str, *, task: dict[str, Any] | None = None, repair_attempt: int = 0) -> dict[str, Any]:
    alias = action_alias(config, action, task=task, repair_attempt=repair_attempt)
    model = alias_config(config, alias) if alias else {}
    return {'alias': alias, **model}


def validate(config: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    r = routing(config)
    if not r:
        return 'FAIL', [], ['model_routing is missing']
    if r.get('enabled') is not True:
        warnings.append('model_routing.enabled is not true; IDE defaults will be used')
    aliases = r.get('aliases', {})
    if not aliases:
        errors.append('model_routing.aliases is empty')
    for role in REQUIRED_ROLES:
        alias = r.get('role_bindings', {}).get(role)
        if not alias:
            errors.append(f'missing role binding for {role}')
        elif alias not in aliases:
            errors.append(f'role {role} references unknown alias {alias}')
    for action in REQUIRED_ACTIONS:
        alias = r.get('action_bindings', {}).get(action)
        if not alias:
            errors.append(f'missing action binding for {action}')
        elif alias not in aliases:
            errors.append(f'action {action} references unknown alias {alias}')
    for alias, value in aliases.items():
        for field in ['provider', 'model', 'reasoning_effort', 'cost_tier']:
            if not value.get(field):
                errors.append(f'alias {alias} missing {field}')
    rb = r.get('role_bindings', {})
    if r.get('independence_policy', {}).get('warn_if_same_alias'):
        if rb.get('build-agent') == rb.get('validator-agent'):
            warnings.append('build-agent and validator-agent share the same alias; prefer independent validation')
        if rb.get('build-agent') == rb.get('principal-engineer-agent'):
            warnings.append('build-agent and principal-engineer-agent share the same alias; prefer independent review')
        if rb.get('build-agent') == rb.get('test-agent'):
            warnings.append('build-agent and test-agent share the same alias; prefer independent test review')
    verdict = 'FAIL' if errors else ('PASS_WITH_WARNINGS' if warnings else 'PASS')
    return verdict, warnings, errors


def render_status(config: dict[str, Any]) -> dict[str, Any]:
    verdict, warnings, errors = validate(config)
    r = routing(config)
    aliases = r.get('aliases', {})
    roles = {
        role: {'alias': alias, **aliases.get(alias, {})}
        for role, alias in r.get('role_bindings', {}).items()
    }
    actions = {
        action: {'alias': alias, **aliases.get(alias, {})}
        for action, alias in r.get('action_bindings', {}).items()
    }
    return {
        'verdict': verdict,
        'enabled': r.get('enabled'),
        'provider_agnostic': r.get('provider_agnostic'),
        'roles': roles,
        'actions': actions,
        'warnings': warnings,
        'errors': errors,
        'fallback_policy': r.get('fallback_policy', {})
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['status', 'validate', 'role', 'action'])
    parser.add_argument('--name')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    repo = repository_root()
    config = load_config(repo)
    if args.command == 'status':
        print(json.dumps(render_status(config), indent=2))
        return 0
    if args.command == 'validate':
        result = render_status(config)
        print(json.dumps({'verdict': result['verdict'], 'warnings': result['warnings'], 'errors': result['errors']}, indent=2))
        return 0 if result['verdict'] != 'FAIL' else 1
    if args.command == 'role':
        if not args.name:
            print(json.dumps({'verdict': 'FAIL', 'error': '--name is required'}, indent=2)); return 1
        alias = role_alias(config, args.name)
        print(json.dumps({'role': args.name, 'alias': alias, 'model': alias_config(config, alias) if alias else {}}, indent=2))
        return 0 if alias else 1
    if args.command == 'action':
        if not args.name:
            print(json.dumps({'verdict': 'FAIL', 'error': '--name is required'}, indent=2)); return 1
        print(json.dumps({'action': args.name, 'model': action_model(config, args.name)}, indent=2))
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
