#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from harnesslib import HarnessError, load_config, load_json, repository_root, validate_json_schema

SCHEMA_BY_KIND = {
    "implementation": "schemas/implementation-result.schema.json",
    "review": "schemas/review-result.schema.json",
    "domain-review": "schemas/domain-review-result.schema.json",
    "validation": "schemas/task-validation.schema.json",
}

KIND_BY_ACTION = {
    "IMPLEMENT_TASK": "implementation",
    "REPAIR_TASK": "implementation",
    "RUN_REVIEW": "review",
    "RUN_DOMAIN_REVIEW": "domain-review",
    "RUN_VALIDATOR": "validation",
}

EXPECTED_AGENT_FIELD = {
    "implementation": "agent",
    "review": "reviewer",
    "domain-review": "reviewer",
    "validation": "validator",
}


def domain_schema(repo: Path) -> Path:
    cfg = load_config(repo)
    pack_name = cfg.get("project_pack", {}).get("active") or cfg.get("project_pack", {}).get("name")
    if pack_name:
        candidate = repo / "project-packs" / pack_name / "schemas" / "domain-review-result.schema.json"
        if candidate.exists():
            return candidate
    return repo / SCHEMA_BY_KIND["domain-review"]


def schema_for(repo: Path, kind: str) -> Path:
    if kind == "domain-review":
        return domain_schema(repo)
    return repo / SCHEMA_BY_KIND[kind]


def validate_basic_consistency(result: dict[str, Any], *, kind: str, task_id: str | None, agent: str | None) -> list[str]:
    errors: list[str] = []
    if task_id and result.get("task_id") != task_id:
        errors.append(f"task_id mismatch: expected {task_id}, got {result.get('task_id')}")
    field = EXPECTED_AGENT_FIELD.get(kind)
    if agent and field and result.get(field) != agent:
        errors.append(f"{field} mismatch: expected {agent}, got {result.get(field)}")
    findings = result.get("findings")
    if isinstance(findings, list):
        ids = [f.get("id") for f in findings if isinstance(f, dict)]
        duplicates = sorted({x for x in ids if ids.count(x) > 1 and x})
        if duplicates:
            errors.append(f"duplicate finding ids: {duplicates}")
    return errors


def validate_file(repo: Path, path: Path, *, kind: str, task_id: str | None = None, agent: str | None = None) -> dict[str, Any]:
    schema = schema_for(repo, kind)
    validate_json_schema(path, schema)
    result = load_json(path)
    errors = validate_basic_consistency(result, kind=kind, task_id=task_id, agent=agent)
    if errors:
        raise HarnessError("; ".join(errors))
    return {"verdict": "PASS", "kind": kind, "path": str(path), "schema": str(schema)}


def validate_action(repo: Path, action_path: Path, result_path: Path) -> dict[str, Any]:
    action = load_json(action_path)
    kind = KIND_BY_ACTION.get(action.get("action"))
    if not kind:
        raise HarnessError(f"No result contract registered for action {action.get('action')}")
    return validate_file(
        repo,
        result_path,
        kind=kind,
        task_id=action.get("task_id"),
        agent=action.get("required_agent"),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate structured agent result artifacts.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    val = sub.add_parser("validate")
    val.add_argument("--kind", required=True, choices=sorted(SCHEMA_BY_KIND))
    val.add_argument("--path", required=True)
    val.add_argument("--task-id")
    val.add_argument("--agent")
    act = sub.add_parser("validate-action")
    act.add_argument("--action", required=True)
    act.add_argument("--result", required=True)
    args = ap.parse_args()
    repo = repository_root()
    try:
        if args.cmd == "validate":
            out = validate_file(repo, repo / args.path, kind=args.kind, task_id=args.task_id, agent=args.agent)
        else:
            out = validate_action(repo, repo / args.action, repo / args.result)
        print(json.dumps(out, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"verdict": "FAIL", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
