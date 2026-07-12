#!/usr/bin/env python3
"""Create and validate a tiny end-to-end IDSD pipeline-planning scenario.

This does not run build-auto implementation. It proves the planning surfaces produce
schema-valid intermediate artifacts before implementation starts.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
from harnesslib import repository_root, write_json, utc_now

INTENT_ID = "simulated-local-pipeline"

def run(cmd: list[str], repo: Path) -> dict:
    p = subprocess.run(cmd, cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"command": cmd, "returncode": p.returncode, "stdout": p.stdout[-3000:], "stderr": p.stderr[-3000:]}

def main() -> int:
    repo = repository_root()
    (repo/"docs/intents").mkdir(parents=True, exist_ok=True)
    (repo/"docs/context").mkdir(parents=True, exist_ok=True)
    (repo/"docs/expectations").mkdir(parents=True, exist_ok=True)
    (repo/"docs/task-contracts").mkdir(parents=True, exist_ok=True)
    (repo/"docs/validation-reports").mkdir(parents=True, exist_ok=True)
    intent_path = repo/f"docs/intents/{INTENT_ID}.md"
    intent_path.write_text("""# Intent: Simulated Local Pipeline\n\n## Goal\n\nBuild a local pipeline that reads fixture source rows and produces validated output records.\n\n## Constraints\n\n- Preserve source lineage.\n- Support deterministic reruns.\n- Keep implementation local; no cloud mutation.\n\n## Failure Conditions\n\n- Accepted output lacks source lineage.\n- Duplicate rerun creates duplicate output.\n- Invalid rows are silently dropped.\n""", encoding="utf-8")
    context = {"schema_version":"1.0","intent_id":INTENT_ID,"runtime":{"language":"python"},"available_tools":["pytest"],"project_pack":{"active":"generic-python"}}
    write_json(repo/f"docs/context/{INTENT_ID}.json", context)
    expectations = {
        "schema_version":"1.0",
        "intent_id":INTENT_ID,
        "source_context_id":INTENT_ID,
        "success_scenarios":["A fixture input row becomes a validated output record with source lineage."],
        "failure_scenarios":["An invalid row is silently dropped instead of rejected."],
        "acceptance_criteria":["Output records include source_file and source_row.","Rerunning the fixture does not duplicate output."],
        "negative_cases":["Malformed rows are classified as rejected."],
        "validation_strategy":["Unit parser tests.","Integration file boundary test.","Local E2E fixture run."],
        "review_requirements":["test-agent","principal-engineer-agent"],
        "stop_conditions":["Cloud execution is required."],
        "testing_expectations_matrix":[
            {"behavior_or_risk":"Parse fixture rows and preserve lineage","unit":"Required: parser and lineage key tests.","integration":"Required: fixture file read/write boundary.","local_e2e":"Required: fixture source to validated output.","cloud_e2e":"Not required: build-auto has no cloud authority."},
            {"behavior_or_risk":"Idempotent rerun","unit":"Required: key/hash logic.","integration":"Required: persisted output duplicate prevention.","local_e2e":"Required: run fixture twice and compare counts.","cloud_e2e":"Not required: reserved for goal loop."}
        ],
        "required_testing_tiers":{
            "unit":{"required":True,"reason":"Parser and key logic are isolated."},
            "integration":{"required":True,"reason":"Filesystem/persistence boundary is touched."},
            "local_e2e":{"required":True,"reason":"Pipeline behaviour must be proven end to end locally."},
            "cloud_e2e":{"required":False,"reason":"Cloud verification belongs to goal-auto or explicit environment authority."}
        }
    }
    exp_path = repo/f"docs/expectations/{INTENT_ID}.json"; write_json(exp_path, expectations)
    tasks = {
        "schema_version":"1.0",
        "intent_id":INTENT_ID,
        "epics":[{"epic_id":"PIPE-EPIC-001","name":"Local pipeline foundation","goal":"Prove the source-to-output pipeline locally with lineage and rerun safety.","sequencing_rationale":"Start with the smallest local vertical slice before adding external integrations.","risk_level":"medium"}],
        "tasks":[{
            "task_id":"PIPE-001","epic_id":"PIPE-EPIC-001","objective":"Implement one local source-to-output pipeline slice","behavior":"Read fixture rows, validate them, write output and rejection records with lineage.","scope":["src/pipeline/**","tests/**"],"allowed_paths":["src/pipeline/**","tests/**"],"forbidden_paths":["docs/intents/**","docs/expectations/**","docs/task-contracts/**",".env"],"non_goals":["No Azure or Databricks execution"],"dependencies":[],"acceptance_criteria":["Output records include source_file and source_row.","Malformed rows are rejected with reason codes.","Rerun does not duplicate output."],"negative_cases":["Malformed row is silently dropped."],"verification":{"commands":[["python","-B","-m","pytest","tests","-q"]],"test_tiers":["unit","integration","local_e2e"]},"required_reviewers":["test-agent","principal-engineer-agent"],"risk_level":"medium","stop_conditions":["Need to mutate cloud resources"],"test_expectations":{"highest_required_tier":"local_e2e","tier_rationale":"Pipeline task touches parsing, persistence, and full local fixture flow.","unit":{"required":True,"what_to_test":["parser validation","lineage key construction"],"evidence_required":["focused unit test output"]},"integration":{"required":True,"what_to_test":["fixture file read/write boundary"],"evidence_required":["integration test output"]},"local_e2e":{"required":True,"what_to_test":["fixture source to validated output and rerun count check"],"evidence_required":["local e2e command output"]},"cloud_e2e":{"required":False,"what_to_test":[],"evidence_required":[],"not_required_reason":"Cloud verification is outside build-auto."},"coverage_map":[{"criterion":"Output records include source_file and source_row.","tiers":["unit","integration","local_e2e"]}]}}
        ]
    }
    task_path = repo/f"docs/task-contracts/{INTENT_ID}.json"; write_json(task_path, tasks)
    commands = [
        [sys.executable,"-B","scripts/schema_validator.py","--kind","expectations","--path",str(exp_path.relative_to(repo))],
        [sys.executable,"-B","scripts/validate_expectations.py","--expectations",str(exp_path.relative_to(repo)),"--output",f"docs/validation-reports/{INTENT_ID}-expectations-validation.json"],
        [sys.executable,"-B","scripts/schema_validator.py","--kind","task-contracts","--path",str(task_path.relative_to(repo))],
        [sys.executable,"-B","scripts/test_strategy.py","validate-contracts","--contracts",str(task_path.relative_to(repo))],
        [sys.executable,"-B","scripts/validate_tasks.py","--tasks",str(task_path.relative_to(repo)),"--output",f"docs/validation-reports/{INTENT_ID}-task-contract-validation.json"]
    ]
    results=[run(c,repo) for c in commands]
    verdict = "PASS" if all(r["returncode"]==0 for r in results) else "FAIL"
    report = {"schema_version":"1.0","scenario":"simulated_pipeline_planning","intent_id":INTENT_ID,"verdict":verdict,"created_at":utc_now(),"artifacts":{"intent":str(intent_path.relative_to(repo)),"context":f"docs/context/{INTENT_ID}.json","expectations":str(exp_path.relative_to(repo)),"tasks":str(task_path.relative_to(repo))},"command_results":results}
    out = repo/"docs/validation-reports/simulated-pipeline-workflow.json"; write_json(out, report)
    print(json.dumps(report, indent=2))
    return 0 if verdict == "PASS" else 1
if __name__ == "__main__": raise SystemExit(main())
