#!/usr/bin/env python3
from __future__ import annotations
import json, re, uuid
from pathlib import Path
from typing import Any
from harnesslib import repository_root, git_runtime_dir, load_json, write_json, utc_now, validate_active_preflight, load_config
from model_router import action_model

RISK_ORDER={'low':1,'medium':2,'high':3,'critical':4}

def action_dir(repo: Path, run_id: str) -> Path:
    p=git_runtime_dir(repo)/'runs'/run_id/'actions'; p.mkdir(parents=True, exist_ok=True); return p

def context_dir(repo: Path, run_id: str) -> Path:
    p=git_runtime_dir(repo)/'runs'/run_id/'context'; p.mkdir(parents=True, exist_ok=True); return p

def new_action(repo: Path, run_id: str, action: str, task_id: str | None = None, **extra) -> dict[str, Any]:
    aid='act-'+uuid.uuid4().hex[:12]
    try:
        cfg = load_config(repo)
        model = action_model(cfg, action)
    except Exception:
        model = {'alias': None}
    obj={'schema_version':'1.0','action_id':aid,'run_id':run_id,'action':action,'task_id':task_id,'created_at':utc_now(),'model_routing':model,**extra}
    path=action_dir(repo,run_id)/f'{aid}.json'; write_json(path,obj); obj['action_path']=str(path); return obj

def action_by_id(repo: Path, run_id: str, action_id: str) -> dict[str, Any]:
    return load_json(action_dir(repo,run_id)/f'{action_id}.json')

def load_run(repo: Path):
    return load_json(repo/'tasks/run_manifest.json'), load_json(repo/'tasks/run_state.json'), load_json(repo/'tasks/feature_list.json'), load_json(repo/'docs/task-contracts'/Path(load_json(repo/'tasks/run_manifest.json')['source_artifacts'][3]['path']).name) if False else None

def task_contracts(repo: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    path=None
    for a in manifest.get('source_artifacts',[]):
        if a.get('kind')=='task_contracts': path=repo/a['path']
    if not path: return {}
    doc=load_json(path); return {t['task_id']: t for t in doc.get('tasks',[])}

def feature_map(features: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {t['task_id']: t for t in features.get('tasks',[])}

def save_feature(repo: Path, features: dict[str, Any]): write_json(repo/'tasks/feature_list.json', features)
def save_state(repo: Path, state: dict[str, Any]): state['last_updated_at']=utc_now(); write_json(repo/'tasks/run_state.json', state)

def dependencies_done(task: dict[str,Any], fm: dict[str,Any]) -> bool:
    return all(fm.get(dep,{}).get('status')=='passed' and fm.get(dep,{}).get('implementation',{}).get('commit_sha') for dep in task.get('dependencies',[]))

def domain_required(config: dict[str,Any], task: dict[str,Any]) -> bool:
    if not config.get('domain_review',{}).get('enabled',False): return False
    if 'domain-reviewer-agent' in task.get('required_reviewers',[]): return True
    threshold=config.get('domain_review',{}).get('required_when_risk_at_least','medium')
    return RISK_ORDER.get(task.get('risk_level','low'),1) >= RISK_ORDER.get(threshold,2) or bool(config.get('domain_review',{}).get('default_required'))

def _resolve_spec_section(spec: dict[str, Any], section: str) -> Any:
    current: Any = spec
    for part in section.replace('/', '.').split('.'):
        if not part:
            continue
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def task_context(repo: Path, manifest: dict[str,Any], task: dict[str,Any], attempt: int) -> Path:
    run_id=manifest['run_id']; p=context_dir(repo,run_id)/f"{task['task_id']}-attempt-{attempt}.json"
    idsd = manifest.get('idsd',{})
    context_path = idsd.get('context')
    context_pack = load_json(repo/context_path) if context_path and (repo/context_path).exists() else {}
    wanted = set(task.get('required_context', []))
    available = {f.get('context_id'): f for f in context_pack.get('project_context',{}).get('included_files', [])}
    selected_context_files = [available[cid] for cid in wanted if cid in available]

    spec_path = idsd.get('technical_spec')
    technical_spec = load_json(repo/spec_path) if spec_path and (repo/spec_path).exists() else {}
    selected_spec_sections = []
    for ref in task.get('technical_spec_refs', []):
        section = ref.get('section')
        selected_spec_sections.append({'section': section, 'reason': ref.get('reason'), 'content': _resolve_spec_section(technical_spec, section)})

    obj={'schema_version':'1.0','run_id':run_id,'task_id':task['task_id'],'attempt':attempt,'intent':idsd.get('intent'),'context':context_path,'expectations':idsd.get('expectations'),'technical_spec':spec_path,'technical_spec_validation':idsd.get('technical_spec_validation'),'task':task,'project_context':{'required_context':task.get('required_context',[]),'context_files':task.get('context_files',[]),'selected_context_files':selected_context_files},'technical_spec_context':{'technical_spec_refs':task.get('technical_spec_refs',[]),'selected_spec_sections':selected_spec_sections},'required_output':f"docs/implementation-results/{task['task_id']}-attempt-{attempt}.json"}
    write_json(p,obj); return p
