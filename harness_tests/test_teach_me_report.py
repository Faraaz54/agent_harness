from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_EXPECTATIONS_FIXTURE = '{\n  "highest_required_tier": "integration",\n  "tier_rationale": "The task touches a local verification boundary.",\n  "unit": {"required": true, "what_to_test": ["focused behaviour"], "evidence_required": ["unit test output"]},\n  "integration": {"required": true, "what_to_test": ["local boundary"], "evidence_required": ["integration test output"]},\n  "local_e2e": {"required": false, "what_to_test": [], "evidence_required": [], "not_required_reason": "No multi-stage pipeline flow in this task."},\n  "cloud_e2e": {"required": false, "what_to_test": [], "evidence_required": [], "not_required_reason": "No explicit cloud environment authority."},\n  "coverage_map": [{"criterion": "add works", "tiers": ["unit"]}]\n}'


class TeachMeReportTests(unittest.TestCase):
    def test_teach_me_report_generates_html_markdown_json_and_checklist(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            shutil.copytree(ROOT, repo, dirs_exist_ok=True)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "T"], cwd=repo, check=True)

            for directory in ["docs/intents", "docs/context", "docs/expectations", "docs/task-contracts", "docs/validation-reports", "tasks"]:
                (repo / directory).mkdir(parents=True, exist_ok=True)
            (repo / "docs/intents/x.md").write_text("# Intent: X\n\n## Goal\nBuild a small calculator core.\n\n## Constraints\n- Simple Python.\n\n## Failure Conditions\n- Tests fail.\n", encoding="utf-8")
            subprocess.run([sys.executable, "-B", "scripts/assemble_context.py", "--intent", "docs/intents/x.md", "--output-json", "docs/context/x.json", "--output-md", "docs/context/x.md"], cwd=repo, check=True)
            ctx = json.loads((repo / "docs/context/x.json").read_text(encoding="utf-8"))
            ctx_files = [{"context_id": f["context_id"], "path": f["path"], "used_for": ["expectation_derivation", "task_decomposition"]} for f in ctx["project_context"]["included_files"]]
            task_context_files = [{"context_id": f["context_id"], "path": f["path"], "used_for": ["implementation", "review", "validation"]} for f in ctx["project_context"]["included_files"]]
            (repo / "docs/expectations/x.json").write_text(json.dumps({"schema_version":"1.0", "intent_id": "x", "source_context_id":"x", "source_context":{"context_pack_path":"docs/context/x.json", "context_pack_id":"x", "project_context_files":ctx_files, "omitted_project_context_files":[]}, "success_scenarios":["add works"], "failure_scenarios":["tests fail"], "acceptance_criteria": ["add works"], "validation_strategy":["unit test"], "testing_expectations_matrix":[{"behavior_or_risk":"add works","unit":"Required","integration":"Not required: no boundary","local_e2e":"Not required: no pipeline","cloud_e2e":"Not required: no authority"}], "required_testing_tiers":{"unit":{"required":True,"reason":"logic"},"integration":{"required":False,"reason":"no boundary"},"local_e2e":{"required":False,"reason":"no pipeline"},"cloud_e2e":{"required":False,"reason":"no authority"}}}), encoding="utf-8")
            (repo / "docs/validation-reports/x-expectations-validation.json").write_text(json.dumps({"schema_version":"1.0","agent":"expectation-validation-agent","intent_id":"x","verdict":"PASS","schema_validation":{"status":"PASS","schema":"schemas/expectations.schema.json","errors":[]},"semantic_checks":[],"findings":[],"model_routing":{"alias":"validation_reasoning","selected_model":"test-model"},"validated_at":"2026-01-01T00:00:00+00:00"}), encoding="utf-8")
            (repo / "docs/task-contracts/x.json").write_text(json.dumps({"schema_version": "1.0", "intent_id": "x", "epics":[{"epic_id":"E-1","name":"Foundation","goal":"Build add","sequencing_rationale":"Smallest slice","risk_level":"low"}], "tasks": [{"task_id": "T-1", "epic_id":"E-1", "objective": "Add", "behavior": "Expose add", "scope": ["src/calc.py"], "allowed_paths":["src/**","tests/**"], "forbidden_paths":["docs/intents/**"], "non_goals":[], "dependencies": [], "acceptance_criteria": ["add works"], "negative_cases": [], "verification": {"commands": ["python -V"]}, "required_reviewers": ["test-agent"], "risk_level": "low", "required_context":[f["context_id"] for f in ctx["project_context"]["included_files"]], "context_files":task_context_files, "test_expectations": json.loads(TEST_EXPECTATIONS_FIXTURE)}]}), encoding="utf-8")
            (repo / "docs/validation-reports/x-task-contract-validation.json").write_text(json.dumps({"schema_version":"1.0","agent":"task-contract-validation-agent","intent_id":"x","verdict":"PASS","schema_validation":{"status":"PASS","schema":"schemas/task-contracts.schema.json","errors":[]},"epic_checks":[],"test_expectation_checks":[],"dependency_checks":[],"context_checks":[],"findings":[],"model_routing":{"alias":"validation_reasoning","selected_model":"test-model"},"validated_at":"2026-01-01T00:00:00+00:00"}), encoding="utf-8")
            subprocess.run([sys.executable, "-B", "scripts/prepare_run.py", "--run-id", "r1", "--intent", "docs/intents/x.md", "--context", "docs/context/x.json", "--expectations", "docs/expectations/x.json", "--tasks", "docs/task-contracts/x.json", "--expectation-validation", "docs/validation-reports/x-expectations-validation.json", "--task-validation", "docs/validation-reports/x-task-contract-validation.json", "--output", "tasks/run_manifest.draft.json", "--state-output", "tasks/run_state.json", "--feature-output", "tasks/feature_list.json"], cwd=repo, check=True, timeout=30)
            manifest = json.loads((repo / "tasks/run_manifest.draft.json").read_text(encoding="utf-8"))
            manifest["status"] = "approved"
            (repo / "tasks/run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            features = json.loads((repo / "tasks/feature_list.json").read_text(encoding="utf-8"))
            features["tasks"][0]["status"] = "passed"
            features["tasks"][0]["implementation"]["commit_sha"] = "abc123"
            features["tasks"][0]["implementation"]["files_changed"] = ["src/calc.py", "tests/test_calc.py"]
            features["tasks"][0]["validator"]["status"] = "passed"
            (repo / "tasks/feature_list.json").write_text(json.dumps(features), encoding="utf-8")
            subprocess.run(["git", "commit", "--allow-empty", "-q", "-m", "fixture"], cwd=repo, check=True)

            p = subprocess.run([sys.executable, "-B", "scripts/teach_me_report.py"], cwd=repo, text=True, capture_output=True)
            self.assertEqual(0, p.returncode, p.stdout + p.stderr)
            result = json.loads(p.stdout)
            self.assertEqual("PASS", result["verdict"])
            for key in ["json", "markdown", "html", "checklist"]:
                self.assertTrue((repo / result["paths"][key]).is_file(), key)
            html = (repo / result["paths"]["html"]).read_text(encoding="utf-8")
            self.assertIn("Mental model", html)
            self.assertIn("Task outcomes", html)
            self.assertIn("Testing hierarchy coverage", html)


if __name__ == "__main__":
    unittest.main()
