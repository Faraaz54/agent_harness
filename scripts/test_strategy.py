#!/usr/bin/env python3
"""Inspect, classify, and validate harness testing hierarchy requirements."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

TIERS = ["unit", "integration", "local_e2e", "cloud_e2e"]
BOUNDARY_KEYWORDS = {
    "database", "db", "sql", "postgres", "filesystem", "file", "schema", "api", "queue", "adapter",
    "orchestration", "docker", "azure", "databricks", "spark", "pipeline", "ingestion", "etl", "elt",
    "bronze", "silver", "gold", "idempotency", "retry", "late", "lineage"
}
PIPELINE_KEYWORDS = {"pipeline", "ingestion", "etl", "elt", "bronze", "silver", "gold", "databricks", "spark", "job"}
CLOUD_KEYWORDS = {"azure", "databricks", "cloud", "workspace", "cluster", "job run", "remote"}


def load_config(root: Path) -> dict[str, Any]:
    return json.loads((root / "harness.config.json").read_text(encoding="utf-8"))


def load_json_file(root: Path, path: Path) -> dict[str, Any]:
    target = path if path.is_absolute() else root / path
    return json.loads(target.read_text(encoding="utf-8"))


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(flatten_text(v) for v in value)
    if isinstance(value, dict):
        return "\n".join(f"{k}: {flatten_text(v)}" for k, v in value.items())
    return str(value)


def find_task(contracts: dict[str, Any], task_id: str | None) -> dict[str, Any]:
    tasks = contracts.get("tasks", [])
    if task_id is None:
        return tasks[0] if tasks else {}
    for task in tasks:
        if task.get("task_id") == task_id:
            return task
    raise SystemExit(f"task_id not found: {task_id}")


def highest_tier_from_test_expectations(test_expectations: dict[str, Any]) -> str | None:
    highest = test_expectations.get("highest_required_tier")
    if highest in TIERS:
        return highest
    required = [tier for tier in TIERS if (test_expectations.get(tier) or {}).get("required") is True]
    return required[-1] if required else None


def classify_task(task: dict[str, Any]) -> dict[str, Any]:
    if isinstance(task.get("test_expectations"), dict):
        te = task["test_expectations"]
        required = [tier for tier in TIERS if (te.get(tier) or {}).get("required") is True]
        highest = highest_tier_from_test_expectations(te) or (required[-1] if required else "unit")
        if highest not in required and highest in TIERS:
            required = [tier for tier in TIERS if TIERS.index(tier) <= TIERS.index(highest)]
        return {
            "task_id": task.get("task_id"),
            "required_tiers": required or ["unit"],
            "highest_required_tier": highest,
            "classification_evidence": ["task_contract.test_expectations present"],
        }

    text = flatten_text(task).lower()
    evidence = []
    required = ["unit"]
    if any(k in text for k in BOUNDARY_KEYWORDS):
        required.append("integration")
        evidence.append("boundary keyword detected")
    if any(k in text for k in PIPELINE_KEYWORDS):
        required.append("local_e2e")
        evidence.append("pipeline keyword detected")
    if any(k in text for k in CLOUD_KEYWORDS):
        required.append("cloud_e2e")
        evidence.append("cloud keyword detected; requires explicit environment/goal authority")
    declared = task.get("test_tiers") or task.get("verification", {}).get("test_tiers")
    if declared:
        for tier in declared:
            if tier not in required and tier in TIERS:
                required.append(tier)
        evidence.append("declared legacy test_tiers present")
    ordered = [tier for tier in TIERS if tier in required]
    return {
        "task_id": task.get("task_id"),
        "required_tiers": ordered,
        "highest_required_tier": ordered[-1],
        "classification_evidence": evidence or ["default unit tier"],
        "warning": "task_contract.test_expectations missing; v0.5.6 requires explicit hierarchy",
    }


def validate_task_test_expectations(task: dict[str, Any]) -> list[str]:
    task_id = task.get("task_id", "<unknown>")
    errors: list[str] = []
    te = task.get("test_expectations")
    if not isinstance(te, dict):
        return [f"{task_id}: test_expectations missing"]
    highest = te.get("highest_required_tier")
    if highest not in TIERS:
        errors.append(f"{task_id}: test_expectations.highest_required_tier must be one of {TIERS}")
    if not str(te.get("tier_rationale", "")).strip():
        errors.append(f"{task_id}: test_expectations.tier_rationale missing")
    for tier in TIERS:
        obj = te.get(tier)
        if not isinstance(obj, dict):
            errors.append(f"{task_id}: test_expectations.{tier} missing")
            continue
        if not isinstance(obj.get("required"), bool):
            errors.append(f"{task_id}: test_expectations.{tier}.required must be boolean")
        if obj.get("required") is True:
            if not obj.get("what_to_test"):
                errors.append(f"{task_id}: required tier {tier} missing what_to_test")
            if not obj.get("evidence_required"):
                errors.append(f"{task_id}: required tier {tier} missing evidence_required")
        else:
            if not str(obj.get("not_required_reason", "")).strip():
                errors.append(f"{task_id}: non-required tier {tier} missing not_required_reason")
    if isinstance(te.get("coverage_map"), list) and not te.get("coverage_map"):
        errors.append(f"{task_id}: coverage_map is present but empty")
    return errors


def status(root: Path) -> int:
    cfg = load_config(root)
    strategy = cfg.get("test_strategy", {})
    print(json.dumps({
        "enabled": strategy.get("enabled", False),
        "default_hierarchy": strategy.get("default_hierarchy", TIERS),
        "gating": strategy.get("gating", {}),
        "pipeline_defaults": strategy.get("pipeline_defaults", {}),
        "idsd_generation": strategy.get("idsd_generation", {}),
        "tiers": list(strategy.get("tiers", {}).keys()),
    }, indent=2))
    return 0


def validate(root: Path) -> int:
    errors = []
    cfg = load_config(root)
    strategy = cfg.get("test_strategy")
    if not strategy or strategy.get("enabled") is not True:
        errors.append("test_strategy.enabled must be true")
    else:
        tiers = strategy.get("tiers", {})
        for tier in TIERS:
            if tier not in tiers:
                errors.append(f"test_strategy.tiers.{tier} missing")
        gating = strategy.get("gating", {})
        for key in TIERS:
            if key not in gating:
                errors.append(f"test_strategy.gating.{key} missing")
        idsd = strategy.get("idsd_generation", {})
        if idsd.get("expectations_must_include_testing_matrix") is not True:
            errors.append("test_strategy.idsd_generation.expectations_must_include_testing_matrix must be true")
        if idsd.get("task_contracts_must_include_test_expectations") is not True:
            errors.append("test_strategy.idsd_generation.task_contracts_must_include_test_expectations must be true")
        declared = idsd.get("all_tiers_must_be_declared", [])
        for tier in TIERS:
            if tier not in declared:
                errors.append(f"test_strategy.idsd_generation.all_tiers_must_be_declared missing {tier}")
    if errors:
        print(json.dumps({"verdict": "FAIL", "errors": errors}, indent=2))
        return 1
    print(json.dumps({"verdict": "PASS"}, indent=2))
    return 0


def classify(root: Path, contracts_path: Path, task_id: str | None) -> int:
    contracts = load_json_file(root, contracts_path)
    task = find_task(contracts, task_id)
    print(json.dumps(classify_task(task), indent=2))
    return 0


def validate_contracts(root: Path, contracts_path: Path) -> int:
    contracts = load_json_file(root, contracts_path)
    errors: list[str] = []
    tasks = contracts.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty list")
    else:
        for task in tasks:
            errors.extend(validate_task_test_expectations(task))
    verdict = "PASS" if not errors else "FAIL"
    print(json.dumps({"verdict": verdict, "errors": errors, "task_count": len(tasks or [])}, indent=2))
    return 0 if not errors else 1



def resolve_gates(root: Path, contracts_path: Path, task_id: str) -> int:
    cfg = load_config(root)
    contracts = load_json_file(root, contracts_path)
    task = find_task(contracts, task_id)
    cls = classify_task(task)
    tiers = cfg.get("test_strategy", {}).get("tiers", {})
    required_gates = []
    for tier in cls.get("required_tiers", []):
        if tier == "cloud_e2e":
            required_gates.append({"tier": tier, "required": False, "reason": "Cloud E2E requires goal loop or explicit environment authority."})
            continue
        commands = tiers.get(tier, {}).get("default_commands", [])
        required_gates.append({"tier": tier, "required": True, "commands": commands})
    out = {"verdict": "PASS", "task_id": task_id, "highest_required_tier": cls.get("highest_required_tier"), "required_gates": required_gates}
    print(json.dumps(out, indent=2))
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("validate")
    c = sub.add_parser("classify")
    c.add_argument("--contracts", required=True)
    c.add_argument("--task-id")
    vc = sub.add_parser("validate-contracts")
    vc.add_argument("--contracts", required=True)
    rg = sub.add_parser("resolve-gates")
    rg.add_argument("--contracts", required=True)
    rg.add_argument("--task-id", required=True)
    args = parser.parse_args()
    root = Path.cwd()
    if args.cmd == "status":
        return status(root)
    if args.cmd == "validate":
        return validate(root)
    if args.cmd == "classify":
        return classify(root, Path(args.contracts), args.task_id)
    if args.cmd == "validate-contracts":
        return validate_contracts(root, Path(args.contracts))
    if args.cmd == "resolve-gates":
        return resolve_gates(root, Path(args.contracts), args.task_id)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
