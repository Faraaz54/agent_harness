#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
sys.dont_write_bytecode=True
from harnesslib import repository_root, validate_active_preflight, run_gate_group, working_tree_fingerprint, save_preflight_state

def run_optional(cmd: list[str], repo):
    p=subprocess.run(cmd,cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try: data=json.loads(p.stdout or '{}')
    except Exception: data={'verdict':'FAIL','stdout':p.stdout,'stderr':p.stderr}
    return p.returncode, data

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--task-id', required=True); args=ap.parse_args(); repo=repository_root(); ok,msg,state=validate_active_preflight(repo)
    if not ok: print(json.dumps({'verdict':'FAIL','error':msg},indent=2)); return 1
    checks=[]; verdict='PASS'
    for name,cmd in [('scope_guard',[sys.executable,'-B','scripts/scope_guard.py','--task-id',args.task_id]),('secret_scan',[sys.executable,'-B','scripts/secret_scan.py','--changed-only'])]:
        rc,data=run_optional(cmd,repo); checks.append({'name':name,'returncode':rc,'result':data})
        if rc!=0: verdict='FAIL'
    report=run_gate_group(repo,'post_implementation'); checks.append({'name':'configured_gates','result':report})
    if report['verdict']!='PASS': verdict='FAIL'
    fp=working_tree_fingerprint(repo)
    result={'task_id':args.task_id,'verdict':verdict,'checks':checks,'report_path':report['report_path'],'working_tree_fingerprint':fp,'stale':False}
    state['last_postflight']=result; save_preflight_state(repo,state); print(json.dumps(result,indent=2)); return 0 if verdict=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
