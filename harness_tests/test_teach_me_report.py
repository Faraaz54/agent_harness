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
            (repo / "docs/context/x.json").write_text(json.dumps({"intent_id": "x"}), encoding="utf-8")
            (repo / "docs/expectations/x.json").write_text(json.dumps({"intent_id": "x", "acceptance_criteria": ["add works"]}), encoding="utf-8")
            (repo / "docs/task-contracts/x.json").write_text(json.dumps({"schema_version": "1.0", "intent_id": "x", "tasks": [{"task_id": "T-1", "objective": "Add", "behavior": "Expose add", "scope": ["src/calc.py"], "dependencies": [], "acceptance_criteria": ["add works"], "negative_cases": [], "verification": {"commands": ["python -V"]}, "required_reviewers": ["test-agent"], "risk_level": "low", "test_expectations": json.loads(TEST_EXPECTATIONS_FIXTURE)}]}), encoding="utf-8")
            (repo / "docs/validation-reports/x-expectations-validation.md").write_text("PASS", encoding="utf-8")
            subprocess.run([sys.executable, "-B", "scripts/prepare_run.py", "--run-id", "r1", "--intent", "docs/intents/x.md", "--context", "docs/context/x.json", "--expectations", "docs/expectations/x.json", "--tasks", "docs/task-contracts/x.json", "--expectation-validation", "docs/validation-reports/x-expectations-validation.md", "--output", "tasks/run_manifest.draft.json", "--state-output", "tasks/run_state.json", "--feature-output", "tasks/feature_list.json"], cwd=repo, check=True)
            manifest = json.loads((repo / "tasks/run_manifest.draft.json").read_text(encoding="utf-8"))
            manifest["status"] = "approved"
            (repo / "tasks/run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            features = json.loads((repo / "tasks/feature_list.json").read_text(encoding="utf-8"))
            features["tasks"][0]["status"] = "passed"
            features["tasks"][0]["implementation"]["commit_sha"] = "abc123"
            features["tasks"][0]["implementation"]["files_changed"] = ["src/calc.py", "tests/test_calc.py"]
            features["tasks"][0]["validator"]["status"] = "passed"
            (repo / "tasks/feature_list.json").write_text(json.dumps(features), encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True)

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
