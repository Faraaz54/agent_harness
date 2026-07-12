#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
sys.dont_write_bytecode = True
from harnesslib import repository_root, validate_json_schema, load_json, write_json, utc_now

TIERS = ["unit", "integration", "local_e2e", "cloud_e2e"]

def check_tasks(doc: dict) -> tuple[list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    epic_checks: list[dict] = []
    test_checks: list[dict] = []
    dependency_checks: list[dict] = []
    epics = doc.get("epics", [])
    epic_ids = {e.get("epic_id") for e in epics}
    if not epics:
        findings.append({"id":"TASK-EPIC-001","severity":"BLOCKER","title":"No epics declared","required_change":"Add top-level epics and assign every task to an epic."})
    task_ids = {t.get("task_id") for t in doc.get("tasks", [])}
    for e in epics:
        status = "PASS" if e.get("epic_id") and e.get("goal") and e.get("sequencing_rationale") else "FAIL"
        epic_checks.append({"epic_id": e.get("epic_id", "UNKNOWN"), "status": status})
    for task in doc.get("tasks", []):
        tid = task.get("task_id", "UNKNOWN")
        if task.get("epic_id") not in epic_ids:
            findings.append({"id":f"TASK-EPIC-{tid}","severity":"BLOCKER","title":"Task references missing epic","required_change":"Assign task.epic_id to a declared top-level epic."})
        te = task.get("test_expectations")
        if not isinstance(te, dict):
            findings.append({"id":f"TASK-TEST-{tid}","severity":"BLOCKER","title":"Task missing test_expectations","required_change":"Declare unit, integration, local_e2e, cloud_e2e expectations."})
            continue
        highest = te.get("highest_required_tier")
        if highest not in TIERS:
            findings.append({"id":f"TASK-TEST-HIGH-{tid}","severity":"BLOCKER","title":"Invalid highest_required_tier","required_change":"Use unit, integration, local_e2e, or cloud_e2e."})
        for tier in TIERS:
            entry = te.get(tier)
            if not isinstance(entry, dict):
                findings.append({"id":f"TASK-TEST-{tid}-{tier}","severity":"BLOCKER","title":f"Task omits {tier} test tier","required_change":"Declare the tier as required or explicitly not required."})
                continue
            if "required" not in entry:
                findings.append({"id":f"TASK-TEST-{tid}-{tier}","severity":"BLOCKER","title":f"Task {tier} tier lacks required flag","required_change":"Add required:boolean."})
            if entry.get("required"):
                if not entry.get("what_to_test") or not entry.get("evidence_required"):
                    findings.append({"id":f"TASK-TEST-{tid}-{tier}","severity":"BLOCKER","title":f"Required {tier} tier lacks evidence detail","required_change":"Add what_to_test and evidence_required."})
            else:
                if not entry.get("not_required_reason"):
                    findings.append({"id":f"TASK-TEST-{tid}-{tier}","severity":"BLOCKER","title":f"Non-required {tier} tier lacks reason","required_change":"Add not_required_reason."})
        test_checks.append({"task_id":tid,"status":"PASS" if not any(f['id'].startswith(f"TASK-TEST-{tid}") for f in findings) else "FAIL","highest_required_tier":highest})
        for dep in task.get("dependencies", []):
            status = "PASS" if dep in task_ids else "FAIL"
            dependency_checks.append({"task_id":tid,"dependency":dep,"status":status})
            if status == "FAIL":
                findings.append({"id":f"TASK-DEP-{tid}-{dep}","severity":"BLOCKER","title":"Unknown task dependency","required_change":"Use a declared task_id or remove the dependency."})
    return epic_checks, test_checks, dependency_checks, findings

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    repo = repository_root(); task_path = repo/args.tasks
    schema_status = "PASS"; schema_errors=[]
    try:
        validate_json_schema(task_path, repo/"schemas/task-contracts.schema.json")
    except Exception as exc:
        schema_status = "FAIL"; schema_errors.append(str(exc))
    doc = load_json(task_path)
    epic_checks, test_checks, dependency_checks, findings = check_tasks(doc)
    if schema_status == "FAIL":
        findings.insert(0,{"id":"TASK-SCHEMA-001","severity":"BLOCKER","title":"Task contract schema validation failed","required_change":"Fix schema errors before preparing a run.","evidence":"; ".join(schema_errors)})
    result = {
        "schema_version":"1.0",
        "agent":"task-contract-validation-agent",
        "intent_id":doc.get("intent_id","UNKNOWN"),
        "verdict":"PASS" if schema_status == "PASS" and not findings else "CHANGES_REQUIRED",
        "schema_validation":{"status":schema_status,"schema":"schemas/task-contracts.schema.json","errors":schema_errors},
        "epic_checks":epic_checks,
        "test_expectation_checks":test_checks,
        "dependency_checks":dependency_checks,
        "findings":findings,
        "model_routing":{"alias":"validation_reasoning","selected_model":"operator-or-ide-selected"},
        "validated_at":utc_now()
    }
    if args.output:
        write_json(repo/args.output, result)
        validate_json_schema(repo/args.output, repo/"schemas/task-contract-validation-result.schema.json")
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "PASS" else 1
if __name__ == "__main__": raise SystemExit(main())
