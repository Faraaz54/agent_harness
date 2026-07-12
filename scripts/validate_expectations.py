#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
from harnesslib import repository_root, validate_json_schema, load_json, write_json, utc_now, HarnessError

TIERS = ["unit", "integration", "local_e2e", "cloud_e2e"]

def validate_semantics(expectations: dict) -> list[dict]:
    findings: list[dict] = []
    matrix = expectations.get("testing_expectations_matrix", [])
    if not matrix:
        findings.append({"id":"EXP-TEST-001","severity":"BLOCKER","title":"Testing Expectations Matrix is missing","required_change":"Add at least one matrix row covering unit, integration, local_e2e and cloud_e2e."})
    for i, row in enumerate(matrix, start=1):
        for tier in TIERS:
            if not str(row.get(tier, "")).strip():
                findings.append({"id":f"EXP-TEST-{i:03d}-{tier}","severity":"BLOCKER","title":f"Matrix row {i} omits {tier}","required_change":f"State what is required or why {tier} is not required."})
    tiers = expectations.get("required_testing_tiers", {})
    for tier in TIERS:
        entry = tiers.get(tier)
        if not isinstance(entry, dict):
            findings.append({"id":f"EXP-TIER-{tier}","severity":"BLOCKER","title":f"required_testing_tiers.{tier} missing","required_change":f"Declare whether {tier} is required and why."})
        elif "required" not in entry or not entry.get("reason"):
            findings.append({"id":f"EXP-TIER-{tier}","severity":"BLOCKER","title":f"required_testing_tiers.{tier} incomplete","required_change":"Include required:boolean and non-empty reason."})
    if not expectations.get("success_scenarios"):
        findings.append({"id":"EXP-SUCCESS-001","severity":"BLOCKER","title":"Missing success scenarios","required_change":"Add observable success scenarios."})
    if not expectations.get("failure_scenarios"):
        findings.append({"id":"EXP-FAIL-001","severity":"BLOCKER","title":"Missing failure scenarios","required_change":"Add observable failure scenarios."})
    return findings

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expectations", required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    repo = repository_root()
    exp_path = repo / args.expectations
    schema_status = "PASS"
    schema_errors: list[str] = []
    try:
        validate_json_schema(exp_path, repo / "schemas/expectations.schema.json")
    except Exception as exc:
        schema_status = "FAIL"; schema_errors.append(str(exc))
    expectations = load_json(exp_path)
    findings = validate_semantics(expectations)
    semantic_checks = [
        {"check":"expectations schema","status":schema_status,"evidence":"schemas/expectations.schema.json"},
        {"check":"testing expectations matrix declares all tiers","status":"PASS" if not any(f['id'].startswith('EXP-TEST') for f in findings) else "FAIL","evidence":"testing_expectations_matrix"},
        {"check":"required_testing_tiers declares all tiers","status":"PASS" if not any(f['id'].startswith('EXP-TIER') for f in findings) else "FAIL","evidence":"required_testing_tiers"},
        {"check":"success and failure scenarios present","status":"PASS" if expectations.get('success_scenarios') and expectations.get('failure_scenarios') else "FAIL","evidence":"success_scenarios/failure_scenarios"},
    ]
    result = {
        "schema_version":"1.0",
        "agent":"expectation-validation-agent",
        "intent_id": expectations.get("intent_id", "UNKNOWN"),
        "verdict":"PASS" if schema_status == "PASS" and not findings else "CHANGES_REQUIRED",
        "schema_validation":{"status":schema_status,"schema":"schemas/expectations.schema.json","errors":schema_errors},
        "semantic_checks":semantic_checks,
        "findings":findings,
        "model_routing":{"alias":"validation_reasoning","selected_model":"operator-or-ide-selected"},
        "validated_at": utc_now()
    }
    if args.output:
        write_json(repo/args.output, result)
        # validate the validation result itself
        validate_json_schema(repo/args.output, repo/"schemas/expectation-validation-result.schema.json")
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "PASS" else 1
if __name__ == "__main__": raise SystemExit(main())
