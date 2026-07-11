#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
sys.dont_write_bytecode=True
from pathlib import Path
from harnesslib import repository_root, load_config, verify_manifest, sha256_file, branch_is_protected, current_branch, current_head, git_status, git, run_gate_group, save_preflight_state, load_preflight_state, utc_now, HarnessError

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest', default='tasks/run_manifest.json'); ap.add_argument('--create-branch', action='store_true'); args=ap.parse_args()
    try:
        repo=repository_root(); cfg=load_config(repo); mp=repo/args.manifest; manifest=verify_manifest(repo,mp); run_id=manifest['run_id']
        existing=load_preflight_state(repo)
        if existing and existing.get('run_id')==run_id and existing.get('branch')==current_branch(repo) and existing.get('manifest_sha256')==sha256_file(mp) and existing.get('status')=='passed':
            existing['resumed_at']=utc_now(); save_preflight_state(repo,existing); print(json.dumps(existing,indent=2)); return 0
        if cfg.get('bootstrap',{}).get('required_before_preflight',True):
            br=run_gate_group(repo,'baseline')
            if br['verdict']!='PASS': raise HarnessError('baseline/bootstrap gates failed: '+br['report_path'])
        if cfg['repository'].get('require_clean_start',True) and git_status(repo):
            raise HarnessError('working tree is not clean before implementation')
        branch=current_branch(repo); base_branch=branch; base_head=current_head(repo)
        if args.create_branch:
            target=cfg['repository'].get('run_branch_pattern','agent/{run_id}').format(run_id=run_id)
            git(repo,'switch','-c',target); branch=target
        if branch_is_protected(branch,cfg): raise HarnessError(f'protected branch: {branch}')
        state={'schema_version':'1.0','run_id':run_id,'status':'passed','active':True,'branch':branch,'base_branch':base_branch,'base_head':base_head,'manifest_path':args.manifest,'manifest_sha256':sha256_file(mp),'started_at':utc_now(),'baseline_report':'see preflight action'}
        save_preflight_state(repo,state); print(json.dumps(state,indent=2)); return 0
    except Exception as e:
        print(json.dumps({'verdict':'FAIL','error':str(e)},indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
