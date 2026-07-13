#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
from harnesslib import repository_root, load_json, write_json, load_config, validate_active_preflight, load_preflight_state, git_runtime_dir, utc_now, HarnessError, validate_json_schema
from orchestratorlib import new_action, action_by_id, task_contracts, feature_map, save_feature, save_state, dependencies_done, domain_required, task_context

def load_all(repo):
    return load_json(repo/'tasks/run_manifest.json'), load_json(repo/'tasks/run_state.json'), load_json(repo/'tasks/feature_list.json')

def pick_task(manifest, contracts, fm):
    for tid in manifest.get('scope',{}).get('task_ids',[]):
        t=contracts[tid]; f=fm[tid]
        if f.get('status') in ['passed','blocked','deferred']: continue
        if dependencies_done(t,fm): return tid
    return None

def next_action(repo: Path, *, once=False):
    cfg=load_config(repo); manifest,state,features=load_all(repo); run_id=manifest['run_id']; contracts=task_contracts(repo,manifest); fm=feature_map(features)
    ok,msg,pf=validate_active_preflight(repo)
    if not ok:
        return new_action(repo,run_id,'RUN_PREFLIGHT',command='python -B scripts/preflight.py --manifest tasks/run_manifest.json --create-branch')
    current=state.get('current_task_id')
    if not current:
        current=pick_task(manifest,contracts,fm)
        if not current:
            return new_action(repo,run_id,'FINALIZE_SESSION',command='python -B scripts/finalize_session.py')
        state['current_task_id']=current; state['current_stage']='selected'; save_state(repo,state)
    task=contracts[current]; f=fm[current]
    attempts=state.setdefault('attempts',{}).setdefault(current,{'implementation':0,'repair':0})
    status=f.get('status')
    if status in ['pending','in_progress']:
        attempts['implementation']+=1; save_state(repo,state); cp=task_context(repo,manifest,task,attempts['implementation'])
        f['status']='in_progress'; save_feature(repo,features)
        return new_action(repo,run_id,'IMPLEMENT_TASK',current,required_agent='build-agent',context_packet=str(cp),expected_output=f"docs/implementation-results/{current}-attempt-{attempts['implementation']}.json")
    if status=='changes_requested':
        if attempts.get('repair',0)>=manifest.get('execution_policy',{}).get('max_repair_attempts_per_task', cfg.get('orchestrator',{}).get('max_repair_attempts_per_task',3)):
            f['status']='blocked'; f.setdefault('blockers',[]).append({'reason':'repair budget exhausted','at':utc_now()}); save_feature(repo,features); state['blocked_task_ids']=sorted(set(state.get('blocked_task_ids',[])+[current])); state['current_task_id']=None; save_state(repo,state); return next_action(repo)
        attempts['repair']+=1; f['status']='in_progress'; save_feature(repo,features); save_state(repo,state)
        return new_action(repo,run_id,'REPAIR_TASK',current,required_agent='build-agent',expected_output=f"docs/implementation-results/{current}-repair-{attempts['repair']}.json")
    if status=='implemented':
        last=(pf or {}).get('last_postflight') or {}
        if last.get('task_id')!=current or last.get('verdict')!='PASS' or last.get('stale'):
            return new_action(repo,run_id,'RUN_POSTFLIGHT',current,command=f'python -B scripts/postflight.py --task-id {current}',expected_output=f'docs/postflight/{current}.json')
        # reviews
        for reviewer, rv in f.get('reviews',{}).items():
            if rv.get('status') in ['pending','changes_required']:
                return new_action(repo,run_id,'RUN_REVIEW',current,required_agent=reviewer,expected_output=f"docs/reviews/{current}/{reviewer}.json")
        if domain_required(cfg,task) and f.get('domain_review',{}).get('status') in ['not_required','pending','changes_required']:
            f.setdefault('domain_review',{})['status']='pending'; save_feature(repo,features)
            return new_action(repo,run_id,'RUN_DOMAIN_REVIEW',current,required_agent='domain-reviewer-agent',project_pack=cfg.get('project_pack',{}),expected_output=f"docs/reviews/{current}/domain-review.json")
        if f.get('validator',{}).get('status') in ['pending','rejected','changes_required']:
            return new_action(repo,run_id,'RUN_VALIDATOR',current,required_agent='validator-agent',expected_output=f"docs/validation-results/{current}-validator.json")
        if f.get('validator',{}).get('status')=='passed':
            last=(pf or {}).get('last_postflight') or {}
            from harnesslib import working_tree_fingerprint
            if last.get('task_id')!=current or last.get('verdict')!='PASS' or last.get('stale') or last.get('working_tree_fingerprint')!=working_tree_fingerprint(repo):
                return new_action(repo,run_id,'RUN_POSTFLIGHT',current,command=f'python -B scripts/postflight.py --task-id {current}',expected_output=f'docs/postflight/{current}.json')
            return new_action(repo,run_id,'COMMIT_TASK',current,command=f'python -B scripts/commit_task.py --task-id {current}',expected_output=f"docs/commit-results/{current}.json")
    return new_action(repo,run_id,'BLOCKED',current,reason=f'No transition for task status {status}')

