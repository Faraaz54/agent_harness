#!/usr/bin/env python3
from __future__ import annotations

import fnmatch, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

class HarnessError(Exception):
    pass

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_command(cmd: list[str], cwd: Path, timeout: int = 120, check: bool = False) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if check and p.returncode != 0:
        raise HarnessError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n{p.stderr or p.stdout}")
    return p

def repository_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    p = run_command(["git", "rev-parse", "--show-toplevel"], start, check=False)
    if p.returncode == 0 and p.stdout.strip():
        return Path(p.stdout.strip()).resolve()
    # allow harness validation outside git
    if (start / "harness.config.json").exists():
        return start
    raise HarnessError("Not inside a Git repository and no harness.config.json at current directory")

def git(repo: Path, *args: str, check: bool = True) -> str:
    return run_command(["git", *args], repo, check=check).stdout.strip()

def current_branch(repo: Path) -> str:
    return git(repo, "branch", "--show-current", check=False) or "DETACHED"

def current_head(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD")

def git_status(repo: Path) -> list[str]:
    out = git(repo, "status", "--porcelain", check=False)
    return [line for line in out.splitlines() if line.strip()]

def git_runtime_dir(repo: Path) -> Path:
    out = git(repo, "rev-parse", "--git-path", "agent-harness", check=False)
    path = repo / ".git" / "agent-harness" if not out else (repo / out if not Path(out).is_absolute() else Path(out))
    path.mkdir(parents=True, exist_ok=True)
    return path

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise HarnessError(f"JSON root must be object: {path}")
    return obj

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_config(repo: Path) -> dict[str, Any]:
    return load_json(repo / "harness.config.json")

def branch_is_protected(branch: str, config: dict[str, Any]) -> bool:
    repo_cfg = config.get("repository", {})
    if branch in repo_cfg.get("protected_branches", []):
        return True
    return any(re.search(pat, branch) for pat in repo_cfg.get("protected_branch_patterns", []))

def state_path(repo: Path) -> Path:
    return git_runtime_dir(repo) / "preflight.json"

def load_preflight_state(repo: Path) -> dict[str, Any] | None:
    p = state_path(repo)
    return load_json(p) if p.is_file() else None

def save_preflight_state(repo: Path, state: dict[str, Any]) -> None:
    write_json(state_path(repo), state)

def working_tree_fingerprint(repo: Path) -> str:
    """Hash final working-tree content independent of index/staging state."""
    tracked = set(git(repo, "ls-files", check=False).splitlines())
    untracked = set(git(repo, "ls-files", "--others", "--exclude-standard", check=False).splitlines())
    paths = sorted(tracked | untracked)
    h = hashlib.sha256()
    for rel in paths:
        p = repo / rel
        h.update(rel.encode() + b"\0")
        if not p.exists():
            h.update(b"DELETED\0")
            continue
        if p.is_symlink():
            h.update(b"SYMLINK\0" + os.readlink(p).encode() + b"\0")
            continue
        if p.is_file():
            mode = p.stat().st_mode
            h.update(b"FILE\0" + (b"X" if mode & 0o111 else b"-") + b"\0")
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            h.update(b"\0")
    return h.hexdigest()

def verify_manifest(repo: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("status") != "approved":
        raise HarnessError("Run manifest is not approved")
    for art in manifest.get("source_artifacts", []):
        p = repo / art["path"]
        if not p.exists():
            raise HarnessError(f"Source artifact missing: {art['path']}")
        if art.get("sha256") != sha256_file(p):
            raise HarnessError(f"Source artifact hash mismatch: {art['path']}")
    return manifest

def validate_active_preflight(repo: Path) -> tuple[bool, str, dict[str, Any] | None]:
    state = load_preflight_state(repo)
    if not state:
        return False, "Missing preflight state", None
    if not state.get("active") or state.get("status") != "passed":
        return False, "Preflight is not active/passed", state
    if current_branch(repo) != state.get("branch"):
        return False, "Current branch does not match preflight branch", state
    manifest_path = repo / state.get("manifest_path", "")
    if not manifest_path.exists():
        return False, "Manifest referenced by preflight is missing", state
    if sha256_file(manifest_path) != state.get("manifest_sha256"):
        return False, "Manifest changed after preflight", state
    return True, "ok", state

def command_to_argv(command: Any) -> list[str]:
    if isinstance(command, list) and all(isinstance(x, str) for x in command):
        return command
    if isinstance(command, str):
        return command.split()
    raise HarnessError(f"Gate command must be string or list[str], got {type(command).__name__}")

def path_matches_any(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pat) or rel == pat for pat in patterns)

def changed_files(repo: Path) -> list[str]:
    out = git(repo, "status", "--porcelain", check=False)
    files: list[str] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        rel = line[3:].strip()
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        files.append(rel)
    return sorted(set(files))

def validate_json_schema(instance_path: Path, schema_path: Path) -> None:
    try:
        import jsonschema
    except Exception as exc:
        raise HarnessError(f"jsonschema is required for schema validation: {exc}")
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    try:
        jsonschema.Draft202012Validator(schema).validate(instance)
    except jsonschema.ValidationError as exc:
        where = "/".join(str(x) for x in exc.absolute_path)
        raise HarnessError(f"Schema validation failed for {instance_path} at {where or '<root>'}: {exc.message}")

def run_gate_group(repo: Path, group: str) -> dict[str, Any]:
    config = load_config(repo)
    results = []
    verdict = "PASS"
    for gate in config.get("gates", {}).get(group, []):
        if all(not (repo / p).exists() for p in gate.get("when_any_paths_exist", [])) and gate.get("when_any_paths_exist"):
            results.append({"id": gate["id"], "status": "SKIPPED"}); continue
        if any(not (repo / p).exists() for p in gate.get("when_all_paths_exist", [])):
            results.append({"id": gate["id"], "status": "SKIPPED"}); continue
        argv = command_to_argv(gate["command"])
        p = run_command(argv, repo, timeout=int(gate.get("timeout_seconds", 120)), check=False)
        status = "PASS" if p.returncode == 0 else ("FAIL" if gate.get("required", True) else "WARN")
        if status == "FAIL": verdict = "FAIL"
        results.append({"id": gate["id"], "status": status, "returncode": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:], "command": argv})
    report = {"group": group, "verdict": verdict, "ran_at": utc_now(), "results": results}
    out = git_runtime_dir(repo) / "gates" / f"{group}-{sha256_text(utc_now())[:8]}.json"
    write_json(out, report)
    report["report_path"] = str(out)
    return report
