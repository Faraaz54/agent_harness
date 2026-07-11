#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, uuid
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, sha256_file, utc_now, load_config

def ledger_path(repo: Path, run_id: str) -> Path:
    cfg=load_config(repo); tmpl=cfg.get('evidence',{}).get('ledger_path','docs/evidence/{run_id}/evidence-ledger.json')
    return repo/tmpl.format(run_id=run_id)

def ensure(repo: Path, run_id: str) -> dict:
    p=ledger_path(repo,run_id)
    if p.exists(): return load_json(p)
    obj={'schema_version':'1.0','run_id':run_id,'created_at':utc_now(),'updated_at':utc_now(),'entries':[]}
    write_json(p,obj); return obj

def add(repo: Path, run_id: str, path: str, kind: str, task_id: str|None, verdict: str|None, tier: str|None) -> dict:
    obj=ensure(repo,run_id); p=repo/path
    entry={'evidence_id':'ev-'+uuid.uuid4().hex[:10], 'task_id':task_id, 'kind':kind, 'tier':tier, 'path':path, 'sha256':sha256_file(p) if p.exists() and p.is_file() else None, 'created_at':utc_now(), 'producer':'evidence_ledger.py', 'verdict':verdict}
    obj['entries'].append(entry); obj['updated_at']=utc_now(); write_json(ledger_path(repo,run_id),obj); return entry

def scan(repo: Path, run_id: str) -> dict:
    obj=ensure(repo,run_id)
    for base,kind in [('docs/implementation-results','implementation'),('docs/reviews','review'),('docs/validation-results','validation'),('docs/commit-results','commit'),('docs/test-evidence','test')]:
        for p in (repo/base).rglob('*.json') if (repo/base).exists() else []:
            rel=str(p.relative_to(repo))
            if any(e.get('path')==rel for e in obj['entries']): continue
            try: verdict=load_json(p).get('verdict')
            except Exception: verdict=None
            obj['entries'].append({'evidence_id':'ev-'+uuid.uuid4().hex[:10],'task_id':None,'kind':kind,'tier':None,'path':rel,'sha256':sha256_file(p),'created_at':utc_now(),'producer':'evidence_ledger.py scan','verdict':verdict})
    obj['updated_at']=utc_now(); write_json(ledger_path(repo,run_id), obj); return obj

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
    for c in ['init','scan','show']:
        sp=sub.add_parser(c); sp.add_argument('--run-id')
    addp=sub.add_parser('add'); addp.add_argument('--run-id'); addp.add_argument('--path', required=True); addp.add_argument('--kind', required=True); addp.add_argument('--task-id'); addp.add_argument('--verdict'); addp.add_argument('--tier')
    args=ap.parse_args(); repo=repository_root(); run_id=args.run_id or load_json(repo/'tasks/run_manifest.json')['run_id']
    if args.cmd=='init': out=ensure(repo,run_id)
    elif args.cmd=='scan': out=scan(repo,run_id)
    elif args.cmd=='show': out=ensure(repo,run_id)
    else: out={'verdict':'PASS','entry':add(repo,run_id,args.path,args.kind,args.task_id,args.verdict,args.tier)}
    print(json.dumps(out,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
