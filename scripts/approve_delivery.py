#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timedelta, timezone
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, current_branch, sha256_file, git_runtime_dir, utc_now

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--approved-by', required=True); ap.add_argument('--hours', type=int, default=24); ap.add_argument('--allow-ready', action='store_true'); args=ap.parse_args(); repo=repository_root()
    manifest=load_json(repo/'tasks/run_manifest.json'); run_id=manifest['run_id']; out=git_runtime_dir(repo)/'approvals'/f'{run_id}-delivery.json'
    approval={'schema_version':'1.0','run_id':run_id,'manifest_sha256':sha256_file(repo/'tasks/run_manifest.json'),'branch':current_branch(repo),'approved_by':args.approved_by,'approved_at':utc_now(),'expires_at':(datetime.now(timezone.utc)+timedelta(hours=args.hours)).isoformat(),'allow_git_push':True,'allow_pull_request_creation':True,'allow_ready_pull_request':bool(args.allow_ready)}
    write_json(out, approval); print(json.dumps({'verdict':'PASS','approval':str(out)}, indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
