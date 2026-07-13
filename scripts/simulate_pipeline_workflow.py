#!/usr/bin/env python3
"""Create and validate a tiny end-to-end IDSD pipeline-planning scenario.

No shell subprocesses are used here. The simulation validates the planning artifacts directly to avoid command-runner hangs while still proving the artifact chain:
Intent -> Context Pack -> Expectations -> expectation validation -> Technical Spec -> technical spec validation -> epics/task contracts -> task validation.
"""
from __future__ import annotations
import json, sys, hashlib
from pathlib import Path
sys.dont_write_bytecode = True
from harnesslib import repository_root, write_json, utc_now, validate_json_schema
from project_context import discover as discover_project_context, validate_index
from validate_expectations import validate_semantics as validate_expectation_semantics
from validate_technical_spec import validate_semantics as validate_technical_spec_semantics
from validate_tasks import check_tasks

INTENT_ID = "simulated-local-pipeline"
TIERS = ["unit", "integration", "local_e2e", "cloud_e2e"]


def make_context_pack(repo: Path, intent_id: str) -> dict:
    pack_path = repo / "project-packs/invoice-governance"
    index = discover_project_context(pack_path, repo)
    errors = validate_index(index)
    if errors:
        raise RuntimeError("project context validation failed: " + "; ".join(errors))
    included_files = []
    for f in index.get("files", []):
        item = dict(f)
        item["available_to_phases"] = item.pop("phase_availability")
        included_files.append(item)
    return {
        "schema_version": "1.0",
        "context_id": intent_id,
        "intent_id": intent_id,
        "created_at": utc_now(),
        "runtime": {},
        "repository": {},
        "project_pack": {"name": "invoice-governance", "path": "project-packs/invoice-governance"},
        "project_context": {
            "context_folder": index.get("context_folder", "project-packs/invoice-governance/context"),
            "included_files": included_files,
            "phase_availability": ["assemble_context", "derive_expectations", "validate_expectations", "derive_tasks", "validate_tasks", "implementation", "review", "domain_review", "validation", "teach_me"],
            "selection_notes": "Simulation context pack: all supported files under project-pack context/ are available; tasks narrow required usage.",
            "warnings": index.get("warnings", []),
        },
    }


