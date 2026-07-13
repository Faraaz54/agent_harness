#!/usr/bin/env python3
"""Discover and validate simple project-pack context folders.

This intentionally supports a minimal setup: a project pack may contain a
`context/` folder with README plus one or more Markdown/JSON/YAML/TXT files.
The files are indexed into stable context cards and then embedded by
`assemble_context.py` into the active Context Pack.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any
sys.dont_write_bytecode = True
from harnesslib import repository_root, load_config, write_json, sha256_file, validate_json_schema

ALLOWED_EXTENSIONS = {".md": "markdown", ".txt": "text", ".json": "json", ".yaml": "yaml", ".yml": "yaml"}
PHASES = ["assemble_context", "derive_expectations", "validate_expectations", "derive_tasks", "validate_tasks", "implementation", "review", "domain_review", "validation", "teach_me"]
MAX_EXCERPT_CHARS = 6000

def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").upper()
    return s or "CONTEXT"

def title_for(path: Path, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.stem
    return path.stem.replace("_", " ").replace("-", " ").title()

def summary_for(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    return " ".join(lines[:3])[:500]

def active_pack_path(repo: Path) -> Path:
    cfg = load_config(repo)
    return repo / cfg.get("project_pack", {}).get("path", "project-packs/generic-python")

def discover(pack_path: Path, repo: Path) -> dict[str, Any]:
    manifest_path = pack_path / "project-pack.json"
    pack_name = pack_path.name
    if manifest_path.exists():
        try:
            pack_name = json.loads(manifest_path.read_text(encoding="utf-8")).get("name", pack_name)
        except Exception:
            pass
    context_dir = pack_path / "context"
    files = []
    warnings = []
    if not context_dir.exists():
        warnings.append(f"context folder not found: {context_dir.relative_to(repo)}")
    else:
        for path in sorted(context_dir.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            kind = ALLOWED_EXTENSIONS.get(path.suffix.lower())
            if not kind:
                warnings.append(f"ignored unsupported context file: {path.relative_to(repo)}")
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                warnings.append(f"ignored non-utf8 context file: {path.relative_to(repo)}")
                continue
            rel = path.relative_to(repo).as_posix()
            cid = "CTX-" + slug(pack_name) + "-" + slug(path.relative_to(context_dir).with_suffix("").as_posix())
            files.append({
                "context_id": cid,
                "path": rel,
                "kind": kind,
                "title": title_for(path, text),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
                "phase_availability": PHASES,
                "summary": summary_for(text),
                "content_excerpt": text[:MAX_EXCERPT_CHARS],
            })
    return {
        "schema_version": "1.0",
        "project_pack": pack_name,
        "context_folder": (context_dir.relative_to(repo).as_posix() if context_dir.exists() else str(context_dir)),
        "selection_strategy": "simple-folder-scan: include supported UTF-8 files under project-pack context/ for all planning/build/review phases; task contracts narrow usage.",
        "files": files,
        "warnings": warnings,
    }

def validate_index(index: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen = set()
    for f in index.get("files", []):
        cid = f.get("context_id")
        if cid in seen:
            errors.append(f"duplicate context_id: {cid}")
        seen.add(cid)
        if not f.get("content_excerpt"):
            errors.append(f"context file has empty excerpt: {f.get('path')}")
    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    idx = sub.add_parser("index"); idx.add_argument("--pack"); idx.add_argument("--output")
    val = sub.add_parser("validate"); val.add_argument("--pack"); val.add_argument("--output")
    args = ap.parse_args(); repo = repository_root()
    pack = repo / args.pack if args.pack else active_pack_path(repo)
    index = discover(pack, repo)
    errors = validate_index(index)
    if args.output:
        write_json(repo / args.output, index)
        try:
            validate_json_schema(repo / args.output, repo / "schemas/project-context-index.schema.json")
        except Exception as exc:
            errors.append(str(exc))
    out = {"verdict": "PASS" if not errors else "FAIL", "pack": str(pack.relative_to(repo) if pack.is_relative_to(repo) else pack), "context_file_count": len(index.get("files", [])), "errors": errors, "warnings": index.get("warnings", []), "index": index if args.cmd == "index" else None}
    print(json.dumps(out, indent=2))
    return 0 if out["verdict"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
