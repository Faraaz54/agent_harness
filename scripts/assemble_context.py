#!/usr/bin/env python3
"""Assemble a schema-valid IDSD Context Pack, including project-pack context/ files."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
from typing import Any
sys.dont_write_bytecode = True
from harnesslib import repository_root, load_config, load_json, write_json, utc_now, validate_json_schema
from project_context import discover as discover_project_context


def rel(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except Exception:
        return str(path)

def infer_intent_id(intent_path: Path) -> str:
    return intent_path.stem

def git_out(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""

def repo_summary(repo: Path) -> dict[str, Any]:
    top_dirs = sorted([p.name for p in repo.iterdir() if p.is_dir() and not p.name.startswith(".")])[:50]
    return {"root": str(repo), "branch": git_out(repo, "branch", "--show-current") or "UNKNOWN", "top_level_directories": top_dirs}

def load_optional_json(path: Path) -> dict[str, Any]:
    if path.exists():
        try: return load_json(path)
        except Exception as exc: return {"load_error": str(exc), "path": str(path)}
    return {"missing": True, "path": str(path)}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intent", required=True)
    ap.add_argument("--output-json")
    ap.add_argument("--output-md")
    ap.add_argument("--intent-id")
    args = ap.parse_args()
    repo = repository_root(); cfg = load_config(repo)
    intent_path = repo / args.intent
    intent_id = args.intent_id or infer_intent_id(intent_path)
    out_json = repo / (args.output_json or f"docs/context/{intent_id}.json")
    out_md = repo / (args.output_md or f"docs/context/{intent_id}.md")
    pack_cfg = cfg.get("project_pack", {})
    pack_path = repo / pack_cfg.get("path", "project-packs/generic-python")
    context_index = discover_project_context(pack_path, repo)
    included_files = []
    for f in context_index.get("files", []):
        item = dict(f)
        item["available_to_phases"] = item.pop("phase_availability")
        included_files.append(item)
    context_pack = {
        "schema_version": "1.0",
        "context_id": intent_id,
        "intent_id": intent_id,
        "created_at": utc_now(),
        "runtime": {"bootstrap": load_optional_json(repo / cfg.get("bootstrap", {}).get("json_path", "docs/bootstrap/environment.json"))},
        "repository": repo_summary(repo),
        "bootstrap": {"json_path": cfg.get("bootstrap", {}).get("json_path"), "markdown_path": cfg.get("bootstrap", {}).get("markdown_path")},
        "project_pack": {"enabled": bool(pack_cfg.get("enabled", True)), "name": pack_cfg.get("name", pack_path.name), "path": rel(repo, pack_path)},
        "project_context": {
            "context_folder": context_index.get("context_folder", rel(repo, pack_path / "context")),
            "selection_notes": "v0.6.3 simple mode: all supported UTF-8 files under the active project pack context/ folder are available to planning, implementation, review, validation, and teach-me phases. Task contracts must narrow required_context/context_files per task.",
            "phase_availability": ["assemble_context", "derive_expectations", "validate_expectations", "derive_tasks", "validate_tasks", "implementation", "review", "domain_review", "validation", "teach_me"],
            "included_files": included_files,
            "warnings": context_index.get("warnings", []),
        },
        "available_tools": ["python", "pytest", "git"],
        "testing": cfg.get("test_strategy", {}),
    }
    write_json(out_json, context_pack)
    validate_json_schema(out_json, repo / "schemas/context-pack.schema.json")
    lines = [f"# Context Pack: {intent_id}", "", f"Created: `{context_pack['created_at']}`", "", "## Active project pack", "", f"- Name: `{context_pack['project_pack']['name']}`", f"- Path: `{context_pack['project_pack']['path']}`", "", "## Project-pack context files", ""]
    if included_files:
        for f in included_files:
            lines += [f"### {f['context_id']} — {f['title']}", "", f"- Path: `{f['path']}`", f"- Kind: `{f['kind']}`", f"- SHA-256: `{f['sha256']}`", "", "```", f.get('content_excerpt',''), "```", ""]
    else:
        lines.append("No project-pack context files were discovered. Add Markdown/JSON/YAML/TXT files under `project-packs/<name>/context/`.")
    out_md.parent.mkdir(parents=True, exist_ok=True); out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"verdict":"PASS","context_json":rel(repo,out_json),"context_md":rel(repo,out_md),"project_context_file_count":len(included_files)}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
