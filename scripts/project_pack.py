#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json
from project_context import discover as discover_context, validate_index as validate_context_index

def validate_pack(path: Path) -> dict:
    manifest=path/'project-pack.json'
    errors=[]
    if not manifest.exists(): errors.append('missing project-pack.json')
    else:
        obj=load_json(manifest)
        for key in ['name','version','compatible_harness_versions']:
            if not obj.get(key): errors.append(f'missing {key}')
        for rel in obj.get('required_files',[]):
            if not (path/rel).exists(): errors.append(f'missing required file {rel}')
    # v0.6.3: context/ is optional, but if present it must be UTF-8, supported, and indexable.
    context_index = discover_context(path, repository_root())
    context_errors = validate_context_index(context_index)
    errors.extend(context_errors)
    return {'verdict':'FAIL' if errors else 'PASS','pack':str(path),'errors':errors,'context_file_count':len(context_index.get('files', [])),'context_warnings':context_index.get('warnings', [])}

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
    st=sub.add_parser('status')
    vp=sub.add_parser('validate'); vp.add_argument('--pack')
    ac=sub.add_parser('activate'); ac.add_argument('--name', required=True)
    args=ap.parse_args(); repo=repository_root()
    if args.cmd=='status':
        cfg=load_json(repo/'harness.config.json'); out={'verdict':'PASS','active':cfg.get('project_pack')}
    elif args.cmd=='validate':
        out=validate_pack(repo/(args.pack or load_json(repo/'harness.config.json').get('project_pack',{}).get('path','project-packs/generic-python')))
    else:
        cfg=load_json(repo/'harness.config.json'); path=f'project-packs/{args.name}'; out=validate_pack(repo/path)
        if out['verdict']=='PASS':
            cfg['project_pack']={'enabled':True,'name':args.name,'path':path}; write_json(repo/'harness.config.json',cfg); out['activated']=args.name
    print(json.dumps(out,indent=2)); return 0 if out['verdict']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
