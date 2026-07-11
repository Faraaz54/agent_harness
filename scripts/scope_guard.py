#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, load_config, changed_files

def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pat) or path == pat for pat in patterns)

def task_contract(repo: Path, task_id: str) -> dict:
    manifest=load_json(repo/'tasks/run_manifest.json')
    contract_path=None
    for a in manifest.get('source_artifacts',[]):
        if a.get('kind')=='task_contracts': contract_path=repo/a['path']
    if not contract_path: raise RuntimeError('task_contracts artifact missing from manifest')
    doc=load_json(contract_path)
    for t in doc.get('tasks',[]):
        if t.get('task_id')==task_id: return t
    raise RuntimeError(f'task not found: {task_id}')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--task-id', required=True); args=ap.parse_args(); repo=repository_root(); cfg=load_config(repo); task=task_contract(repo,args.task_id)
    allowed=task.get('allowed_paths') or task.get('scope',{}).get('allowed_paths') or []
    forbidden=(cfg.get('scope_control',{}).get('default_forbidden_paths',[]) + task.get('forbidden_paths',[]) + task.get('scope',{}).get('forbidden_paths',[]))
    governance=cfg.get('scope_control',{}).get('allow_governance_paths',[])
    errors=[]; inspected=changed_files(repo)
    for rel in inspected:
        if matches(rel, forbidden): errors.append({'path':rel,'reason':'forbidden_path'})
        elif allowed and not (matches(rel, allowed) or matches(rel, governance)):
            errors.append({'path':rel,'reason':'outside_allowed_paths'})
    verdict='FAIL' if errors else 'PASS'
    print(json.dumps({'verdict':verdict,'task_id':args.task_id,'changed_files':inspected,'violations':errors}, indent=2)); return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
