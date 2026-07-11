#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, sha256_file, load_json, write_json, utc_now

def rel(repo,p):
    path=Path(p); return str((path if path.is_absolute() else repo/path).relative_to(repo))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run-id', required=True); ap.add_argument('--intent', required=True); ap.add_argument('--context', required=True); ap.add_argument('--expectations', required=True); ap.add_argument('--tasks', required=True); ap.add_argument('--expectation-validation', required=True); ap.add_argument('--output', required=True); ap.add_argument('--state-output', required=True); ap.add_argument('--feature-output', required=True); args=ap.parse_args()
    repo=repository_root(); task_doc=load_json(repo/args.tasks); task_ids=[t['task_id'] for t in task_doc.get('tasks',[])]
    artifacts=[]
    for kind,path in [('intent',args.intent),('context',args.context),('expectations',args.expectations),('task_contracts',args.tasks),('expectation_validation',args.expectation_validation)]:
        p=repo/path
        artifacts.append({'kind':kind,'path':str(p.relative_to(repo)),'sha256':sha256_file(p)})
    manifest={'schema_version':'1.0','run_id':args.run_id,'status':'draft','created_at':utc_now(),'idsd':{'intent':args.intent,'context':args.context,'expectations':args.expectations},'scope':{'task_ids':task_ids},'source_artifacts':artifacts,'execution_policy':{'allow_git_push':False,'allow_pull_request_creation':False,'max_repair_attempts_per_task':3}}
    state={'schema_version':'1.0','run_id':args.run_id,'status':'draft','current_stage':'not_started','current_task_id':None,'completed_task_ids':[],'blocked_task_ids':[],'deferred_task_ids':[],'attempts':{},'actions':[],'last_updated_at':utc_now()}
    features={'schema_version':'1.0','run_id':args.run_id,'tasks':[]}
    for t in task_doc.get('tasks',[]):
        features['tasks'].append({'task_id':t['task_id'],'epic_id':t.get('epic_id'),'status':'pending','implementation':{'files_changed':[],'commit_sha':None},'verification':{'status':'pending','evidence':[]},'reviews':{r:{'status':'pending','findings':[]} for r in t.get('required_reviewers',[])},'domain_review':{'status':'not_required','findings':[]},'validator':{'status':'pending','findings':[]}})
    write_json(repo/args.output,manifest); write_json(repo/args.state_output,state); write_json(repo/args.feature_output,features)
    print(json.dumps({'verdict':'PASS','manifest':args.output,'tasks':task_ids},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