def main() -> int:
    repo = repository_root()
    for d in ["docs/intents", "docs/context", "docs/expectations", "docs/technical-specs", "docs/task-contracts", "docs/validation-reports"]:
        (repo/d).mkdir(parents=True, exist_ok=True)

    intent_path = repo / f"docs/intents/{INTENT_ID}.md"
    intent_path.write_text("""# Intent: Simulated Local Pipeline

## Goal

Build a local pipeline that reads fixture source rows and produces validated output records.

## Constraints

- Preserve source lineage.
- Support deterministic idempotent reruns.
- Keep implementation local; no cloud mutation.

## Failure Conditions

- Accepted output lacks source lineage.
- Duplicate rerun creates duplicate output.
- Invalid rows are silently dropped.
""", encoding="utf-8")

    context = make_context_pack(repo, INTENT_ID)
    context_path = repo / f"docs/context/{INTENT_ID}.json"; write_json(context_path, context)
    validate_json_schema(context_path, repo / "schemas/context-pack.schema.json")
    project_files = context.get("project_context", {}).get("included_files", [])
    project_context_refs = [{"context_id": f["context_id"], "path": f["path"], "used_for": ["expectation_derivation", "technical_specification", "task_decomposition"]} for f in project_files]

    expectations = {
        "schema_version": "1.0",
        "intent_id": INTENT_ID,
        "source_context_id": INTENT_ID,
        "source_context": {"context_pack_path": f"docs/context/{INTENT_ID}.json", "context_pack_id": INTENT_ID, "project_context_files": project_context_refs, "omitted_project_context_files": []},
        "success_scenarios": ["A fixture input row becomes a validated output record with source lineage."],
        "failure_scenarios": ["An invalid row is silently dropped instead of rejected."],
        "acceptance_criteria": ["Output records include source_file and source_row.", "Rerunning the fixture does not duplicate output."],
        "negative_cases": ["Malformed rows are classified as rejected."],
        "validation_strategy": ["Unit parser tests.", "Integration file boundary test.", "Local E2E fixture run."],
        "review_requirements": ["test-agent", "principal-engineer-agent"],
        "stop_conditions": ["Cloud execution is required."],
        "testing_expectations_matrix": [
            {"behavior_or_risk": "Parse fixture rows and preserve lineage", "unit": "Required: parser and lineage key tests.", "integration": "Required: fixture file read/write boundary.", "local_e2e": "Required: fixture source to validated output.", "cloud_e2e": "Not required: build-auto has no cloud authority."},
            {"behavior_or_risk": "Idempotent rerun", "unit": "Required: key/hash logic.", "integration": "Required: persisted output duplicate prevention.", "local_e2e": "Required: run fixture twice and compare counts.", "cloud_e2e": "Not required: reserved for goal loop."}
        ],
        "required_testing_tiers": {"unit": {"required": True, "reason": "Parser and key logic are isolated."}, "integration": {"required": True, "reason": "Filesystem/persistence boundary is touched."}, "local_e2e": {"required": True, "reason": "Pipeline behaviour must be proven end to end locally."}, "cloud_e2e": {"required": False, "reason": "Cloud verification belongs to goal-auto or explicit environment authority."}}
    }
    exp_path = repo / f"docs/expectations/{INTENT_ID}.json"; write_json(exp_path, expectations)
    validate_json_schema(exp_path, repo / "schemas/expectations.schema.json")
    exp_findings = validate_expectation_semantics(expectations, repo)
    exp_val = {"schema_version": "1.0", "agent": "expectation-validation-agent", "intent_id": INTENT_ID, "verdict": "PASS" if not exp_findings else "CHANGES_REQUIRED", "schema_validation": {"status": "PASS", "schema": "schemas/expectations.schema.json", "errors": []}, "semantic_checks": [], "findings": exp_findings, "model_routing": {"alias": "validation_reasoning"}, "validated_at": utc_now()}
    exp_val_path = repo / f"docs/validation-reports/{INTENT_ID}-expectations-validation.json"; write_json(exp_val_path, exp_val)
    validate_json_schema(exp_val_path, repo / "schemas/expectation-validation-result.schema.json")

    tech_spec = {
        "schema_version": "1.0", "intent_id": INTENT_ID, "spec_id": f"TECH-{INTENT_ID}", "status": "validated",
        "source_artifacts": {"intent_path": str(intent_path.relative_to(repo)), "context_pack_path": str(context_path.relative_to(repo)), "expectations_path": str(exp_path.relative_to(repo)), "project_context_files": project_context_refs, "omitted_project_context_files": []},
        "architecture": {"style": "modular local batch pipeline", "runtime_targets": ["local_python"], "entrypoints": ["python -m pipeline.run"]},
        "dependencies": {"package_manager": "pip", "required_libraries": [{"name": "pytest", "reason": "Run unit/integration/local E2E tests", "allowed_usage": "test execution only"}], "forbidden_libraries": [{"name": "cloud SDK mutation clients", "reason": "Cloud execution is outside build-auto authority"}]},
        "module_design": {"src/pipeline/sources": "source readers and parsers", "src/pipeline/validation": "row validation and rejection reasons", "src/pipeline/lineage": "lineage key construction and idempotency helpers", "src/pipeline/run.py": "local pipeline entrypoint"},
        "data_flow": [{"stage": "read_fixture", "description": "Read fixture rows from local source files.", "inputs": ["fixture source file"], "outputs": ["raw parsed rows"]}, {"stage": "validate_and_write", "description": "Validate rows and emit accepted/rejected outputs with lineage.", "inputs": ["raw parsed rows"], "outputs": ["validated output records", "rejection records"]}],
        "implementation_rules": ["Preserve source lineage on accepted and rejected rows.", "Use deterministic idempotency keys for reruns.", "Do not call Azure or Databricks APIs in build-auto."],
        "configuration": {"source_path": "CLI argument or config object, not hard-coded absolute path", "secrets": "none required for local fixture"},
        "observability": {"logging": "record source path, row counts, rejection counts"},
        "error_handling": {"invalid_rows": "write rejection records with reason and lineage", "fatal_config": "fail loud"},
        "testing_implications": {"unit": ["parser validation", "lineage/idempotency key construction"], "integration": ["fixture read/write boundary"], "local_e2e": ["fixture source to validated output and rerun count check"], "cloud_e2e": ["deferred to goal-auto"]},
        "technical_decisions": [{"decision": "Use modular local Python pipeline for build-auto proof", "rationale": "Build-auto must prove local behaviour without mutating cloud resources.", "alternatives_considered": ["Databricks job execution"]}],
        "deferred_items": [{"item": "Azure/Databricks job submission", "reason": "Reserved for goal-auto or explicit environment authority."}],
        "risks": [{"risk": "Fixture divergence from production APIs", "mitigation": "Project-pack context and future goal loop cloud verification."}],
    }
    tech_path = repo / f"docs/technical-specs/{INTENT_ID}.json"; write_json(tech_path, tech_spec)
    (repo / f"docs/technical-specs/{INTENT_ID}.md").write_text("# Technical Spec: simulated local pipeline\n\nSee JSON artifact for schema-backed details.\n", encoding="utf-8")
    validate_json_schema(tech_path, repo / "schemas/technical-spec.schema.json")
    tech_checks, tech_findings = validate_technical_spec_semantics(repo, tech_spec)
    tech_val = {"schema_version": "1.0", "agent": "technical-spec-validation-agent", "intent_id": INTENT_ID, "spec_id": tech_spec["spec_id"], "verdict": "PASS" if not tech_findings else "CHANGES_REQUIRED", "schema_validation": {"status": "PASS", "schema": "schemas/technical-spec.schema.json", "errors": []}, "checks": tech_checks, "findings": tech_findings, "model_routing": {"alias": "validation_reasoning"}, "validated_at": utc_now()}
    tech_val_path = repo / f"docs/validation-reports/{INTENT_ID}-technical-spec-validation.json"; write_json(tech_val_path, tech_val)
    validate_json_schema(tech_val_path, repo / "schemas/technical-spec-validation-result.schema.json")

    required_context = [f["context_id"] for f in project_files]
    context_files = [{"context_id": f["context_id"], "path": f["path"], "used_for": ["implementation", "review", "validation"]} for f in project_files]
    tasks = {
        "schema_version": "1.0", "intent_id": INTENT_ID,
        "technical_spec": {"path": str(tech_path.relative_to(repo)), "validation_path": str(tech_val_path.relative_to(repo)), "spec_id": tech_spec["spec_id"], "status": "validated"},
        "epics": [{"epic_id": "PIPE-EPIC-001", "name": "Local pipeline foundation", "goal": "Prove the source-to-output pipeline locally with lineage and rerun safety.", "sequencing_rationale": "Start with the smallest local vertical slice before adding external integrations.", "risk_level": "medium"}],
        "tasks": [{
            "task_id": "PIPE-001", "epic_id": "PIPE-EPIC-001", "objective": "Implement one local source-to-output pipeline slice", "behavior": "Read fixture rows, validate them, write output and rejection records with lineage.", "scope": ["src/pipeline/**", "tests/**"], "allowed_paths": ["src/pipeline/**", "tests/**"], "forbidden_paths": ["docs/intents/**", "docs/expectations/**", "docs/task-contracts/**", "docs/technical-specs/**", ".env"], "non_goals": ["No Azure or Databricks execution"], "dependencies": [], "acceptance_criteria": ["Output records include source_file and source_row.", "Malformed rows are rejected with reason codes.", "Rerun does not duplicate output."], "negative_cases": ["Malformed row is silently dropped."], "verification": {"commands": [["python", "-B", "-m", "pytest", "tests", "-q"]], "test_tiers": ["unit", "integration", "local_e2e"]}, "required_reviewers": ["test-agent", "principal-engineer-agent"], "risk_level": "medium", "stop_conditions": ["Need to mutate cloud resources"], "required_context": required_context, "context_files": context_files,
            "technical_spec_refs": [{"section": "module_design", "reason": "Task implements the approved module boundaries."}, {"section": "implementation_rules", "reason": "Task must preserve lineage/idempotency and avoid cloud calls."}, {"section": "testing_implications", "reason": "Task tests must align to approved hierarchy."}],
            "test_expectations": {"highest_required_tier": "local_e2e", "tier_rationale": "Pipeline task touches parsing, persistence, and full local fixture flow.", "unit": {"required": True, "what_to_test": ["parser validation", "lineage key construction"], "evidence_required": ["focused unit test output"]}, "integration": {"required": True, "what_to_test": ["fixture file read/write boundary"], "evidence_required": ["integration test output"]}, "local_e2e": {"required": True, "what_to_test": ["fixture source to validated output and rerun count check"], "evidence_required": ["local e2e command output"]}, "cloud_e2e": {"required": False, "what_to_test": [], "evidence_required": [], "not_required_reason": "Cloud verification is outside build-auto."}, "coverage_map": [{"criterion": "Output records include source_file and source_row.", "tiers": ["unit", "integration", "local_e2e"]}]}
        }]
    }
    task_path = repo / f"docs/task-contracts/{INTENT_ID}.json"; write_json(task_path, tasks)
    validate_json_schema(task_path, repo / "schemas/task-contracts.schema.json")
    epic_checks, test_checks, dep_checks, context_checks, tech_checks2, task_findings = check_tasks(tasks)
    task_val = {"schema_version": "1.0", "agent": "task-contract-validation-agent", "intent_id": INTENT_ID, "verdict": "PASS" if not task_findings else "CHANGES_REQUIRED", "schema_validation": {"status": "PASS", "schema": "schemas/task-contracts.schema.json", "errors": []}, "epic_checks": epic_checks, "test_expectation_checks": test_checks, "dependency_checks": dep_checks, "context_checks": context_checks, "technical_spec_checks": tech_checks2, "findings": task_findings, "model_routing": {"alias": "validation_reasoning"}, "validated_at": utc_now()}
    task_val_path = repo / f"docs/validation-reports/{INTENT_ID}-task-contract-validation.json"; write_json(task_val_path, task_val)
    validate_json_schema(task_val_path, repo / "schemas/task-contract-validation-result.schema.json")

    verdict = "PASS" if not (exp_findings or tech_findings or task_findings) else "FAIL"
    report = {"schema_version": "1.0", "scenario": "simulated_pipeline_planning_with_technical_spec", "intent_id": INTENT_ID, "verdict": verdict, "created_at": utc_now(), "artifacts": {"intent": str(intent_path.relative_to(repo)), "context": str(context_path.relative_to(repo)), "expectations": str(exp_path.relative_to(repo)), "technical_spec": str(tech_path.relative_to(repo)), "tasks": str(task_path.relative_to(repo))}, "project_context_file_count": len(project_files), "checks": {"expectations_findings": len(exp_findings), "technical_spec_findings": len(tech_findings), "task_findings": len(task_findings)}}
    out = repo / "docs/validation-reports/simulated-pipeline-workflow.json"; write_json(out, report)
    print(json.dumps(report, indent=2))
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
