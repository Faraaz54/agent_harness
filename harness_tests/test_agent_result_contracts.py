from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_validator(kind: str, path: Path, task_id: str = "T-1", agent: str | None = None):
    cmd = [sys.executable, "-B", "scripts/agent_result_contracts.py", "validate", "--kind", kind, "--path", str(path.relative_to(ROOT)), "--task-id", task_id]
    if agent:
        cmd += ["--agent", agent]
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def write(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_implementation_result_contract_accepts_structured_output(tmp_path):
    path = ROOT / "tmp-agent-result-implementation.json"
    try:
        write(path, {
            "schema_version": "1.0",
            "agent": "build-agent",
            "task_id": "T-1",
            "attempt": 1,
            "verdict": "IMPLEMENTED_AWAITING_REVIEW",
            "active_skills": ["red-green-vertical-slice"],
            "files_read_before_write": ["src/a.py"],
            "files_changed": ["src/a.py", "tests/test_a.py"],
            "red_evidence": {"status": "FAILED_AS_EXPECTED", "summary": "test failed before implementation", "command": "pytest tests/test_a.py", "evidence_paths": []},
            "green_evidence": {"status": "PASS", "summary": "focused tests passed", "evidence_paths": []},
            "commands_run": [{"command": "pytest tests/test_a.py", "status": "PASS", "returncode": 0, "summary": "ok"}],
            "assumptions": [],
            "residual_concerns": [],
            "learning": {"summary": "Implemented minimal vertical slice", "repair_memory_candidates": []},
            "model_routing": {"alias": "execution_medium", "selected_model": "test-model", "fallback_used": False},
        })
        out = run_validator("implementation", path, agent="build-agent")
        assert out.returncode == 0, out.stdout
    finally:
        path.unlink(missing_ok=True)


def test_review_result_contract_rejects_prose_like_output(tmp_path):
    path = ROOT / "tmp-agent-result-review.json"
    try:
        write(path, {"task_id": "T-1", "verdict": "PASS", "summary": "Looks good"})
        out = run_validator("review", path, agent="test-agent")
        assert out.returncode == 1, out.stdout
        assert "FAIL" in out.stdout
    finally:
        path.unlink(missing_ok=True)


def test_domain_review_result_contract_accepts_structured_findings(tmp_path):
    path = ROOT / "tmp-agent-result-domain.json"
    try:
        write(path, {
            "schema_version": "1.0",
            "review_type": "domain",
            "reviewer": "domain-reviewer-agent",
            "project_pack": "generic-python",
            "domain_skill": "python-domain-review",
            "task_id": "T-1",
            "attempt": 1,
            "verdict": "CHANGES_REQUIRED",
            "domain_entities_reviewed": ["public API"],
            "invariants": [{"id": "API-001", "description": "API matches expectations", "status": "FAIL", "evidence": ["src/a.py"], "finding_ids": ["DR-001"]}],
            "findings": [{"id": "DR-001", "severity": "MAJOR", "title": "API mismatch", "problem": "Function name differs", "required_outcome": "Expose requested API", "evidence": ["src/a.py"], "blocks_completion": True}],
            "repair_guidance": {"allowed": True, "scope": ["src/a.py"], "do_not_change": ["docs/intents/**"]},
            "model_routing": {"alias": "domain_reasoning", "selected_model": "test-model", "fallback_used": False},
        })
        out = run_validator("domain-review", path, agent="domain-reviewer-agent")
        assert out.returncode == 0, out.stdout
    finally:
        path.unlink(missing_ok=True)
