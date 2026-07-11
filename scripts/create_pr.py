#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, current_branch, git_status, git_runtime_dir

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--draft', action='store_true', default=True); args=ap.parse_args(); repo=repository_root(); manifest=load_json(repo/'tasks/run_manifest.json'); run_id=manifest['run_id']
    approval=git_runtime_dir(repo)/'approvals'/f'{run_id}-delivery.json'
    if not approval.exists(): print(json.dumps({'verdict':'DELIVERY_BLOCKED','error':'missing delivery approval'}, indent=2)); return 1
    if git_status(repo): print(json.dumps({'verdict':'DELIVERY_BLOCKED','error':'working tree is not clean'}, indent=2)); return 1
    meta=repo/'docs/pull-requests'/f'{run_id}.json'
    if not meta.exists(): print(json.dumps({'verdict':'DELIVERY_BLOCKED','error':'run prepare_pr.py first'}, indent=2)); return 1
    gh=subprocess.run(['gh','--version'], cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if gh.returncode!=0: print(json.dumps({'verdict':'DELIVERY_BLOCKED','error':'GitHub CLI unavailable'}, indent=2)); return 1
    print(json.dumps({'verdict':'DRY_READY','message':'Remote PR creation is intentionally not executed by the scaffold. Replace this with project-approved gh flow.','branch':current_branch(repo)}, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
