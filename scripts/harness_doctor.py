#!/usr/bin/env python3
"""Read-only harness health check."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

REQUIRED = [
    "AGENTS.md",
    "harness.config.json",
    ".cursor/commands/build-auto.md",
    ".cursor/commands/build-next.md",
    ".cursor/commands/build-status.md",
    ".cursor/agents/build-agent.md",
    ".cursor/agents/test-agent.md",
    ".cursor/agents/principal-engineer-agent.md",
    ".cursor/agents/validator-agent.md",
    ".cursor/skills/build-orchestration/SKILL.md",
    ".cursor/skills/using-agent-skills/SKILL.md",
    "scripts/build_orchestrator.py",
    "scripts/model_router.py",
    "scripts/validate_harness.py",
    "schemas/orchestrator-action.schema.json",
    "schemas/model-routing.schema.json",
]


def run(cmd: list[str], root: Path) -> tuple[bool, str]:
    try:
        out = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        return out.returncode == 0, out.stdout.strip()[-1000:]
    except Exception as exc:  # read-only diagnostic, report instead of raising
        return False, str(exc)


def main() -> int:
    root = Path.cwd()
    checks = []
    for rel in REQUIRED:
        path = root / rel
        checks.append({"check": f"exists:{rel}", "status": "PASS" if path.exists() else "FAIL", "fix": f"restore {rel} from harness package"})
    git_ok, git_out = run(["git", "rev-parse", "--is-inside-work-tree"], root) if shutil.which("git") else (False, "git not on PATH")
    checks.append({"check": "git repository", "status": "PASS" if git_ok else "WARN", "detail": git_out, "fix": "run inside a git repository before implementation"})
    if (root / "scripts/check_python_syntax.py").exists():
        ok, out = run([sys.executable, "-B", "scripts/check_python_syntax.py", "scripts", "harness_tests"], root)
        checks.append({"check": "python syntax", "status": "PASS" if ok else "FAIL", "detail": out, "fix": "fix Python syntax errors reported above"})
    if (root / "scripts/validate_harness.py").exists():
        ok, out = run([sys.executable, "-B", "scripts/validate_harness.py", "."], root)
        checks.append({"check": "harness validation", "status": "PASS" if ok else "FAIL", "detail": out, "fix": "restore missing harness files or update validate_harness.py"})
    if (root / "scripts/model_router.py").exists():
        ok, out = run([sys.executable, "-B", "scripts/model_router.py", "validate"], root)
        checks.append({"check": "model routing", "status": "PASS" if ok else "FAIL", "detail": out, "fix": "fix harness.config.json:model_routing aliases/bindings"})
    bootstrap = root / "docs/bootstrap/environment.json"
    checks.append({"check": "bootstrap snapshot", "status": "PASS" if bootstrap.exists() else "WARN", "fix": "python -B scripts/bootstrap_environment.py"})
    try:
        config = json.loads((root / "harness.config.json").read_text())
        pack = config.get("project_pack", {})
        if pack.get("enabled"):
            pack_path = root / pack.get("path", "")
            checks.append({"check": "project pack path", "status": "PASS" if pack_path.exists() else "FAIL", "fix": "set project_pack.path to an existing pack or disable project_pack.enabled"})
    except Exception as exc:
        checks.append({"check": "harness.config.json parse", "status": "FAIL", "detail": str(exc), "fix": "fix JSON syntax"})
    status_order = {"FAIL": 2, "WARN": 1, "PASS": 0}
    worst = max(checks, key=lambda item: status_order[item["status"]])["status"] if checks else "PASS"
    print(json.dumps({"verdict": "FAIL" if worst == "FAIL" else "PASS_WITH_WARNINGS" if worst == "WARN" else "PASS", "checks": checks}, indent=2))
    return 1 if worst == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