SCHEMA_BY_ACTION = {
    'IMPLEMENT_TASK': 'schemas/implementation-result.schema.json',
    'REPAIR_TASK': 'schemas/implementation-result.schema.json',
    'RUN_POSTFLIGHT': 'schemas/postflight-result.schema.json',
    'RUN_REVIEW': 'schemas/review-result.schema.json',
    'RUN_DOMAIN_REVIEW': 'schemas/domain-review-result.schema.json',
    'RUN_VALIDATOR': 'schemas/task-validation.schema.json',
    'COMMIT_TASK': 'schemas/commit-result.schema.json',
}

def schema_for_action(repo: Path, action: dict) -> Path | None:
    action_name = action.get('action')
    if action_name == 'RUN_DOMAIN_REVIEW':
        cfg = load_config(repo)
        pack_name = cfg.get('project_pack', {}).get('active') or cfg.get('project_pack', {}).get('name')
        if pack_name:
            pack_schema = repo / 'project-packs' / pack_name / 'schemas' / 'domain-review-result.schema.json'
            if pack_schema.exists():
                return pack_schema
    schema = SCHEMA_BY_ACTION.get(action_name)
    return repo / schema if schema else None

def validate_result_for_action(repo: Path, action: dict, result_path: Path) -> dict:
    schema = schema_for_action(repo, action)
    if schema:
        validate_json_schema(result_path, schema)
    result = load_json(result_path)
    expected_task_id = action.get('task_id')
    if expected_task_id and result.get('task_id') != expected_task_id:
        raise HarnessError(f"Result task_id {result.get('task_id')} does not match action task_id {expected_task_id}")
    expected_agent = action.get('required_agent')
    if expected_agent:
        actual_agent = result.get('agent') or result.get('reviewer') or result.get('validator')
        if actual_agent and actual_agent != expected_agent:
            raise HarnessError(f"Result agent {actual_agent} does not match required agent {expected_agent}")
    return result

def record(repo: Path, action_id: str, result_path: Path):
    manifest,state,features=load_all(repo); run_id=manifest['run_id']; action=action_by_id(repo,run_id,action_id); result=validate_result_for_action(repo, action, result_path); fm=feature_map(features); tid=action.get('task_id')
    verdict=str(result.get('verdict') or result.get('status') or '').upper()
    if tid and tid in fm:
        f=fm[tid]
        if action['action']=='IMPLEMENT_TASK':
            if verdict in ['PASS','IMPLEMENTED','IMPLEMENTED_AWAITING_REVIEW']:
                f['status']='implemented'; f['implementation']['files_changed']=result.get('files_changed', f['implementation'].get('files_changed',[])); f['verification']=result.get('verification', f.get('verification',{}))
            else: f['status']='changes_requested'
        elif action['action']=='RUN_POSTFLIGHT':
            # postflight writes its durable state into .git/agent-harness/preflight.json.
            # Recording it here adds an auditable action receipt without changing task status.
            if verdict != 'PASS':
                f['status']='changes_requested'
        elif action['action']=='RUN_REVIEW':
            reviewer=action.get('required_agent','reviewer'); status='passed' if verdict in ['PASS','APPROVE','APPROVED'] else 'changes_required'
            f.setdefault('reviews',{}).setdefault(reviewer,{}) .update({'status':status,'findings':result.get('findings',[])})
            if status!='passed': f['status']='changes_requested'
        elif action['action']=='RUN_DOMAIN_REVIEW':
            status='passed' if verdict in ['PASS','APPROVE','APPROVED'] else 'changes_required'
            f.setdefault('domain_review',{}).update({'status':status,'findings':result.get('findings',[])})
            if status!='passed': f['status']='changes_requested'
        elif action['action']=='RUN_VALIDATOR':
            status='passed' if verdict in ['PASS','APPROVED'] else 'rejected'
            f.setdefault('validator',{}).update({'status':status,'findings':result.get('findings',[])})
            if status!='passed': f['status']='changes_requested'
        elif action['action']=='COMMIT_TASK':
            if verdict=='PASS':
                f['status']='passed'; f['implementation']['commit_sha']=result.get('commit_sha'); state['completed_task_ids']=sorted(set(state.get('completed_task_ids',[])+[tid])); state['current_task_id']=None; state['current_stage']='selecting_task'
            else: f['status']='changes_requested'
    state.setdefault('actions',[]).append({'action_id':action_id,'action':action['action'],'task_id':tid,'result':str(result_path),'verdict':verdict,'recorded_at':utc_now()})
    save_feature(repo,features); save_state(repo,state); print(json.dumps({'verdict':'PASS','recorded_action':action_id},indent=2)); return 0

def status(repo: Path):
    manifest,state,features=load_all(repo); print(json.dumps({'run_id':manifest['run_id'],'stage':state.get('current_stage'),'current_task_id':state.get('current_task_id'),'tasks':[{k:t.get(k) for k in ['task_id','status']} for t in features.get('tasks',[])]},indent=2)); return 0

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd', required=True); sub.add_parser('next'); sub.add_parser('status'); sub.add_parser('reconcile'); rr=sub.add_parser('record-result'); rr.add_argument('--action-id', required=True); rr.add_argument('--result', required=True)
    args=ap.parse_args(); repo=repository_root()
    try:
        if args.cmd=='next': print(json.dumps(next_action(repo),indent=2)); return 0
        if args.cmd=='status': return status(repo)
        if args.cmd=='reconcile': return status(repo)
        if args.cmd=='record-result': return record(repo,args.action_id,repo/args.result)
    except Exception as e:
        print(json.dumps({'verdict':'FAIL','error':str(e)}, indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
