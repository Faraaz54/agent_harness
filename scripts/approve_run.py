#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, utc_now

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--draft', required=True); ap.add_argument('--approved-output', required=True); ap.add_argument('--approval-output', required=True); ap.add_argument('--approved-by', required=True); args=ap.parse_args()
    repo=repository_root(); m=load_json(repo/args.draft); m['status']='approved'; m['approved_at']=utc_now(); m['approved_by']=args.approved_by
    write_json(repo/args.approved_output,m); write_json(repo/args.approval_output,{'run_id':m['run_id'],'approved_by':args.approved_by,'approved_at':m['approved_at'],'manifest':args.approved_output})
    print(json.dumps({'verdict':'PASS','approved_manifest':args.approved_output},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
