#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, socket, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, git_runtime_dir, write_json, load_json, utc_now, load_config, HarnessError

def lock_path(repo: Path, run_id: str) -> Path:
    p=git_runtime_dir(repo)/'runs'/run_id/'orchestrator.lock'; p.parent.mkdir(parents=True, exist_ok=True); return p

def is_stale(obj: dict, minutes: int) -> bool:
    # Conservative: require explicit --force-clear for stale parsing failure.
    return False

def acquire(repo: Path, run_id: str, action_id: str|None=None) -> dict:
    path=lock_path(repo,run_id)
    obj={'schema_version':'1.0','run_id':run_id,'pid':os.getpid(),'hostname':socket.gethostname(),'started_at':utc_now(),'last_heartbeat_at':utc_now(),'action_id':action_id}
    try:
        fd=os.open(str(path), os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(obj,f,indent=2); f.write('\n')
        return {'verdict':'PASS','lock':str(path),'acquired':True}
    except FileExistsError:
        existing=load_json(path)
        raise HarnessError(f"orchestrator lock already exists for run {run_id}: pid={existing.get('pid')} host={existing.get('hostname')}")

def release(repo: Path, run_id: str, force=False) -> dict:
    path=lock_path(repo,run_id)
    if not path.exists(): return {'verdict':'PASS','released':False,'reason':'no lock'}
    path.unlink()
    return {'verdict':'PASS','released':True,'lock':str(path)}

def status(repo: Path, run_id: str) -> dict:
    path=lock_path(repo,run_id)
    return {'verdict':'PASS','exists':path.exists(),'lock':str(path),'state':load_json(path) if path.exists() else None}

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True)
    for c in ['acquire','release','status']:
        sp=sub.add_parser(c); sp.add_argument('--run-id', required=True); sp.add_argument('--action-id')
    args=ap.parse_args(); repo=repository_root()
    try:
        if args.cmd=='acquire': out=acquire(repo,args.run_id,args.action_id)
        elif args.cmd=='release': out=release(repo,args.run_id)
        else: out=status(repo,args.run_id)
        print(json.dumps(out,indent=2)); return 0
    except Exception as e:
        print(json.dumps({'verdict':'FAIL','error':str(e)}, indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
