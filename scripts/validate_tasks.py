#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
sys.dont_write_bytecode = True
from harnesslib import repository_root, validate_json_schema, load_json, write_json, utc_now

TIERS = ["unit", "integration", "local_e2e", "cloud_e2e"]

def check_tasks(doc: dict) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict], list[dict]]:
    findings: list[dict] = []
    epic_checks: list[dict] = []
    test_checks: list[dict] = []
    dependency_checks: list[dict] = []
    context_checks: list[dict] = []
    technical_spec_checks: list[dict] = []
    epics = doc.get("epics", [])
    epic_ids = {e.get("epic_id") for e in epics}
    if not epics:
        findings.append({"id":"TASK-EPIC-001","severity":"BLOCKER","title":"No epics declared","required_change":"Add top-level epics and assign every task to an epic."})
    task_ids = {t.get("task_id") for t in doc.get("tasks", [])}
    tech = doc.get("technical_spec")
    if not isinstance(tech, dict):
        findings.append({"id":"TASK-TECH-000","severity":"BLOCKER","title":"Task contracts missing technical_spec","required_change":"Reference docs/technical-specs/<intent-id>.json and its validation result before decomposing tasks."})
        technical_spec_checks.append({"status":"FAIL","path":None,"spec_id":None})
    else:
        ok = bool(tech.get("path") and tech.get("validation_path") and tech.get("spec_id"))
        technical_spec_checks.append({"status":"PASS" if ok else "FAIL","path":tech.get("path"),"validation_path":tech.get("validation_path"),"spec_id":tech.get("spec_id")})
        if not ok:
            findings.append({"id":"TASK-TECH-001","severity":"BLOCKER","title":"Incomplete technical_spec reference","required_change":"technical_spec must include path, validation_path, and spec_id."})
    for e in epics:
        status = "PASS" if e.get("epic_id") and e.get("goal") and e.get("sequencing_rationale") else "FAIL"
        epic_checks.append({"epic_id": e.get("epic_id", "UNKNOWN"), "status": status})
    for task in doc.get("tasks", []):
        tid = task.get("task_id", "UNKNOWN")
        if task.get("epic_id") not in epic_ids:
            findings.append({"id":f"TASK-EPIC-{tid}","severity":"BLOCKER","title":"Task references missing epic","required_change":"Assign task.epic_id to a declared top-level epic."})
        required_context = task.get("required_context")
        context_files = task.get("context_files")
        if not isinstance(required_context, list) or not required_context:
            findings.append({"id":f"TASK-CONTEXT-{tid}","severity":"BLOCKER","title":"Task missing required_context","required_change":"Declare context IDs from the assembled Context Pack required for this task."})
        if not isinstance(context_files, list) or not context_files:
            findings.append({"id":f"TASK-CONTEXT-FILES-{tid}","severity":"BLOCKER","title":"Task missing context_files","required_change":"Reference project-pack context files with context_id, path, and used_for."})
        else:
            for i, cf in enumerate(context_files, 1):
                if not cf.get("context_id") or not cf.get("path") or not cf.get("used_for"):
                    findings.append({"id":f"TASK-CONTEXT-FILE-{tid}-{i}","severity":"BLOCKER","title":"Incomplete task context file reference","required_change":"Each context_files entry needs context_id, path, and used_for."})
        refs = task.get("technical_spec_refs")
        if not isinstance(refs, list) or not refs:
            findings.append({"id":f"TASK-TECH-{tid}","severity":"BLOCKER","title":"Task missing technical_spec_refs","required_change":"Reference the Technical Spec sections that govern this task."})
        else:
            for i, ref in enumerate(refs, 1):
                if not ref.get("section") or not ref.get("reason"):
                    findings.append({"id":f"TASK-TECH-REF-{tid}-{i}","severity":"BLOCKER","title":"Incomplete technical spec reference","required_change":"Each technical_spec_refs entry needs section and reason."})
        technical_spec_checks.append({"task_id":tid,"status":"PASS" if isinstance(refs, list) and refs and not any(f.get('id','').startswith(f"TASK-TECH-{tid}") for f in findings) else "FAIL","ref_count":len(refs or [])})

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
        context_checks.append({"task_id":tid,"status":"PASS" if isinstance(required_context, list) and required_context and isinstance(context_files, list) and context_files else "FAIL", "required_context": required_context or [], "context_file_count": len(context_files or [])})
        for dep in task.get("dependencies", []):
            status = "PASS" if dep in task_ids else "FAIL"
            dependency_checks.append({"task_id":tid,"dependency":dep,"status":status})
            if status == "FAIL":
                findings.append({"id":f"TASK-DEP-{tid}-{dep}","severity":"BLOCKER","title":"Unknown task dependency","required_change":"Use a declared task_id or remove the dependency."})
    return epic_checks, test_checks, dependency_checks, context_checks, technical_spec_checks, findings

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
    epic_checks, test_checks, dependency_checks, context_checks, technical_spec_checks, findings = check_tasks(doc)
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
        "context_checks":context_checks,
        "technical_spec_checks":technical_spec_checks,
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
