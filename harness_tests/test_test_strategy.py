from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEST_EXPECTATIONS = {
    "highest_required_tier": "local_e2e",
    "tier_rationale": "Pipeline task touches persistence and multi-stage data flow.",
    "unit": {"required": True, "what_to_test": ["parser"], "evidence_required": ["unit test output"]},
    "integration": {"required": True, "what_to_test": ["local db writes"], "evidence_required": ["integration test output"]},
    "local_e2e": {"required": True, "what_to_test": ["fixture to output"], "evidence_required": ["local e2e output"]},
    "cloud_e2e": {"required": False, "what_to_test": [], "evidence_required": [], "not_required_reason": "No explicit environment authority."},
    "coverage_map": [{"criterion": "lineage retained", "tiers": ["integration", "local_e2e"]}],
}


def test_test_strategy_validate_passes():
    out = subprocess.run([sys.executable, "-B", "scripts/test_strategy.py", "validate"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert out.returncode == 0, out.stdout
    assert '"verdict": "PASS"' in out.stdout


def test_test_strategy_classifies_pipeline_task(tmp_path):
    contracts = tmp_path / "tasks.json"
    contracts.write_text(json.dumps({"tasks": [{"task_id": "T1", "objective": "Build ingestion pipeline writing bronze and silver tables with idempotency"}]}))
    out = subprocess.run([sys.executable, "-B", "scripts/test_strategy.py", "classify", "--contracts", str(contracts), "--task-id", "T1"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert out.returncode == 0, out.stdout
    data = json.loads(out.stdout)
    assert data["highest_required_tier"] == "local_e2e"
    assert "integration" in data["required_tiers"]
    assert "test_expectations missing" in data["warning"]


def test_test_strategy_validate_contracts_passes_when_all_tiers_declared(tmp_path):
    contracts = tmp_path / "tasks.json"
    contracts.write_text(json.dumps({"tasks": [{"task_id": "T1", "test_expectations": TEST_EXPECTATIONS}]}))
    out = subprocess.run([sys.executable, "-B", "scripts/test_strategy.py", "validate-contracts", "--contracts", str(contracts)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert out.returncode == 0, out.stdout
    data = json.loads(out.stdout)
    assert data["verdict"] == "PASS"


def test_test_strategy_validate_contracts_rejects_missing_non_required_reason(tmp_path):
    contracts = tmp_path / "tasks.json"
    bad = json.loads(json.dumps(TEST_EXPECTATIONS))
    bad["cloud_e2e"].pop("not_required_reason")
    contracts.write_text(json.dumps({"tasks": [{"task_id": "T1", "test_expectations": bad}]}))
    out = subprocess.run([sys.executable, "-B", "scripts/test_strategy.py", "validate-contracts", "--contracts", str(contracts)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert out.returncode == 1, out.stdout
    data = json.loads(out.stdout)
    assert data["verdict"] == "FAIL"
    assert any("cloud_e2e" in error for error in data["errors"])
