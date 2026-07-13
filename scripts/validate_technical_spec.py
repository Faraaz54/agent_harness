#!/usr/bin/env python3
"""Validate the IDSD Technical Spec before task decomposition."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
from harnesslib import repository_root, validate_json_schema, load_json, write_json, utc_now

TIERS = ["unit", "integration", "local_e2e", "cloud_e2e"]
REQUIRED_CORE_SECTIONS = [
    "architecture", "dependencies", "module_design", "data_flow",
    "implementation_rules", "configuration", "testing_implications",
    "technical_decisions", "deferred_items",
]


def _exists(repo: Path, rel: str | None) -> bool:
    return bool(rel) and (repo / rel).exists()


def validate_semantics(repo: Path, spec: dict) -> tuple[list[dict], list[dict]]:
    checks: list[dict] = []
    findings: list[dict] = []

    def check(check_id: str, ok: bool, title: str, finding_id: str, required_change: str, severity: str = "BLOCKER") -> None:
        checks.append({"id": check_id, "status": "PASS" if ok else "FAIL", "title": title})
        if not ok:
            findings.append({"id": finding_id, "severity": severity, "title": title, "required_change": required_change})

    source = spec.get("source_artifacts", {})
    check("TECH-SOURCE-INTENT", _exists(repo, source.get("intent_path")), "Intent artifact exists", "TECH-SOURCE-001", "Set source_artifacts.intent_path to an existing docs/intents file.")
    check("TECH-SOURCE-CONTEXT", _exists(repo, source.get("context_pack_path")), "Context Pack artifact exists", "TECH-SOURCE-002", "Set source_artifacts.context_pack_path to the assembled Context Pack.")
    check("TECH-SOURCE-EXPECTATIONS", _exists(repo, source.get("expectations_path")), "Expectations artifact exists", "TECH-SOURCE-003", "Set source_artifacts.expectations_path to the validated Expectations artifact.")

    for section in REQUIRED_CORE_SECTIONS:
        value = spec.get(section)
        ok = value is not None and value != {} and value != []
        check(f"TECH-SECTION-{section.upper()}", ok, f"Technical spec declares {section}", f"TECH-SECTION-{section.upper()}", f"Add a non-empty `{section}` section.")

    libs = spec.get("dependencies", {}).get("required_libraries", [])
    if libs:
        for i, lib in enumerate(libs, 1):
            ok = bool(lib.get("name") and lib.get("reason") and lib.get("allowed_usage"))
            check(f"TECH-LIB-{i}", ok, f"Required library #{i} is justified", f"TECH-LIB-{i}", "Every required library must include name, reason, and allowed_usage.")
    else:
        findings.append({"id": "TECH-LIB-000", "severity": "MAJOR", "title": "No required libraries declared", "required_change": "Declare required_libraries, even if the list is intentionally empty with a rationale in technical_decisions."})
        checks.append({"id": "TECH-LIBRARIES", "status": "FAIL", "title": "Required libraries are declared"})

    testing = spec.get("testing_implications", {})
    for tier in TIERS:
        ok = isinstance(testing.get(tier), list)
        check(f"TECH-TEST-{tier}", ok, f"Testing implications include {tier}", f"TECH-TEST-{tier}", f"Add testing_implications.{tier} as an array. Use an empty array only with an explicit deferred item/decision explaining why.")

    ctx_files = source.get("project_context_files", [])
    if not isinstance(ctx_files, list):
        findings.append({"id":"TECH-CONTEXT-000","severity":"BLOCKER","title":"project_context_files is not a list","required_change":"Use source_artifacts.project_context_files as an array of context_id/path/used_for entries."})
    else:
        for i, cf in enumerate(ctx_files, 1):
            ok = bool(cf.get("context_id") and cf.get("path") and cf.get("used_for")) and _exists(repo, cf.get("path"))
            check(f"TECH-CONTEXT-{i}", ok, f"Project context reference #{i} is resolvable", f"TECH-CONTEXT-{i}", "Each project context reference must include context_id/path/used_for and the file must exist.")

    # Pipeline specs should explicitly address lineage/idempotency when those words appear in inputs/rules.
    combined = json.dumps(spec, sort_keys=True).lower()
    for keyword in ["lineage", "idempot"]:
        if keyword in combined:
            continue
        findings.append({"id": f"TECH-PIPE-{keyword.upper()}", "severity": "MAJOR", "title": f"Pipeline technical spec does not mention {keyword}", "required_change": f"For pipeline work, document the {keyword} strategy or explain why it is out of scope."})
        checks.append({"id": f"TECH-PIPE-{keyword.upper()}", "status": "FAIL", "title": f"Pipeline spec addresses {keyword}"})

    return checks, findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    repo = repository_root(); spec_path = repo / args.spec
    schema_status = "PASS"; schema_errors: list[str] = []
    try:
        validate_json_schema(spec_path, repo / "schemas/technical-spec.schema.json")
    except Exception as exc:
        schema_status = "FAIL"; schema_errors.append(str(exc))
    spec = load_json(spec_path)
    checks, findings = validate_semantics(repo, spec)
    if schema_status == "FAIL":
        findings.insert(0, {"id":"TECH-SCHEMA-001", "severity":"BLOCKER", "title":"Technical spec schema validation failed", "required_change":"Fix schema errors before task decomposition.", "evidence":"; ".join(schema_errors)})
    verdict = "PASS" if schema_status == "PASS" and not findings else "CHANGES_REQUIRED"
    if findings and all(f.get("severity") != "BLOCKER" for f in findings) and schema_status == "PASS":
        verdict = "PASS_WITH_WARNINGS"
    result = {
        "schema_version": "1.0",
        "agent": "technical-spec-validation-agent",
        "intent_id": spec.get("intent_id", "UNKNOWN"),
        "spec_id": spec.get("spec_id", "UNKNOWN"),
        "verdict": verdict,
        "schema_validation": {"status": schema_status, "schema": "schemas/technical-spec.schema.json", "errors": schema_errors},
        "checks": checks,
        "findings": findings,
        "model_routing": {"alias": "validation_reasoning", "selected_model": "operator-or-ide-selected"},
        "validated_at": utc_now(),
    }
    if args.output:
        write_json(repo / args.output, result)
        validate_json_schema(repo / args.output, repo / "schemas/technical-spec-validation-result.schema.json")
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 1

if __name__ == "__main__":
    raise SystemExit(main())
