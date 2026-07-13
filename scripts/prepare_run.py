#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, sha256_file, load_json, write_json, utc_now, validate_json_schema

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--intent', required=True)
    ap.add_argument('--context', required=True)
    ap.add_argument('--expectations', required=True)
    ap.add_argument('--tasks', required=True)
    ap.add_argument('--technical-spec', required=True)
    ap.add_argument('--technical-spec-validation', required=True)
    ap.add_argument('--expectation-validation', required=True)
    ap.add_argument('--task-validation')
    ap.add_argument('--output', required=True)
    ap.add_argument('--state-output', required=True)
    ap.add_argument('--feature-output', required=True)
    args=ap.parse_args()
    repo=repository_root()
    # Deterministic planning-side validation before run authority exists.
    validate_json_schema(repo/args.context, repo/'schemas/context-pack.schema.json')
    validate_json_schema(repo/args.expectations, repo/'schemas/expectations.schema.json')
    validate_json_schema(repo/args.technical_spec, repo/'schemas/technical-spec.schema.json')
    validate_json_schema(repo/args.technical_spec_validation, repo/'schemas/technical-spec-validation-result.schema.json')
    validate_json_schema(repo/args.tasks, repo/'schemas/task-contracts.schema.json')
    validate_json_schema(repo/args.expectation_validation, repo/'schemas/expectation-validation-result.schema.json')
    if args.task_validation:
        validate_json_schema(repo/args.task_validation, repo/'schemas/task-contract-validation-result.schema.json')
    task_doc=load_json(repo/args.tasks); task_ids=[t['task_id'] for t in task_doc.get('tasks',[])]
    artifacts=[]
    base=[('intent',args.intent),('context',args.context),('expectations',args.expectations),('technical_spec',args.technical_spec),('technical_spec_validation',args.technical_spec_validation),('task_contracts',args.tasks),('expectation_validation',args.expectation_validation)]
    if args.task_validation:
        base.append(('task_contract_validation', args.task_validation))
    for kind,path in base:
        p=repo/path
        artifacts.append({'kind':kind,'path':str(p.relative_to(repo)),'sha256':sha256_file(p)})
    manifest={'schema_version':'1.0','run_id':args.run_id,'status':'draft','created_at':utc_now(),'idsd':{'intent':args.intent,'context':args.context,'expectations':args.expectations,'technical_spec':args.technical_spec,'technical_spec_validation':args.technical_spec_validation,'task_contracts':args.tasks,'expectation_validation':args.expectation_validation,'task_validation':args.task_validation},'scope':{'task_ids':task_ids},'source_artifacts':artifacts,'execution_policy':{'allow_git_push':False,'allow_pull_request_creation':False,'max_repair_attempts_per_task':3}}
    state={'schema_version':'1.0','run_id':args.run_id,'status':'draft','current_stage':'not_started','current_task_id':None,'completed_task_ids':[],'blocked_task_ids':[],'deferred_task_ids':[],'attempts':{},'actions':[],'last_updated_at':utc_now()}
    features={'schema_version':'1.0','run_id':args.run_id,'tasks':[]}
    for t in task_doc.get('tasks',[]):
        features['tasks'].append({'task_id':t['task_id'],'epic_id':t.get('epic_id'),'status':'pending','required_context':t.get('required_context',[]),'context_files':t.get('context_files',[]),'technical_spec_refs':t.get('technical_spec_refs',[]),'implementation':{'files_changed':[],'commit_sha':None},'verification':{'status':'pending','evidence':[]},'reviews':{r:{'status':'pending','findings':[]} for r in t.get('required_reviewers',[])},'domain_review':{'status':'not_required','findings':[]},'validator':{'status':'pending','findings':[]}})
    write_json(repo/args.output,manifest); write_json(repo/args.state_output,state); write_json(repo/args.feature_output,features)
    print(json.dumps({'verdict':'PASS','manifest':args.output,'tasks':task_ids},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
